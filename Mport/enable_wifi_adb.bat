@echo off
echo ╔═══════════════════════════════════════════════════════╗
echo ║   📱 ENABLE WIFI ADB - Step by Step                  ║
echo ╚═══════════════════════════════════════════════════════╝
echo.
echo [STEP 1] Connect your phone via USB cable
echo.
pause
echo.
echo [STEP 2] Checking for phone...
adb devices
echo.
echo If you see a device above, press any key to continue...
echo If NOT, enable USB Debugging on phone and try again!
pause
echo.
echo [STEP 3] Enabling WiFi ADB mode...
adb tcpip 5555
echo.
echo ✅ WiFi ADB mode enabled!
echo.
echo [STEP 4] You can now UNPLUG the USB cable
pause
echo.
echo [STEP 5] Connecting to phone at 192.168.100.2:5555...
timeout /t 2 > nul
adb connect 192.168.100.2:5555
echo.
echo [STEP 6] Verifying connection...
adb devices
echo.
echo ✅ If you see "192.168.100.2:5555    device" above, you're ready!
echo.
pause
