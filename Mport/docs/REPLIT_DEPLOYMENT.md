# Replit Deployment Guide - NO CARD REQUIRED! 🎉

**Perfect for:** Testing Mport RIGHT NOW without any credit card!  
**Cost:** $0 forever (free tier) or $7/month for Reserved VM (optional)  
**Setup Time:** 3 minutes  
**Migration:** Easy to move to DigitalOcean later

---

## ✨ Why Replit?

✅ **No credit card required** - Sign up with GitHub/Google/Email  
✅ **3-minute setup** - Import from GitHub, click Run  
✅ **Always-on** - Can stay running 24/7 (use UptimeRobot)  
✅ **Public URLs** - Auto-generated HTTPS URLs  
✅ **Built-in editor** - Edit code directly in browser  
✅ **Free tier** - Enough for testing (10-30 concurrent users)  

---

## 🚀 Quick Deployment (3 Steps)

### Step 1: Sign Up on Replit

1. Go to: https://replit.com/signup
2. **Sign up with GitHub** (easiest - auto-imports repos)
3. No credit card needed! ✅

---

### Step 2: Import Mport from GitHub

#### Option A: Import via GitHub (Recommended)

1. Click **"+ Create Repl"**
2. Select **"Import from GitHub"**
3. Enter repository URL:
   ```
   https://github.com/Baymax005/PhoneControl
   ```
4. Select **"main"** branch
5. Click **"Import from GitHub"**

#### Option B: Manual Import

1. Click **"+ Create Repl"**
2. Select **"Python"** as language
3. Name it: `mport-tunnel`
4. Click **"Create Repl"**
5. In the Shell tab, run:
   ```bash
   git clone https://github.com/Baymax005/PhoneControl.git
   cd PhoneControl/Mport
   ```

---

### Step 3: Configure and Run

#### Install Dependencies:

In the **Shell** tab:
```bash
cd Mport  # If you imported the full repo
pip install colorama
```

#### Run the Server:

Click the **"Run"** button (big green button at top)

Or in Shell:
```bash
python3 server/tunnel_server.py --host 0.0.0.0
```

**That's it!** 🎉 Your server is now running!

---

## 🌐 Get Your Public URL

### Replit Auto-Generated URLs:

After clicking Run, Replit will show you URLs in the **Webview** panel:

1. **Main URL** (port 8080):
   ```
   https://mport-tunnel.your-username.repl.co
   ```

2. **Control Port** (8081):
   ```
   https://mport-tunnel.your-username.repl.co:8081
   ```

3. **Tunnel Port** (8082):
   ```
   https://mport-tunnel.your-username.repl.co:8082
   ```

**Copy these URLs!** You'll use them to connect clients.

---

## 🧪 Test Your Deployment

### Test from Local PC:

```powershell
# Replace with YOUR Replit URL
python client/tunnel_client.py --server mport-tunnel.your-username.repl.co --port 8081
```

### Test ADB Connection:

```powershell
# Connect to public port
adb connect mport-tunnel.your-username.repl.co:8080
```

---

## ⚙️ Configuration

### Keep Repl Always-On (FREE)

**Problem:** Free Repls sleep after 1 hour of inactivity.

**Solution:** Use UptimeRobot (FREE) to ping your Repl every 5 minutes:

1. Sign up: https://uptimerobot.com/ (no card!)
2. Add monitor:
   - **Type:** HTTP(s)
   - **URL:** `https://mport-tunnel.your-username.repl.co`
   - **Interval:** 5 minutes
3. Your Repl will stay awake! ✅

### Environment Variables (Optional):

In Replit, click **"Secrets"** (lock icon):

```
PORT = 8080
CONTROL_PORT = 8081
TUNNEL_PORT = 8082
```

### Reserved VM (Optional, $7/month):

For better performance (dedicated CPU/RAM):

1. Click **"Upgrade"** button
2. Choose **"Reserved VM"** plan
3. $7/month - Better than traditional VPS for testing!

---

## 📊 Performance Expectations

### Free Tier:

```
Concurrent connections: 10-30
Latency: 100-200ms (depends on location)
CPU: Shared (0.2-0.5 vCPU)
RAM: Shared (~500MB available)
Storage: 10 GB
Uptime: 99%+ (with UptimeRobot)
```

**Good for:** Testing, development, small demos (5-20 users)

### Reserved VM ($7/month):

```
Concurrent connections: 50-100
Latency: 80-150ms
CPU: 2 vCPU (dedicated)
RAM: 2 GB (dedicated)
Storage: 20 GB
Uptime: 99.9%
```

**Good for:** Small production (50+ users), better than free VPS!

---

## 🐛 Troubleshooting

### Issue 1: "Repl keeps sleeping"

**Solution:** Use UptimeRobot (see above)

### Issue 2: "Connection timeout"

**Problem:** Ports not exposed properly.

**Solution:** Make sure `.replit` file has port configuration:
```toml
[[ports]]
localPort = 8080
externalPort = 80

[[ports]]
localPort = 8081
externalPort = 8081
```

### Issue 3: "Module not found: colorama"

**Solution:** Install in Shell:
```bash
pip install colorama
```

Or add to `requirements.txt` and Replit auto-installs.

### Issue 4: "Out of memory"

**Problem:** Too many connections on free tier.

**Solution:**
- Reduce `--max-connections` in server startup
- Upgrade to Reserved VM ($7/month)
- Or migrate to DigitalOcean

### Issue 5: "Slow performance"

**Problem:** Shared resources on free tier.

**Solution:**
- Upgrade to Reserved VM
- Or migrate to DigitalOcean ($6/month with student credits)

---

## 🔄 Migration to DigitalOcean (Later)

### When to migrate?

1. ✅ **More users** - Need 100+ concurrent connections
2. ✅ **Better performance** - Need <50ms latency
3. ✅ **More control** - Need custom Nginx, system config
4. ✅ **Cost** - DigitalOcean cheaper for heavy usage

### How to migrate:

**Step 1: Get DigitalOcean Student Pack**
- Sign up: https://www.digitalocean.com/github-students
- Get $200 credit (33 months free @ $6/month)

**Step 2: Deploy to DigitalOcean**
```bash
# SSH into DO droplet
git clone https://github.com/Baymax005/PhoneControl.git
cd PhoneControl/Mport/deployment
sudo ./deploy.sh
```

**Step 3: Update Clients**
- Change server URL from Replit to DigitalOcean IP
- Done! 🎉

**Step 4: Stop Replit**
- Just stop the Repl (no need to delete)

---

## 💰 Cost Comparison

| Platform | Free Tier | After Free | Setup Time | Card Required? |
|----------|-----------|------------|------------|----------------|
| **Replit** | ✅ FREE | $7/mo (optional) | 3 min | ❌ **NO!** |
| **DigitalOcean** | $200 credit | $6/mo | 15 min | ⚠️ Yes |
| **Fly.io** | FREE tier | $5-10/mo | 5 min | ⚠️ Yes |
| **Oracle Cloud** | ✅ FREE forever | Still free | 30 min | ⚠️ Yes |

**Winner for NO CARD:** Replit! 🏆

---

## 📚 Replit Resources

- **Docs:** https://docs.replit.com/
- **Community:** https://ask.replit.com/
- **Status:** https://status.replit.com/
- **Pricing:** https://replit.com/pricing

---

## 🎯 Recommended Workflow

### Phase 1: Test on Replit (NOW!)
1. ✅ Deploy to Replit (3 minutes, no card)
2. ✅ Test with 5-10 friends
3. ✅ Validate everything works
4. ✅ Use for 1-2 weeks

### Phase 2: Scale to DigitalOcean (When Ready)
1. Get DigitalOcean Student Pack (with card)
2. Deploy with `deploy.sh`
3. Migrate users
4. Stop Replit or keep as backup

---

## 🚀 Quick Commands

```bash
# Run server
python3 server/tunnel_client.py --host 0.0.0.0

# Install dependencies
pip install colorama

# View logs (in Shell)
# Logs appear in Console tab automatically

# Restart
# Click Stop, then Run again

# Clone repo
git clone https://github.com/Baymax005/PhoneControl.git
cd PhoneControl/Mport
```

---

## ✅ Next Steps

1. **Sign up on Replit**: https://replit.com/signup (use GitHub!)
2. **Import Mport**: Import from `https://github.com/Baymax005/PhoneControl`
3. **Click Run**: Server starts automatically!
4. **Get URL**: Copy from Webview panel
5. **Test**: Connect client with `--server YOUR_REPL_URL`
6. **Keep alive**: Set up UptimeRobot
7. **Share**: Test with friends!

---

**Deployment Time:** ~3 minutes  
**Cost:** $0  
**Card Required:** NO! ✅  
**Good for:** Testing, development, small demos  

🎉 **Deploy NOW without credit card hassles!**
