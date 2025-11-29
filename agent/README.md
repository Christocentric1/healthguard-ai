# Cyber HealthGuard AI - Endpoint Agent

Deploy this agent on your endpoints (laptops, servers, workstations) to monitor security events and compliance in real-time on your Cyber HealthGuard AI dashboard.

## 🎯 What It Does

The endpoint agent collects and reports:
- ✅ **System Information**: OS, IP address, uptime
- 🔐 **Login Attempts**: Failed authentication events
- 💻 **Running Processes**: Active processes and suspicious executables
- 🌐 **Network Connections**: Established connections and unusual ports
- 📁 **File Integrity**: Changes to critical system files
- 👥 **User Accounts**: User and admin account audits
- 🛡️ **Security Posture**: Firewall, antivirus, and update status

All data is sent to your Cyber HealthGuard AI backend for:
- AI-powered anomaly detection
- MITRE ATT&CK threat mapping
- DSPT/HIPAA/GDPR compliance scoring
- Real-time alerting

## 📋 Prerequisites

### For Linux/Unix Servers:
- Root/sudo access (for full monitoring capabilities)
- `curl` installed
- `systemd` (for automatic startup)
- Python 3 (optional, for enhanced monitoring)

### For Windows Laptops/Servers:
- Administrator access
- PowerShell 5.1 or higher
- Windows 7/Server 2008 R2 or newer

## 🚀 Quick Start

### Option 1: Linux/Unix (Ubuntu, Debian, CentOS, RHEL)

#### 1. Deploy Backend API (if not already done)

On your home server:
```bash
cd /path/to/cyber-guardian-ai
./deploy-backend.sh
# Select option 2: Test Backend Locally with Docker
```

This starts the API at `http://YOUR_SERVER_IP:8000`

#### 2. Install Agent on Endpoints

On each laptop/server you want to monitor:

```bash
# Download agent files
cd /tmp
wget https://your-repo.com/agent/install-agent.sh
wget https://your-repo.com/agent/cyberguard-agent.sh

# Or copy from your repo
# scp user@server:/path/to/cyber-guardian-ai/agent/*.sh /tmp/

# Make executable
chmod +x install-agent.sh cyberguard-agent.sh

# Run installer
sudo ./install-agent.sh
```

**During installation, provide:**
- **API URL**: `http://YOUR_HOME_SERVER_IP:8000` (your backend API)
- **Organisation ID**: `org_001` (or your org ID)
- **Interval**: `60` (seconds between data collection)

The installer will:
- ✅ Create `/opt/cyberguard-agent/` directory
- ✅ Install agent scripts
- ✅ Create systemd service for auto-start
- ✅ Start monitoring immediately

#### 3. Verify Installation

```bash
# Check agent status
sudo systemctl status cyberguard-agent

# View real-time logs
sudo journalctl -u cyberguard-agent -f

# Check if data is being sent
sudo tail -f /var/log/cyberguard-agent.log
```

---

### Option 2: Windows (Laptop/Desktop)

#### 1. Download Agent Script

Download `cyberguard-agent.ps1` to your computer:
- From your repo: `\\server\share\cyber-guardian-ai\agent\cyberguard-agent.ps1`
- Or copy from GitHub/repository

#### 2. Run as Administrator

Open **PowerShell as Administrator**:

```powershell
# Navigate to agent directory
cd C:\path\to\downloaded\agent

# Test run (temporary)
.\cyberguard-agent.ps1 `
    -ApiUrl "http://YOUR_HOME_SERVER_IP:8000" `
    -OrgId "org_001" `
    -Interval 60
```

#### 3. Install as Windows Service (Optional)

For permanent monitoring:

```powershell
# Install NSSM (Non-Sucking Service Manager)
# Download from: https://nssm.cc/download

# Create service
nssm install CyberGuardAgent "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"

# Set parameters
nssm set CyberGuardAgent AppParameters `
    "-ExecutionPolicy Bypass -File C:\CyberGuardAgent\cyberguard-agent.ps1 -ApiUrl http://YOUR_SERVER:8000 -OrgId org_001 -Interval 60"

# Start service
nssm start CyberGuardAgent

# Check status
nssm status CyberGuardAgent
```

---

## 🖥️ Example: Home Network Setup

**Scenario**: Monitor your laptop and home server

### 1. Backend on Home Server (Ubuntu)

```bash
# On your home server (192.168.1.10)
cd ~/cyber-guardian-ai
./deploy-backend.sh
# Select option 2: Test Backend Locally

# Backend now running at: http://192.168.1.10:8000
```

### 2. Agent on Home Server (Monitor Itself)

```bash
# On same home server
cd agent
sudo ./install-agent.sh

# When prompted:
# API URL: http://localhost:8000
# Org ID: org_001
# Interval: 60
```

### 3. Agent on Your Laptop (Windows)

```powershell
# On your Windows laptop
cd C:\Downloads\cyber-guardian-ai\agent

.\cyberguard-agent.ps1 `
    -ApiUrl "http://192.168.1.10:8000" `
    -OrgId "org_001" `
    -Interval 60
```

### 4. View Dashboard

Open browser and go to your frontend:
- **Frontend URL**: `http://192.168.1.10:3000` (or Netlify URL)
- **Check Endpoints**: Navigate to "Endpoints" page
- **View Compliance**: Check DSPT/HIPAA/GDPR scores
- **Monitor Threats**: Check MITRE ATT&CK page for detections

You should now see:
- 📊 **2 endpoints** listed (server + laptop)
- 🚨 **Alerts** for suspicious activity
- ✅ **Compliance scores** based on endpoint data
- 🎯 **MITRE techniques** detected

---

## ⚙️ Configuration

### Agent Configuration File (Linux)

Located at: `/opt/cyberguard-agent/config.env`

```bash
API_URL=http://your-server:8000
ORG_ID=org_001
INTERVAL=60
HOSTNAME=WKS-001
```

Edit and restart:
```bash
sudo nano /opt/cyberguard-agent/config.env
sudo systemctl restart cyberguard-agent
```

### Agent Parameters (Windows)

Pass as command-line arguments:
```powershell
.\cyberguard-agent.ps1 -ApiUrl "http://server:8000" -OrgId "org_001" -Interval 60
```

---

## 🔍 What Gets Monitored

### System Events
- Operating system and version
- IP address and network info
- System uptime
- Architecture

### Security Events
- ❌ Failed login attempts
- 🔒 Suspicious process execution (mimikatz, procdump, netcat, etc.)
- 🌐 Network connections to unusual ports (4444, 5555, etc.)
- 📝 Modifications to critical files (/etc/passwd, sudoers, etc.)
- 👤 User account changes
- 🛡️ Firewall status
- 🦠 Antivirus status
- 📦 Pending security updates

### Windows-Specific
- Windows Defender status
- Windows Update status
- Local user accounts
- Firewall profiles

---

## 🚨 Alerts & Detection

The agent sends data to the backend, which performs:

1. **Rule-Based Detection**
   - Failed login threshold (default: 5 attempts)
   - Suspicious process patterns
   - Critical file modifications

2. **AI Anomaly Detection**
   - Machine learning (Isolation Forest)
   - Behavioral analysis
   - Anomaly scoring

3. **MITRE ATT&CK Mapping**
   - Credential dumping (T1003)
   - Process injection (T1055)
   - Command execution (T1059)
   - And 17+ more techniques

4. **Compliance Scoring**
   - DSPT (NHS) compliance
   - HIPAA controls
   - GDPR requirements
   - Cyber Essentials

---

## 🛠️ Management Commands

### Linux

```bash
# Check status
sudo systemctl status cyberguard-agent

# Start/Stop/Restart
sudo systemctl start cyberguard-agent
sudo systemctl stop cyberguard-agent
sudo systemctl restart cyberguard-agent

# View logs
sudo journalctl -u cyberguard-agent -f
sudo tail -f /var/log/cyberguard-agent.log

# Disable auto-start
sudo systemctl disable cyberguard-agent

# Uninstall
sudo systemctl stop cyberguard-agent
sudo systemctl disable cyberguard-agent
sudo rm -rf /opt/cyberguard-agent
sudo rm /etc/systemd/system/cyberguard-agent.service
```

### Windows

```powershell
# If running as service (with NSSM)
nssm status CyberGuardAgent
nssm stop CyberGuardAgent
nssm start CyberGuardAgent
nssm restart CyberGuardAgent

# View logs
Get-Content "$env:ProgramData\CyberGuardAgent\agent.log" -Tail 50 -Wait

# Uninstall service
nssm stop CyberGuardAgent
nssm remove CyberGuardAgent confirm
```

---

## 🐛 Troubleshooting

### Agent Not Sending Data

1. **Check API connectivity**:
   ```bash
   curl -I http://YOUR_SERVER_IP:8000/health
   ```
   Should return: `HTTP/1.1 200 OK`

2. **Check firewall**:
   - Ensure port 8000 is open on your backend server
   - Check laptop/server firewall allows outbound connections

3. **Check agent logs**:
   ```bash
   # Linux
   sudo journalctl -u cyberguard-agent -n 50

   # Windows
   Get-Content "$env:ProgramData\CyberGuardAgent\agent.log" -Tail 50
   ```

### Endpoints Not Showing on Dashboard

1. **Verify API is receiving data**:
   - Check backend logs: `docker-compose logs -f` (if using Docker)
   - Check database: Logs should appear in MongoDB `logs` collection

2. **Check organisation ID**:
   - Agent `ORG_ID` must match your dashboard login org ID
   - Default: `org_001`

3. **Frontend using mock data**:
   - Check `.env.local`: Should have `VITE_USE_MOCK_DATA=false`
   - Check `VITE_API_URL` points to your backend

### Permission Denied Errors (Linux)

```bash
# Agent needs root for full access
sudo systemctl restart cyberguard-agent

# Check file permissions
ls -la /var/log/auth.log
ls -la /etc/shadow
```

### High CPU Usage

- Increase monitoring interval:
  ```bash
  # Edit config
  sudo nano /opt/cyberguard-agent/config.env
  # Change: INTERVAL=300  (5 minutes)
  sudo systemctl restart cyberguard-agent
  ```

---

## 🔐 Security Considerations

### Data Privacy
- Agent only collects security-relevant metadata
- No personal file contents are transmitted
- No passwords or credentials are collected
- Process names and commands are truncated (200 chars)

### Network Security
- Use HTTPS in production (configure reverse proxy)
- Restrict API access with firewall rules
- Use organization-based authentication
- Consider VPN for remote endpoints

### Agent Security
- Runs as root/SYSTEM (required for security monitoring)
- Scripts are auditable (view source before installation)
- Systemd service prevents unauthorized execution
- Logs are local and transmitted over authenticated channels

---

## 📊 Example Dashboard View

After deploying agents, your dashboard will show:

### Endpoints Page
```
┌─────────────────────────────────────────────────────┐
│ ENDPOINTS (2)                                       │
├─────────────┬────────────┬──────────┬───────────────┤
│ Hostname    │ Risk Score │ Status   │ Last Seen     │
├─────────────┼────────────┼──────────┼───────────────┤
│ HOME-SERVER │ 85 (HIGH)  │ 🔴 5     │ 1 min ago     │
│ MY-LAPTOP   │ 42 (MED)   │ 🟡 2     │ 2 mins ago    │
└─────────────┴────────────┴──────────┴───────────────┘
```

### Compliance Page (DSPT Tab)
```
┌─────────────────────────────────────────────────────┐
│ DSPT COMPLIANCE SCORE: 72%                          │
│                                                     │
│ Personal Data:           ✅ 85% Compliant          │
│ Managing Data Access:    ⚠️  65% Partial           │
│ Cyber Security:          ✅ 78% Compliant          │
│ Staff Training:          ❌ 45% Non-Compliant      │
└─────────────────────────────────────────────────────┘
```

### MITRE ATT&CK Page
```
┌─────────────────────────────────────────────────────┐
│ ACTIVE DETECTIONS (2)                               │
│                                                     │
│ 🔴 CRITICAL: OS Credential Dumping (T1003)         │
│    Host: MY-LAPTOP | User: john.smith              │
│    AI Analysis: Credential dumping tool detected   │
│                                                     │
│ 🟡 MEDIUM: PowerShell Execution (T1059.001)        │
│    Host: HOME-SERVER | User: admin                 │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 Next Steps

1. **Deploy backend** on your home server
2. **Install agents** on all endpoints you want to monitor
3. **Configure frontend** to connect to your backend API
4. **Monitor dashboard** for security events and compliance
5. **Tune detection rules** based on your environment
6. **Set up alerting** (email/Slack notifications - optional)

---

## 📖 Additional Resources

- **Backend API Docs**: `http://YOUR_SERVER:8000/docs`
- **Deployment Guide**: `../DEPLOYMENT_GUIDE.md`
- **DSPT Framework**: `../DSPT_FRAMEWORK_DESIGN.md`
- **MITRE ATT&CK**: `../MITRE_ATTACK_DESIGN.md`

---

## 💡 Tips

- Start with a longer interval (300 seconds) and decrease as needed
- Monitor your server resources when adding many endpoints
- Use HTTPS with Let's Encrypt for production deployments
- Consider log rotation for `/var/log/cyberguard-agent.log`
- Test agent on one endpoint before mass deployment

---

## 🆘 Support

For issues or questions:
1. Check logs: `sudo journalctl -u cyberguard-agent -f`
2. Verify API health: `curl http://SERVER:8000/health`
3. Review this README
4. Check main project documentation

---

**🛡️ Happy Monitoring! Your endpoints are now protected by Cyber HealthGuard AI.**
