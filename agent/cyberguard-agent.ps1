# Cyber HealthGuard AI - Windows Endpoint Agent
# PowerShell script to monitor Windows endpoints

param(
    [string]$ApiUrl = "http://localhost:8000",
    [string]$OrgId = "org_001",
    [int]$Interval = 60
)

$ErrorActionPreference = "Continue"
$LogFile = "$env:ProgramData\CyberGuardAgent\agent.log"

# Create log directory if it doesn't exist
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

        # No backticks, single-line call to avoid parsing issues
        $response = Invoke-RestMethod -Uri ("{0}/ingest/logs" -f $ApiUrl) -Method Post -Headers $headers -Body $payload -TimeoutSec 10

        Write-Log "✓ Sent $EventType event"
        return $true
    }
    catch {
        Write-Log "✗ Failed to send $EventType event: $($_.Exception.Message)"
        return $false
    }
}

function Collect-SystemInfo {
    Write-Log "Collecting system information..."

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
}

function Collect-LoginAttempts {
    Write-Log "Checking login attempts..."

    # Get failed login events from last 1 minute
    $startTime = (Get-Date).AddMinutes(-1)

    try {
        $failedLogins = Get-WinEvent -FilterHashtable @{
            LogName   = 'Security'
            Id        = 4625  # Failed login
            StartTime = $startTime
        } -MaxEvents 10 -ErrorAction SilentlyContinue

        foreach ($event in $failedLogins) {
            $details = @{
                success        = $false
                ip_address     = ($event.Properties[19].Value -replace '\s', '')
                failure_reason = "Invalid credentials"
                event_id       = $event.Id
                workstation    = $event.Properties[13].Value
            }

            $user = $event.Properties[5].Value
            Send-Event -EventType "login" -Source "Windows_Security" -Details $details -User $user
        }
    }
    catch {
        # No failed logins or access denied
    }
}

function Collect-RunningProcesses {
    Write-Log "Collecting process information..."

    $processes = Get-Process | Sort-Object CPU -Descending | Select-Object -First 10
    $topProcesses = ($processes | Select-Object -ExpandProperty Name) -join ","

    $details = @{
        total_processes   = (Get-Process).Count
        top_processes     = $topProcesses
        collection_method = "Get-Process"
    }

    Send-Event -EventType "process_snapshot" -Source "agent" -Details $details -User "SYSTEM"
}

function Check-SuspiciousProcesses {
    Write-Log "Checking for suspicious processes..."

    $suspiciousNames = @(
        "mimikatz", "procdump", "pwdump", "nc", "netcat",
        "psexec", "cobalt", "meterpreter", "empire"
    )

    $allProcesses = Get-Process

    foreach ($suspicious in $suspiciousNames) {
        $found = $allProcesses | Where-Object { $_.Name -like "*$suspicious*" }

        if ($found) {
            foreach ($proc in $found) {
                $pathValue = "Access Denied"
                try {
                    $pathValue = $proc.Path
                }
                catch { }

                $details = @{
                    suspicious_pattern = $suspicious
                    process_name       = $proc.Name
                    process_id         = $proc.Id
                    path               = $pathValue
                    severity           = "high"
                }

                Send-Event -EventType "suspicious_process" -Source "agent" -Details $details -User "SYSTEM"
                Write-Log "⚠️  Suspicious process detected: $($proc.Name)"
            }
        }
    }
}

function Check-NetworkConnections {
    Write-Log "Checking network connections..."

    $established = (Get-NetTCPConnection -State Established -ErrorAction SilentlyContinue).Count
    $listening   = (Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue).Count

    # Check for unusual ports
    $unusualPorts = @(4444, 5555, 6666, 7777, 8888, 9999)
    $unusualConnections = Get-NetTCPConnection -State Established -ErrorAction SilentlyContinue |
        Where-Object { $unusualPorts -contains $_.RemotePort }

    $details = @{
        established_connections   = $established
        listening_ports           = $listening
        unusual_port_connections  = $unusualConnections.Count
    }

    Send-Event -EventType "network_snapshot" -Source "agent" -Details $details -User "SYSTEM"

    if ($unusualConnections.Count -gt 0) {
        Write-Log "⚠️  Detected $($unusualConnections.Count) connections to unusual ports"
    }
}

function Check-UserAccounts {
    Write-Log "Checking user accounts..."

    $localUsers   = Get-LocalUser | Measure-Object
    $enabledUsers = (Get-LocalUser | Where-Object { $_.Enabled -eq $true }).Count
    $adminUsers   = (Get-LocalGroupMember -Group "Administrators" -ErrorAction SilentlyContinue).Count

    $details = @{
        total_users   = $localUsers.Count
        enabled_users = $enabledUsers
        admin_users   = $adminUsers
    }

    Send-Event -EventType "user_audit" -Source "agent" -Details $details -User "SYSTEM"
}

function Check-WindowsDefender {
    Write-Log "Checking Windows Defender status..."

    try {
        $defender = Get-MpComputerStatus

        $details = @{
            antivirus_enabled   = $defender.AntivirusEnabled
            realtime_protection = $defender.RealTimeProtectionEnabled
            signature_age_days  = $defender.AntivirusSignatureAge
            last_scan           = $defender.LastFullScanEndTime
            threat_detections   = $defender.NISSignatureVersion
        }

        Send-Event -EventType "antivirus_status" -Source "Windows_Defender" -Details $details -User "SYSTEM"

        if (-not $defender.RealTimeProtectionEnabled) {
            Write-Log "⚠️  Real-time protection is DISABLED"
        }
    }
    catch {
        Write-Log "Could not check Windows Defender status"
    }
}

function Check-WindowsUpdates {
    Write-Log "Checking Windows updates..."

    try {
        $session  = New-Object -ComObject Microsoft.Update.Session
        $searcher = $session.CreateUpdateSearcher()
        $updates  = $searcher.Search("IsInstalled=0")

        $securityUpdates = ($updates.Updates | Where-Object {
            $_.Categories | Where-Object { $_.Name -like "*Security*" }
        }).Count

        $details = @{
            pending_updates          = $updates.Updates.Count
            pending_security_updates = $securityUpdates
            last_check               = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        }

        Send-Event -EventType "security_updates" -Source "Windows_Update" -Details $details -User "SYSTEM"

        if ($securityUpdates -gt 0) {
            Write-Log "⚠️  $securityUpdates security updates available"
        }
    }
    catch {
        Write-Log "Could not check Windows updates"
    }
}

function Check-Firewall {
    Write-Log "Checking Windows Firewall..."

    try {
        $profiles = Get-NetFirewallProfile

        foreach ($profile in $profiles) {
            $details = @{
                profile_name           = $profile.Name
                enabled                = $profile.Enabled
                default_inbound_action = $profile.DefaultInboundAction
                default_outbound_action= $profile.DefaultOutboundAction
            }

            Send-Event -EventType "firewall_status" -Source "Windows_Firewall" -Details $details -User "SYSTEM"

            if (-not $profile.Enabled) {
                Write-Log "⚠️  Firewall profile '$($profile.Name)' is DISABLED"
            }
        }
    }
    catch {
        Write-Log "Could not check firewall status"
    }
}

# Main monitoring loop
Write-Log "========================================"
Write-Log "Cyber HealthGuard AI Agent Starting"
Write-Log "API URL: $ApiUrl"
Write-Log "Organisation: $OrgId"
Write-Log "Hostname: $env:COMPUTERNAME"
Write-Log "Interval: $Interval seconds"
Write-Log "========================================"

while ($true) {
    Write-Log "--- Collection cycle started ---"

    try {
        Collect-SystemInfo
        Collect-LoginAttempts
        Collect-RunningProcesses
        Check-SuspiciousProcesses
        Check-NetworkConnections
        Check-UserAccounts
        Check-WindowsDefender
        Check-WindowsUpdates
        Check-Firewall
    }
    catch {
        Write-Log "Error in collection cycle: $($_.Exception.Message)"
    }

    Write-Log "--- Collection cycle completed ---"
    Write-Log "Sleeping for $Interval seconds..."
    Start-Sleep -Seconds $Interval
}
