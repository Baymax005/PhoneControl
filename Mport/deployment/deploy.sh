#!/bin/bash

##############################################################################
# Mport VPS Deployment Script
# Week 2: Deploy to DigitalOcean with HTTPS/Nginx wrapper
#
# This script:
# 1. Sets up Ubuntu 22.04 VPS
# 2. Installs dependencies (Python 3.13, Nginx, Certbot)
# 3. Configures firewall
# 4. Deploys Mport server
# 5. Obtains SSL certificate
# 6. Configures Nginx reverse proxy
# 7. Sets up systemd service
#
# Usage: sudo ./deploy.sh
##############################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="mport.app"
EMAIL="your-email@example.com"  # Change this!
MPORT_USER="mport"
MPORT_DIR="/opt/mport"
LOG_DIR="/var/log/mport"

echo -e "${CYAN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║        🚀 MPORT VPS DEPLOYMENT SCRIPT (WEEK 2)       ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root (sudo ./deploy.sh)${NC}"
    exit 1
fi

echo -e "${BLUE}📋 Deployment Configuration:${NC}"
echo -e "   Domain: ${GREEN}${DOMAIN}${NC}"
echo -e "   Email: ${GREEN}${EMAIL}${NC}"
echo -e "   Install Directory: ${GREEN}${MPORT_DIR}${NC}"
echo ""
read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Deployment cancelled.${NC}"
    exit 0
fi

##############################################################################
# STEP 1: System Update
##############################################################################
echo -e "${BLUE}📦 Step 1/10: Updating system packages...${NC}"
apt update && apt upgrade -y
echo -e "${GREEN}✅ System updated${NC}\n"

##############################################################################
# STEP 2: Install Dependencies
##############################################################################
echo -e "${BLUE}📦 Step 2/10: Installing dependencies...${NC}"

# Install essential packages
apt install -y \
    software-properties-common \
    build-essential \
    git \
    curl \
    wget \
    vim \
    ufw \
    certbot \
    python3-certbot-nginx

# Install Python 3.13 (from deadsnakes PPA)
add-apt-repository -y ppa:deadsnakes/ppa
apt update
apt install -y \
    python3.13 \
    python3.13-venv \
    python3.13-dev \
    python3-pip

# Install Nginx
apt install -y nginx

# Install colorama for Mport
python3.13 -m pip install colorama

echo -e "${GREEN}✅ Dependencies installed${NC}\n"

##############################################################################
# STEP 3: Create Mport User
##############################################################################
echo -e "${BLUE}👤 Step 3/10: Creating mport user...${NC}"

if id "$MPORT_USER" &>/dev/null; then
    echo -e "${YELLOW}⚠️  User $MPORT_USER already exists${NC}"
else
    useradd -r -m -s /bin/bash "$MPORT_USER"
    echo -e "${GREEN}✅ User $MPORT_USER created${NC}"
fi
echo ""

##############################################################################
# STEP 4: Setup Directories
##############################################################################
echo -e "${BLUE}📁 Step 4/10: Setting up directories...${NC}"

mkdir -p "$MPORT_DIR"
mkdir -p "$LOG_DIR"
mkdir -p /var/www/mport
mkdir -p /var/www/certbot

chown -R "$MPORT_USER":"$MPORT_USER" "$MPORT_DIR"
chown -R "$MPORT_USER":"$MPORT_USER" "$LOG_DIR"
chown -R www-data:www-data /var/www/mport

echo -e "${GREEN}✅ Directories created${NC}\n"

##############################################################################
# STEP 5: Clone Repository
##############################################################################
echo -e "${BLUE}📥 Step 5/10: Cloning Mport repository...${NC}"

cd "$MPORT_DIR"
if [ -d ".git" ]; then
    echo -e "${YELLOW}⚠️  Repository already exists, pulling latest...${NC}"
    sudo -u "$MPORT_USER" git pull
else
    sudo -u "$MPORT_USER" git clone https://github.com/Baymax005/PhoneControl.git .
fi

echo -e "${GREEN}✅ Repository cloned${NC}\n"

##############################################################################
# STEP 6: Configure Firewall
##############################################################################
echo -e "${BLUE}🔥 Step 6/10: Configuring firewall (UFW)...${NC}"

# Reset UFW to default
ufw --force reset

# Default policies
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (IMPORTANT!)
ufw allow 22/tcp comment 'SSH'

# Allow HTTP/HTTPS (for Nginx)
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'

# Allow Mport HTTPS-wrapped ports (TLS stream)
ufw allow 8090/tcp comment 'Mport Public (TLS)'
ufw allow 8091/tcp comment 'Mport Control (TLS)'
ufw allow 8092/tcp comment 'Mport Tunnel (TLS)'

# Internal ports (localhost only - no firewall rule needed)
# 8080, 8081, 8082 only accessible via nginx proxy

# Enable firewall
ufw --force enable

echo -e "${GREEN}✅ Firewall configured${NC}"
ufw status numbered
echo ""

##############################################################################
# STEP 7: Configure Nginx
##############################################################################
echo -e "${BLUE}🌐 Step 7/10: Configuring Nginx...${NC}"

# Backup original nginx.conf
cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup

# Copy Nginx config (TCP stream + HTTP)
cp "$MPORT_DIR/Mport/deployment/nginx-stream.conf" /etc/nginx/nginx.conf

# Remove default site
rm -f /etc/nginx/sites-enabled/default

# Create simple index page
cat > /var/www/mport/index.html <<'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Mport - Your Port to the World</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            text-align: center;
            background: rgba(255,255,255,0.1);
            padding: 50px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }
        h1 { font-size: 4em; margin: 0; }
        p { font-size: 1.5em; margin: 20px 0; }
        .status { color: #4ade80; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Mport</h1>
        <p>Your Port to the World</p>
        <p class="status">● Online</p>
        <p style="font-size: 1em; opacity: 0.8;">Week 2 - HTTPS Enabled</p>
    </div>
</body>
</html>
EOF

# Test Nginx config
nginx -t

echo -e "${GREEN}✅ Nginx configured${NC}\n"

##############################################################################
# STEP 8: Obtain SSL Certificate
##############################################################################
echo -e "${BLUE}🔒 Step 8/10: Obtaining SSL certificate from Let's Encrypt...${NC}"

# Stop Nginx temporarily
systemctl stop nginx

# Obtain certificate
certbot certonly \
    --standalone \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    -d "$DOMAIN" \
    -d "www.$DOMAIN"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ SSL certificate obtained${NC}"
else
    echo -e "${RED}❌ Failed to obtain SSL certificate${NC}"
    echo -e "${YELLOW}⚠️  Make sure DNS is pointing to this server!${NC}"
    exit 1
fi

# Setup auto-renewal
systemctl enable certbot.timer
systemctl start certbot.timer

echo -e "${GREEN}✅ SSL auto-renewal configured${NC}\n"

##############################################################################
# STEP 9: Create Systemd Service
##############################################################################
echo -e "${BLUE}⚙️  Step 9/10: Creating systemd service...${NC}"

cat > /etc/systemd/system/mport.service <<EOF
[Unit]
Description=Mport TCP Tunneling Service
After=network.target

[Service]
Type=simple
User=$MPORT_USER
WorkingDirectory=$MPORT_DIR/Mport
ExecStart=/usr/bin/python3.13 server/tunnel_server.py --host 0.0.0.0 --log-file $LOG_DIR/server.log
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$LOG_DIR

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

# Enable and start service
systemctl enable mport
systemctl start mport

# Check status
sleep 2
if systemctl is-active --quiet mport; then
    echo -e "${GREEN}✅ Mport service started${NC}"
else
    echo -e "${RED}❌ Mport service failed to start${NC}"
    systemctl status mport
    exit 1
fi

echo ""

##############################################################################
# STEP 10: Start Nginx
##############################################################################
echo -e "${BLUE}🌐 Step 10/10: Starting Nginx...${NC}"

systemctl enable nginx
systemctl restart nginx

if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✅ Nginx started${NC}"
else
    echo -e "${RED}❌ Nginx failed to start${NC}"
    systemctl status nginx
    exit 1
fi

echo ""

##############################################################################
# Deployment Complete
##############################################################################
echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         ✅ DEPLOYMENT COMPLETE! 🎉                    ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}📋 Service Information:${NC}"
echo -e "   🌐 Website: ${GREEN}https://$DOMAIN${NC}"
echo -e "   🔒 SSL: ${GREEN}Enabled (Let's Encrypt)${NC}"
echo -e "   📊 Status: ${GREEN}https://$DOMAIN/health${NC}"
echo ""
echo -e "${CYAN}📡 TLS-wrapped TCP Ports:${NC}"
echo -e "   Control: ${GREEN}$DOMAIN:8091${NC} (wraps 8081)"
echo -e "   Tunnel:  ${GREEN}$DOMAIN:8092${NC} (wraps 8082)"
echo -e "   Public:  ${GREEN}$DOMAIN:8090${NC} (wraps 8080)"
echo ""
echo -e "${CYAN}🔧 Service Management:${NC}"
echo -e "   Status:  ${YELLOW}sudo systemctl status mport${NC}"
echo -e "   Restart: ${YELLOW}sudo systemctl restart mport${NC}"
echo -e "   Logs:    ${YELLOW}sudo journalctl -u mport -f${NC}"
echo -e "   Files:   ${YELLOW}$LOG_DIR${NC}"
echo ""
echo -e "${CYAN}🔥 Firewall Status:${NC}"
ufw status numbered | head -10
echo ""
echo -e "${CYAN}✅ Next Steps:${NC}"
echo -e "   1. Test web: ${YELLOW}curl https://$DOMAIN/health${NC}"
echo -e "   2. Test API: ${YELLOW}curl https://$DOMAIN/api${NC}"
echo -e "   3. Connect client: ${YELLOW}python client/tunnel_client.py --server $DOMAIN --port 8091${NC}"
echo -e "   4. Monitor logs: ${YELLOW}tail -f $LOG_DIR/server.log${NC}"
echo ""
echo -e "${GREEN}🚀 Your port to the world is now online!${NC}\n"
