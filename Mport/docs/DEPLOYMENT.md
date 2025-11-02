# Mport Deployment Guide
# Week 2: VPS Deployment with HTTPS/Nginx Wrapper

**Status:** Ready for deployment  
**Target:** DigitalOcean VPS (Bangalore, India)  
**Domain:** mport.app  
**Cost:** FREE with GitHub Student Pack ($200 credit)

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Quick Deployment](#quick-deployment)
4. [Manual Deployment](#manual-deployment)
5. [Testing](#testing)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)
8. [Maintenance](#maintenance)

---

## 🎯 Prerequisites

### 1. GitHub Student Pack
- Sign up: https://education.github.com/pack
- Get $200 DigitalOcean credit (12 months)
- Get free .app domain from Name.com

### 2. Domain Setup
1. Claim **mport.app** from Name.com (Student Pack)
2. Point DNS to VPS IP:
   ```
   A Record:  @     → YOUR_VPS_IP
   A Record:  www   → YOUR_VPS_IP
   A Record:  *     → YOUR_VPS_IP (for subdomains)
   ```
3. Wait 5-60 minutes for DNS propagation

### 3. DigitalOcean VPS
- **Size:** Basic ($6/month) - FREE with credit
- **CPU:** 1 vCPU
- **RAM:** 1 GB
- **Storage:** 25 GB SSD
- **Transfer:** 1 TB
- **OS:** Ubuntu 22.04 LTS x64
- **Datacenter:** Bangalore, India (BLR1) - closest to Pakistan

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    MPORT DEPLOYMENT ARCHITECTURE            │
└─────────────────────────────────────────────────────────────┘

INTERNET (Port 443 HTTPS)
    │
    ├─ https://mport.app/health          → Health check
    ├─ https://mport.app/api/control     → Client control (Port 8081)
    ├─ https://mport.app/tunnel/*        → Tunnel data (Port 8082)
    ├─ https://mport.app/connect         → User connections (Port 8080)
    └─ https://mport.app/                → Web dashboard
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  NGINX REVERSE PROXY (TLS Termination)                     │
│  • Handles SSL/TLS (Let's Encrypt)                         │
│  • Routes requests to internal ports                       │
│  • Rate limiting & security headers                        │
│  • Access logging                                          │
└─────────────────────────────────────────────────────────────┘
    │
    ├─────────────┬─────────────┬─────────────┐
    ▼             ▼             ▼             ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│ Port    │ │ Port    │ │ Port    │ │ Future  │
│ 8080    │ │ 8081    │ │ 8082    │ │ 5432    │
│ Public  │ │ Control │ │ Tunnel  │ │ Postgres│
└─────────┘ └─────────┘ └─────────┘ └─────────┘
    │             │             │
    └─────────────┴─────────────┴─> Your Python Code (UNCHANGED!)
                                     /opt/mport/server/tunnel_server.py
```

### Benefits of This Architecture

✅ **Firewall-Friendly:** Port 443 (HTTPS) is rarely blocked  
✅ **Encrypted:** TLS 1.3 with modern ciphers  
✅ **Professional:** Industry-standard reverse proxy pattern  
✅ **Zero Code Changes:** Your 2,016 lines stay intact  
✅ **Easy Scaling:** Add more servers behind Nginx later  
✅ **Web Dashboard Ready:** Can serve static files from /  

---

## 🚀 Quick Deployment (Automated)

### Step 1: Create VPS

1. Go to [DigitalOcean](https://cloud.digitalocean.com/)
2. Create Droplet:
   - **Image:** Ubuntu 22.04 LTS x64
   - **Plan:** Basic $6/month
   - **Datacenter:** Bangalore (BLR1)
   - **Authentication:** SSH key (recommended) or password
   - **Hostname:** mport-production
3. Wait 1-2 minutes for creation
4. Note the IP address (e.g., 157.230.xxx.xxx)

### Step 2: Configure DNS

1. Go to Name.com domain settings
2. Add DNS records:
   ```
   Type    Name    Value              TTL
   A       @       157.230.xxx.xxx    300
   A       www     157.230.xxx.xxx    300
   A       *       157.230.xxx.xxx    300
   ```
3. Wait 5-60 minutes for propagation
4. Test: `nslookup mport.app` should return your IP

### Step 3: Run Deployment Script

```bash
# SSH into VPS
ssh root@YOUR_VPS_IP

# Download deployment script
curl -o deploy.sh https://raw.githubusercontent.com/Baymax005/PhoneControl/main/Mport/deployment/deploy.sh

# Make executable
chmod +x deploy.sh

# Edit email in script
nano deploy.sh
# Change: EMAIL="your-email@example.com"

# Run deployment (takes 5-10 minutes)
sudo ./deploy.sh
```

**The script will:**
1. ✅ Update system packages
2. ✅ Install Python 3.13, Nginx, Certbot
3. ✅ Configure firewall (UFW)
4. ✅ Clone your GitHub repository
5. ✅ Obtain SSL certificate (Let's Encrypt)
6. ✅ Configure Nginx reverse proxy
7. ✅ Create systemd service
8. ✅ Start everything

### Step 4: Verify Deployment

```bash
# Check health endpoint
curl https://mport.app/health
# Should return: healthy

# Check service status
sudo systemctl status mport

# Check Nginx
sudo systemctl status nginx

# View logs
sudo journalctl -u mport -f
```

---

## 🔧 Manual Deployment (Step-by-Step)

If you prefer manual control:

### 1. System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y software-properties-common build-essential git curl wget vim ufw certbot python3-certbot-nginx

# Install Python 3.13
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.13 python3.13-venv python3.13-dev python3-pip

# Install Nginx
sudo apt install -y nginx

# Install Python packages
python3.13 -m pip install colorama
```

### 2. Create User & Directories

```bash
# Create mport user
sudo useradd -r -m -s /bin/bash mport

# Create directories
sudo mkdir -p /opt/mport
sudo mkdir -p /var/log/mport
sudo mkdir -p /var/www/mport
sudo mkdir -p /var/www/certbot

# Set permissions
sudo chown -R mport:mport /opt/mport
sudo chown -R mport:mport /var/log/mport
sudo chown -R www-data:www-data /var/www/mport
```

### 3. Clone Repository

```bash
cd /opt/mport
sudo -u mport git clone https://github.com/Baymax005/PhoneControl.git .
```

### 4. Configure Firewall

```bash
# Reset firewall
sudo ufw --force reset

# Configure rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'
sudo ufw allow 8080/tcp comment 'Mport Public'
sudo ufw allow 8081/tcp comment 'Mport Control'
sudo ufw allow 8082/tcp comment 'Mport Tunnel'

# Enable
sudo ufw --force enable
sudo ufw status
```

### 5. Obtain SSL Certificate

```bash
# Stop Nginx temporarily
sudo systemctl stop nginx

# Get certificate
sudo certbot certonly \
    --standalone \
    --non-interactive \
    --agree-tos \
    --email your-email@example.com \
    -d mport.app \
    -d www.mport.app

# Setup auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### 6. Configure Nginx

```bash
# Copy config
sudo cp /opt/mport/Mport/deployment/nginx.conf /etc/nginx/sites-available/mport

# Create symlink
sudo ln -sf /etc/nginx/sites-available/mport /etc/nginx/sites-enabled/mport

# Remove default
sudo rm -f /etc/nginx/sites-enabled/default

# Test config
sudo nginx -t

# Start Nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### 7. Create Systemd Service

```bash
sudo nano /etc/systemd/system/mport.service
```

Paste:
```ini
[Unit]
Description=Mport TCP Tunneling Service
After=network.target

[Service]
Type=simple
User=mport
WorkingDirectory=/opt/mport/Mport
ExecStart=/usr/bin/python3.13 server/tunnel_server.py --host 0.0.0.0 --log-file /var/log/mport/server.log
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable mport
sudo systemctl start mport
sudo systemctl status mport
```

---

## ✅ Testing

### 1. Health Check

```bash
# From VPS
curl https://mport.app/health
# Expected: healthy

# From your PC
curl https://mport.app/health
```

### 2. Test Client Connection

```bash
# On your PC (Windows PowerShell)
cd "C:\Users\muham\OneDrive\Desktop\OTHER LANGS\web dev\PhoneControl\Mport"

# Connect to VPS (modify client to use HTTPS - Week 2 task)
python client/tunnel_client.py --server mport.app --port 443

# For now, test direct TCP connection
python client/tunnel_client.py --server mport.app --port 8081
```

### 3. Test ADB Tunnel

```bash
# From any computer with ADB
adb connect mport.app:8080

# Test command
adb -s mport.app:8080 shell getprop ro.product.model
# Should return: BE2029
```

### 4. Monitor Logs

```bash
# Server logs
sudo tail -f /var/log/mport/server.log

# Nginx access logs
sudo tail -f /var/log/nginx/mport-access.log

# Nginx error logs
sudo tail -f /var/log/nginx/mport-error.log

# Systemd logs
sudo journalctl -u mport -f
```

---

## 📊 Monitoring

### Service Status

```bash
# Mport service
sudo systemctl status mport

# Nginx
sudo systemctl status nginx

# Certificate expiry
sudo certbot certificates
```

### Performance

```bash
# Active connections
sudo ss -tunlp | grep -E '8080|8081|8082|443'

# Resource usage
htop

# Disk space
df -h

# Memory
free -h
```

### Nginx Stats

```bash
# Access log summary
sudo cat /var/log/nginx/mport-access.log | awk '{print $7}' | sort | uniq -c | sort -rn | head -20

# Error log
sudo tail -50 /var/log/nginx/mport-error.log
```

---

## 🔍 Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u mport -n 100 --no-pager

# Check Python version
python3.13 --version

# Test manually
cd /opt/mport/Mport
python3.13 server/tunnel_server.py --host 0.0.0.0
```

### SSL Certificate Issues

```bash
# Check certificate
sudo certbot certificates

# Renew manually
sudo certbot renew --force-renewal

# Check DNS
nslookup mport.app
dig mport.app
```

### Nginx Won't Start

```bash
# Check config
sudo nginx -t

# Check logs
sudo tail -f /var/log/nginx/error.log

# Check ports
sudo ss -tunlp | grep nginx
```

### Can't Connect from Client

```bash
# Check firewall
sudo ufw status

# Test connectivity
telnet mport.app 8081
nc -zv mport.app 8081

# Check if service is listening
sudo ss -tunlp | grep 8081
```

### High CPU/Memory Usage

```bash
# Check process
top -c | grep python

# Restart service
sudo systemctl restart mport

# Check for memory leaks
sudo systemctl status mport
```

---

## 🔧 Maintenance

### Update Code

```bash
cd /opt/mport
sudo -u mport git pull origin main
sudo systemctl restart mport
```

### Renew SSL Certificate

```bash
# Auto-renewal (enabled by default)
sudo systemctl status certbot.timer

# Manual renewal
sudo certbot renew
sudo systemctl reload nginx
```

### Backup

```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
mkdir -p /backups
tar -czf /backups/mport-$DATE.tar.gz /opt/mport /etc/nginx/sites-available/mport
```

### Log Rotation

```bash
# Create logrotate config
sudo nano /etc/logrotate.d/mport
```

Paste:
```
/var/log/mport/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 mport mport
    sharedscripts
    postrotate
        systemctl reload mport > /dev/null 2>&1 || true
    endscript
}
```

### Security Updates

```bash
# Update system weekly
sudo apt update && sudo apt upgrade -y
sudo systemctl restart mport
sudo systemctl restart nginx
```

---

## 📈 Next Steps (Week 3+)

1. **Client HTTPS Support:** Modify client to use HTTPS endpoints
2. **WebSocket Tunneling:** Add WebSocket support for browser clients
3. **User Authentication:** Token-based auth system
4. **Web Dashboard:** React/Vue frontend for tunnel management
5. **Database:** PostgreSQL for user/tunnel persistence
6. **Monitoring:** Prometheus + Grafana dashboard

---

## 📚 Resources

- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)
- [DigitalOcean Community](https://www.digitalocean.com/community/tutorials)
- [Ubuntu Server Guide](https://ubuntu.com/server/docs)

---

**Document Version:** 1.0  
**Last Updated:** November 3, 2025  
**Maintained By:** Muhammad (Baymax005)  
**Status:** Ready for Deployment

---

*Mport - Your Port to the World* 🚀
