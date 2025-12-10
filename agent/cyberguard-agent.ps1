# Cyber HealthGuard AI - Windows Endpoint Agent
# Simple version that works with /ingest/logs endpoint

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

        $response = Invoke-RestMethod -Uri "$ApiUrl/ingest/logs" -Method Post -Headers $headers -Body $payload -TimeoutSec 10
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

    # Process Info
    Write-Log "Collecting process information..."
    $processes = Get-Process | Sort-Object CPU -Descending | Select-Object -First 10
    $topProcesses = ($processes | Select-Object -ExpandProperty Name) -join ","

    $details = @{
        total_processes   = (Get-Process).Count
        top_processes     = $topProcesses
        collection_method = "Get-Process"
    }
    Send-Event -EventType "process_snapshot" -Source "agent" -Details $details -User "SYSTEM"

    Write-Log "--- Collection cycle completed ---"
    Write-Log "Sleeping for $Interval seconds..."
    Start-Sleep -Seconds $Interval
}
