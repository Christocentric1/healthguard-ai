#!/bin/bash
# Cyber HealthGuard AI - Endpoint Agent Installer
# Install this agent on endpoints (laptops, servers) to monitor security events

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🛡️  Cyber HealthGuard AI - Endpoint Agent Installer${NC}"
echo "=========================================================="
echo ""

# Check for root/sudo
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}⚠️  This script should be run with sudo for full functionality${NC}"
    echo "Some security events require elevated privileges to collect"
    read -p "Continue anyway? (y/n): " continue
    if [ "$continue" != "y" ]; then
        exit 1
    fi
fi

# Get configuration from user
echo "📝 Configuration"
echo "----------------"
read -p "Enter your API URL (e.g., http://your-server:8000): " API_URL
read -p "Enter your Organisation ID (e.g., org_001): " ORG_ID
read -p "Enter monitoring interval in seconds (default: 60): " INTERVAL
INTERVAL=${INTERVAL:-60}

# Validate inputs
if [ -z "$API_URL" ] || [ -z "$ORG_ID" ]; then
    echo -e "${RED}❌ API URL and Organisation ID are required${NC}"
    exit 1
fi

# Create agent directory
AGENT_DIR="/opt/cyberguard-agent"
echo ""
echo "📁 Creating agent directory: $AGENT_DIR"
mkdir -p $AGENT_DIR

# Create configuration file
echo ""
echo "⚙️  Writing configuration..."
cat > $AGENT_DIR/config.env <<EOF
# Cyber HealthGuard AI Agent Configuration
API_URL=$API_URL
ORG_ID=$ORG_ID
INTERVAL=$INTERVAL
HOSTNAME=$(hostname)
EOF

# Download/copy agent script
echo ""
echo "📥 Installing agent script..."
cp "$(dirname "$0")/cyberguard-agent.sh" $AGENT_DIR/cyberguard-agent.sh
chmod +x $AGENT_DIR/cyberguard-agent.sh

# Install Python dependencies (if Python is available)
if command -v python3 &> /dev/null; then
    echo ""
    echo "🐍 Installing Python dependencies..."
    pip3 install requests psutil >/dev/null 2>&1 || echo "Warning: Could not install Python packages"
fi

# Create systemd service
echo ""
echo "🔧 Creating systemd service..."
cat > /etc/systemd/system/cyberguard-agent.service <<EOF
[Unit]
Description=Cyber HealthGuard AI Endpoint Agent
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$AGENT_DIR
EnvironmentFile=$AGENT_DIR/config.env
ExecStart=$AGENT_DIR/cyberguard-agent.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
echo ""
echo "🚀 Starting agent service..."
systemctl daemon-reload
systemctl enable cyberguard-agent.service
systemctl start cyberguard-agent.service

# Check status
echo ""
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo ""
echo "Agent Status:"
systemctl status cyberguard-agent.service --no-pager | head -10

echo ""
echo "📊 Configuration:"
echo "   API URL: $API_URL"
echo "   Organisation ID: $ORG_ID"
echo "   Hostname: $(hostname)"
echo "   Interval: $INTERVAL seconds"
echo ""
echo "🔍 Useful Commands:"
echo "   Check status:  sudo systemctl status cyberguard-agent"
echo "   View logs:     sudo journalctl -u cyberguard-agent -f"
echo "   Restart:       sudo systemctl restart cyberguard-agent"
echo "   Stop:          sudo systemctl stop cyberguard-agent"
echo "   Uninstall:     sudo systemctl stop cyberguard-agent && sudo systemctl disable cyberguard-agent"
echo ""
echo -e "${GREEN}🎉 Your endpoint is now being monitored!${NC}"
echo "Check your dashboard at: $API_URL"
