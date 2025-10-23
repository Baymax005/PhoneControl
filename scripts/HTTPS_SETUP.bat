@echo off
echo ================================================================
echo   NGROK SETUP - Camera Access via HTTPS
echo ================================================================
echo.
echo Windows Defender blocked ngrok download!
echo.
echo SOLUTION - Choose one option:
echo.
echo ════════════════════════════════════════════════════════════════
echo  OPTION 1: Use VS Code Port Forwarding (EASIEST)
echo ════════════════════════════════════════════════════════════════
echo.
echo 1. Make sure your Flask server is running (python web_exploit_server.py)
echo 2. In VS Code, go to PORTS tab (bottom panel)
echo 3. Find port 5000, right-click
echo 4. Select "Port Visibility" -^> "Public"
echo 5. Copy the forwarded URL (looks like: https://xyz-5000.preview.app.github.dev)
echo 6. Share that URL - it's HTTPS and camera will work!
echo.
echo.
echo ════════════════════════════════════════════════════════════════
echo  OPTION 2: Manual ngrok Download
echo ════════════════════════════════════════════════════════════════
echo.
echo 1. Go to: https://ngrok.com/download
echo 2. Download Windows 64-bit version
echo 3. Extract ngrok.exe to this folder
echo 4. Add Windows Defender exception for ngrok.exe
echo 5. Run: ngrok http 5000
echo 6. Copy the HTTPS URL it gives you
echo.
echo.
echo ════════════════════════════════════════════════════════════════
echo  OPTION 3: Use Localhost Tunnel
echo ════════════════════════════════════════════════════════════════
echo.
echo 1. Install: npm install -g localtunnel
echo 2. Run: lt --port 5000
echo 3. Copy the HTTPS URL
echo.
echo.
echo ════════════════════════════════════════════════════════════════
echo  OPTION 4: Accept Self-Signed Certificate (Android)
echo ════════════════════════════════════════════════════════════════
echo.
echo On Android Chrome:
echo 1. Open: https://192.168.100.59:5000
echo 2. You'll see "Your connection is not private"
echo 3. Click "Advanced"
echo 4. Click "Proceed to 192.168.100.59 (unsafe)"
echo 5. Camera will work after accepting!
echo.
echo Then run: python web_exploit_server_https.py
echo.
echo ================================================================
echo.
pause
