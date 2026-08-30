# Oktopios v0.2.2 — Commit & push script (run from PowerShell)
# Namespace Path: manipulation de chemins de fichiers cross-platform
Set-Location "$PSScriptRoot"

# Remove stale lock files if present
Remove-Item -Force ".git\*.lock" -ErrorAction SilentlyContinue
Remove-Item -Force ".git\objects\*.lock" -ErrorAction SilentlyContinue

git add -A
git commit -m "feat: namespace Path — manipulation de chemins de fichiers cross-platform (v0.2.2)"
git push origin main
