@echo off
title Phone Control - Main Launcher
color 0B

echo.
echo 
echo    PHONE CONTROL LAUNCHER                     
echo 
echo.
echo Choose what to launch:
echo.
echo 1. Wireless Connector (Main Tool)
echo 2. Auto USB Setup (First Time)
echo 3. Web Exploit Server
echo 4. Exit
echo.

set /p choice="Enter choice (1-4): "

if "%choice%"=="1" (
    cd WirelessConnector
    python wireless_connector.py
)
if "%choice%"=="2" (
    cd WirelessConnector
    python auto_usb_connector.py
)
if "%choice%"=="3" (
    cd WebExploit
    python web_exploit_server.py
)
if "%choice%"=="4" exit

pause
