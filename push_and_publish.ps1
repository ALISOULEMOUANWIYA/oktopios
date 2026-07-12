# Oktopios v0.1.2 — Push to GitHub & publish to PyPI
# Run from: C:\Users\mouan\PycharmProjects\Oktopios\version.0.0.1
# Usage: Right-click -> "Run with PowerShell" or open a terminal and run: .\push_and_publish.ps1

Set-Location $PSScriptRoot

Write-Host "🐙 Oktopios v0.1.2 — Release script" -ForegroundColor Cyan

# 1. Remove stale git lock if it exists
$lockFile = ".git\index.lock"
if (Test-Path $lockFile) {
    Remove-Item $lockFile -Force
    Write-Host "  ✅ Removed stale .git/index.lock" -ForegroundColor Green
}

# 2. Git commit & push
Write-Host "`n📦 Committing changes..." -ForegroundColor Yellow
git add -A
git commit -m "feat: namespace List fonctionnel + Type enrichi (v0.1.2)

- Ajout de List avec 25 utilitaires : head/tail/last/init, take/drop,
  flatten, unique, zip/unzip, chunk, sorted/reversed, concat, enumerate,
  rotate, sum/product/max/min/avg, contains/indexOf/count,
  intersect/subtract/union
- Type.type() retourne desormais des noms Oktopios (int, float, bool,
  string, list, map, null) au lieu des noms Python internes
- Ajout de Type.isInt/isFloat/isBool/isString/isList/isMap/isNull/isNum"

Write-Host "`n🚀 Pushing to GitHub..." -ForegroundColor Yellow
git push origin main

# 3. Build & upload to PyPI
Write-Host "`n🏗️  Building package..." -ForegroundColor Yellow
python -m build

Write-Host "`n📤 Uploading to PyPI..." -ForegroundColor Yellow
python -m twine upload dist/oktopios-0.1.2*

Write-Host "`n✅ Done! Oktopios v0.1.2 published." -ForegroundColor Green
