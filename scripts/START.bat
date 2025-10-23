@echo off
echo Starting Android Remote Access Controller...
echo.

REM Refresh PATH to include Scoop
set PATH=%USERPROFILE%\scoop\shims;%PATH%

REM Start the controller
python phone_controller.py

pause
