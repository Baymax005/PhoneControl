# Oracle Cloud Free Tier Deployment Guide
# Mport Week 2 - FREE FOREVER VPS Alternative

**Cost:** $0 (Always Free Tier - no credit card charges)  
**Performance:** 1 OCPU, 1GB RAM (similar to DigitalOcean $6/month)  
**Advantage:** Free forever, no expiration after student credits run out

---

## 🎯 Why Oracle Cloud?

| Feature | Oracle Cloud Free | DigitalOcean Student |
|---------|-------------------|---------------------|
| **Cost** | ✅ FREE FOREVER | $200 credit (33 months) |
| **After Credits** | ✅ Still free | ❌ $6/month |
| **Performance** | 1 OCPU, 1GB RAM | 1 vCPU, 1GB RAM |
| **Network** | 10TB/month | 1TB/month |
| **Public IP** | ✅ Free | ✅ Included |
| **Best For** | Long-term testing | Quick start |

**Recommendation:** Use Oracle Cloud for **permanent free hosting** or DigitalOcean for **faster setup**.

---

## 📋 Prerequisites

### 1. Oracle Cloud Account
1. Go to https://www.oracle.com/cloud/free/
2. Click "Start for free"
3. Fill in details (email, country, etc.)
4. **Phone verification** required
5. **Credit card verification** (one-time, no charges for Always Free)
6. Wait 5-10 minutes for account activation

### 2. Choose Your Region
- **Closest to Pakistan:** Mumbai (India Central - BOM)
- **Alternatives:** Singapore, Tokyo, Seoul
- **Note:** Some regions run out of Always Free capacity
- **Tip:** Try multiple regions if one is full

---

## 🚀 Quick Deployment (Recommended)

### Step 1: Create Compute Instance

1. **Login** to Oracle Cloud Console
2. **Navigate:** Menu → Compute → Instances
3. **Click:** "Create Instance"

#### Instance Configuration:

```yaml
Name: mport-production
Image: Canonical Ubuntu 22.04
Shape: VM.Standard.E2.1.Micro (Always Free)
  - 1 OCPU (x86_64 AMD)
  - 1 GB RAM
  - Always Free eligible ✅

Networking:
  - Create new VCN: mport-vcn (auto-creates subnets)
  - Assign public IP: Yes (required!)

SSH Keys:
  - Generate new key pair (download .pem file)
  - OR: Paste your public key
```

4. **Click:** "Create"
5. **Wait:** 1-2 minutes for provisioning
6. **Note:** Public IP address (e.g., 150.230.xxx.xxx)

### Step 2: Configure Firewall (Security List)

**IMPORTANT:** OCI blocks all ports by default!

1. **Navigate:** Networking → Virtual Cloud Networks → mport-vcn
2. **Click:** Public Subnet → Default Security List
3. **Add Ingress Rules:**

```
Rule 1: SSH
Source: 0.0.0.0/0
Port: 22
Description: SSH access

Rule 2: HTTP
Source: 0.0.0.0/0
Port: 80
Description: Let's Encrypt verification

Rule 3: HTTPS
Source: 0.0.0.0/0
Port: 443
Description: Web dashboard

Rule 4: Mport Control (TLS)
Source: 0.0.0.0/0
Port: 8091
Description: Mport control connections

Rule 5: Mport Tunnel (TLS)
Source: 0.0.0.0/0
Port: 8092
Description: Mport tunnel data

Rule 6: Mport Public (TLS)
Source: 0.0.0.0/0
Port: 8090
Description: Mport user connections
```

### Step 3: Configure DNS

Point your domain to Oracle Cloud IP:

```
Type    Name    Value               TTL
A       @       150.230.xxx.xxx     300
A       www     150.230.xxx.xxx     300
A       *       150.230.xxx.xxx     300
```

Wait 5-60 minutes for DNS propagation.

### Step 4: SSH into Instance

```bash
# Windows PowerShell:
ssh -i path\to\ssh-key.pem ubuntu@150.230.xxx.xxx

# First time only - fix permissions:
chmod 600 ssh-key.pem

# Linux/Mac:
ssh -i ~/Downloads/ssh-key.pem ubuntu@150.230.xxx.xxx
```

**Default user:** `ubuntu` (not `root`)

### Step 5: Run Deployment Script

```bash
# Download script
curl -o deploy.sh https://raw.githubusercontent.com/Baymax005/PhoneControl/main/Mport/deployment/deploy.sh

# Make executable
chmod +x deploy.sh

# Edit email
nano deploy.sh
# Change: EMAIL="your-email@example.com"

# Run (auto-detects Oracle Cloud)
sudo ./deploy.sh
```

**Script will:**
- ✅ Detect Oracle Cloud ARM64 or x86_64
- ✅ Install Python 3.13 (pyenv fallback on ARM)
- ✅ Configure Ubuntu firewall (in addition to Security List)
- ✅ Install Nginx, Certbot
- ✅ Deploy Mport service
- ✅ Obtain SSL certificate
- ✅ Start everything

### Step 6: Verify Deployment

```bash
# Check health
curl https://mport.app/health
# Expected: healthy

# Check services
sudo systemctl status mport
sudo systemctl status nginx

# View logs
sudo journalctl -u mport -f
```

---

## 🏗️ Manual Deployment (Step-by-Step)

If automated script fails, follow these manual steps:

### 1. Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Configure Ubuntu Firewall

```bash
# OCI uses both Security Lists + UFW
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8090/tcp
sudo ufw allow 8091/tcp
sudo ufw allow 8092/tcp
sudo ufw --force enable
```

### 3. Install Dependencies

**For x86_64 (AMD):**
```bash
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.13 python3.13-venv python3-pip
```

**For ARM64 (Ampere - if you chose ARM shape):**
```bash
# Install pyenv (Python 3.13 not in deadsnakes for ARM)
curl https://pyenv.run | bash

# Add to ~/.bashrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc

# Install Python 3.13
pyenv install 3.13.0
pyenv global 3.13.0
```

**Common packages:**
```bash
sudo apt install -y nginx certbot python3-certbot-nginx git curl wget
python3 -m pip install colorama
```

### 4. Clone Repository

```bash
sudo mkdir -p /opt/mport
sudo chown ubuntu:ubuntu /opt/mport
cd /opt/mport
git clone https://github.com/Baymax005/PhoneControl.git .
```

### 5. Configure Nginx

```bash
sudo cp /opt/mport/Mport/deployment/nginx-stream.conf /etc/nginx/nginx.conf
sudo nginx -t
```

### 6. Obtain SSL Certificate

```bash
sudo systemctl stop nginx
sudo certbot certonly \
    --standalone \
    --non-interactive \
    --agree-tos \
    --email your-email@example.com \
    -d mport.app \
    -d www.mport.app
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
User=ubuntu
WorkingDirectory=/opt/mport/Mport
ExecStart=/usr/bin/python3.13 server/tunnel_server.py --host 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable mport nginx
sudo systemctl start mport nginx
```

---

## 🔍 Troubleshooting

### Issue 1: Security List vs UFW

**Problem:** Ports open in UFW but still can't connect  
**Solution:** Check OCI Security List (takes precedence)

```bash
# Verify UFW
sudo ufw status

# If blocked, check OCI Console:
# Networking → VCN → Security Lists → Ingress Rules
```

### Issue 2: ARM64 Python Issues

**Problem:** `deadsnakes` PPA doesn't work on ARM  
**Solution:** Use pyenv (see manual deployment above)

### Issue 3: Out of Always Free Capacity

**Problem:** "Out of host capacity" when creating instance  
**Solution:**
1. Try different region (Mumbai, Singapore, Tokyo)
2. Try different availability domain
3. Try at different time (3 AM UTC often works)
4. Use notification feature to alert when capacity available

### Issue 4: SSL Certificate Fails

**Problem:** Let's Encrypt can't verify domain  
**Solution:**
1. Check DNS: `nslookup mport.app` should return OCI IP
2. Check Security List: Port 80 must be open
3. Check UFW: `sudo ufw allow 80/tcp`
4. Wait longer for DNS propagation (up to 48 hours)

### Issue 5: Default User

**Problem:** Can't login as `root`  
**Solution:** Default user is `ubuntu`, not `root`

```bash
# Correct:
ssh ubuntu@IP

# To become root:
sudo su -
```

---

## 📊 Performance Notes

### Always Free Limits

```
Compute:
- 2 AMD Micro instances (1 OCPU, 1GB RAM each)
- OR 4 ARM Ampere A1 cores + 24GB RAM total

Storage:
- 200GB total block storage
- 10GB object storage

Network:
- 10TB outbound/month
- Unlimited inbound
```

### Expected Performance

```
Mport on VM.Standard.E2.1.Micro:
- Concurrent connections: 50-100
- Latency: 50-100ms (Mumbai → Pakistan)
- Throughput: 100+ KB/s
- CPU usage: 20-40% under load
- Memory usage: 400-600MB
```

### Comparison to DigitalOcean

```
Feature                OCI Free      DO $6/month
────────────────────────────────────────────────
Performance            Similar       Similar
Network bandwidth      10TB/month    1TB/month
Always Free shapes     2 VMs         0
Cost after credits     $0            $72/year
Setup complexity       Medium        Easy
```

---

## 🎓 Advanced: OCI CLI Automation

### Install OCI CLI

```bash
# Linux/Mac:
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"

# Windows PowerShell:
# Download from: https://github.com/oracle/oci-cli/releases
```

### Configure CLI

```bash
oci setup config
# Follow prompts to add tenancy OCID, user OCID, region, etc.
```

### Create Instance via CLI

```bash
# List available shapes
oci compute shape list --compartment-id <compartment-ocid>

# Create instance
oci compute instance launch \
  --availability-domain <AD> \
  --compartment-id <compartment-ocid> \
  --shape VM.Standard.E2.1.Micro \
  --image-id <ubuntu-22.04-image-ocid> \
  --subnet-id <subnet-ocid> \
  --display-name mport-production \
  --assign-public-ip true \
  --ssh-authorized-keys-file ~/.ssh/id_rsa.pub
```

---

## 🚀 Next Steps After Deployment

1. **Test Connection:**
   ```bash
   curl https://mport.app/health
   ```

2. **Connect Client:**
   ```bash
   python client/tunnel_client.py --server mport.app --port 8091
   ```

3. **Monitor Logs:**
   ```bash
   sudo journalctl -u mport -f
   ```

4. **Run Stress Test:**
   ```bash
   python tests/stress_test.py
   ```

5. **Update DNS** (if using subdomain routing)

---

## 📚 Resources

- **OCI Free Tier:** https://www.oracle.com/cloud/free/
- **OCI Documentation:** https://docs.oracle.com/en-us/iaas/
- **OCI CLI:** https://docs.oracle.com/en-us/iaas/tools/oci-cli/latest/
- **Ubuntu on OCI:** https://ubuntu.com/oracle
- **Security Lists:** https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/securitylists.htm

---

## 💡 Tips & Tricks

### Extend Beyond Free Tier

If you outgrow Always Free:
- Add paid compute ($0.01-0.02/hour)
- Add load balancer
- Add PostgreSQL database
- Add Redis cache

### Multi-Region Deployment

Deploy to multiple OCI regions:
- Mumbai (Asia - closest to Pakistan)
- Singapore (Asia - backup)
- Frankfurt (Europe)
- Use DNS-based load balancing

### Save Money on DigitalOcean

Use OCI Free Tier for development/testing, DigitalOcean for production when you have users.

---

**Document Version:** 1.0  
**Last Updated:** November 3, 2025  
**Status:** Ready for deployment

---

*Free forever hosting for your port to the world!* 🚀
