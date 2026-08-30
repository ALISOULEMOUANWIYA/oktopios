#!/data/data/com.termux/files/usr/bin/bash
# ================================================
#  Oktopios - Installeur Android (Termux)
#  Usage : bash termux-install.sh
#
#  Termux : https://f-droid.org/packages/com.termux/
#  (Utilisez la version F-Droid, pas celle du Play Store)
#
#  Depuis la 0.2.6, le cœur d'Oktopios est 100 % pur Python :
#  aucune compilation, l'install se fait directement via pip et
#  crée la commande `okp` (entry-point) dans $PREFIX/bin.
# ================================================

set -u

GREEN="\033[32m"; CYAN="\033[36m"
YELLOW="\033[33m"; RED="\033[31m"; RESET="\033[0m"; BOLD="\033[1m"

ok()   { echo -e "  ${GREEN}✓${RESET}  $1"; }
info() { echo -e "  ${YELLOW}→${RESET}  $1"; }
fail() { echo -e "  ${RED}✗  ERREUR: $1${RESET}"; exit 1; }

echo -e ""
echo -e "${CYAN}  ════════════════════════════════════════════${RESET}"
echo -e "${CYAN}   🐙  Oktopios - Termux (Android)${RESET}"
echo -e "${CYAN}  ════════════════════════════════════════════${RESET}"
echo -e ""

# 1. Mise à jour des paquets Termux
echo -e "  ${BOLD}[1/3]${RESET} Mise à jour de Termux..."
pkg update -y -q 2>/dev/null || apt-get update -y -q 2>/dev/null || info "mise à jour ignorée (pas de réseau ?)"
ok "Termux à jour"

# 2. Installer Python
echo -e "\n  ${BOLD}[2/3]${RESET} Installation de Python..."
if ! command -v python3 &>/dev/null; then
    pkg install python -y -q || fail "Impossible d'installer Python (pkg install python)"
fi
command -v python3 &>/dev/null || fail "python3 introuvable après installation"
ok "Python $(python3 --version | awk '{print $2}')"

# 3. Installer Oktopios via pip
echo -e "\n  ${BOLD}[3/3]${RESET} Installation d'Oktopios..."

# Install simple ; replis au cas où (PEP 668 sur environnements récents,
# puis contrainte de version ignorée pour un très vieux Python).
if python3 -m pip install --upgrade oktopios >/dev/null 2>&1; then
    ok "Oktopios installé"
elif python3 -m pip install --upgrade --break-system-packages oktopios >/dev/null 2>&1; then
    ok "Oktopios installé (--break-system-packages)"
elif python3 -m pip install --upgrade --break-system-packages --ignore-requires-python oktopios >/dev/null 2>&1; then
    ok "Oktopios installé (Python ancien, contrainte de version ignorée)"
else
    fail "Échec de l'installation via pip. Essayez : python3 -m pip install oktopios"
fi

# Vérification
if command -v okp &>/dev/null; then
    ok "Commande okp disponible ($(okp --version 2>/dev/null || echo '?'))"
else
    info "La commande 'okp' n'est pas encore dans le PATH — ouvrez un nouveau Termux."
fi

echo ""
echo -e "  ${GREEN}════════════════════════════════════════════${RESET}"
echo -e "  ${GREEN}  ✅ Oktopios installé sur Termux !${RESET}"
echo -e "  ${GREEN}════════════════════════════════════════════${RESET}"
echo ""
echo -e "  Tapez maintenant :"
echo ""
echo -e "  ${CYAN}    okp --version${RESET}"
echo -e "  ${CYAN}    okp 'print(\"Bonjour depuis Android !\")'${RESET}"
echo -e "  ${CYAN}    okp --repl${RESET}"
echo ""
echo -e "  Extras optionnels :"
echo -e "  ${CYAN}    pip install oktopios[system]${RESET}   (System.uptime / memory_info)"
echo ""

# Test immédiat
okp 'print("🐙 Oktopios fonctionne sur Android !")' 2>/dev/null && \
    ok "Test réussi !" || info "Redémarrez Termux puis : okp --version"
