# Mport Week 2 Checklist
# HTTPS/Nginx Wrapper + VPS Deployment

**Goal:** Deploy Mport to VPS with HTTPS encryption and firewall-friendly architecture  
**Timeline:** Nov 3-10, 2025 (7 days)  
**Status:** 🟡 In Progress

---

## 📋 Pre-Deployment Checklist

### ✅ Completed (Week 1)
- [x] Basic TCP tunneling working locally
- [x] 3-port architecture (8080, 8081, 8082)
- [x] Client persistent connection with auto-reconnect
- [x] Statistics tracking
- [x] Rate limiting
- [x] Error handling
- [x] Stress testing (100% pass rate)
- [x] Documentation (README, TESTING, PROGRESS, ROADMAP, BRANDING)
- [x] Architecture documentation (1,600+ lines)

### 🔲 Week 2 Tasks

#### Day 1: Preparation (Nov 3, 2025)
- [x] Create nginx.conf (reverse proxy configuration)
- [x] Create deploy.sh (automated deployment script)
- [x] Create DEPLOYMENT.md (deployment guide)
- [ ] Sign up for DigitalOcean with GitHub Student Pack
- [ ] Claim mport.app domain from Name.com
- [ ] Test nginx config locally (optional)

#### Day 2: VPS Setup (Nov 4, 2025)
- [ ] Create DigitalOcean droplet
  - [ ] Size: Basic ($6/month)
  - [ ] OS: Ubuntu 22.04 LTS x64
  - [ ] Datacenter: Bangalore, India (BLR1)
  - [ ] Add SSH key
  - [ ] Note IP address
- [ ] Configure DNS records at Name.com
  - [ ] A record: @ → VPS_IP
  - [ ] A record: www → VPS_IP
  - [ ] A record: * → VPS_IP (wildcard for subdomains)
- [ ] Wait for DNS propagation (5-60 minutes)
- [ ] Test: `nslookup mport.app` returns correct IP

#### Day 3: Server Deployment (Nov 5, 2025)
- [ ] SSH into VPS: `ssh root@YOUR_VPS_IP`
- [ ] Run deployment script
  - [ ] Download: `curl -o deploy.sh https://raw.githubusercontent.com/...`
  - [ ] Make executable: `chmod +x deploy.sh`
  - [ ] Edit email in script
  - [ ] Run: `sudo ./deploy.sh`
- [ ] Verify installation
  - [ ] Check Mport service: `sudo systemctl status mport`
  - [ ] Check Nginx: `sudo systemctl status nginx`
  - [ ] Check SSL: `sudo certbot certificates`
- [ ] Test health endpoint: `curl https://mport.app/health`

#### Day 4: Testing & Verification (Nov 6, 2025)
- [ ] Test HTTPS endpoints
  - [ ] `curl https://mport.app/` (should show landing page)
  - [ ] `curl https://mport.app/health` (should return "healthy")
  - [ ] `curl https://mport.app/api/status` (control port)
- [ ] Test client connection from local PC
  - [ ] Direct TCP: `python client/tunnel_client.py --server mport.app --port 8081`
  - [ ] Verify client registers successfully
  - [ ] Check server logs: `sudo journalctl -u mport -f`
- [ ] Test ADB tunnel from local PC
  - [ ] `adb connect mport.app:8080`
  - [ ] `adb -s mport.app:8080 shell getprop ro.product.model`
  - [ ] Should return: BE2029
- [ ] Test from mobile data (different network)
  - [ ] Connect phone to mobile data (not WiFi)
  - [ ] Test ADB connection
  - [ ] Verify tunnel works over internet

#### Day 5: Client HTTPS Adaptation (Nov 7, 2025)
- [ ] Update tunnel_client.py for HTTPS support
  - [ ] Add `--use-https` CLI flag
  - [ ] Modify control connection to use HTTPS endpoint
  - [ ] Modify tunnel connection to use HTTPS endpoint
  - [ ] Test both HTTP and HTTPS modes
- [ ] Update quick_start.py
  - [ ] Add HTTPS support
  - [ ] Update default server to mport.app
- [ ] Test HTTPS client connection
  - [ ] Connect via HTTPS
  - [ ] Verify tunnel creation works
  - [ ] Check performance vs raw TCP

#### Day 6: Monitoring & Optimization (Nov 8, 2025)
- [ ] Set up log monitoring
  - [ ] Server logs: `/var/log/mport/server.log`
  - [ ] Nginx access logs: `/var/log/nginx/mport-access.log`
  - [ ] Nginx error logs: `/var/log/nginx/mport-error.log`
  - [ ] Systemd logs: `journalctl -u mport`
- [ ] Configure log rotation
  - [ ] Create `/etc/logrotate.d/mport`
  - [ ] Test rotation: `sudo logrotate -f /etc/logrotate.d/mport`
- [ ] Performance testing
  - [ ] Run stress test from remote location
  - [ ] Measure latency (target: <100ms)
  - [ ] Measure throughput (target: >100 KB/s)
  - [ ] Check CPU/memory usage on VPS
- [ ] Optimization (if needed)
  - [ ] Adjust nginx worker processes
  - [ ] Tune TCP keepalive settings
  - [ ] Adjust rate limits if necessary

#### Day 7: Documentation & Week 1+2 Summary (Nov 9-10, 2025)
- [ ] Update README.md
  - [ ] Add HTTPS endpoints
  - [ ] Update quick start with VPS connection
  - [ ] Add deployment status badge
- [ ] Create WEEK2_COMPLETE.md
  - [ ] Deployment summary
  - [ ] Performance metrics (VPS)
  - [ ] Screenshots (curl tests, systemctl status)
  - [ ] Comparison: Local vs VPS
- [ ] Update CHANGELOG.md
  - [ ] Week 2 changes
  - [ ] New features (HTTPS, Nginx, VPS)
- [ ] Update ROADMAP.md
  - [ ] Mark Week 2 complete
  - [ ] Update Week 3 priorities
- [ ] Git commit and push
  - [ ] Commit all Week 2 changes
  - [ ] Tag release: `v0.2.0-week2`
  - [ ] Push to GitHub

---

## 🎯 Success Criteria (Week 2)

### Must Have ✅
- [ ] Mport running on VPS (24/7 uptime)
- [ ] HTTPS enabled (Let's Encrypt certificate)
- [ ] Nginx reverse proxy working
- [ ] Client can connect from internet
- [ ] ADB tunnel works from remote location
- [ ] DNS resolves correctly (mport.app → VPS IP)
- [ ] SSL certificate auto-renewal configured
- [ ] Systemd service auto-starts on boot
- [ ] Firewall properly configured

### Nice to Have 🌟
- [ ] Client HTTPS support (can connect via HTTPS endpoints)
- [ ] Log rotation configured
- [ ] Performance metrics documented
- [ ] Mobile data testing complete
- [ ] Web landing page looks good

### Future (Week 3+) 🔮
- WebSocket tunneling (for browser clients)
- Token authentication
- User registration system
- Multiple tunnels per user
- Web dashboard
- Database integration (PostgreSQL)

---

## 📊 Metrics to Track

### Performance
- **Latency:** Connection time (target: <100ms)
- **Throughput:** Data transfer rate (target: >100 KB/s)
- **Uptime:** Service availability (target: 99%+)
- **Response Time:** API endpoints (target: <50ms)

### Usage
- **Connections:** Total connections per day
- **Tunnels:** Active tunnels count
- **Clients:** Registered clients count
- **Errors:** Error rate (target: <1%)

### System
- **CPU:** Average usage (target: <50%)
- **Memory:** Average usage (target: <70%)
- **Disk:** Space used (target: <50%)
- **Network:** Bandwidth used

---

## 🚨 Common Issues & Solutions

### Issue 1: DNS Not Resolving
**Problem:** `nslookup mport.app` doesn't return VPS IP  
**Solution:**
- Check DNS records at Name.com
- Wait 5-60 minutes for propagation
- Use `dig mport.app` to check TTL
- Try `nslookup mport.app 8.8.8.8` (Google DNS)

### Issue 2: SSL Certificate Failed
**Problem:** Let's Encrypt certificate request fails  
**Solution:**
- Ensure DNS is pointing to VPS
- Check firewall allows port 80
- Stop nginx before certbot: `sudo systemctl stop nginx`
- Try manual mode: `sudo certbot certonly --standalone -d mport.app`

### Issue 3: Service Won't Start
**Problem:** `systemctl status mport` shows failed  
**Solution:**
- Check logs: `sudo journalctl -u mport -n 50`
- Test manually: `python3.13 server/tunnel_server.py`
- Check Python version: `python3.13 --version`
- Check permissions: `ls -la /opt/mport`

### Issue 4: Nginx 502 Bad Gateway
**Problem:** `curl https://mport.app` returns 502 error  
**Solution:**
- Check Mport service running: `sudo systemctl status mport`
- Check ports listening: `sudo ss -tunlp | grep -E '8080|8081|8082'`
- Check nginx logs: `sudo tail -f /var/log/nginx/mport-error.log`
- Test upstream: `curl localhost:8080`

### Issue 5: Can't Connect from Client
**Problem:** Client gets connection refused  
**Solution:**
- Check firewall: `sudo ufw status`
- Test connectivity: `telnet mport.app 8081`
- Check service listening: `sudo ss -tunlp | grep 8081`
- Check if --host 0.0.0.0 is set in service

---

## 📝 Notes

### DigitalOcean Student Pack
- $200 credit = 33 months of $6/month droplet
- Can upgrade droplet size anytime
- Free while credit lasts, then $6/month

### Domain (mport.app)
- Free with Student Pack (1 year)
- .app domains require HTTPS (good for us!)
- Can add subdomains (api.mport.app, etc.)

### Let's Encrypt
- Free SSL certificates
- Auto-renewal every 90 days
- Wildcard support (*.mport.app)

### VPS Location
- Bangalore, India = ~40-60ms latency from Pakistan
- Could add Singapore droplet later (load balancing)
- Could add US/EU droplets for global users

---

## 🎓 Learning Goals

By end of Week 2, you should understand:

✅ **Reverse Proxy Pattern**
- How Nginx routes requests to internal services
- TLS termination (SSL handled at proxy, internal = HTTP)
- Why this is industry standard

✅ **SSL/TLS**
- How Let's Encrypt works (ACME protocol)
- Certificate renewal process
- HTTPS vs HTTP performance impact

✅ **DevOps Basics**
- systemd service management
- UFW firewall configuration
- SSH and remote server management
- Log monitoring and debugging

✅ **DNS**
- A records, CNAME records
- DNS propagation
- TTL (Time To Live)

✅ **Linux Server Admin**
- Ubuntu package management (apt)
- User and permission management
- Service debugging (journalctl, systemctl)

---

**Checklist Version:** 1.0  
**Last Updated:** November 3, 2025  
**Status:** Ready for Week 2 execution

---

*Let's deploy to production! 🚀*
