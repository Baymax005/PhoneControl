# Fly.io Deployment Guide - Quick Start (5 Minutes!)

**Perfect for:** Testing Mport **NOW** without credit card hassles!  
**Migration Path:** Once tested, easily move to DigitalOcean for more resources.

---

## Why Fly.io First?

✅ **No credit card** required for free tier  
✅ **5-minute setup** vs 30 minutes on traditional VPS  
✅ **Auto HTTPS** - No manual SSL certificate setup  
✅ **Global CDN** - Lower latency than single-region VPS  
✅ **Easy migration** - Export config, move to DO later  

---

## Free Tier Limits

| Resource | Free Allowance | Mport Usage |
|----------|----------------|-------------|
| **RAM** | 256MB (3 VMs) | ~200MB ✅ |
| **Storage** | 3GB | ~50MB ✅ |
| **Transfer** | 160GB/month | ~10GB typical ✅ |
| **VMs** | 3 shared-cpu | 1 needed ✅ |

**Perfect fit!** Mport works well within free tier limits.

---

## Prerequisites

1. **Email address** (for Fly.io account)
2. **flyctl CLI** (install below)
3. **Docker** (optional, Fly.io builds remotely)
4. **Domain** (optional, Fly.io provides free subdomain)

---

## Step 1: Install flyctl CLI

### Windows (PowerShell):
```powershell
# Option 1: Scoop
scoop install flyctl

# Option 2: Direct download
iwr https://fly.io/install.ps1 -useb | iex
```

### macOS/Linux:
```bash
curl -L https://fly.io/install.sh | sh
```

### Verify installation:
```powershell
flyctl version
```

---

## Step 2: Sign Up & Login

```powershell
# Sign up (opens browser)
flyctl auth signup

# Or login if you have account
flyctl auth login
```

**No credit card required!** Just verify your email.

---

## Step 3: Launch Mport

```powershell
cd C:\Users\muham\OneDrive\Desktop\OTHER LANGS\web dev\PhoneControl\Mport

# Launch app (interactive)
flyctl launch
```

**Answer the prompts:**
1. **App name:** `mport-tunnel` (or choose your own)
2. **Region:** Singapore (`sin`) - closest to Pakistan
3. **Deploy now?** `Yes`

Fly.io will:
- ✅ Detect `Dockerfile` and `fly.toml`
- ✅ Build Docker image remotely
- ✅ Deploy to global edge network
- ✅ Provision free HTTPS certificate
- ✅ Give you a URL: `mport-tunnel.fly.dev`

**That's it!** Your server is live! 🎉

---

## Step 4: Test Your Deployment

### Check app status:
```powershell
flyctl status
```

### View logs:
```powershell
flyctl logs
```

### Check health:
```powershell
curl https://mport-tunnel.fly.dev
```

### Test control port:
```powershell
# From your local PC, test connection
python client/tunnel_client.py --server mport-tunnel.fly.dev --port 8081
```

---

## Step 5: Monitor & Debug

### View dashboard:
```powershell
flyctl dashboard
# Opens browser to https://fly.io/dashboard
```

### SSH into container:
```powershell
flyctl ssh console
```

### Check metrics:
```powershell
flyctl monitor
```

### Restart app:
```powershell
flyctl apps restart mport-tunnel
```

---

## Custom Domain (Optional)

### Add your domain (e.g., mport.app):

```powershell
# Add certificate
flyctl certs create mport.app

# Get DNS records to add
flyctl certs show mport.app
```

### Add to your DNS provider:
```
A     @      66.241.124.123  (Fly.io IP, changes per region)
AAAA  @      [IPv6 address]
```

**Wait 5-10 minutes** for DNS propagation.

### Verify:
```powershell
curl https://mport.app
```

---

## Configuration

### Environment Variables

Edit `fly.toml` to add secrets:

```powershell
# Set secrets (encrypted)
flyctl secrets set AUTH_TOKEN=your-secret-token
flyctl secrets set DB_PASSWORD=password123

# List secrets
flyctl secrets list
```

### Scale Resources (If Needed)

```powershell
# Upgrade RAM (beyond free tier, $0.0000008/sec = ~$2/month for 512MB)
flyctl scale memory 512

# Add more VMs
flyctl scale count 2

# View pricing
flyctl scale show
```

---

## Troubleshooting

### Issue 1: "Not enough memory"

**Problem:** App crashes due to 256MB limit.

**Solution:**
```powershell
# Check memory usage
flyctl logs | grep "memory"

# Optimize: Reduce connections in fly.toml
# Edit hard_limit from 100 to 50
flyctl deploy
```

### Issue 2: "Connection timeout"

**Problem:** Ports not accessible.

**Solution:**
```powershell
# Verify ports in fly.toml
flyctl services list

# Redeploy
flyctl deploy
```

### Issue 3: "Build failed"

**Problem:** Docker build error.

**Solution:**
```powershell
# Build locally first
docker build -t mport .

# Test locally
docker run -p 8080:8080 -p 8081:8081 -p 8082:8082 mport

# If local build works, try deploy again
flyctl deploy
```

### Issue 4: "Out of free tier"

**Problem:** Exceeded 160GB transfer.

**Solution:**
```powershell
# Check usage
flyctl billing show

# Reduce connections or upgrade
flyctl scale count 0  # Stop until next month
```

---

## Performance Expectations

### Fly.io Free Tier:

```
Concurrent connections: 30-50
Latency: 30-80ms (Singapore → Pakistan)
Throughput: 50-100 KB/s
CPU usage: 40-60% under load
Memory usage: 180-220MB
Uptime: 99.5%+ (Fly.io SLA)
```

**Good for:** Testing, development, small-scale production (10-20 users)

---

## Migration to DigitalOcean (Later)

### When to migrate?

1. ✅ **More RAM needed** - Need 1GB+ for 100+ users
2. ✅ **More storage** - Need 10GB+ for logs/data
3. ✅ **More control** - Need custom Nginx, system tools
4. ✅ **Cost optimization** - DO $6/month vs Fly.io $5-10/month after free tier

### How to migrate:

**Step 1: Export data (if any)**
```powershell
flyctl ssh sftp get /app/data ./data
```

**Step 2: Deploy to DigitalOcean**
```bash
# On DO droplet
git clone https://github.com/Baymax005/PhoneControl.git
cd PhoneControl/Mport/deployment
sudo ./deploy.sh
```

**Step 3: Update DNS**
```
A     @      [DO_DROPLET_IP]
```

**Step 4: Destroy Fly.io app**
```powershell
flyctl apps destroy mport-tunnel
```

**That's it!** No downtime if you update DNS properly.

---

## Cost Comparison

| Scenario | Fly.io | DigitalOcean |
|----------|--------|--------------|
| **First month** | $0 | $0 (credits) |
| **Testing (10 users)** | $0 | $0 |
| **Production (50 users)** | $0-5/mo | $6/mo |
| **Heavy usage (100+ users)** | $10-15/mo | $6/mo |

**Recommendation:**
- **Now:** Use Fly.io (free, no card)
- **Later:** Migrate to DO (better value at scale)

---

## Quick Commands Reference

```powershell
# Deploy
flyctl deploy

# View logs
flyctl logs -a mport-tunnel

# SSH
flyctl ssh console

# Status
flyctl status

# Scale
flyctl scale show
flyctl scale memory 512
flyctl scale count 2

# Secrets
flyctl secrets set KEY=value
flyctl secrets list

# Destroy
flyctl apps destroy mport-tunnel
```

---

## Support & Resources

- **Fly.io Docs:** https://fly.io/docs/
- **Community:** https://community.fly.io/
- **Status:** https://status.fly.io/
- **Pricing:** https://fly.io/docs/about/pricing/

---

## Next Steps

### ✅ You're Live!

1. **Test from internet:** Use your phone's 4G (not WiFi)
2. **Share with friends:** Get 5-10 people to test
3. **Monitor usage:** Watch Fly.io dashboard
4. **Optimize if needed:** Adjust `fly.toml` settings

### 📈 When Ready to Scale:

1. Read `docs/DEPLOYMENT.md` for DigitalOcean guide
2. Sign up for DO Student Pack ($200 credit)
3. Deploy with `deployment/deploy.sh`
4. Update DNS
5. Destroy Fly.io app

---

**Deployment Time:** ~5 minutes  
**Cost:** $0 for testing  
**Migration:** Easy to DigitalOcean later  

🚀 **Start testing NOW without credit card hassles!**
