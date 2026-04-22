# ================================================
#  Oktopios v0.0.1 - Installeur PowerShell
#  Usage: powershell -ExecutionPolicy Bypass -File install.ps1
# ================================================

$ErrorActionPreference = "Stop"
$OKP_VERSION = "0.0.1"
$INSTALL_DIR = "$env:LOCALAPPDATA\Oktopios"
$BIN_DIR = "$INSTALL_DIR\bin"

function Write-Header {
    Write-Host ""
    Write-Host "  ====================================================" -ForegroundColor Cyan
    Write-Host "   *** Oktopios v$OKP_VERSION - Installeur Windows" -ForegroundColor Cyan
    Write-Host "  ====================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step($n, $total, $msg) {
    Write-Host "  [$n/$total] $msg" -ForegroundColor Yellow
}

function Write-OK($msg) {
    Write-Host "  [OK] $msg" -ForegroundColor Green
}

function Write-Fail($msg) {
    Write-Host "  [ERREUR] $msg" -ForegroundColor Red
    exit 1
}

Write-Header

# 1. Vérifier Python 3.10+
Write-Step 1 5 "Verification de Python..."
try {
    $pyver = python --version 2>&1
    if ($pyver -match "Python (\d+)\.(\d+)") {
        $major = [int]$Matches[1]
        $minor = [int]$Matches[2]
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
            Write-Fail "Python 3.10+ requis (detecte: $pyver). Telechargez sur https://python.org"
        }
        Write-OK "$pyver detecte"
    }
} catch {
    Write-Fail "Python non installe. Telechargez sur https://python.org (cochez 'Add to PATH')"
}

# 2. Créer les dossiers
Write-Step 2 5 "Creation des dossiers..."
New-Item -ItemType Directory -Force -Path $INSTALL_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $BIN_DIR | Out-Null
New-Item -ItemType Directory -Force -Path "$INSTALL_DIR\oktopios" | Out-Null
Write-OK "Dossiers crees dans $INSTALL_DIR"

# 3. Copier les fichiers du projet
Write-Step 3 5 "Copie des fichiers Oktopios..."
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PROJECT_DIR = Split-Path -Parent $SCRIPT_DIR

if (Test-Path "$PROJECT_DIR\vm\main.py") {
    Copy-Item -Recurse -Force "$PROJECT_DIR\*" "$INSTALL_DIR\oktopios\" -ErrorAction SilentlyContinue
    Write-OK "Fichiers copies"
} else {
    # Fallback: pip install
    Write-Host "  [INFO] Installation via pip..." -ForegroundColor Cyan
    pip install oktopios --quiet
    if ($LASTEXITCODE -ne 0) { Write-Fail "pip install oktopios echoue" }
    Write-OK "Installe via pip"

    # Créer wrapper pip-based
    $wrapper = "@echo off`npython -m oktopios %*"
    Set-Content -Path "$BIN_DIR\okp.bat" -Value $wrapper -Encoding ASCII
    goto done
}

# 4. Installer les dépendances
Write-Step 4 5 "Installation des dependances..."
pip install colorama tabulate psutil --quiet
if ($LASTEXITCODE -ne 0) { Write-Fail "Installation des dependances echouee" }
Write-OK "colorama, tabulate, psutil installes"

# Créer wrapper okp.bat
$MAIN_PATH = "$INSTALL_DIR\oktopios\vm\main.py"
$wrapper = "@echo off`npython `"$MAIN_PATH`" %*"
Set-Content -Path "$BIN_DIR\okp.bat" -Value $wrapper -Encoding ASCII

:done
# 5. Ajouter au PATH
Write-Step 5 5 "Mise a jour du PATH..."
$userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($userPath -notlike "*$BIN_DIR*") {
    [Environment]::SetEnvironmentVariable("PATH", "$userPath;$BIN_DIR", "User")
    Write-OK "$BIN_DIR ajoute au PATH utilisateur"
} else {
    Write-OK "Deja dans le PATH"
}

# Résumé
Write-Host ""
Write-Host "  ====================================================" -ForegroundColor Green
Write-Host "   Installation terminee avec succes !" -ForegroundColor Green
Write-Host "  ====================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Fermez et rouvrez PowerShell, puis :" -ForegroundColor White
Write-Host ""
Write-Host "      okp --version" -ForegroundColor Cyan
Write-Host "      okp 'print(""Bonjour Oktopios !"")'" -ForegroundColor Cyan
Write-Host "      okp --repl" -ForegroundColor Cyan
Write-Host ""
Write-Host "  okp --help pour toute la documentation" -ForegroundColor Gray
Write-Host ""
