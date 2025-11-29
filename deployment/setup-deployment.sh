#!/bin/bash

# Cyber HealthGuard AI - Homelab Deployment Script
# Run this on your Proxmox Ubuntu VM

set -e

echo "🚀 Cyber HealthGuard AI - Homelab Deployment"
echo "============================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
DOMAIN="cyberwavesecurity.org"
API_SUBDOMAIN="api.cyberwavesecurity.org"

# Step 1: Update system
echo -e "${GREEN}[1/7] Updating system...${NC}"
sudo apt update && sudo apt upgrade -y

# Step 2: Install Docker
echo -e "${GREEN}[2/7] Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
else
    echo "Docker already installed"
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    sudo apt install docker-compose -y
else
    echo "Docker Compose already installed"
fi

# Step 3: Install additional tools
echo -e "${GREEN}[3/7] Installing additional tools...${NC}"
sudo apt install -y git curl wget certbot python3-certbot-nginx ufw

# Step 4: Configure firewall
echo -e "${GREEN}[4/7] Configuring firewall...${NC}"
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw --force enable

# Step 5: Clone repository (if not exists)
echo -e "${GREEN}[5/7] Setting up application...${NC}"
if [ ! -d "cyber-guardian-ai" ]; then
    git clone https://github.com/Christocentric1/cyber-guardian-ai.git
fi

cd cyber-guardian-ai/backend

# Step 6: Start backend
echo -e "${GREEN}[6/7] Starting backend services...${NC}"
docker compose up -d

# Wait for services to be healthy
echo "Waiting for services to start..."
sleep 10

# Check if services are running
if docker compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Backend services are running${NC}"
else
    echo -e "${YELLOW}⚠️  Some services may not be running. Check with: docker compose ps${NC}"
fi

# Step 7: Display next steps
echo ""
echo "============================================="
echo -e "${GREEN}✅ Backend Deployment Complete!${NC}"
echo "============================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Set up SSL certificates:"
echo "   - Option A (Cloudflare Origin Certificate - Recommended):"
echo "     • Go to Cloudflare SSL/TLS → Origin Server"
echo "     • Create certificate for $DOMAIN and $API_SUBDOMAIN"
echo "     • Save cert as: deployment/nginx/ssl/cert.pem"
echo "     • Save key as: deployment/nginx/ssl/key.pem"
echo ""
echo "   - Option B (Let's Encrypt):"
echo "     • sudo certbot certonly --standalone -d $DOMAIN -d $API_SUBDOMAIN"
echo ""
echo "2. Start Nginx reverse proxy:"
echo "   cd ../deployment/nginx"
echo "   docker compose up -d"
echo ""
echo "3. Configure router port forwarding:"
echo "   • Forward port 80 → $(hostname -I | awk '{print $1}'):80"
echo "   • Forward port 443 → $(hostname -I | awk '{print $1}'):443"
echo ""
echo "4. Point domain to your home IP:"
echo "   • Get your public IP: curl ifconfig.me"
echo "   • In Cloudflare DNS:"
echo "     - A record: @ → your-public-ip"
echo "     - A record: api → your-public-ip"
echo ""
echo "5. Test deployment:"
echo "   • Local: curl http://localhost:8000/health"
echo "   • After DNS: curl https://$API_SUBDOMAIN/health"
echo ""
echo "🔗 Current status:"
echo "   Backend API: http://$(hostname -I | awk '{print $1}'):8000"
echo "   API Docs: http://$(hostname -I | awk '{print $1}'):8000/docs"
echo ""
echo "📊 Monitor logs:"
echo "   docker compose logs -f"
echo ""
