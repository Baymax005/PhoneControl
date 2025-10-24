# Mport Week 1 Day 2 - Testing Instructions

## 🚀 Quick Test Guide

### Architecture Understanding
```
Internet User (Port 8080) → Mport Server → Mport Client (Port 8081) → Phone ADB (5555)
```

### Step 1: Prepare Your Phone
Make sure your phone is connected to ADB over WiFi:
```powershell
adb connect 192.168.100.148:5555
```

Verify it's working:
```powershell
adb devices
```

You should see:
```
192.168.100.148:5555    device
```

### Step 2: Start the Mport Server
Open **Terminal 1** (PowerShell):
```powershell
cd "c:\Users\muham\OneDrive\Desktop\OTHER LANGS\web dev\PhoneControl"
python Mport/server/tunnel_server.py
```

You should see:
```
🚀 MPORT SERVER - YOUR PORT TO THE WORLD

Starting Mport Server...
  • Public port:  8080 (for internet users)
  • Control port: 8081 (for Mport clients)

[PUBLIC SERVER] Listening on ('0.0.0.0', 8080)
[CONTROL SERVER] Listening on ('0.0.0.0', 8081)
```

### Step 3: Start the Mport Client
Open **Terminal 2** (PowerShell):
```powershell
cd "c:\Users\muham\OneDrive\Desktop\OTHER LANGS\web dev\PhoneControl"
python Mport/client/tunnel_client.py
```

When prompted, use these values:
- Server host: **localhost** (press Enter for default)
- Server port: **8081** (press Enter for default)
- Local service host: **192.168.100.148** (press Enter for default)
- Local service port: **5555** (press Enter for default)

You should see:
```
✅ Registered as: client_1
✅ Tunnel established!
Waiting for traffic...
```

### Step 4: Test with ADB
Open **Terminal 3** (PowerShell):
```powershell
# Connect to the tunnel instead of directly to phone
adb connect localhost:8080
```

If the tunnel works, you should be able to run ADB commands:
```powershell
adb -s localhost:8080 shell getprop ro.product.model
```

### Expected Flow
When you run the ADB command:
1. **Terminal 3**: ADB sends data to localhost:8080
2. **Terminal 1** (Server): Receives on port 8080, forwards to client on port 8081
3. **Terminal 2** (Client): Receives from server, forwards to phone 192.168.100.148:5555
4. **Phone**: Responds to ADB command
5. **Response flows back**: Phone → Client → Server → ADB

### Logs to Watch For

**Terminal 1 (Server):**
```
[PUBLIC] New connection from ('127.0.0.1', XXXXX)
[PUBLIC] Routing ('127.0.0.1', XXXXX) -> client_1
[TUNNEL tunnel_1] Starting bidirectional forward
[FORWARD ('127.0.0.1', XXXXX)->CLIENT] XX bytes
[FORWARD CLIENT->('127.0.0.1', XXXXX)] XX bytes
```

**Terminal 2 (Client):**
```
Connecting to local service 192.168.100.148:5555
✅ Connected to local service
Starting bidirectional tunnel
[FORWARD SERVER->LOCAL] XX bytes
[FORWARD LOCAL->SERVER] XX bytes
```

### Troubleshooting

**Problem**: "No Mport clients connected!"
- **Solution**: Start the client (Terminal 2) before testing with ADB

**Problem**: "Cannot connect to local service 192.168.100.148:5555"
- **Solution**: Make sure phone is connected via `adb connect 192.168.100.148:5555`

**Problem**: ADB connection hangs
- **Solution**: Check that all 3 terminals show traffic flowing

**Problem**: Client shows "Connection refused"
- **Solution**: Make sure server (Terminal 1) is running first

### Success Criteria ✅
- [ ] Server starts on both ports (8080, 8081)
- [ ] Client connects and gets registered (client_1)
- [ ] ADB can connect to localhost:8080
- [ ] ADB commands work through the tunnel
- [ ] Logs show bidirectional data flow

### What This Proves
When this works, you've built a WORKING TCP tunnel! 🎉

This is the core of ngrok, Cloudflare Tunnel, and all similar services.

Next steps (Week 1 Days 3-7):
- Add proper error handling
- Support multiple simultaneous connections
- Add connection persistence
- Prepare for Week 2: Security (TLS/SSL)
