@echo off
title Android Remote Access - Auto Installer
color 0A

echo.
echo ============================================================
echo    ANDROID REMOTE ACCESS - AUTOMATIC INSTALLER
echo ============================================================
echo.

:: Check if ADB is installed
echo [*] Checking ADB installation...
adb version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] ADB is already installed
) else (
    echo [!] ADB not found
    echo.
    echo Installing ADB via Chocolatey...
    choco --version >nul 2>&1
    if %errorlevel% equ 0 (
        choco install adb -y
    ) else (
        echo [!] Chocolatey not found
        echo Please install ADB manually or install Chocolatey first
        pause
        exit /b
    )
)

echo.
echo [*] Installing Python dependencies...
pip install colorama qrcode[pil] Pillow

echo.
echo [*] Checking scrcpy (optional)...
scrcpy --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] scrcpy is installed
) else (
    echo [!] scrcpy not found (optional for screen mirroring)
    choice /C YN /M "Install scrcpy"
    if errorlevel 2 goto skip_scrcpy
    if errorlevel 1 (
        choco --version >nul 2>&1
        if %errorlevel% equ 0 (
            choco install scrcpy -y
        ) else (
            echo Install via: scoop install scrcpy
        )
    )
)

:skip_scrcpy

echo.
echo ============================================================
echo    INSTALLATION COMPLETE!
echo ============================================================
echo.
echo [*] To start the controller, run:
echo     python phone_controller.py
echo.
echo [*] For quick access, run:
echo     python quick_launch.py
echo.
echo [*] Don't forget to enable USB Debugging on your phone!
echo.
pause
