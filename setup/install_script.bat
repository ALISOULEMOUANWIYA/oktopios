@echo off
SETLOCAL ENABLEEXTENSIONS
SET "TARGET_PATH=%~dp0\..\bin"
SETX PATH "%PATH%;%TARGET_PATH%" /M
echo.
echo ✅ Oktopios a été ajouté au PATH utilisateur.
echo 🔁 Redémarre ton terminal pour que le changement prenne effet.
pause
