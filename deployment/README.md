# Cyber HealthGuard AI - Homelab Deployment Guide

Complete guide for deploying to your Proxmox homelab server.

## 🖥️ Server Requirements

- **Proxmox Server** (you have this ✅)
- **Ubuntu 22.04 LTS VM** with:
  - 4 CPU cores
  - 8GB RAM
  - 100GB disk
  - Static IP address

## 🚀 Quick Start

### 1. Create Ubuntu VM on Proxmox

1. Download Ubuntu 22.04 Server ISO
2. In Proxmox:
   - Create VM → 4 cores, 8GB RAM, 100GB disk
   - Install Ubuntu
   - Set hostname: `cyber-healthguard`
   - Set static IP (e.g., `192.168.1.100`)

### 2. Run Deployment Script

SSH into your VM and run:

```bash
# Download the deployment script
wget https://raw.githubusercontent.com/Christocentric1/cyber-guardian-ai/main/deployment/setup-deployment.sh

# Make it executable
chmod +x setup-deployment.sh

# Run it
./setup-deployment.sh
```

This script will:
- ✅ Install Docker & Docker Compose
- ✅ Clone the repository
- ✅ Start backend services
- ✅ Configure firewall
- ✅ Display next steps

### 3. Set Up SSL with Cloudflare

**Why Cloudflare?**
- Free SSL certificates
- DDoS protection
- Hides your home IP
- CDN for faster loading

**Steps:**

1. **Add domain to Cloudflare:**
   - Go to https://cloudflare.com (free account)
   - Add site: `cyberwavesecurity.org`
   - Follow nameserver update instructions in IONOS

2. **Get Origin Certificate:**
   - Cloudflare → SSL/TLS → Origin Server
   - Create Certificate
   - Hostnames: `cyberwavesecurity.org`, `*.cyberwavesecurity.org`
   - Validity: 15 years
   - Copy certificate and private key

3. **Save certificates on VM:**
   ```bash
   cd ~/cyber-guardian-ai/deployment/nginx
   mkdir -p ssl

   # Paste certificate
   nano ssl/cert.pem
   # (paste certificate, Ctrl+X, Y, Enter)

   # Paste private key
   nano ssl/key.pem
   # (paste key, Ctrl+X, Y, Enter)

   # Secure the files
   chmod 600 ssl/*.pem
   ```

4. **Configure Cloudflare DNS:**
   - DNS → Add record
   - Type: `A`, Name: `@`, Content: `your-public-ip`, Proxy: ✅ Enabled
   - Type: `A`, Name: `api`, Content: `your-public-ip`, Proxy: ✅ Enabled
   - Type: `CNAME`, Name: `www`, Content: `cyberwavesecurity.org`, Proxy: ✅ Enabled

5. **Set SSL mode:**
   - SSL/TLS → Overview
   - Set to: **Full (strict)**

### 4. Start Nginx Reverse Proxy

```bash
cd ~/cyber-guardian-ai/deployment/nginx
docker compose up -d

# Check it's running
docker compose ps
docker compose logs -f
```

### 5. Configure Router Port Forwarding

**Get your VM's local IP:**
```bash
hostname -I  # e.g., 192.168.1.100
```

**In your router settings:**
- Forward port `80` → `192.168.1.100:80`
- Forward port `443` → `192.168.1.100:443`

### 6. Update IONOS Nameservers

In IONOS domain management for `cyberwavesecurity.org`:
- Change nameservers to Cloudflare's (provided when you added the site)
- Example:
  - `ns1.cloudflare.com`
  - `ns2.cloudflare.com`

**DNS propagation takes 24-48 hours** (usually faster)

### 7. Test Deployment

```bash
# Get your public IP
curl ifconfig.me

# Test locally first
curl http://localhost:8000/health

# Test from internet (after DNS propagates)
curl https://api.cyberwavesecurity.org/health
```

**Open in browser:**
- API Docs: https://api.cyberwavesecurity.org/docs
- Main site: https://cyberwavesecurity.org

## 📁 Directory Structure

```
cyber-guardian-ai/
├── backend/
│   ├── app/                    # FastAPI application
│   ├── docker-compose.yml      # Backend services
│   └── scripts/
│       └── seed_data.py        # Generate test data
├── deployment/
│   ├── nginx/
│   │   ├── docker-compose.yml  # Nginx reverse proxy
│   │   ├── nginx.conf          # Nginx configuration
│   │   ├── ssl/                # SSL certificates
│   │   └── html/               # Frontend files
│   ├── setup-deployment.sh     # Automated setup script
│   └── README.md               # This file
└── frontend/                   # Frontend code (build and deploy here)
```

## 🔧 Maintenance

### View Logs

```bash
# Backend logs
cd ~/cyber-guardian-ai/backend
docker compose logs -f

# Nginx logs
cd ~/cyber-guardian-ai/deployment/nginx
docker compose logs -f nginx
```

### Restart Services

```bash
# Restart backend
cd ~/cyber-guardian-ai/backend
docker compose restart

# Restart Nginx
cd ~/cyber-guardian-ai/deployment/nginx
docker compose restart
```

### Update Application

```bash
cd ~/cyber-guardian-ai
git pull
cd backend
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Backup Database

```bash
# Backup MongoDB
docker exec cyber_healthguard_mongodb mongodump --out /tmp/backup
docker cp cyber_healthguard_mongodb:/tmp/backup ./mongodb-backup-$(date +%Y%m%d)
```

## 🔒 Security Checklist

- ✅ Firewall enabled (UFW)
- ✅ SSH key authentication (disable password auth)
- ✅ Fail2ban installed
- ✅ SSL/TLS enabled
- ✅ Cloudflare proxy enabled (hides home IP)
- ✅ Rate limiting configured
- ✅ Security headers enabled
- ✅ Regular backups scheduled

### Install Fail2ban (optional but recommended)

```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## 🌐 URLs After Deployment

| Service | URL |
|---------|-----|
| API Docs | https://api.cyberwavesecurity.org/docs |
| API Base | https://api.cyberwavesecurity.org |
| Frontend | https://cyberwavesecurity.org |
| Health Check | https://api.cyberwavesecurity.org/health |

## 🆘 Troubleshooting

### Services won't start
```bash
# Check Docker status
sudo systemctl status docker

# Check logs
docker compose logs

# Restart Docker
sudo systemctl restart docker
```

### Can't access from internet
```bash
# Check firewall
sudo ufw status

# Check if ports are open
sudo netstat -tulpn | grep -E '80|443'

# Check Nginx
docker compose ps
curl http://localhost:80
```

### SSL errors
```bash
# Verify certificates exist
ls -la deployment/nginx/ssl/

# Check Nginx config
docker exec nginx_reverse_proxy nginx -t

# Check Cloudflare SSL mode (should be "Full (strict)")
```

### DNS not resolving
```bash
# Check DNS propagation
nslookup api.cyberwavesecurity.org
dig api.cyberwavesecurity.org

# Wait for propagation (can take 24-48 hours)
```

## 📊 Monitoring

### System Resources

```bash
# CPU and RAM usage
htop

# Disk usage
df -h

# Docker stats
docker stats
```

### Application Health

```bash
# Check all services
docker compose ps

# Test API
curl https://api.cyberwavesecurity.org/health
```

## 🚀 Performance Optimization

Your hardware is powerful, but here are some optimizations:

1. **Enable MongoDB replica set** (for production)
2. **Add Redis caching** (for faster responses)
3. **Configure Nginx caching** (for static assets)
4. **Set up monitoring** (Grafana + Prometheus)

## 📝 Notes

- Your homelab specs are excellent for this application
- Consider setting up a UPS for your server
- Configure automatic backups to external storage
- Monitor bandwidth usage from your ISP
- Keep Ubuntu and Docker updated regularly

## 🎯 Next Steps

1. Deploy frontend to `deployment/nginx/html/`
2. Set up monitoring (optional)
3. Configure automated backups
4. Add more security hardening
5. Set up CI/CD pipeline

---

**Need help?** Check the logs or create an issue on GitHub.
