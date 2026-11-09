# ================================================
#  Oktopios - Installeur Windows (PowerShell, via pip)
#  Usage: powershell -ExecutionPolicy Bypass -File install.ps1
#
#  Depuis la 0.2.6, le cœur d'Oktopios est 100 % pur Python :
#  installation directe via pip (crée la commande `okp`).
# ================================================

$ErrorActionPreference = "Stop"

function Write-Header {
    Write-Host ""
    Write-Host "  ====================================================" -ForegroundColor Cyan
    Write-Host "   ***  Oktopios - Installeur Windows" -ForegroundColor Cyan
    Write-Host "  ====================================================" -ForegroundColor Cyan
    Write-Host ""
}
function Write-Step($n, $total, $msg) { Write-Host "  [$n/$total] $msg" -ForegroundColor Yellow }
function Write-OK($msg)   { Write-Host "  [OK] $msg" -ForegroundColor Green }
function Write-Fail($msg) { Write-Host "  [ERREUR] $msg" -ForegroundColor Red; exit 1 }

Write-Header

# 1. Vérifier Python
Write-Step 1 3 "Verification de Python..."
try {
    $pyVersion = python -c "import sys; print('%d.%d' % sys.version_info[:2])"
    if ($LASTEXITCODE -ne 0 -or [version]$pyVersion -lt [version]'3.8') {
        Write-Fail "Python 3.8 ou plus recent est requis."
    }
    Write-OK "Python $pyVersion detecte"
} catch {
    Write-Fail "Python 3.8+ non installe. Telechargez sur https://python.org (cochez 'Add Python to PATH')"
}

# 2. Installer Oktopios via pip
Write-Step 2 3 "Installation d'Oktopios (pip)..."
python -m pip install --upgrade oktopios
if ($LASTEXITCODE -ne 0) {
    python -m pip install --upgrade --user oktopios
    if ($LASTEXITCODE -ne 0) { Write-Fail "Installation via pip echouee. Essayez: python -m pip install oktopios" }
}
Write-OK "Oktopios installe"

# 3. S'assurer que le dossier des scripts est dans le PATH
Write-Step 3 3 "Verification du PATH..."
$scriptsDirs = @(
    (python -c "import sysconfig; print(sysconfig.get_path('scripts'))" 2>$null).Trim(),
    (python -c "import sysconfig; print(sysconfig.get_path('scripts', 'nt_user'))" 2>$null).Trim()
) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -Unique
if ($scriptsDirs.Count -gt 0 -and -not (Get-Command okp -ErrorAction SilentlyContinue)) {
    $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    $pathsToAdd = @($scriptsDirs | Where-Object { ($userPath -split ';') -notcontains $_ })
    if ($pathsToAdd.Count -gt 0) {
        $newUserPath = (@($userPath) + $pathsToAdd | Where-Object { $_ }) -join ';'
        [Environment]::SetEnvironmentVariable("PATH", $newUserPath, "User")
        $env:PATH = (@($env:PATH) + $pathsToAdd) -join ';'
        Write-OK "$($pathsToAdd -join ', ') ajoute au PATH utilisateur"
    } else {
        Write-OK "Dossier des scripts deja dans le PATH"
    }
} else {
    Write-OK "La commande okp est deja disponible ou le dossier utilisateur est indisponible"
}

# Résumé
Write-Host ""
Write-Host "  ====================================================" -ForegroundColor Green
Write-Host "   Installation terminee avec succes !" -ForegroundColor Green
Write-Host "  ====================================================" -ForegroundColor Green
Write-Host ""
try {
    $v = (okp --version 2>&1)
    Write-Host "  okp disponible : $v" -ForegroundColor Green
} catch {
    Write-Host "  Fermez et rouvrez PowerShell, puis :" -ForegroundColor White
}
Write-Host ""
Write-Host "      okp --version" -ForegroundColor Cyan
Write-Host "      okp 'print(\"Bonjour Oktopios !\")'" -ForegroundColor Cyan
Write-Host "      okp --repl" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Extras : pip install oktopios[all]   (data / recognition / ia / system)" -ForegroundColor Gray
Write-Host ""
