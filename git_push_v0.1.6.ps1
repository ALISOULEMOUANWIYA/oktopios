# Script PowerShell — à exécuter depuis le dossier du projet
# Supprime les lock files orphelins et pousse les changements v0.1.6

$gitDir = ".git"

# Suppression des lock files orphelins
@("HEAD.lock", "index.lock", "ORIG_HEAD.lock", "objects/maintenance.lock") | ForEach-Object {
    $f = Join-Path $gitDir $_
    if (Test-Path $f) {
        Remove-Item $f -Force
        Write-Host "Supprimé : $f"
    }
}

# Git
git add -A
git commit -m "feat: namespace Json — manipulation JSON en memoire [v0.1.6]"
git push origin main

# Build + PyPI
python -m build
python -m twine upload dist/oktopios-0.1.6*

Write-Host "✅ v0.1.6 publiée sur GitHub et PyPI"
