@echo off
title Quick Wireless Connect
color 0B

echo.
echo ============================================
echo    QUICK WIRELESS CONNECT
echo ============================================
echo.

REM Add Scoop to PATH
set PATH=%USERPROFILE%\scoop\shims;%PATH%

:menu
echo [1] Connect by IP Address
echo [2] Connect to Last Device
echo [3] Launch Wireless Manager
echo [4] Scan Network
echo [5] Exit
echo.

set /p choice="Select option: "

if "%choice%"=="1" goto connect_ip
if "%choice%"=="2" goto connect_last
if "%choice%"=="3" goto manager
if "%choice%"=="4" goto scan
if "%choice%"=="5" goto end
goto menu

:connect_ip
echo.
set /p ip="Enter phone IP address: "
set /p port="Enter port (default 5555): "
if "%port%"=="" set port=5555

echo.
echo [*] Connecting to %ip%:%port%...
adb connect %ip%:%port%

echo.
echo [*] Connected devices:
adb devices

echo.
pause
goto menu

:connect_last
echo.
echo [*] Attempting to connect to last device...
if exist "last_device.txt" (
    set /p lastip=<last_device.txt
    adb connect %lastip%
    echo.
    echo [*] Connected devices:
    adb devices
) else (
    echo [!] No previous device found
)
echo.
pause
goto menu

:manager
python wireless_connector.py
goto menu

:scan
echo.
echo [*] Scanning network for Android devices...
echo [!] This may take 1-2 minutes...
python wireless_connector.py
goto menu

:end
echo.
echo Goodbye!
timeout /t 2
