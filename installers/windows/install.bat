@echo off
setlocal enabledelayedexpansion
title Oktopios Installer

echo.
echo  ====================================================
echo   Oktopios - Installeur Windows
echo  ====================================================
echo.
echo  Le coeur d'Oktopios est 100%% pur Python : installation via pip.
echo.

:: Verifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERREUR] Python n'est pas installe ou pas dans le PATH.
    echo  Telechargez Python 3.8+ sur https://python.org
    echo  ^(Cochez "Add Python to PATH" lors de l'installation^)
    pause
    exit /b 1
)
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo  [OK] Python %PYVER% detecte

:: Installer Oktopios via pip
echo.
echo  [1/2] Installation d'Oktopios via pip...
python -m pip install --upgrade oktopios
if errorlevel 1 (
    echo  [INFO] Nouvelle tentative en mode utilisateur...
    python -m pip install --upgrade --user oktopios
    if errorlevel 1 (
        echo  [ERREUR] Installation echouee. Essayez: python -m pip install oktopios
        pause
        exit /b 1
    )
)
echo  [OK] Oktopios installe

:: Ajouter le dossier des scripts au PATH
echo.
echo  [2/2] Verification du PATH...
for /f "delims=" %%s in ('python -c "import sysconfig; print(sysconfig.get_path('scripts'))" 2^>nul') do set "SCRIPTS_DIR=%%s"

if defined SCRIPTS_DIR (
    set "CURRENT_PATH="
    for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "CURRENT_PATH=%%b"
    echo !CURRENT_PATH! | findstr /i /c:"!SCRIPTS_DIR!" >nul 2>&1
    if errorlevel 1 (
        if defined CURRENT_PATH (
            setx PATH "!CURRENT_PATH!;!SCRIPTS_DIR!" >nul
        ) else (
            setx PATH "!SCRIPTS_DIR!" >nul
        )
        echo  [OK] !SCRIPTS_DIR! ajoute au PATH
    ) else (
        echo  [OK] Dossier des scripts deja dans le PATH
    )
) else (
    echo  [OK] okp fourni par l'entry-point pip
)

echo.
echo  ====================================================
echo   Installation terminee avec succes !
echo  ====================================================
echo.
echo  Fermez et rouvrez le terminal, puis testez avec :
echo.
echo      okp --version
echo      okp "print('Bonjour Oktopios !')"
echo      okp --repl
echo.
echo  Extras : pip install oktopios[all]   ^(data / recognition / ia / system^)
echo.
pause
