#!/bin/bash

##############################################################################
# Mport VPS-Agnostic Deployment Script
# Week 2: Universal deployment for ANY cloud provider
#
# Supports:
# - DigitalOcean, Oracle Cloud (OCI), AWS, Azure, Vultr, Linode, etc.
# - x86_64 (AMD/Intel) and ARM64 (Ampere, Graviton) architectures
# - Auto-detection of cloud provider, OS, and CPU architecture
# - Intelligent fallbacks for Python installation
#
# This script:
# 1. Detects cloud provider and system architecture
# 2. Sets up Ubuntu 22.04+ VPS (Debian-based)
# 3. Installs Python 3.13 (with pyenv fallback for ARM)
# 4. Installs Nginx and Certbot
# 5. Configures firewall (UFW + cloud provider specific)
# 6. Deploys Mport server
# 7. Obtains SSL certificate
# 8. Configures Nginx TCP stream proxy
# 9. Sets up systemd service
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
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="mport.app"
EMAIL="your-email@example.com"  # Change this!
MPORT_USER="mport"
MPORT_DIR="/opt/mport"
LOG_DIR="/var/log/mport"

# Detect current user (for non-root execution context)
ACTUAL_USER="${SUDO_USER:-ubuntu}"

echo -e "${CYAN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║      🚀 MPORT VPS-AGNOSTIC DEPLOYMENT (WEEK 2)       ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root (sudo ./deploy.sh)${NC}"
    exit 1
fi

##############################################################################
# DETECTION FUNCTIONS
##############################################################################

detect_cloud_provider() {
    echo -e "${PURPLE}🔍 Detecting cloud provider...${NC}"
    
    # Check for cloud provider metadata services
    if curl -s -f -m 2 http://169.254.169.254/opc/v1/instance/ > /dev/null 2>&1; then
        CLOUD_PROVIDER="Oracle Cloud (OCI)"
    elif curl -s -f -m 2 http://169.254.169.254/metadata/v1/ > /dev/null 2>&1; then
        CLOUD_PROVIDER="DigitalOcean"
    elif curl -s -f -m 2 http://169.254.169.254/latest/meta-data/ > /dev/null 2>&1; then
        # Could be AWS, Azure, or others
        if curl -s -f -m 2 -H "Metadata:true" http://169.254.169.254/metadata/instance?api-version=2021-02-01 > /dev/null 2>&1; then
            CLOUD_PROVIDER="Microsoft Azure"
        else
            CLOUD_PROVIDER="Amazon AWS"
        fi
    elif [ -f "/sys/hypervisor/uuid" ] && grep -q "ec2" /sys/hypervisor/uuid 2>/dev/null; then
        CLOUD_PROVIDER="Amazon AWS"
    else
        CLOUD_PROVIDER="Generic VPS"
    fi
    
    echo -e "   Provider: ${GREEN}${CLOUD_PROVIDER}${NC}"
}

detect_architecture() {
    echo -e "${PURPLE}🔍 Detecting CPU architecture...${NC}"
    
    ARCH=$(uname -m)
    case "$ARCH" in
        x86_64)
            CPU_ARCH="x86_64 (AMD/Intel)"
            ARCH_SHORT="x86_64"
            ;;
        aarch64|arm64)
            CPU_ARCH="ARM64 (Ampere/Graviton)"
            ARCH_SHORT="arm64"
            ;;
        *)
            CPU_ARCH="Unknown ($ARCH)"
            ARCH_SHORT="unknown"
            ;;
    esac
    
    echo -e "   Architecture: ${GREEN}${CPU_ARCH}${NC}"
}

detect_os() {
    echo -e "${PURPLE}🔍 Detecting operating system...${NC}"
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS_NAME="$NAME"
        OS_VERSION="$VERSION_ID"
    else
        OS_NAME="Unknown"
        OS_VERSION="Unknown"
    fi
    
    echo -e "   OS: ${GREEN}${OS_NAME} ${OS_VERSION}${NC}"
    
    # Check if Debian-based
    if ! command -v apt &> /dev/null; then
        echo -e "${RED}❌ This script requires apt (Debian/Ubuntu)${NC}"
        echo -e "${YELLOW}⚠️  Detected non-Debian OS. Please use Ubuntu 22.04+${NC}"
        exit 1
    fi
}

# Run detections
detect_cloud_provider
detect_architecture
detect_os

echo ""
echo -e "${BLUE}📋 Deployment Configuration:${NC}"
echo -e "   Cloud: ${GREEN}${CLOUD_PROVIDER}${NC}"
echo -e "   Architecture: ${GREEN}${CPU_ARCH}${NC}"
echo -e "   OS: ${GREEN}${OS_NAME} ${OS_VERSION}${NC}"
echo -e "   Domain: ${GREEN}${DOMAIN}${NC}"
echo -e "   Email: ${GREEN}${EMAIL}${NC}"
echo -e "   Install Directory: ${GREEN}${MPORT_DIR}${NC}"
echo -e "   User: ${GREEN}${ACTUAL_USER}${NC}"
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
    python3-certbot-nginx \
    libssl-dev \
    libffi-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    liblzma-dev

# Install Nginx
apt install -y nginx

# Install Python 3.13 - Architecture-specific approach
echo -e "${PURPLE}🐍 Installing Python 3.13 for ${ARCH_SHORT}...${NC}"

PYTHON_INSTALLED=false

if [ "$ARCH_SHORT" = "x86_64" ]; then
    # x86_64: Try deadsnakes PPA first (fastest)
    echo -e "${BLUE}   Attempting deadsnakes PPA installation...${NC}"
    if add-apt-repository -y ppa:deadsnakes/ppa 2>/dev/null; then
        apt update
        if apt install -y python3.13 python3.13-venv python3.13-dev python3-pip 2>/dev/null; then
            PYTHON_INSTALLED=true
            echo -e "${GREEN}   ✅ Python 3.13 installed via deadsnakes PPA${NC}"
        fi
    fi
fi

# Fallback: Install via pyenv (works on ALL architectures)
if [ "$PYTHON_INSTALLED" = false ]; then
    echo -e "${YELLOW}   Deadsnakes unavailable, using pyenv fallback...${NC}"
    
    # Install pyenv if not present
    if [ ! -d "/home/${ACTUAL_USER}/.pyenv" ]; then
        echo -e "${BLUE}   Installing pyenv...${NC}"
        sudo -u "$ACTUAL_USER" bash -c 'curl https://pyenv.run | bash'
        
        # Add pyenv to bashrc
        sudo -u "$ACTUAL_USER" bash -c 'cat >> ~/.bashrc << EOF
export PYENV_ROOT="\$HOME/.pyenv"
export PATH="\$PYENV_ROOT/bin:\$PATH"
eval "\$(pyenv init -)"
EOF'
    fi
    
    # Install Python 3.13 via pyenv
    echo -e "${BLUE}   Compiling Python 3.13 (may take 5-10 minutes)...${NC}"
    sudo -u "$ACTUAL_USER" bash -c '
        export PYENV_ROOT="$HOME/.pyenv"
        export PATH="$PYENV_ROOT/bin:$PATH"
        eval "$(pyenv init -)"
        pyenv install -s 3.13.0
        pyenv global 3.13.0
    '
    
    # Create symlink for system-wide access
    PYENV_PYTHON="/home/${ACTUAL_USER}/.pyenv/versions/3.13.0/bin/python3.13"
    if [ -f "$PYENV_PYTHON" ]; then
        ln -sf "$PYENV_PYTHON" /usr/local/bin/python3.13
        PYTHON_INSTALLED=true
        echo -e "${GREEN}   ✅ Python 3.13 installed via pyenv${NC}"
    fi
fi

# Verify Python installation
if command -v python3.13 &> /dev/null; then
    PYTHON_VERSION=$(python3.13 --version)
    echo -e "${GREEN}   ✓ $PYTHON_VERSION available${NC}"
    
    # Install colorama
    python3.13 -m pip install --upgrade pip
    python3.13 -m pip install colorama
else
    echo -e "${RED}❌ Failed to install Python 3.13${NC}"
    exit 1
fi

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

# Cloud-specific firewall notes
if [ "$CLOUD_PROVIDER" = "Oracle Cloud (OCI)" ]; then
    echo -e "${YELLOW}⚠️  Oracle Cloud detected!${NC}"
    echo -e "${YELLOW}   IMPORTANT: UFW alone is NOT enough on OCI!${NC}"
    echo -e "${YELLOW}   You MUST also configure Security Lists in OCI Console:${NC}"
    echo -e "${YELLOW}   Networking → VCN → Security Lists → Ingress Rules${NC}"
    echo -e "${YELLOW}   Required ports: 22, 80, 443, 8090, 8091, 8092${NC}"
    echo ""
fi

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

echo -e "${GREEN}✅ UFW firewall configured${NC}"
ufw status numbered

# Cloud-specific additional notes
case "$CLOUD_PROVIDER" in
    "Oracle Cloud (OCI)")
        echo -e "${CYAN}📝 OCI Post-Setup Checklist:${NC}"
        echo -e "   1. Configure Security Lists (REQUIRED!)${NC}"
        echo -e "   2. Verify public IP assigned${NC}"
        echo -e "   3. Check route table and gateway${NC}"
        ;;
    "Amazon AWS")
        echo -e "${CYAN}📝 AWS Note: Verify Security Groups allow required ports${NC}"
        ;;
    "Microsoft Azure")
        echo -e "${CYAN}📝 Azure Note: Verify Network Security Group rules${NC}"
        ;;
esac

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
echo -e "${PURPLE}☁️  Cloud Provider: ${GREEN}${CLOUD_PROVIDER}${NC}"
echo -e "${PURPLE}🖥️  Architecture: ${GREEN}${CPU_ARCH}${NC}"
echo -e "${PURPLE}🐍 Python: ${GREEN}${PYTHON_VERSION}${NC}"
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

# Cloud-specific next steps
case "$CLOUD_PROVIDER" in
    "Oracle Cloud (OCI)")
        echo -e "${RED}⚠️  CRITICAL: Oracle Cloud Security Lists${NC}"
        echo -e "${YELLOW}   UFW is configured, but OCI blocks at network level!${NC}"
        echo -e "${YELLOW}   Before testing, configure Security Lists:${NC}"
        echo ""
        echo -e "${CYAN}   1. Go to: OCI Console → Networking → VCN${NC}"
        echo -e "${CYAN}   2. Select: Your VCN → Public Subnet${NC}"
        echo -e "${CYAN}   3. Click: Default Security List${NC}"
        echo -e "${CYAN}   4. Add Ingress Rules for ports:${NC}"
        echo -e "      • 22 (SSH)"
        echo -e "      • 80 (HTTP - Let's Encrypt)"
        echo -e "      • 443 (HTTPS - Web)"
        echo -e "      • 8090, 8091, 8092 (Mport TLS)"
        echo ""
        echo -e "${YELLOW}   Source: 0.0.0.0/0 for all rules${NC}"
        echo ""
        ;;
    "Amazon AWS")
        echo -e "${YELLOW}⚠️  AWS: Verify Security Groups allow ports 22, 80, 443, 8090-8092${NC}"
        echo ""
        ;;
    "Microsoft Azure")
        echo -e "${YELLOW}⚠️  Azure: Verify Network Security Group rules allow required ports${NC}"
        echo ""
        ;;
esac

echo -e "${CYAN}✅ Next Steps:${NC}"
echo -e "   1. Test web: ${YELLOW}curl https://$DOMAIN/health${NC}"
echo -e "   2. Test API: ${YELLOW}curl https://$DOMAIN/api${NC}"
echo -e "   3. Connect client: ${YELLOW}python client/tunnel_client.py --server $DOMAIN --port 8091${NC}"
echo -e "   4. Monitor logs: ${YELLOW}tail -f $LOG_DIR/server.log${NC}"
echo ""
echo -e "${GREEN}🚀 Your port to the world is now online!${NC}"
echo -e "${PURPLE}   Cloud: ${CLOUD_PROVIDER} | Arch: ${ARCH_SHORT}${NC}\n"
