# push_v0.2.0.ps1 — Supprimer les verrous git périmés, commit et push v0.2.0
# Exécuter depuis PowerShell dans le dossier version.0.0.1 :
#   .\push_v0.2.0.ps1

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host "🔓 Suppression des verrous git périmés..." -ForegroundColor Cyan
$locks = @(".git\index.lock", ".git\HEAD.lock", ".git\ORIG_HEAD.lock", ".git\index_tmp.lock")
foreach ($lock in $locks) {
    $path = Join-Path $root $lock
    if (Test-Path $path) {
        Remove-Item $path -Force
        Write-Host "  ✓ $lock supprimé"
    }
}

Write-Host ""
Write-Host "📦 Staging des fichiers modifiés..." -ForegroundColor Cyan
git add -A
git status

Write-Host ""
Write-Host "✍️  Commit v0.2.0..." -ForegroundColor Cyan
git commit -m "feat: namespace Hash — hachage cryptographique & encodage Base64 (v0.2.0)

- Hash.md5 / sha1 / sha256 / sha512 — digests hexadecimaux (stdlib hashlib)
- Hash.hmac(key, msg, algo?) — HMAC signe, algo configurable (defaut sha256)
- Hash.b64encode / b64decode — Base64 standard RFC 4648
- Hash.b64urlEncode / b64urlDecode — Base64 URL-safe (JWT, URLs)
- Hash.compare(h1, h2) — comparaison en temps constant (anti timing-attack)
- 9 nouveaux tests unitaires (120 tests au total, tous verts)"

Write-Host ""
Write-Host "🚀 Push vers GitHub..." -ForegroundColor Cyan
git push origin main

Write-Host ""
Write-Host "📦 Build PyPI..." -ForegroundColor Cyan
python -m build

Write-Host ""
Write-Host "🚀 Upload vers PyPI..." -ForegroundColor Cyan
python -m twine upload dist/oktopios-0.2.0*

Write-Host ""
Write-Host "✅ Terminé !" -ForegroundColor Green
