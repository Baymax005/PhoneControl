# 📁 PhoneControl - Project Structure

## 🎯 Main Projects

### 1️⃣ **WirelessConnector/** - ADB Wireless Manager
Complete Android device control over WiFi
- `wireless_connector.py` - Main control panel (15+ features)
- `auto_usb_connector.py` - One-time USB setup wizard
- `setup_*.py` - Remote access setup scripts
- `wireless_devices.json` - Saved devices

**Features:**
- Screenshots & screen recording
- File manager
- App installation
- Shell access
- Live screen monitoring (scrcpy)
- Power-off prevention

---

### 2️⃣ **WebExploit/** - Browser-Based Remote Access
Web server for browser exploitation demo
- `web_exploit_server.py` - Flask + Socket.IO server
- `templates/` - HTML/JS interface

**Features:**
- Camera access
- Vibration control
- Browser info extraction
- Hacker-style interface

---

### 3️⃣ **TunnelProject/** - 🚀 NEW Production-Level Tunnel Service
Building custom ngrok-like tunneling service

**Goal:** Production-ready tunneling platform
**Status:** 🏗️ In Development

---

## 📚 Supporting Folders

### `docs/`
All documentation, guides, and README files
- Setup guides
- Usage instructions
- Feature documentation

### `scripts/`
Batch files and automation scripts
- `launcher.bat` - Main launcher
- Quick start scripts

### `archived/`
Old versions and deprecated files
- Legacy code
- Backup files
- Testing files

### `static/` & `payloads/`
WebExploit assets and resources

---

## 🚀 Quick Start

### Local ADB Control:
```bash
python WirelessConnector/wireless_connector.py
```

### Web Exploit:
```bash
python WebExploit/web_exploit_server.py
```

### Main Menu:
```bash
scripts/launcher.bat
```

---

## 🎓 Learning Project

**Current Focus:** Building production-level tunnel service
**Tech Stack:** Python → Go (later)
**Timeline:** 2-3 months for MVP

---

## 📝 Notes

- **WirelessConnector**: Fully functional, production-ready
- **WebExploit**: Complete demo, educational use only
- **TunnelProject**: New ambitious project, building from scratch

**Author:** Learning ethical hacking & network programming
**Purpose:** Educational project portfolio
