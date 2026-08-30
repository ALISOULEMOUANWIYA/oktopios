# Oktopios v0.2.1 — Push to GitHub & publish to PyPI
# Run from: C:\Users\mouan\PycharmProjects\Oktopios\version.0.0.1
# Usage: Right-click -> "Run with PowerShell" or: .\push_v0.2.1.ps1

Set-Location $PSScriptRoot

Write-Host "🐙 Oktopios v0.2.1 — Release script (Stats namespace)" -ForegroundColor Cyan

# 1. Remove stale git lock files if they exist
foreach ($lock in @(".git\index.lock", ".git\HEAD.lock", ".git\ORIG_HEAD.lock", ".git\ORIG_HEAD", ".git\index_tmp.lock")) {
    if (Test-Path $lock) {
        Remove-Item $lock -Force
        Write-Host "  ✅ Removed stale $lock" -ForegroundColor Green
    }
}

# 2. Apply the bundle (contains all commits including v0.2.0 and v0.2.1)
$bundle = "oktopios_v0.2.1.bundle"
if (Test-Path $bundle) {
    Write-Host "`n📦 Applying git bundle (v0.2.1)..." -ForegroundColor Yellow
    git fetch $bundle "refs/heads/main:refs/heads/main" --update-head-ok
    Write-Host "  ✅ Bundle applied" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Bundle not found, skipping" -ForegroundColor Yellow
}

# 3. Push to GitHub
Write-Host "`n🚀 Pushing to GitHub..." -ForegroundColor Yellow
git push origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ Push failed. Check your credentials." -ForegroundColor Red
    exit 1
}
Write-Host "  ✅ Pushed to GitHub" -ForegroundColor Green

# 4. Publish to PyPI
Write-Host "`n📦 Publishing to PyPI..." -ForegroundColor Yellow
python -m twine upload dist/oktopios-0.2.1*
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Published to PyPI" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  PyPI upload failed (credentials missing?)" -ForegroundColor Yellow
}

Write-Host "`n🎉 Done! Oktopios v0.2.1 released." -ForegroundColor Cyan
