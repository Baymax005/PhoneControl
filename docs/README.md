# 🔒 Android Remote Access Controller

**Ethical Hacking Project** - Complete remote Android device control system with multiple access methods.

## 🌟 Features

### Connection Methods
- **⚡ Quick Connect** - One-click reconnect to saved devices
- **📱 Wireless Access** - QR code-based wireless setup (no USB needed after first setup)
- **🔌 USB Connection** - Traditional ADB connection

### Device Control
- **📊 Device Information** - Model, Android version, battery, screen state
- **📲 App Installation** - Install APKs remotely
- **🖥️ Screen Mirroring** - Real-time screen view with scrcpy
- **📁 File Management** - Upload/download files, browse device storage
- **🎮 Remote Control** - Full device control from your computer

### Advanced Features
- **📸 Screenshots & Recording** - Capture screen silently
- **🔔 Notifications** - Send custom notifications
- **📞 Call & SMS** - Make calls and send messages remotely
- **🔓 Lock/Unlock** - Control device lock state
- **🕵️ Stealth Mode** - Silent operations for monitoring

## 🚀 Quick Start

### Step 1: Installation
```powershell
# Run the automatic setup script
python quick_setup.py
```

Or install manually:
```powershell
# Install Python dependencies
pip install -r requirements.txt

# Install ADB (choose one):
choco install adb -y          # Using Chocolatey
scoop install adb             # Using Scoop

# Optional: Install scrcpy for screen mirroring
choco install scrcpy -y
```

### Step 2: Prepare Your Android Device
1. **Enable Developer Options:**
   - Go to `Settings` > `About Phone`
   - Tap `Build Number` 7 times
   - You'll see "You are now a developer!"

2. **Enable USB Debugging:**
   - Go to `Settings` > `Developer Options`
   - Turn ON `USB Debugging`
   - (Optional) Turn ON `Wireless debugging` for Android 11+

3. **Connect Device:**
   - Connect phone via USB cable
   - Authorize computer when prompted on phone

### Step 3: Run the Controller
```powershell
python phone_controller.py
```

## 📋 Usage Guide

### First Time Setup (Wireless)
1. Run `phone_controller.py`
2. Select option `2` (Wireless Setup)
3. Follow the prompts
4. Scan the QR code for quick reconnect later
5. Disconnect USB cable - you're now wireless! 🎉

### Quick Reconnect
1. Make sure phone and PC are on same WiFi
2. Run `phone_controller.py`
3. Select option `1` (Quick Connect)
4. Done! ⚡

## 🎯 Main Features Explained

### 📱 Remote Control Operations
- **Take Screenshot** - Capture current screen
- **Record Screen** - Record video up to specified duration
- **Send Notification** - Display custom notifications
- **Open URL** - Launch any URL in browser
- **Make Call** - Initiate phone calls
- **Send SMS** - Send text messages
- **Lock/Unlock** - Control device lock state
- **Reboot** - Restart the device

### 📁 File Management
- **List Files** - Browse device storage
- **Pull Files** - Download files from device
- **Push Files** - Upload files to device
- **Custom Paths** - Browse any directory

### 🕵️ Stealth Mode (Ethical Use Only!)
- **Silent Screenshots** - Capture screen without traces
- **Location Data** - Get GPS information
- **Installed Apps** - List all applications
- **SMS Access** - Read messages (requires root)
- **Call Logs** - View call history
- **Contacts** - Access contact list
- **Clipboard Monitor** - Read clipboard content

## ⚠️ Important Notes

### Legal & Ethical Use
- ✅ Use ONLY on devices you own
- ✅ Educational and ethical hacking purposes
- ✅ With explicit permission from device owner
- ❌ Unauthorized access is ILLEGAL
- ❌ Respect privacy laws

### Permissions Required
- USB Debugging must be enabled
- Some features require additional permissions
- Root access needed for advanced features (SMS, calls)

### Troubleshooting

**Device not detected:**
```powershell
adb devices
# If no devices, check USB cable and try different port
# Make sure USB debugging is authorized on phone
```

**Wireless connection fails:**
```powershell
# Make sure both devices are on same WiFi network
# Check if firewall is blocking port 5555
# Restart ADB: adb kill-server && adb start-server
```

**ADB not found:**
```powershell
# Install using Chocolatey:
choco install adb -y

# Or using Scoop:
scoop install adb

# Or download Platform Tools manually
```

## 🛠️ Advanced Usage

### Manual Wireless Connection
```powershell
# Enable TCP/IP mode (phone connected via USB)
adb tcpip 5555

# Get device IP (Settings > About Phone > Status)
# Connect wirelessly
adb connect 192.168.1.100:5555

# Disconnect USB cable
```

### Custom ADB Commands
```python
# In the controller, you can run any ADB command:
controller.run_adb_command("your command here")
```

## 📦 Project Structure
```
PhoneControl/
├── phone_controller.py    # Main application
├── quick_setup.py         # Automatic installer
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── device_config.json    # Saved device info (auto-generated)
└── connection_qr.png     # QR code for quick connect (auto-generated)
```

## 🔧 Technologies Used
- **ADB** (Android Debug Bridge) - Core communication
- **Python** - Main programming language
- **colorama** - Colored terminal output
- **qrcode** - QR code generation
- **scrcpy** - Screen mirroring (optional)

## 🎓 Educational Use Cases
- Learning Android internals
- Testing mobile applications
- Security research
- Automation testing
- Remote device management

## 📝 License
This project is for educational purposes only. Use responsibly and ethically.

## 🤝 Contributing
This is a personal ethical hacking project. Feel free to extend it for your own learning!

## ⚡ Pro Tips
1. Save the QR code for quick reconnects
2. Use wireless mode for true remote access
3. Keep device on charger for long operations
4. Test features on your own device first
5. Always respect privacy and legal boundaries

---

**Remember:** With great power comes great responsibility! 🦸‍♂️

Made with ❤️ for ethical hacking education
