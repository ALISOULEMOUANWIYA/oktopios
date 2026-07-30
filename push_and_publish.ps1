# Oktopios v0.1.5 — Push to GitHub & publish to PyPI
# Run from: C:\Users\mouan\PycharmProjects\Oktopios\version.0.0.1
# Usage: Right-click -> "Run with PowerShell" or open a terminal and run: .\push_and_publish.ps1

Set-Location $PSScriptRoot

Write-Host "🐙 Oktopios v0.1.5 — Release script" -ForegroundColor Cyan

# 1. Remove stale git lock files if they exist
foreach ($lock in @(".git\index.lock", ".git\HEAD.lock", ".git\ORIG_HEAD.lock", ".git\objects\maintenance.lock")) {
    if (Test-Path $lock) {
        Remove-Item $lock -Force
        Write-Host "  ✅ Removed stale $lock" -ForegroundColor Green
    }
}

# 2. Apply the bundle created by the automated run (contains all commits up to v0.1.5)
$bundle = "oktopios_push_bundle.bundle"
if (Test-Path $bundle) {
    Write-Host "`n📦 Applying git bundle (v0.1.5)..." -ForegroundColor Yellow
    git fetch $bundle "refs/heads/main:refs/heads/main" --update-head-ok
    Write-Host "  ✅ Bundle applied" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Bundle not found, skipping" -ForegroundColor Yellow
}

# 3. Push to GitHub
Write-Host "`n🚀 Pushing to GitHub..." -ForegroundColor Yellow
git push origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ Push failed" -ForegroundColor Red
    exit 1
}
Write-Host "  ✅ Pushed to GitHub" -ForegroundColor Green

# 4. Build and publish to PyPI
Write-Host "`n📦 Building distribution..." -ForegroundColor Yellow
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
python -m build
if ($LASTEXITCODE -ne 0) { Write-Host "  ❌ Build failed" -ForegroundColor Red; exit 1 }

Write-Host "`n🚀 Uploading to PyPI..." -ForegroundColor Yellow
python -m twine upload dist/*
if ($LASTEXITCODE -ne 0) { Write-Host "  ❌ PyPI upload failed" -ForegroundColor Red; exit 1 }

Write-Host "`n✅ Done! Oktopios v0.1.5 is live on GitHub and PyPI." -ForegroundColor Green
