@echo off
REM Quick Phone Connection Check
REM =============================

echo.
echo ╔═══════════════════════════════════════════════════════╗
echo ║   📱 PHONE CONNECTION SETUP                          ║
echo ╚═══════════════════════════════════════════════════════╝
echo.

echo [STEP 1] Enable WiFi ADB on your phone:
echo   1. Go to Settings ^> Developer Options
echo   2. Enable "Wireless debugging" or "ADB over network"
echo   3. Note the IP address shown (e.g., 192.168.1.100:5555)
echo.

echo [STEP 2] Find your phone's current IP:
echo.
echo Checking network for Android devices...
adb devices -l
echo.

echo [STEP 3] If phone is connected via USB, enable WiFi:
adb tcpip 5555
timeout /t 2 > nul
echo.

echo [STEP 4] Try to connect (update IP if needed):
set /p phone_ip="Enter phone IP (press Enter for 192.168.100.148): "
if "%phone_ip%"=="" set phone_ip=192.168.100.148

echo Connecting to %phone_ip%:5555...
adb connect %phone_ip%:5555
echo.

echo [STEP 5] Verify connection:
adb devices
echo.

echo ✅ If you see your device listed above, you're ready!
echo 🔴 If not, check WiFi settings on phone and try again.
echo.
pause
