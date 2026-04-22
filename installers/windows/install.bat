@echo off
setlocal enabledelayedexpansion
title Oktopios Installer v0.0.1

echo.
echo  ====================================================
echo   🐙  Oktopios v0.0.1 - Installeur Windows
echo  ====================================================
echo.

:: Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERREUR] Python n'est pas installe ou pas dans le PATH.
    echo  Telechargez Python 3.10+ sur https://python.org
    echo  (Cochez "Add Python to PATH" lors de l'installation)
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo  [OK] Python %PYVER% detecte

:: Vérifier pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo  [ERREUR] pip non disponible.
    pause
    exit /b 1
)
echo  [OK] pip disponible

:: Définir dossier d'installation
set "INSTALL_DIR=%LOCALAPPDATA%\Oktopios"
set "BIN_DIR=%INSTALL_DIR%\bin"

echo.
echo  Dossier d'installation : %INSTALL_DIR%
echo.

:: Créer les dossiers
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%BIN_DIR%" mkdir "%BIN_DIR%"

:: Copier les fichiers du projet
echo  [1/4] Copie des fichiers Oktopios...
xcopy /E /I /Y "%~dp0..\" "%INSTALL_DIR%\oktopios\" >nul 2>&1
if errorlevel 1 (
    :: Fallback: télécharger depuis PyPI
    echo  [INFO] Installation depuis PyPI...
    pip install oktopios --quiet
    if errorlevel 1 (
        echo  [ERREUR] Installation echouee.
        pause
        exit /b 1
    )
    goto :create_wrapper
)

:: Installer les dépendances
echo  [2/4] Installation des dependances...
pip install colorama tabulate psutil --quiet
if errorlevel 1 (
    echo  [ERREUR] Installation des dependances echouee.
    pause
    exit /b 1
)
echo  [OK] Dependances installees

:create_wrapper
:: Créer le wrapper okp.bat
echo  [3/4] Creation du lanceur okp...
(
    echo @echo off
    echo python "%INSTALL_DIR%\oktopios\vm\main.py" %%*
) > "%BIN_DIR%\okp.bat"

:: Ajouter au PATH utilisateur
echo  [4/4] Ajout au PATH...
set "CURRENT_PATH="
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "CURRENT_PATH=%%b"

echo !CURRENT_PATH! | findstr /i "%BIN_DIR%" >nul 2>&1
if errorlevel 1 (
    if defined CURRENT_PATH (
        setx PATH "!CURRENT_PATH!;%BIN_DIR%" >nul
    ) else (
        setx PATH "%BIN_DIR%" >nul
    )
    echo  [OK] %BIN_DIR% ajoute au PATH
) else (
    echo  [OK] Deja dans le PATH
)

echo.
echo  ====================================================
echo   Installation terminee avec succes !
echo  ====================================================
echo.
echo  Fermez et rouvrez PowerShell, puis testez avec :
echo.
echo      okp --version
echo      okp "print(\"Bonjour Oktopios !\")"
echo      okp --repl
echo.
echo  Documentation : okp --help
echo.
pause
