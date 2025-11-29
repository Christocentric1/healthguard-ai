#!/bin/bash
# Cyber HealthGuard AI - Endpoint Monitoring Agent
# Collects security events and sends to API

# Load configuration
if [ -f "/opt/cyberguard-agent/config.env" ]; then
    source /opt/cyberguard-agent/config.env
else
    echo "Error: Configuration file not found"
    exit 1
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

    # Construct JSON payload
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

    # Send to API
    response=$(curl -s -X POST "$API_URL/ingest/logs" \
        -H "Content-Type: application/json" \
        -H "X-Org-Id: $ORG_ID" \
        -d "$payload" \
        -w "\n%{http_code}" 2>&1)

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$http_code" = "201" ] || [ "$http_code" = "200" ]; then
        log "✓ Sent $event_type event"
        return 0
    else
        log "✗ Failed to send $event_type event (HTTP $http_code): $body"
        return 1
    fi
}

collect_system_info() {
    log "Collecting system information..."

    local os_name=$(uname -s)
    local os_version=$(uname -r)
    local ip_address=$(hostname -I | awk '{print $1}')
    local uptime_hours=$(awk '{print int($1/3600)}' /proc/uptime)

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

collect_login_attempts() {
    log "Checking login attempts..."

    # Check recent failed login attempts (last 1 minute)
    if [ -f "/var/log/auth.log" ]; then
        failed_logins=$(grep "Failed password" /var/log/auth.log 2>/dev/null | tail -5)
    elif [ -f "/var/log/secure" ]; then
        failed_logins=$(grep "Failed password" /var/log/secure 2>/dev/null | tail -5)
    else
        return
    fi

    if [ -n "$failed_logins" ]; then
        while IFS= read -r line; do
            # Extract username and IP if possible
            user=$(echo "$line" | grep -oP 'for \K[^ ]+' | head -1)
            ip=$(echo "$line" | grep -oP 'from \K[0-9.]+' | head -1)

            local details=$(cat <<EOF
{
    "success": false,
    "ip_address": "${ip:-unknown}",
    "failure_reason": "Invalid credentials",
    "log_entry": "$(echo $line | sed 's/"/\\"/g' | head -c 200)"
}
EOF
)

            send_event "login" "auth_log" "$details" "${user:-unknown}"
        done <<< "$failed_logins"
    fi
}

collect_running_processes() {
    log "Collecting process information..."

    # Get top 5 CPU-consuming processes
    local top_processes=$(ps aux --sort=-%cpu | head -6 | tail -5 | awk '{print $11}' | tr '\n' ',' | sed 's/,$//')
    local process_count=$(ps aux | wc -l)

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

check_suspicious_processes() {
    log "Checking for suspicious processes..."

    # List of suspicious process names/patterns
    suspicious_patterns=(
        "mimikatz"
        "procdump"
        "pwdump"
        "nc -l"
        "netcat"
        "/tmp/.*\.sh"
        "wget.*raw\.githubusercontent"
        "curl.*raw\.githubusercontent"
    )

    for pattern in "${suspicious_patterns[@]}"; do
        # Check if any process matches the pattern
        if pgrep -f "$pattern" > /dev/null 2>&1; then
            local proc_info=$(ps aux | grep -i "$pattern" | grep -v grep | head -1)
            local proc_user=$(echo "$proc_info" | awk '{print $1}')
            local proc_cmd=$(echo "$proc_info" | awk '{for(i=11;i<=NF;i++) printf $i" "; print ""}')

            local details=$(cat <<EOF
{
    "suspicious_pattern": "$pattern",
    "command": "$(echo $proc_cmd | sed 's/"/\\"/g' | head -c 200)",
    "severity": "high"
}
EOF
)

            send_event "suspicious_process" "agent" "$details" "$proc_user"
            log "⚠️  Suspicious process detected: $pattern"
        fi
    done
}

check_network_connections() {
    log "Checking network connections..."

    # Count established connections
    local established=$(netstat -an 2>/dev/null | grep ESTABLISHED | wc -l)
    local listening=$(netstat -an 2>/dev/null | grep LISTEN | wc -l)

    # Check for connections to unusual ports
    local unusual_ports=$(netstat -an 2>/dev/null | grep ESTABLISHED | awk '{print $4}' | grep -E ':(4444|5555|6666|7777|8888|9999)' | wc -l)

    local details=$(cat <<EOF
{
    "established_connections": $established,
    "listening_ports": $listening,
    "unusual_port_connections": $unusual_ports
}
EOF
)

    send_event "network_snapshot" "agent" "$details" "system"

    if [ $unusual_ports -gt 0 ]; then
        log "⚠️  Detected $unusual_ports connections to unusual ports"
    fi
}

check_file_integrity() {
    log "Checking critical file integrity..."

    # Check if critical files have been modified recently (last 60 minutes)
    critical_files=(
        "/etc/passwd"
        "/etc/shadow"
        "/etc/sudoers"
        "/etc/ssh/sshd_config"
    )

    for file in "${critical_files[@]}"; do
        if [ -f "$file" ]; then
            # Check if modified in last 60 minutes
            if [ $(find "$file" -mmin -60 2>/dev/null | wc -l) -gt 0 ]; then
                local mod_time=$(stat -c %Y "$file" 2>/dev/null)
                local details=$(cat <<EOF
{
    "file_path": "$file",
    "modified_time": "$mod_time",
    "severity": "high",
    "action": "modified"
}
EOF
)

                send_event "file_modification" "agent" "$details" "system"
                log "⚠️  Critical file modified: $file"
            fi
        fi
    done
}

check_user_accounts() {
    log "Checking user accounts..."

    # Count users
    local total_users=$(cat /etc/passwd | wc -l)
    local users_with_shell=$(grep -E '/bin/(ba)?sh$' /etc/passwd | wc -l)
    local sudo_users=$(getent group sudo 2>/dev/null | cut -d: -f4 | tr ',' '\n' | wc -l)

    local details=$(cat <<EOF
{
    "total_users": $total_users,
    "shell_users": $users_with_shell,
    "sudo_users": $sudo_users
}
EOF
)

    send_event "user_audit" "agent" "$details" "system"
}

check_security_updates() {
    log "Checking for security updates..."

    # For Debian/Ubuntu
    if command -v apt &> /dev/null; then
        local updates=$(apt list --upgradable 2>/dev/null | grep -i security | wc -l)
        local details=$(cat <<EOF
{
    "pending_security_updates": $updates,
    "package_manager": "apt"
}
EOF
)
        send_event "security_updates" "agent" "$details" "system"

        if [ $updates -gt 0 ]; then
            log "⚠️  $updates security updates available"
        fi
    fi

    # For RHEL/CentOS
    if command -v yum &> /dev/null; then
        local updates=$(yum list updates --security 2>/dev/null | grep -v "^Updated" | wc -l)
        local details=$(cat <<EOF
{
    "pending_security_updates": $updates,
    "package_manager": "yum"
}
EOF
)
        send_event "security_updates" "agent" "$details" "system"

        if [ $updates -gt 0 ]; then
            log "⚠️  $updates security updates available"
        fi
    fi
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

    # Collect various security events
    collect_system_info
    collect_login_attempts
    collect_running_processes
    check_suspicious_processes
    check_network_connections
    check_file_integrity
    check_user_accounts
    check_security_updates

    log "--- Collection cycle completed ---"
    log "Sleeping for $INTERVAL seconds..."
    sleep $INTERVAL
done
