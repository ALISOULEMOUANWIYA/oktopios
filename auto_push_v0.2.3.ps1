$ErrorActionPreference = "Stop"
$repo = "C:\Users\mouan\PycharmProjects\Oktopios\version.0.0.1"

# Remove stale git lock files
$locks = @("HEAD.lock", "ORIG_HEAD.lock", "index.lock", "index_tmp.lock", "index.new")
foreach ($lock in $locks) {
    $path = Join-Path $repo ".git\$lock"
    if (Test-Path $path) {
        Remove-Item $path -Force
        Write-Host "Removed lock: $lock"
    }
}

Set-Location $repo

# Add, commit, push
git add -A
git commit -m "feat: namespace Csv — 7 fonctions CSV natives (stdlib uniquement) (v0.2.3)"
git push origin main

Write-Host "`nPush done!"

# Build for PyPI
Write-Host "`nBuilding for PyPI..."
python -m build

# Upload to PyPI
Write-Host "`nUploading to PyPI..."
python -m twine upload dist/oktopios-0.2.3* --skip-existing

Write-Host "`nAll done — v0.2.3 published!"
Read-Host "Press Enter to close"
