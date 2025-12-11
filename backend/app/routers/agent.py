"""Agent installation and download endpoints"""
from fastapi import APIRouter, Query
from fastapi.responses import PlainTextResponse

router = APIRouter(tags=["Agent"])


WINDOWS_AGENT_SCRIPT = r'''# Cyber HealthGuard AI - Windows Endpoint Agent
# Simple version that works with /api/ingest/logs endpoint

param(
    [string]$ApiUrl = "http://localhost:8000",
    [string]$OrgId = "org_001",
    [int]$Interval = 60
)

$ErrorActionPreference = "Continue"
$LogFile = "$env:ProgramData\CyberGuardAgent\agent.log"

# Create log directory
$LogDir = Split-Path $LogFile -Parent
if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    Write-Host $logMessage
    Add-Content -Path $LogFile -Value $logMessage
}

function Send-Event {
    param(
        [string]$EventType,
        [string]$Source,
        [hashtable]$Details,
        [string]$User = $env:USERNAME
    )

    $timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $hostname = $env:COMPUTERNAME

    $payload = @{
        organisation_id = $OrgId
        host            = $hostname
        user            = $User
        timestamp       = $timestamp
        event_type      = $EventType
        source          = $Source
        details         = $Details
    } | ConvertTo-Json -Depth 10

    try {
        $headers = @{
            "Content-Type" = "application/json"
            "X-Org-Id"     = $OrgId
        }

        $response = Invoke-RestMethod -Uri "$ApiUrl/api/ingest/logs" -Method Post -Headers $headers -Body $payload -TimeoutSec 10
        Write-Log "Sent $EventType event"
        return $true
    }
    catch {
        Write-Log "Failed to send $EventType`: $($_.Exception.Message)"
        return $false
    }
}

Write-Log "========================================"
Write-Log "Cyber HealthGuard AI Agent Starting"
Write-Log "API URL: $ApiUrl"
Write-Log "Organisation: $OrgId"
Write-Log "Hostname: $env:COMPUTERNAME"
Write-Log "Interval: $Interval seconds"
Write-Log "========================================"

while ($true) {
    Write-Log "--- Collection cycle started ---"

    # System Info
    Write-Log "Collecting system information..."
    try {
        $os = Get-CimInstance Win32_OperatingSystem
        $computer = Get-CimInstance Win32_ComputerSystem
        $ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -ne "127.0.0.1" } | Select-Object -First 1).IPAddress

        $details = @{
            os            = $os.Caption
            os_version    = $os.Version
            ip_address    = $ip
            uptime_hours  = [math]::Round((New-TimeSpan -Start $os.LastBootUpTime).TotalHours, 2)
            architecture  = $env:PROCESSOR_ARCHITECTURE
            domain        = $computer.Domain
        }
        Send-Event -EventType "system_info" -Source "agent" -Details $details -User "SYSTEM"
    } catch {
        Write-Log "Error collecting system info: $($_.Exception.Message)"
    }

    # Process Info
    Write-Log "Collecting process information..."
    try {
        $processes = Get-Process | Sort-Object CPU -Descending | Select-Object -First 10
        $topProcesses = ($processes | Select-Object -ExpandProperty Name) -join ","

        $details = @{
            total_processes   = (Get-Process).Count
            top_processes     = $topProcesses
            collection_method = "Get-Process"
        }
        Send-Event -EventType "process_snapshot" -Source "agent" -Details $details -User "SYSTEM"
    } catch {
        Write-Log "Error collecting process info: $($_.Exception.Message)"
    }

    # Check for suspicious processes
    Write-Log "Checking for suspicious processes..."
    $suspiciousPatterns = @("mimikatz", "procdump", "pwdump", "netcat", "nc.exe", "psexec")
    foreach ($pattern in $suspiciousPatterns) {
        $found = Get-Process | Where-Object { $_.Name -like "*$pattern*" }
        if ($found) {
            $details = @{
                suspicious_pattern = $pattern
                process_name       = $found.Name
                severity           = "high"
            }
            Send-Event -EventType "suspicious_process" -Source "agent" -Details $details -User "SYSTEM"
            Write-Log "WARNING: Suspicious process detected - $pattern"
        }
    }

    # Network connections
    Write-Log "Collecting network information..."
    try {
        $connections = Get-NetTCPConnection -State Established -ErrorAction SilentlyContinue
        $details = @{
            established_connections = ($connections | Measure-Object).Count
            listening_ports         = (Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Measure-Object).Count
        }
        Send-Event -EventType "network_snapshot" -Source "agent" -Details $details -User "SYSTEM"
    } catch {
        Write-Log "Error collecting network info: $($_.Exception.Message)"
    }

    # Security status
    Write-Log "Checking security status..."
    try {
        $defender = Get-MpComputerStatus -ErrorAction SilentlyContinue
        if ($defender) {
            $details = @{
                antivirus_enabled     = $defender.AntivirusEnabled
                realtime_protection   = $defender.RealTimeProtectionEnabled
                antispyware_enabled   = $defender.AntispywareEnabled
                signature_age_days    = $defender.AntivirusSignatureAge
            }
            Send-Event -EventType "security_status" -Source "defender" -Details $details -User "SYSTEM"
        }
    } catch {
        Write-Log "Error checking security status: $($_.Exception.Message)"
    }

    # Failed logins (requires admin and Security log access)
    Write-Log "Checking failed logins..."
    try {
        $failedLogins = Get-WinEvent -FilterHashtable @{LogName='Security';Id=4625} -MaxEvents 5 -ErrorAction SilentlyContinue
        foreach ($event in $failedLogins) {
            $details = @{
                success        = $false
                failure_reason = "Invalid credentials"
                event_id       = 4625
            }
            Send-Event -EventType "login" -Source "security_log" -Details $details -User "unknown"
        }
    } catch {
        # This often fails without admin rights - that's ok
    }

    Write-Log "--- Collection cycle completed ---"
    Write-Log "Sleeping for $Interval seconds..."
    Start-Sleep -Seconds $Interval
}
'''


WINDOWS_INSTALLER_TEMPLATE = r'''# Cyber HealthGuard AI - Windows Agent Installer
# Downloads and installs the endpoint monitoring agent

param(
    [Parameter(Mandatory=$false)]
    [string]$Server = "{server_url}",
    
    [Parameter(Mandatory=$false)]
    [string]$OrgId = "{org_id}",
    
    [Parameter(Mandatory=$false)]
    [int]$Interval = 60,
    
    [Parameter(Mandatory=$false)]
    [switch]$AsService = $false
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Cyber HealthGuard AI - Agent Installer   " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Validate parameters
if ([string]::IsNullOrEmpty($Server) -or $Server -eq "{server_url}") {{
    Write-Host "ERROR: Server URL is required." -ForegroundColor Red
    Write-Host "Usage: .\install.ps1 -Server https://your-server.com -OrgId your_org_id" -ForegroundColor Yellow
    exit 1
}}

if ([string]::IsNullOrEmpty($OrgId) -or $OrgId -eq "{org_id}") {{
    Write-Host "ERROR: Organisation ID is required." -ForegroundColor Red
    Write-Host "Usage: .\install.ps1 -Server https://your-server.com -OrgId your_org_id" -ForegroundColor Yellow
    exit 1
}}

Write-Host "Configuration:" -ForegroundColor Green
Write-Host "  Server URL: $Server"
Write-Host "  Organisation ID: $OrgId"
Write-Host "  Interval: $Interval seconds"
Write-Host ""

# Create installation directory
$InstallDir = "$env:ProgramData\CyberGuardAgent"
Write-Host "Creating installation directory: $InstallDir" -ForegroundColor Yellow

if (!(Test-Path $InstallDir)) {{
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}}

# Download the agent script
Write-Host "Downloading agent script..." -ForegroundColor Yellow
$AgentUrl = "$Server/agent/cyberguard-agent.ps1"
$AgentPath = "$InstallDir\cyberguard-agent.ps1"

try {{
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $AgentUrl -OutFile $AgentPath -UseBasicParsing
    Write-Host "  Downloaded agent to: $AgentPath" -ForegroundColor Green
}} catch {{
    Write-Host "ERROR: Failed to download agent script from $AgentUrl" -ForegroundColor Red
    Write-Host "  $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}}

# Create configuration file
Write-Host "Creating configuration..." -ForegroundColor Yellow
$ConfigPath = "$InstallDir\config.ps1"
$ConfigContent = @"
# Cyber HealthGuard AI Agent Configuration
`$script:ApiUrl = "$Server"
`$script:OrgId = "$OrgId"
`$script:Interval = $Interval
"@
Set-Content -Path $ConfigPath -Value $ConfigContent
Write-Host "  Configuration saved to: $ConfigPath" -ForegroundColor Green

# Create a launcher script
$LauncherPath = "$InstallDir\start-agent.ps1"
$LauncherContent = @"
# Cyber HealthGuard AI Agent Launcher
Set-Location "$InstallDir"
& "$AgentPath" -ApiUrl "$Server" -OrgId "$OrgId" -Interval $Interval
"@
Set-Content -Path $LauncherPath -Value $LauncherContent

# Test API connectivity
Write-Host "Testing API connectivity..." -ForegroundColor Yellow
try {{
    $HealthUrl = "$Server/health"
    $response = Invoke-RestMethod -Uri $HealthUrl -Method Get -TimeoutSec 10
    if ($response.status -eq "ok") {{
        Write-Host "  API is healthy!" -ForegroundColor Green
    }}
}} catch {{
    Write-Host "  WARNING: Could not reach API at $Server/health" -ForegroundColor Yellow
    Write-Host "  The agent will retry when started." -ForegroundColor Yellow
}}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Agent installed to: $InstallDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the agent manually (run as Administrator):" -ForegroundColor Yellow
Write-Host "  & `"$LauncherPath`"" -ForegroundColor White
Write-Host ""
Write-Host "Or run directly with parameters:" -ForegroundColor Yellow
Write-Host "  & `"$AgentPath`" -ApiUrl `"$Server`" -OrgId `"$OrgId`" -Interval $Interval" -ForegroundColor White
Write-Host ""
Write-Host "To install as a Windows Service (requires NSSM):" -ForegroundColor Yellow
Write-Host "  1. Download NSSM from https://nssm.cc/download" -ForegroundColor Gray
Write-Host "  2. Run: nssm install CyberGuardAgent powershell.exe" -ForegroundColor Gray
Write-Host "  3. Set AppParameters: -ExecutionPolicy Bypass -File `"$LauncherPath`"" -ForegroundColor Gray
Write-Host ""
Write-Host "View logs at: $InstallDir\agent.log" -ForegroundColor Cyan
Write-Host ""

# Optionally start the agent now
$startNow = Read-Host "Start the agent now? (y/n)"
if ($startNow -eq "y" -or $startNow -eq "Y") {{
    Write-Host ""
    Write-Host "Starting agent..." -ForegroundColor Yellow
    Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
    Write-Host ""
    & $AgentPath -ApiUrl $Server -OrgId $OrgId -Interval $Interval
}}
'''


LINUX_INSTALLER_TEMPLATE = '''#!/bin/bash
# Cyber HealthGuard AI - Linux Agent Installer

set -e

GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
RED='\\033[0;31m'
CYAN='\\033[0;36m'
NC='\\033[0m'

echo ""
echo -e "${{CYAN}}============================================${{NC}}"
echo -e "${{CYAN}}  Cyber HealthGuard AI - Agent Installer   ${{NC}}"
echo -e "${{CYAN}}============================================${{NC}}"
echo ""

# Default values (can be overridden by environment or arguments)
SERVER="${{SERVER:-{server_url}}}"
ORG_ID="${{ORG_ID:-{org_id}}}"
INTERVAL="${{INTERVAL:-60}}"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--server)
            SERVER="$2"
            shift 2
            ;;
        -o|--org-id)
            ORG_ID="$2"
            shift 2
            ;;
        -i|--interval)
            INTERVAL="$2"
            shift 2
            ;;
        *)
            echo -e "${{RED}}Unknown option: $1${{NC}}"
            exit 1
            ;;
    esac
done

# Validate parameters
if [ -z "$SERVER" ] || [ "$SERVER" = "{{server_url}}" ]; then
    echo -e "${{RED}}ERROR: Server URL is required.${{NC}}"
    echo "Usage: curl -sSL $SERVER/install.sh | sudo bash -s -- -s https://your-server.com -o your_org_id"
    exit 1
fi

if [ -z "$ORG_ID" ] || [ "$ORG_ID" = "{{org_id}}" ]; then
    echo -e "${{RED}}ERROR: Organisation ID is required.${{NC}}"
    echo "Usage: curl -sSL $SERVER/install.sh | sudo bash -s -- -s https://your-server.com -o your_org_id"
    exit 1
fi

echo -e "${{GREEN}}Configuration:${{NC}}"
echo "  Server URL: $SERVER"
echo "  Organisation ID: $ORG_ID"
echo "  Interval: $INTERVAL seconds"
echo ""

# Check for root
if [ "$EUID" -ne 0 ]; then
    echo -e "${{YELLOW}}Warning: Running without root. Some features may be limited.${{NC}}"
fi

# Create installation directory
INSTALL_DIR="/opt/cyberguard-agent"
echo -e "${{YELLOW}}Creating installation directory: $INSTALL_DIR${{NC}}"
mkdir -p $INSTALL_DIR

# Download the agent script
echo -e "${{YELLOW}}Downloading agent script...${{NC}}"
AGENT_URL="$SERVER/agent/cyberguard-agent.sh"
curl -sSL "$AGENT_URL" -o "$INSTALL_DIR/cyberguard-agent.sh"
chmod +x "$INSTALL_DIR/cyberguard-agent.sh"
echo -e "${{GREEN}}  Downloaded agent to: $INSTALL_DIR/cyberguard-agent.sh${{NC}}"

# Create configuration file
echo -e "${{YELLOW}}Creating configuration...${{NC}}"
cat > "$INSTALL_DIR/config.env" <<EOF
# Cyber HealthGuard AI Agent Configuration
API_URL=$SERVER
ORG_ID=$ORG_ID
INTERVAL=$INTERVAL
HOSTNAME=$(hostname)
EOF
echo -e "${{GREEN}}  Configuration saved to: $INSTALL_DIR/config.env${{NC}}"

# Test API connectivity
echo -e "${{YELLOW}}Testing API connectivity...${{NC}}"
if curl -sSf "$SERVER/health" > /dev/null 2>&1; then
    echo -e "${{GREEN}}  API is healthy!${{NC}}"
else
    echo -e "${{YELLOW}}  WARNING: Could not reach API at $SERVER/health${{NC}}"
    echo -e "${{YELLOW}}  The agent will retry when started.${{NC}}"
fi

# Create systemd service if available
if command -v systemctl &> /dev/null; then
    echo -e "${{YELLOW}}Creating systemd service...${{NC}}"
    cat > /etc/systemd/system/cyberguard-agent.service <<EOF
[Unit]
Description=Cyber HealthGuard AI Endpoint Agent
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=$INSTALL_DIR/config.env
ExecStart=$INSTALL_DIR/cyberguard-agent.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable cyberguard-agent.service
    echo -e "${{GREEN}}  Systemd service created and enabled${{NC}}"
fi

echo ""
echo -e "${{GREEN}}============================================${{NC}}"
echo -e "${{GREEN}}  Installation Complete!${{NC}}"
echo -e "${{GREEN}}============================================${{NC}}"
echo ""
echo -e "${{CYAN}}Agent installed to: $INSTALL_DIR${{NC}}"
echo ""
echo -e "${{YELLOW}}To start the agent:${{NC}}"
echo "  sudo systemctl start cyberguard-agent"
echo ""
echo -e "${{YELLOW}}To check status:${{NC}}"
echo "  sudo systemctl status cyberguard-agent"
echo ""
echo -e "${{YELLOW}}To view logs:${{NC}}"
echo "  sudo journalctl -u cyberguard-agent -f"
echo ""

# Ask to start now
read -p "Start the agent now? (y/n): " START_NOW
if [ "$START_NOW" = "y" ] || [ "$START_NOW" = "Y" ]; then
    echo ""
    echo -e "${{YELLOW}}Starting agent...${{NC}}"
    systemctl start cyberguard-agent
    sleep 2
    systemctl status cyberguard-agent --no-pager | head -10
fi
'''


LINUX_AGENT_SCRIPT = r'''#!/bin/bash
# Cyber HealthGuard AI - Endpoint Monitoring Agent

# Load configuration
if [ -f "/opt/cyberguard-agent/config.env" ]; then
    source /opt/cyberguard-agent/config.env
fi

# Set defaults if not configured
API_URL=${API_URL:-"http://localhost:8000"}
ORG_ID=${ORG_ID:-"org_001"}
INTERVAL=${INTERVAL:-60}
HOSTNAME=${HOSTNAME:-$(hostname)}

LOG_FILE="/var/log/cyberguard-agent.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

send_event() {
    local event_type=$1
    local source=$2
    local details=$3
    local user=${4:-$(whoami)}

    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local payload=$(cat <<EOF
{
    "organisation_id": "$ORG_ID",
    "host": "$HOSTNAME",
    "user": "$user",
    "timestamp": "$timestamp",
    "event_type": "$event_type",
    "source": "$source",
    "details": $details
}
EOF
)

    response=$(curl -s -X POST "$API_URL/api/ingest/logs" \
        -H "Content-Type: application/json" \
        -H "X-Org-Id: $ORG_ID" \
        -d "$payload" \
        -w "\n%{http_code}" 2>&1)

    http_code=$(echo "$response" | tail -n1)

    if [ "$http_code" = "201" ] || [ "$http_code" = "200" ]; then
        log "✓ Sent $event_type event"
        return 0
    else
        log "✗ Failed to send $event_type event (HTTP $http_code)"
        return 1
    fi
}

collect_system_info() {
    log "Collecting system information..."

    local os_name=$(uname -s)
    local os_version=$(uname -r)
    local ip_address=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "unknown")
    local uptime_hours=$(awk '{print int($1/3600)}' /proc/uptime 2>/dev/null || echo 0)

    local details=$(cat <<EOF
{
    "os": "$os_name",
    "os_version": "$os_version",
    "ip_address": "$ip_address",
    "uptime_hours": $uptime_hours,
    "architecture": "$(uname -m)"
}
EOF
)

    send_event "system_info" "agent" "$details" "system"
}

collect_running_processes() {
    log "Collecting process information..."

    local top_processes=$(ps aux --sort=-%cpu 2>/dev/null | head -6 | tail -5 | awk '{print $11}' | tr '\n' ',' | sed 's/,$//' || echo "unknown")
    local process_count=$(ps aux 2>/dev/null | wc -l || echo 0)

    local details=$(cat <<EOF
{
    "total_processes": $process_count,
    "top_processes": "$top_processes",
    "collection_method": "ps"
}
EOF
)

    send_event "process_snapshot" "agent" "$details" "system"
}

check_network_connections() {
    log "Checking network connections..."

    local established=$(netstat -an 2>/dev/null | grep ESTABLISHED | wc -l || echo 0)
    local listening=$(netstat -an 2>/dev/null | grep LISTEN | wc -l || echo 0)

    local details=$(cat <<EOF
{
    "established_connections": $established,
    "listening_ports": $listening
}
EOF
)

    send_event "network_snapshot" "agent" "$details" "system"
}

# Main monitoring loop
log "========================================"
log "Cyber HealthGuard AI Agent Starting"
log "API URL: $API_URL"
log "Organisation: $ORG_ID"
log "Hostname: $HOSTNAME"
log "Interval: $INTERVAL seconds"
log "========================================"

while true; do
    log "--- Collection cycle started ---"

    collect_system_info
    collect_running_processes
    check_network_connections

    log "--- Collection cycle completed ---"
    log "Sleeping for $INTERVAL seconds..."
    sleep $INTERVAL
done
'''


@router.get("/install.ps1", response_class=PlainTextResponse)
async def get_windows_installer(
    Server: str = Query(default="", description="API server URL"),
    OrgId: str = Query(default="", description="Organisation ID"),
):
    """
    Serve the Windows PowerShell agent installer script.
    
    Usage:
        powershell -Command "& { iex (irm 'https://your-server/install.ps1?Server=https://your-server&OrgId=org_001') }"
    
    Or download and run:
        Invoke-WebRequest -Uri "https://your-server/install.ps1" -OutFile install.ps1
        ./install.ps1 -Server https://your-server -OrgId org_001
    """
    script = WINDOWS_INSTALLER_TEMPLATE.format(
        server_url=Server if Server else "{server_url}",
        org_id=OrgId if OrgId else "{org_id}"
    )
    return PlainTextResponse(content=script, media_type="text/plain")


@router.get("/install.sh", response_class=PlainTextResponse)
async def get_linux_installer(
    Server: str = Query(default="", description="API server URL"),
    OrgId: str = Query(default="", description="Organisation ID"),
):
    """
    Serve the Linux bash agent installer script.
    
    Usage:
        curl -sSL "https://your-server/install.sh?Server=https://your-server&OrgId=org_001" | sudo bash
    
    Or with arguments:
        curl -sSL https://your-server/install.sh | sudo bash -s -- -s https://your-server -o org_001
    """
    script = LINUX_INSTALLER_TEMPLATE.format(
        server_url=Server if Server else "{server_url}",
        org_id=OrgId if OrgId else "{org_id}"
    )
    return PlainTextResponse(content=script, media_type="text/plain")


@router.get("/agent/cyberguard-agent.ps1", response_class=PlainTextResponse)
async def get_windows_agent():
    """
    Serve the Windows PowerShell agent script.
    
    This is the actual monitoring agent that collects and sends security events.
    """
    return PlainTextResponse(content=WINDOWS_AGENT_SCRIPT, media_type="text/plain")


@router.get("/agent/cyberguard-agent.sh", response_class=PlainTextResponse)
async def get_linux_agent():
    """
    Serve the Linux bash agent script.
    
    This is the actual monitoring agent that collects and sends security events.
    """
    return PlainTextResponse(content=LINUX_AGENT_SCRIPT, media_type="text/plain")
