# MITRE ATT&CK Framework Integration Design
## Threat Detection and Response

This document outlines the design for MITRE ATT&CK framework integration in Cyber HealthGuard AI.

---

## Overview

MITRE ATT&CK is a globally-accessible knowledge base of adversary tactics and techniques based on real-world observations. This integration maps endpoint telemetry to ATT&CK techniques for threat detection and response.

**Implementation Strategy:**
- 20 high-impact techniques covering all tactics
- Behaviour-based detection rules
- Automated technique identification from logs
- Threat likelihood scoring
- AI-powered analyst summaries
- Automated response recommendations

---

## Selected MITRE ATT&CK Techniques

### Tactic: Initial Access

#### T1078 - Valid Accounts
**Name:** Valid Accounts
**Description:** Adversaries use legitimate credentials to gain initial access, maintain persistence, and escalate privileges.

**Detection via Endpoint Data:**
- Failed login attempts followed by success
- Login from unusual location/IP
- Login outside normal working hours
- Multiple account logins from same IP
- Dormant account suddenly active

**Detection Rule:**
```python
def detect_t1078(log_events):
    suspicious_patterns = [
        # Pattern 1: Failed logins then success
        (failed_login_count > 5 and successful_login within 10 minutes),

        # Pattern 2: Unusual location
        (login_location not in user.normal_locations),

        # Pattern 3: Unusual time
        (login_hour < 6 or login_hour > 22) and not in user.shift_hours,

        # Pattern 4: Dormant account
        (days_since_last_login > 90 and sudden_activity)
    ]
    return any(suspicious_patterns)
```

**Severity:** HIGH
**Likelihood Score:** 75 (when multiple indicators present)

**AI Explanation:**
"This account shows signs of credential compromise. The login pattern deviates from the user's historical behaviour, including access from an unusual location and outside normal working hours. These indicators suggest an attacker may have obtained valid credentials through phishing or credential stuffing."

**Recommended Mitigation:**
- Force password reset for affected account
- Enable MFA if not already active
- Review account activity for unauthorized actions
- Check for lateral movement to other systems
- Implement geolocation-based access controls
- Deploy UEBA (User and Entity Behaviour Analytics)

---

#### T1566 - Phishing
**Name:** Phishing
**Sub-techniques:** Spearphishing Attachment (T1566.001), Spearphishing Link (T1566.002)

**Detection via Endpoint Data:**
- Email with suspicious attachment opened
- Click on URL in email followed by credential prompt
- Office macro execution from email attachment
- Browser download from email link
- Process spawned from Office application

**Detection Rule:**
```python
def detect_t1566(log_events, email_logs, process_logs):
    indicators = []

    # Attachment-based
    if email_has_attachment(email_logs):
        if attachment_type in ['.exe', '.scr', '.bat', '.vbs', '.js', '.doc', '.xls']:
            if file_executed_within(process_logs, minutes=5):
                indicators.append('suspicious_attachment_execution')

    # Link-based
    if email_contains_url(email_logs):
        if user_clicked_link(email_logs):
            if credential_prompt_appeared(process_logs, minutes=2):
                indicators.append('credential_harvesting_attempt')

    # Macro execution
    if office_macro_executed(process_logs):
        if parent_process == 'outlook.exe':
            indicators.append('macro_from_email')

    return len(indicators) > 0, indicators
```

**Severity:** CRITICAL
**Likelihood Score:** 90 (with multiple indicators)

**AI Explanation:**
"A phishing attack is in progress. The user opened an email attachment that executed a macro, which spawned suspicious processes. This is a common malware delivery mechanism. The attachment may contain ransomware, banking trojans, or remote access tools."

**Recommended Mitigation:**
- Immediately isolate the affected endpoint from network
- Quarantine the malicious email from all mailboxes
- Run full antivirus scan on affected system
- Review other emails from same sender across organisation
- Block sender domain at email gateway
- Conduct forensic analysis of executed files
- Provide immediate security awareness training to user
- Implement attachment sandboxing for email

---

### Tactic: Execution

#### T1059 - Command and Scripting Interpreter
**Name:** Command and Scripting Interpreter
**Sub-techniques:** PowerShell (T1059.001), Windows Command Shell (T1059.003), Python (T1059.006)

**Detection via Endpoint Data:**
- PowerShell execution with encoded commands
- CMD.exe spawned by Office applications
- Suspicious script execution (unusual parent process)
- Obfuscated command lines
- PowerShell download cradles

**Detection Rule:**
```python
def detect_t1059(process_logs):
    powershell_indicators = [
        '-encodedcommand' in cmdline,
        '-enc' in cmdline and len(cmdline) > 100,
        'IEX' in cmdline,  # Invoke-Expression
        'DownloadString' in cmdline,
        'Net.WebClient' in cmdline,
        'Start-Process' in cmdline and '-Hidden' in cmdline
    ]

    cmd_indicators = [
        parent_process in ['winword.exe', 'excel.exe', 'powerpnt.exe'],
        '/c' in cmdline and 'echo' not in cmdline,
        'certutil' in cmdline and '-decode' in cmdline,
        'bitsadmin' in cmdline and '/transfer' in cmdline
    ]

    return (
        any(powershell_indicators) and process_name == 'powershell.exe'
    ) or (
        any(cmd_indicators) and process_name == 'cmd.exe'
    )
```

**Severity:** HIGH
**Likelihood Score:** 80

**AI Explanation:**
"Suspicious scripting activity detected. An attacker is using encoded PowerShell commands to evade detection. This technique is commonly used for downloading additional malware, credential theft, or establishing persistence. The obfuscation indicates malicious intent."

**Recommended Mitigation:**
- Enable PowerShell script block logging
- Implement PowerShell Constrained Language Mode
- Block PowerShell execution for standard users
- Use application whitelisting (AppLocker/WDAC)
- Monitor and alert on encoded commands
- Investigate parent process that spawned scripting interpreter
- Collect PowerShell command history for forensics

---

### Tactic: Persistence

#### T1053 - Scheduled Task/Job
**Name:** Scheduled Task/Job
**Sub-techniques:** At (T1053.002), Cron (T1053.003), Scheduled Task (T1053.005)

**Detection via Endpoint Data:**
- New scheduled task created outside normal hours
- Scheduled task pointing to unusual executable location
- Task created by non-administrative tool
- Task with high privilege but created by low-privilege user
- Task frequency set to very short intervals

**Detection Rule:**
```python
def detect_t1053(task_creation_events):
    suspicious_indicators = []

    if task_created_time.hour not in range(8, 18):
        suspicious_indicators.append('unusual_creation_time')

    if task_executable_path in [
        'C:\\Users\\*\\AppData\\',
        'C:\\Windows\\Temp\\',
        'C:\\ProgramData\\'
    ]:
        suspicious_indicators.append('suspicious_executable_location')

    if task_trigger_frequency < 60:  # Less than 1 hour
        suspicious_indicators.append('high_frequency_execution')

    if task_runs_as == 'SYSTEM' and created_by_user != 'SYSTEM':
        suspicious_indicators.append('privilege_escalation')

    if creating_process not in [
        'schtasks.exe',
        'taskschd.msc',
        'taskeng.exe'
    ]:
        suspicious_indicators.append('unusual_creation_method')

    return len(suspicious_indicators) >= 2, suspicious_indicators
```

**Severity:** MEDIUM
**Likelihood Score:** 70

**AI Explanation:**
"A scheduled task was created with suspicious characteristics, indicating possible persistence mechanism. Attackers create scheduled tasks to maintain access even after system reboots. The task location and frequency suggest automated malicious activity."

**Recommended Mitigation:**
- Review and delete unauthorized scheduled tasks
- Enable scheduled task creation auditing
- Restrict scheduled task creation to administrators
- Monitor for tasks in user-writable directories
- Implement least privilege for scheduled tasks
- Regularly audit all scheduled tasks for legitimacy

---

### Tactic: Privilege Escalation

#### T1003 - OS Credential Dumping
**Name:** OS Credential Dumping
**Sub-techniques:** LSASS Memory (T1003.001), Security Account Manager (T1003.002), NTDS (T1003.003)

**Detection via Endpoint Data:**
- Process accessing LSASS memory
- Tools like mimikatz, procdump, comsvcs.dll usage
- Registry access to SAM database
- NTDS.dit file access
- Unusual access to credential stores

**Detection Rule:**
```python
def detect_t1003(process_logs, file_access_logs):
    credential_dump_indicators = []

    # LSASS memory access
    if target_process == 'lsass.exe':
        if access_type == 'PROCESS_VM_READ':
            if source_process not in [
                'svchost.exe',
                'csrss.exe',
                'wininit.exe'
            ]:
                credential_dump_indicators.append('lsass_memory_access')

    # Mimikatz detection
    mimikatz_patterns = [
        'sekurlsa::logonpasswords',
        'lsadump::sam',
        'kerberos::golden',
        'misc::memssp'
    ]
    if any(pattern in cmdline for pattern in mimikatz_patterns):
        credential_dump_indicators.append('mimikatz_detected')

    # Procdump on LSASS
    if 'procdump' in process_name and 'lsass' in cmdline:
        credential_dump_indicators.append('procdump_lsass')

    # Registry SAM access
    if file_path == 'C:\\Windows\\System32\\config\\SAM':
        if access_type == 'READ':
            credential_dump_indicators.append('sam_database_access')

    # NTDS.dit access
    if file_path.endswith('ntds.dit'):
        if source_process != 'lsass.exe':
            credential_dump_indicators.append('ntds_dit_access')

    return len(credential_dump_indicators) > 0, credential_dump_indicators
```

**Severity:** CRITICAL
**Likelihood Score:** 95

**AI Explanation:**
"CRITICAL: Credential dumping activity detected. An attacker is attempting to extract credentials from memory or registry, likely using tools like Mimikatz. This is typically performed after initial compromise to escalate privileges and enable lateral movement. Immediate containment required."

**Recommended Mitigation:**
- IMMEDIATE: Isolate affected system from network
- Force password reset for all accounts on compromised system
- Enable Credential Guard on Windows 10/11 systems
- Implement LSASS protection (RunAsPPL)
- Deploy EDR with memory protection
- Hunt for lateral movement indicators
- Review all privileged account activity
- Consider domain-wide password reset if domain admin compromised

---

#### T1068 - Exploitation for Privilege Escalation
**Name:** Exploitation for Privilege Escalation

**Detection via Endpoint Data:**
- Known CVE exploitation patterns
- Unusual process privilege escalation
- Service exploitation
- DLL hijacking indicators
- Kernel driver loading

**Detection Rule:**
```python
def detect_t1068(process_logs, driver_logs):
    indicators = []

    # Process privilege change
    if process_integrity_level changed from 'Medium' to 'High':
        if process_name not in ['runas.exe', 'UAC prompts']:
            indicators.append('unexpected_privilege_escalation')

    # Known exploit patterns
    exploit_patterns = {
        'CVE-2021-1675': ['C:\\Windows\\System32\\spoolsv.exe', 'RpcAddPrinterDriverEx'],
        'CVE-2020-0796': ['srv2.sys', 'SMBv3'],
        'CVE-2019-0708': ['rdpcorets.dll', 'BlueKeep']
    }

    for cve, pattern in exploit_patterns.items():
        if all(p in process_data for p in pattern):
            indicators.append(f'exploit_{cve}_detected')

    # Unsigned driver loading
    if driver_loaded and not driver_signed:
        indicators.append('unsigned_driver_load')

    return len(indicators) > 0, indicators
```

**Severity:** CRITICAL
**Likelihood Score:** 85

**AI Explanation:**
"A privilege escalation exploit has been detected. The attacker is leveraging a known vulnerability to gain SYSTEM or Administrator privileges. This indicates an advanced attacker who can now fully control the compromised system."

**Recommended Mitigation:**
- Immediately patch the exploited vulnerability
- Isolate affected system
- Review patch status across all systems
- Deploy virtual patching if patch not available
- Enable exploit protection features (Windows Defender Exploit Guard)
- Implement application whitelisting
- Monitor for additional exploitation attempts

---

### Tactic: Defense Evasion

#### T1070 - Indicator Removal on Host
**Name:** Indicator Removal on Host
**Sub-techniques:** Clear Windows Event Logs (T1070.001), File Deletion (T1070.004)

**Detection via Endpoint Data:**
- Event log clearing
- Large number of file deletions
- Shadow copy deletion
- Timestomping (file timestamp modification)
- Registry deletion

**Detection Rule:**
```python
def detect_t1070(event_logs, file_logs):
    evasion_indicators = []

    # Event log clearing
    if event_id == 1102:  # Security log cleared
        evasion_indicators.append('security_log_cleared')

    if event_id == 104:  # System log cleared
        evasion_indicators.append('system_log_cleared')

    # Shadow copy deletion
    if 'vssadmin' in cmdline and 'delete shadows' in cmdline:
        evasion_indicators.append('shadow_copy_deletion')

    if 'wmic' in cmdline and 'shadowcopy delete' in cmdline:
        evasion_indicators.append('shadow_copy_deletion')

    # Mass file deletion
    if file_deletion_count > 100 within 60 seconds:
        evasion_indicators.append('mass_file_deletion')

    # Timestomping
    if file_modified_time < file_created_time:
        evasion_indicators.append('timestamp_manipulation')

    return len(evasion_indicators) > 0, evasion_indicators
```

**Severity:** HIGH
**Likelihood Score:** 75

**AI Explanation:**
"An attacker is attempting to cover their tracks by clearing logs and deleting evidence. This typically occurs after credential theft or data exfiltration. The deletion of shadow copies also indicates potential ransomware preparation."

**Recommended Mitigation:**
- Enable centralized log forwarding to prevent local deletion
- Implement log immutability with WORM storage
- Enable Protected Event Logging
- Monitor for vssadmin and wmic usage
- Restrict log clearing to administrator accounts
- Implement file integrity monitoring (FIM)
- Preserve forensic evidence before system cleanup

---

#### T1562 - Impair Defenses
**Name:** Impair Defenses
**Sub-techniques:** Disable or Modify Tools (T1562.001), Disable Windows Event Logging (T1562.002)

**Detection via Endpoint Data:**
- Antivirus/EDR service stopped
- Windows Defender disabled
- Firewall disabled
- Event log service stopped
- Security software uninstalled

**Detection Rule:**
```python
def detect_t1562(service_logs, registry_logs):
    defense_impairment = []

    # AV/EDR service stopped
    av_services = ['WinDefend', 'SentinelAgent', 'CrowdStrike', 'CarbonBlack']
    if service_name in av_services and service_status == 'stopped':
        defense_impairment.append(f'{service_name}_disabled')

    # Windows Defender disabled via registry
    if registry_path == 'HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender':
        if value_name == 'DisableAntiSpyware' and value_data == 1:
            defense_impairment.append('defender_disabled')

    # Firewall disabled
    if 'netsh' in cmdline and 'firewall' in cmdline and 'off' in cmdline:
        defense_impairment.append('firewall_disabled')

    # Event log service manipulation
    if service_name == 'EventLog' and service_status == 'stopped':
        defense_impairment.append('event_logging_disabled')

    return len(defense_impairment) > 0, defense_impairment
```

**Severity:** CRITICAL
**Likelihood Score:** 90

**AI Explanation:**
"CRITICAL: Security controls are being actively disabled by an attacker. This is a clear indicator of advanced malware or human-operated attack. The attacker is preparing the environment for malicious activity without detection."

**Recommended Mitigation:**
- IMMEDIATE: Isolate system from network
- Force re-enable security services
- Implement tamper protection for security software
- Alert SOC for immediate investigation
- Collect memory dump before further action
- Review all recent system changes
- Implement application control to prevent security tool manipulation

---

### Tactic: Credential Access

#### T1110 - Brute Force
**Name:** Brute Force
**Sub-techniques:** Password Guessing (T1110.001), Password Cracking (T1110.002), Password Spraying (T1110.003)

**Detection via Endpoint Data:**
- Multiple failed login attempts
- Failed logins across multiple accounts from same source
- Rapid authentication attempts
- Dictionary attack patterns
- Account lockouts

**Detection Rule:**
```python
def detect_t1110(auth_logs):
    brute_force_indicators = []

    # Multiple failed logins - single account
    if failed_login_count > 10 within 5 minutes:
        brute_force_indicators.append('password_guessing')

    # Password spraying - multiple accounts
    unique_accounts_failed = count(distinct usernames with failed auth)
    if unique_accounts_failed > 5 from same_source_ip within 30 minutes:
        brute_force_indicators.append('password_spraying')

    # Rapid attempts
    if auth_attempts_per_second > 5:
        brute_force_indicators.append('automated_brute_force')

    # Account lockouts
    if account_lockout_count > 3 within 1 hour:
        brute_force_indicators.append('brute_force_lockouts')

    return len(brute_force_indicators) > 0, brute_force_indicators
```

**Severity:** HIGH
**Likelihood Score:** 80

**AI Explanation:**
"A brute force attack is underway. An attacker is systematically attempting to guess passwords for multiple accounts. Password spraying detected - attacker is using common passwords across many accounts to avoid lockouts."

**Recommended Mitigation:**
- Block source IP at firewall
- Enable account lockout policy (5 failed attempts)
- Implement MFA for all accounts
- Deploy CAPTCHA for authentication
- Enable rate limiting on authentication endpoints
- Monitor for successful logins after failed attempts
- Implement geolocation-based access controls

---

### Tactic: Discovery

#### T1082 - System Information Discovery
**Name:** System Information Discovery

**Detection via Endpoint Data:**
- System info commands (systeminfo, hostname, whoami)
- Network configuration queries (ipconfig, route)
- Environment variable enumeration
- Installed software enumeration

**Detection Rule:**
```python
def detect_t1082(process_logs):
    discovery_commands = [
        'systeminfo',
        'hostname',
        'whoami',
        'set',  # Environment variables
        'ipconfig /all',
        'net config',
        'wmic computersystem',
        'wmic os'
    ]

    discovery_score = 0
    commands_executed = []

    for cmd in discovery_commands:
        if cmd in cmdline:
            discovery_score += 10
            commands_executed.append(cmd)

    # Multiple discovery commands in sequence
    if len(commands_executed) >= 3 within 5 minutes:
        discovery_score += 30

    return discovery_score >= 30, commands_executed
```

**Severity:** MEDIUM
**Likelihood Score:** 60

**AI Explanation:**
"An attacker is performing reconnaissance on the compromised system. Multiple system discovery commands indicate an adversary learning about the environment to plan lateral movement or privilege escalation."

**Recommended Mitigation:**
- Monitor for command sequences typical of reconnaissance
- Implement command-line logging
- Deploy EDR with behaviour analytics
- Investigate process that spawned discovery commands
- Review recent authentication events for initial access
- Check for follow-on lateral movement activity

---

#### T1057 - Process Discovery
**Name:** Process Discovery

**Detection via Endpoint Data:**
- Tasklist command execution
- Process enumeration via API
- WMI queries for processes
- PowerShell Get-Process usage

**Detection Rule:**
```python
def detect_t1057(process_logs):
    indicators = []

    process_discovery_commands = [
        'tasklist',
        'Get-Process',
        'wmic process',
        'ps' if is_powershell_session else None
    ]

    if any(cmd in cmdline for cmd in process_discovery_commands):
        indicators.append('process_enumeration_command')

    # API-based discovery
    if api_call == 'CreateToolhelp32Snapshot':
        indicators.append('process_snapshot_api')

    # Targeting specific security processes
    security_processes = ['av', 'defender', 'carbon', 'sentinel', 'crowdstrike']
    if any(proc in cmdline.lower() for proc in security_processes):
        indicators.append('security_process_targeting')

    return len(indicators) > 0, indicators
```

**Severity:** LOW
**Likelihood Score:** 50

**AI Explanation:**
"Process discovery activity detected. The attacker is identifying running security tools and potential targets. This is typically followed by defense evasion or privilege escalation attempts."

**Recommended Mitigation:**
- Log all process enumeration activities
- Monitor for targeting of security processes
- Deploy EDR with visibility into API calls
- Implement least privilege to limit process visibility
- Alert on unusual process discovery patterns

---

### Tactic: Lateral Movement

#### T1021 - Remote Services
**Name:** Remote Services
**Sub-techniques:** Remote Desktop Protocol (T1021.001), SMB/Windows Admin Shares (T1021.002), SSH (T1021.004), WinRM (T1021.006)

**Detection via Endpoint Data:**
- RDP connections to multiple systems
- Admin share access (C$, ADMIN$)
- PsExec usage
- WinRM connections
- SSH connections from unusual sources

**Detection Rule:**
```python
def detect_t1021(network_logs, auth_logs):
    lateral_movement_indicators = []

    # RDP lateral movement
    if protocol == 'RDP':
        if destination_count > 3 within 1 hour:
            lateral_movement_indicators.append('rdp_lateral_movement')

    # Admin share access
    if share_name in ['C$', 'ADMIN$', 'IPC$']:
        if source_ip != expected_admin_system:
            lateral_movement_indicators.append('admin_share_access')

    # PsExec detection
    if 'psexesvc.exe' in process_name:
        lateral_movement_indicators.append('psexec_lateral_movement')

    if file_path == '\\\\*\\ADMIN$\\*' and contains('psexec'):
        lateral_movement_indicators.append('psexec_deployment')

    # WinRM
    if protocol == 'WinRM' and auth_type == 'NTLM':
        if source not in authorized_winrm_hosts:
            lateral_movement_indicators.append('winrm_lateral_movement')

    return len(lateral_movement_indicators) > 0, lateral_movement_indicators
```

**Severity:** HIGH
**Likelihood Score:** 85

**AI Explanation:**
"Lateral movement detected across your network. An attacker with compromised credentials is accessing multiple systems. This represents a significant breach requiring immediate containment to prevent further spread."

**Recommended Mitigation:**
- IMMEDIATE: Isolate source and destination systems
- Disable compromised account credentials
- Review authentication logs for all accessed systems
- Enable network segmentation to limit lateral movement
- Implement RDP/WinRM restrictions via firewall rules
- Deploy deception technology (honeypots) to detect lateral movement
- Force MFA for all remote access protocols

---

#### T1080 - Taint Shared Content
**Name:** Taint Shared Content

**Detection via Endpoint Data:**
- File writes to network shares
- Modification of shared documents
- DLL writes to shared directories
- Script files placed in startup folders

**Detection Rule:**
```python
def detect_t1080(file_logs):
    indicators = []

    # Files written to network shares
    if file_path.startswith('\\\\'):
        if file_extension in ['.exe', '.dll', '.scr', '.bat', '.vbs', '.js']:
            indicators.append('executable_on_network_share')

    # Startup folder modification
    startup_paths = [
        '\\*\\Start Menu\\Programs\\Startup\\',
        '\\*\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\'
    ]

    if any(path in file_path for path in startup_paths):
        indicators.append('startup_folder_modification')

    # Common shared locations
    if file_path in [
        '\\\\*\\NETLOGON\\',
        '\\\\*\\SYSVOL\\',
        '\\\\*\\Public\\'
    ]:
        if action == 'write':
            indicators.append('shared_location_taint')

    return len(indicators) > 0, indicators
```

**Severity:** MEDIUM
**Likelihood Score:** 65

**AI Explanation:**
"An attacker is placing malicious files on shared network resources to infect other users who access them. This technique enables passive lateral movement as unsuspecting users execute the malicious files."

**Recommended Mitigation:**
- Scan all network shares for malicious files
- Implement write restrictions on shared folders
- Enable file integrity monitoring on shared resources
- Deploy network share access logging
- Educate users not to execute files from shared drives
- Implement application whitelisting

---

### Tactic: Collection

#### T1005 - Data from Local System
**Name:** Data from Local System

**Detection via Endpoint Data:**
- Bulk file access to sensitive directories
- Archive creation (zip, rar, 7z) of documents
- Clipboard access
- Screenshot capture
- Browser data theft

**Detection Rule:**
```python
def detect_t1005(file_logs, process_logs):
    collection_indicators = []

    sensitive_directories = [
        'Documents',
        'Desktop',
        'Downloads',
        'AppData',
        'OneDrive',
        'Dropbox'
    ]

    # Bulk file access
    files_accessed = count(file_access within 5 minutes)
    if files_accessed > 50:
        if any(dir in file_paths for dir in sensitive_directories):
            collection_indicators.append('bulk_file_access')

    # Archive creation
    if process_name in ['7z.exe', 'winrar.exe', 'tar.exe']:
        if archive_size > 100MB:
            collection_indicators.append('large_archive_creation')

    # Browser data access
    browser_data_paths = [
        'AppData\\Local\\Google\\Chrome\\User Data',
        'AppData\\Roaming\\Mozilla\\Firefox\\Profiles'
    ]

    if any(path in file_path for path in browser_data_paths):
        if process_name not in ['chrome.exe', 'firefox.exe']:
            collection_indicators.append('browser_data_theft')

    return len(collection_indicators) > 0, collection_indicators
```

**Severity:** HIGH
**Likelihood Score:** 75

**AI Explanation:**
"Data collection activity detected. An attacker is gathering sensitive files and preparing them for exfiltration. The creation of large archives and bulk file access indicate data theft in progress."

**Recommended Mitigation:**
- Identify and quarantine created archives
- Enable Data Loss Prevention (DLP) controls
- Monitor for subsequent exfiltration attempts
- Review files accessed for classification/sensitivity
- Implement file access auditing
- Enable encryption for sensitive data at rest
- Restrict archive utility usage to authorized users

---

### Tactic: Exfiltration

#### T1041 - Exfiltration Over C2 Channel
**Name:** Exfiltration Over C2 Channel

**Detection via Endpoint Data:**
- Large outbound data transfers
- Unusual destination IPs/domains
- Encrypted traffic to suspicious destinations
- Beaconing behaviour
- DNS tunnelling

**Detection Rule:**
```python
def detect_t1041(network_logs):
    exfiltration_indicators = []

    # Large outbound transfer
    if outbound_bytes > 100MB within 10 minutes:
        if destination_ip not in known_cloud_providers:
            exfiltration_indicators.append('large_outbound_transfer')

    # Unusual destination
    if destination_reputation == 'malicious' or 'suspicious':
        exfiltration_indicators.append('connection_to_malicious_ip')

    # Beaconing detection
    connection_intervals = calculate_intervals(connection_timestamps)
    if is_regular_pattern(connection_intervals):  # e.g., every 60 seconds
        exfiltration_indicators.append('c2_beaconing')

    # DNS tunnelling
    if dns_query_length > 100:
        if dns_query_frequency > 50 per minute:
            exfiltration_indicators.append('dns_tunnelling')

    # Unusual protocols
    if protocol not in ['HTTP', 'HTTPS'] and data_size > 10MB:
        exfiltration_indicators.append('unusual_protocol_large_transfer')

    return len(exfiltration_indicators) > 0, exfiltration_indicators
```

**Severity:** CRITICAL
**Likelihood Score:** 90

**AI Explanation:**
"CRITICAL: Data exfiltration in progress. An attacker is transferring stolen data out of your network. The connection pattern and volume indicate an active breach. Immediate action required to prevent data loss."

**Recommended Mitigation:**
- IMMEDIATE: Block destination IP at firewall
- Isolate source system from network
- Capture network traffic for forensics
- Identify exfiltrated data type and classification
- Enable DLP rules to block sensitive data egress
- Implement egress filtering at network perimeter
- Review all outbound connections for additional exfiltration
- Notify legal/compliance teams if PCD/PII exfiltrated

---

#### T1048 - Exfiltration Over Alternative Protocol
**Name:** Exfiltration Over Alternative Protocol
**Sub-techniques:** Exfiltration Over DNS (T1048.003)

**Detection via Endpoint Data:**
- DNS queries with encoded data
- FTP/FTPS unusual activity
- ICMP tunnelling
- Non-HTTP/HTTPS large transfers

**Detection Rule:**
```python
def detect_t1048(network_logs):
    indicators = []

    # DNS exfiltration
    if protocol == 'DNS':
        if query_length > 60:  # Suspiciously long
            if query_frequency > 20 per minute:
                indicators.append('dns_exfiltration')

    # FTP exfiltration
    if protocol == 'FTP':
        if direction == 'outbound' and bytes_transferred > 10MB:
            if destination not in known_ftp_servers:
                indicators.append('ftp_exfiltration')

    # ICMP tunnelling
    if protocol == 'ICMP':
        if packet_size > 64:  # Unusual ICMP size
            if icmp_traffic > 1MB within 5 minutes:
                indicators.append('icmp_tunnelling')

    return len(indicators) > 0, indicators
```

**Severity:** HIGH
**Likelihood Score:** 80

**AI Explanation:**
"An attacker is using alternative protocols to exfiltrate data, likely to evade standard DLP controls. DNS tunnelling or ICMP covert channels indicate a sophisticated adversary."

**Recommended Mitigation:**
- Deploy DNS security filtering
- Block unnecessary outbound protocols (FTP, ICMP large packets)
- Implement protocol-aware DLP
- Monitor for protocol anomalies
- Enable DNS query logging and analysis
- Deploy network behaviour analysis tools

---

### Tactic: Impact

#### T1486 - Data Encrypted for Impact (Ransomware)
**Name:** Data Encrypted for Impact

**Detection via Endpoint Data:**
- Rapid file modifications/renames
- File extension changes (.encrypted, .locked, .crypted)
- Shadow copy deletion
- Ransom note creation
- High CPU usage from encryption

**Detection Rule:**
```python
def detect_t1486(file_logs, process_logs):
    ransomware_indicators = []

    # Mass file encryption
    if file_modification_count > 100 within 1 minute:
        ransomware_indicators.append('mass_file_modification')

    # File extension changes
    suspicious_extensions = ['.encrypted', '.locked', '.crypted', '.enc', '.crypto']
    if any(ext in new_file_extension for ext in suspicious_extensions):
        ransomware_indicators.append('encryption_extension_change')

    # Ransom note detection
    ransom_note_names = [
        'README.txt',
        'HOW_TO_DECRYPT.txt',
        'DECRYPT_INSTRUCTIONS.txt',
        'RECOVER_FILES.txt'
    ]
    if filename in ransom_note_names and file_created:
        ransomware_indicators.append('ransom_note_created')

    # Shadow copy deletion (preparation for ransomware)
    if 'vssadmin delete shadows' in cmdline:
        ransomware_indicators.append('shadow_copy_deletion')

    # High CPU usage
    if process_cpu_usage > 80 and process_name not in known_intensive_processes:
        if file_io_operations > 1000 per minute:
            ransomware_indicators.append('intensive_encryption_activity')

    return len(ransomware_indicators) >= 2, ransomware_indicators
```

**Severity:** CRITICAL
**Likelihood Score:** 95

**AI Explanation:**
"CRITICAL: RANSOMWARE DETECTED! Mass file encryption is in progress. Immediate isolation required to prevent spread. Shadow copies have been deleted, limiting recovery options. This is an active ransomware incident requiring emergency response."

**Recommended Mitigation:**
- IMMEDIATE: Isolate ALL affected systems from network
- Do NOT power off systems (preserves memory for forensics)
- Activate incident response plan
- Disable all network shares to prevent spread
- Identify ransomware variant from ransom note
- Check for available decryption tools
- Restore from backups if available
- Do NOT pay ransom without consulting legal/law enforcement
- Notify law enforcement (FBI, NCSC)
- Engage ransomware negotiation specialist if needed

---

#### T1490 - Inhibit System Recovery
**Name:** Inhibit System Recovery

**Detection via Endpoint Data:**
- Backup deletion
- System restore disabled
- Recovery partition deletion
- Boot configuration modification

**Detection Rule:**
```python
def detect_t1490(process_logs):
    recovery_inhibition = []

    # Backup deletion
    if 'wbadmin' in cmdline and 'delete' in cmdline:
        recovery_inhibition.append('backup_deletion')

    # System restore disabled
    if 'vssadmin delete shadows /all' in cmdline:
        recovery_inhibition.append('shadow_copy_deletion')

    # Boot config modification
    if 'bcdedit' in cmdline and ('recoveryenabled no' in cmdline or 'bootstatuspolicy ignoreallfailures' in cmdline):
        recovery_inhibition.append('boot_recovery_disabled')

    # Recovery partition deletion
    if 'diskpart' in cmdline and 'delete partition' in cmdline:
        recovery_inhibition.append('recovery_partition_deletion')

    return len(recovery_inhibition) > 0, recovery_inhibition
```

**Severity:** CRITICAL
**Likelihood Score:** 90

**AI Explanation:**
"CRITICAL: An attacker is destroying recovery mechanisms. This is typically performed immediately before deploying ransomware to prevent recovery without paying ransom. Emergency response required."

**Recommended Mitigation:**
- IMMEDIATE: Isolate system before encryption begins
- Check offsite/offline backups immediately
- Do not rely on local system restore
- Deploy emergency backup validation
- Hunt for ransomware payload before execution
- Enable boot recovery options if not yet executed

---

## AI Threat Diagnosis Workflow

### Step 1: Log Parsing and Normalization
```python
def parse_endpoint_logs(raw_logs):
    """
    Parse raw endpoint logs into structured format
    Normalize fields across different log sources
    """
    normalized_events = []

    for log in raw_logs:
        event = {
            'timestamp': parse_timestamp(log),
            'host': extract_hostname(log),
            'user': extract_user(log),
            'process': extract_process_info(log),
            'network': extract_network_info(log),
            'file': extract_file_info(log),
            'registry': extract_registry_info(log),
            'event_type': classify_event_type(log)
        }
        normalized_events.append(event)

    return normalized_events
```

### Step 2: Technique Matching
```python
def match_mitre_techniques(events):
    """
    Match normalized events against MITRE ATT&CK detection rules
    Returns list of detected techniques with confidence scores
    """
    detected_techniques = []

    for technique in mitre_techniques:
        detection_result = technique.detection_rule(events)

        if detection_result['detected']:
            detected_techniques.append({
                'technique_id': technique.id,
                'technique_name': technique.name,
                'confidence': detection_result['confidence'],
                'indicators': detection_result['indicators'],
                'evidence': detection_result['matching_events'],
                'severity': technique.severity,
                'tactic': technique.tactic
            })

    return detected_techniques
```

### Step 3: Threat Likelihood Scoring
```python
def calculate_threat_likelihood(detected_techniques, context):
    """
    Calculate overall threat likelihood based on:
    - Number of techniques detected
    - Technique severities
    - Temporal correlation
    - Environmental context
    """

    # Base score from techniques
    base_score = sum(t['confidence'] * severity_weights[t['severity']]
                     for t in detected_techniques)

    # Temporal correlation bonus
    time_window_bonus = 0
    if techniques_detected_within(detected_techniques, minutes=10):
        time_window_bonus = 20  # Rapid succession indicates active attack

    # Attack chain detection
    attack_chain_bonus = 0
    if forms_attack_chain(detected_techniques):
        attack_chain_bonus = 30  # Techniques span multiple tactics

    # Environmental factors
    environment_multiplier = 1.0
    if context['asset_criticality'] == 'high':
        environment_multiplier = 1.3
    if context['user_privilege'] == 'admin':
        environment_multiplier *= 1.2

    final_score = min(100,
        (base_score + time_window_bonus + attack_chain_bonus) * environment_multiplier
    )

    return {
        'likelihood_score': final_score,
        'risk_level': score_to_risk_level(final_score),
        'confidence': calculate_confidence(detected_techniques)
    }
```

### Step 4: AI Analyst Summary Generation
```python
def generate_ai_summary(detected_techniques, threat_score, context):
    """
    Generate natural language summary in analyst style
    """

    # Identify attack narrative
    attack_chain = identify_attack_chain(detected_techniques)

    summary = {
        'executive_summary': generate_executive_summary(attack_chain, threat_score),
        'detailed_analysis': generate_detailed_analysis(detected_techniques),
        'iocs': extract_indicators(context['events']),
        'affected_assets': identify_affected_assets(context),
        'timeline': construct_attack_timeline(detected_techniques),
        'attacker_profile': infer_attacker_profile(attack_chain)
    }

    return summary

def generate_executive_summary(attack_chain, threat_score):
    """
    Example output:
    'A sophisticated multi-stage attack has been detected with high confidence (85/100).
     The attacker gained initial access via phishing (T1566), escalated privileges using
     credential dumping (T1003), and is attempting lateral movement via RDP (T1021).
     This pattern is consistent with ransomware deployment. Immediate containment required.'
    """
    pass
```

### Step 5: Automated Response Recommendations
```python
def generate_response_recommendations(detected_techniques, threat_score):
    """
    Provide prioritized response actions based on detected techniques
    """

    recommendations = []

    # Critical immediate actions
    if threat_score['risk_level'] == 'critical':
        recommendations.append({
            'priority': 1,
            'action': 'Immediate network isolation of affected systems',
            'automated': True,
            'automation_confidence': 0.95
        })

    # Technique-specific responses
    for technique in detected_techniques:
        technique_responses = get_technique_mitigations(technique['technique_id'])
        for response in technique_responses:
            recommendations.append({
                'priority': calculate_priority(response, technique['severity']),
                'action': response['description'],
                'automated': response['automatable'],
                'automation_confidence': response['confidence'],
                'technique': technique['technique_name']
            })

    # Sort by priority
    recommendations.sort(key=lambda x: x['priority'])

    return recommendations
```

---

## JSON Schemas

### MITRE ATT&CK Detection Schema
```json
{
  "mitre_detection": {
    "detection_id": "string (UUID)",
    "organisation_id": "string",
    "timestamp": "ISO8601 datetime",
    "host": "string",
    "user": "string",
    "techniques_detected": [
      {
        "technique_id": "string (e.g., T1003)",
        "technique_name": "string",
        "tactic": "string",
        "sub_technique": "string (optional)",
        "confidence_score": "number (0-100)",
        "severity": "low|medium|high|critical",
        "indicators": [
          {
            "indicator_type": "process|file|network|registry",
            "indicator_value": "string",
            "timestamp": "ISO8601 datetime"
          }
        ],
        "evidence_logs": [
          {
            "log_id": "string",
            "log_source": "string",
            "relevant_fields": "object"
          }
        ],
        "ai_explanation": "string",
        "recommended_mitigations": ["string"]
      }
    ],
    "threat_assessment": {
      "likelihood_score": "number (0-100)",
      "risk_level": "low|medium|high|critical",
      "confidence": "number (0-1)",
      "attack_chain_detected": "boolean",
      "temporal_correlation": "boolean"
    },
    "ai_summary": {
      "executive_summary": "string",
      "detailed_analysis": "string",
      "attacker_profile": "string",
      "timeline": [
        {
          "timestamp": "ISO8601 datetime",
          "technique": "string",
          "action": "string"
        }
      ]
    },
    "iocs": {
      "ip_addresses": ["string"],
      "domains": ["string"],
      "file_hashes": ["string"],
      "file_paths": ["string"],
      "registry_keys": ["string"],
      "processes": ["string"]
    },
    "response_recommendations": [
      {
        "priority": "number (1-10)",
        "action": "string",
        "automated": "boolean",
        "automation_confidence": "number (0-1)",
        "status": "pending|in_progress|completed"
      }
    ],
    "status": "active|investigating|contained|resolved"
  }
}
```

### MITRE Technique Mapping Schema
```json
{
  "mitre_technique": {
    "technique_id": "string (e.g., T1003)",
    "technique_name": "string",
    "tactic": "string",
    "sub_techniques": [
      {
        "id": "string (e.g., T1003.001)",
        "name": "string"
      }
    ],
    "description": "string",
    "detection_rule": {
      "data_sources": ["string"],
      "detection_logic": "string (pseudocode)",
      "indicators": ["string"]
    },
    "severity": "low|medium|high|critical",
    "likelihood_base_score": "number (0-100)",
    "ai_explanation": "string",
    "real_world_examples": ["string"],
    "recommended_mitigations": [
      {
        "mitigation_id": "string",
        "description": "string",
        "automated": "boolean",
        "effectiveness": "number (0-100)"
      }
    ],
    "related_techniques": ["string"],
    "platforms": ["Windows|Linux|macOS|Cloud"],
    "data_sources": ["Process monitoring|File monitoring|Network traffic"],
    "permissions_required": ["User|Administrator|SYSTEM"]
  }
}
```

---

## UI Components Design Specifications

See separate UI design document for:
- MITRE ATT&CK Heatmap component
- Active Threat Techniques panel
- AI Threat Summary dashboard
- Recommended Mitigations widget

---

This framework provides comprehensive MITRE ATT&CK-based threat detection integrated with AI-powered analysis and automated response recommendations.
