# Oktopios v0.1.9 — Script de push automatique
# Exécuter depuis: C:\Users\mouan\PycharmProjects\Oktopios\version.0.0.1

$repoPath = "C:\Users\mouan\PycharmProjects\Oktopios\version.0.0.1"
Set-Location $repoPath

# Supprimer les fichiers de verrou git laissés par les sessions précédentes
$locks = @(".git\index.lock", ".git\index.lock.bak", ".git\HEAD.lock", ".git\HEAD.lock.bak", ".git\index.new", ".git\ORIG_HEAD.lock.bak")
foreach ($lock in $locks) {
    $f = Join-Path $repoPath $lock
    if (Test-Path $f) { Remove-Item $f -Force; Write-Host "Supprimé: $lock" }
}

# Appliquer le bundle v0.1.9
git fetch "$repoPath\oktopios_v0.1.9.bundle" main:main
git push origin main
Write-Host "✅ v0.1.9 poussé sur GitHub !"

# Build + publish PyPI
Write-Host "`n📦 Build PyPI..."
python -m pip install build twine --quiet
python -m build
Write-Host "🚀 Upload PyPI..."
python -m twine upload dist/oktopios-0.1.9*
Write-Host "✅ Publié sur PyPI !"
