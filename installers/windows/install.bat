@echo off
title Oktopios Installer
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
if errorlevel 1 (
    echo.
    echo  Installation echouee. Consultez le message ci-dessus.
    pause
    exit /b 1
)
