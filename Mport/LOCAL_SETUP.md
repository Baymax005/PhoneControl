# 🚀 Mport - Local Setup (Working!)

## ✅ What Works

Your Mport tunnel is **fully functional on localhost**!

---

## 🎯 Quick Start (3 Steps)

### Step 1: Connect Your Phone via WiFi ADB

**Option A: Use the batch file**
```
Double-click: enable_wifi_adb.bat
```

**Option B: Manual**
```powershell
# Connect phone via USB
adb devices
adb tcpip 5555

# Unplug USB, then connect via WiFi
adb connect 192.168.100.2:5555
```

---

### Step 2: Start Server & Client

**Terminal 1: Start Server**
```
Double-click: start_server_local.bat
```

**Terminal 2: Start Client**
```
Double-click: start_client_local.bat
```

---

### Step 3: Use ADB Through Tunnel

```powershell
# Connect
adb connect localhost:8080

# Test
adb -s localhost:8080 shell getprop ro.product.model
# Output: BE2029 ✅

# Use normally
adb -s localhost:8080 shell ls /sdcard
adb -s localhost:8080 install app.apk
```

---

## 📊 Architecture

```
┌─────────────┐         ┌─────────────┐         ┌──────────┐
│  ADB Client │ ──────► │   Server    │ ──────► │  Client  │
│ localhost   │         │ (Your PC)   │         │ (Your PC)│
└─────────────┘         └─────────────┘         └──────────┘
     :8080                   :8080/:8081                │
                                                        │
                                                        ▼
                                                 ┌─────────────┐
                                                 │   Phone     │
                                                 │ 192.168.100.2│
                                                 └─────────────┘
```

---

## 🎯 What You Have

✅ **Working:** Local tunnel on your PC  
✅ **Phone:** BE2029 connected via WiFi (192.168.100.2:5555)  
✅ **ADB:** Fully functional through localhost:8080  

❌ **Not Working:** Replit (doesn't support raw TCP on free tier)

---

## 🌍 For Remote Access (Future)

To share access with friends over the internet, you'll need:

### Option 1: ngrok (Easiest)
```powershell
# Install ngrok
# Run tunnel
ngrok tcp 8080
```

### Option 2: Real VPS
- DigitalOcean ($6/month with student credits)
- Oracle Cloud (free tier)
- Linode, Vultr, etc.

---

## 📝 Files

- `enable_wifi_adb.bat` - Connect phone via WiFi
- `start_server_local.bat` - Start Mport server
- `start_client_local.bat` - Start Mport client
- `setup_phone.bat` - Interactive phone setup

---

**Status:** ✅ WORKING PERFECTLY on localhost!  
**Tested:** BE2029 phone via WiFi ADB  
**Next:** Deploy to VPS for remote access (optional)
