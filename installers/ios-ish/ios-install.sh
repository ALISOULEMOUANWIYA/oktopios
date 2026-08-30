#!/bin/sh
# ================================================
#  Oktopios - Installeur iPhone / iPad (iSH Shell)
#  Usage : sh ios-install.sh
#
#  Prérequis : l'app iSH Shell (App Store, gratuit)
#  https://apps.apple.com/app/ish-shell/id1436902243
#
#  iSH émule Alpine Linux (x86) sur iOS. Depuis la 0.2.6, le cœur
#  d'Oktopios est 100 % pur Python : aucune compilation, donc pas
#  besoin de gcc/musl-dev — l'install se fait via pip directement.
# ================================================

set -u

GREEN="$(printf '\033[32m')"; CYAN="$(printf '\033[36m')"
YELLOW="$(printf '\033[33m')"; RED="$(printf '\033[31m')"
RESET="$(printf '\033[0m')"; BOLD="$(printf '\033[1m')"

ok()   { printf '  %s✓%s  %s\n'  "$GREEN"  "$RESET" "$1"; }
info() { printf '  %s→%s  %s\n'  "$YELLOW" "$RESET" "$1"; }
fail() { printf '  %s✗  ERREUR: %s%s\n' "$RED" "$1" "$RESET"; exit 1; }

printf '\n%s  ════════════════════════════════════════════%s\n' "$CYAN" "$RESET"
printf '%s   🐙  Oktopios - iPhone / iPad (iSH)%s\n'             "$CYAN" "$RESET"
printf '%s  ════════════════════════════════════════════%s\n\n' "$CYAN" "$RESET"

# 1. Mise à jour d'Alpine
printf '  %s[1/3]%s Mise à jour d'\''Alpine...\n' "$BOLD" "$RESET"
apk update -q 2>/dev/null || info "apk update ignoré (pas de réseau ?)"
ok "Système à jour"

# 2. Installer Python + pip
printf '\n  %s[2/3]%s Installation de Python...\n' "$BOLD" "$RESET"
if ! command -v python3 >/dev/null 2>&1; then
    apk add python3 py3-pip -q || fail "Impossible d'installer python3 (apk add python3 py3-pip)"
fi
command -v python3 >/dev/null 2>&1 || fail "python3 introuvable après installation"
ok "Python $(python3 --version 2>&1 | awk '{print $2}')"

# 3. Installer Oktopios via pip
printf '\n  %s[3/3]%s Installation d'\''Oktopios...\n' "$BOLD" "$RESET"

# Alpine récent applique PEP 668 (environnement « externally-managed ») :
# pip refuse d'installer dans le système sans --break-system-packages.
# On tente d'abord l'install simple, puis les replis nécessaires.
if python3 -m pip install --upgrade oktopios >/dev/null 2>&1; then
    ok "Oktopios installé"
elif python3 -m pip install --upgrade --break-system-packages oktopios >/dev/null 2>&1; then
    ok "Oktopios installé (--break-system-packages)"
elif python3 -m pip install --upgrade --break-system-packages --ignore-requires-python oktopios >/dev/null 2>&1; then
    ok "Oktopios installé (Python ancien, contrainte de version ignorée)"
else
    fail "Échec de l'installation via pip. Essayez manuellement : python3 -m pip install --break-system-packages oktopios"
fi

# Vérification
if command -v okp >/dev/null 2>&1; then
    VER="$(okp --version 2>/dev/null || echo '?')"
    ok "Commande okp disponible ($VER)"
else
    info "La commande 'okp' n'est pas encore dans le PATH."
    info "Utilisez : python3 -m vm.main --version"
fi

printf '\n%s  ════════════════════════════════════════════%s\n' "$GREEN" "$RESET"
printf '%s   ✅ Oktopios installé sur iPhone / iPad !%s\n'      "$GREEN" "$RESET"
printf '%s  ════════════════════════════════════════════%s\n\n' "$GREEN" "$RESET"

printf '  Testez maintenant :\n\n'
printf '  %s    okp --version%s\n'                          "$CYAN" "$RESET"
printf '  %s    okp '\''print("Bonjour depuis iPhone !")'\''%s\n' "$CYAN" "$RESET"
printf '  %s    okp --repl%s\n\n'                           "$CYAN" "$RESET"

printf '  Options utiles :\n'
printf '  %s    pip install --break-system-packages oktopios[system]%s   (System.uptime / memory_info)\n' "$CYAN" "$RESET"
printf '\n'

# Test immédiat
okp 'print("🐙 Oktopios fonctionne sur iPhone !")' 2>/dev/null && \
    ok "Test réussi !" || info "Ouvrez un nouveau shell puis : okp --version"
