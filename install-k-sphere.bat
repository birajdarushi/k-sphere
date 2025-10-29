@echo off
REM K-Sphere One-Click Installer for Windows
REM Double-click this file to install K-Sphere

title K-Sphere Installer

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo ============================================
    echo   Administrator privileges required
    echo ============================================
    echo.
    echo Please right-click this file and select
    echo "Run as administrator"
    echo.
    pause
    exit /b 1
)

REM Run PowerShell installer
powershell.exe -ExecutionPolicy Bypass -File "%~dp0install-standalone.ps1"

pause
