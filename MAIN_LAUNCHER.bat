@echo off
title PhoneControl - Main Launcher
color 0A
cls

echo.
echo ╔═══════════════════════════════════════════════════════╗
echo ║         📱 PHONECONTROL - MAIN MENU                  ║
echo ╚═══════════════════════════════════════════════════════╝
echo.
echo  [1] 📡 Wireless ADB Connector (Local Control)
echo  [2] 🌐 Web Exploit Server
echo  [3] 🚀 Mport - "Your Port to the World" (In Development)
echo.
echo  [4] 📚 View Documentation
echo  [5] ⚙️  Project Structure
echo.
echo  [0] ❌ Exit
echo.

set /p choice="Choose option (0-5): "

if "%choice%"=="1" goto wireless
if "%choice%"=="2" goto webexploit
if "%choice%"=="3" goto tunnel
if "%choice%"=="4" goto docs
if "%choice%"=="5" goto structure
if "%choice%"=="0" goto exit

echo Invalid choice!
timeout /t 2 >nul
goto start

:wireless
cls
echo.
echo Starting Wireless ADB Connector...
echo.
cd WirelessConnector
python wireless_connector.py
cd ..
pause
goto start

:webexploit
cls
echo.
echo Starting Web Exploit Server...
echo.
cd WebExploit
python web_exploit_server.py
cd ..
pause
goto start

:tunnel
cls
echo.
echo ╔═══════════════════════════════════════════════════════╗
echo ║   🚀 MPORT - "YOUR PORT TO THE WORLD"                ║
echo ╚═══════════════════════════════════════════════════════╝
echo.
echo Status: 🏗️  IN DEVELOPMENT
echo.
echo Building production-level tunneling service from scratch!
echo.
echo What is Mport?
echo  • Like ngrok, but works in Pakistan
echo  • Free for students (GitHub Student Pack)
echo  • Multi-user support with web dashboard
echo  • Production-ready security
echo.
echo Features (Planned):
echo  ✅ Custom tunnel protocol
echo  ✅ Server + Client architecture  
echo  ✅ Multi-user support
echo  ✅ Web dashboard
echo  ✅ Production-ready
echo.
cd Mport
if exist main.py (
    python main.py
) else (
    echo No files yet. Ready to start Phase 1!
    echo.
    echo Next Steps:
    echo  1. Read: ROADMAP.md
    echo  2. Read: BRANDING.md
    echo  3. Start Week 1 - Basic TCP Tunnel
)
cd ..
pause
goto start

:docs
cls
echo.
echo Opening documentation folder...
explorer docs
goto start

:structure
cls
type PROJECT_STRUCTURE.md
echo.
pause
goto start

:exit
cls
echo.
echo Thanks for using PhoneControl!
echo.
timeout /t 1 >nul
exit

:start
cls
goto :eof
