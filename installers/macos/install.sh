#!/usr/bin/env bash
# ================================================
#  Oktopios - Installeur macOS (via pip)
#  Usage: bash install.sh
#  Testé sur: macOS 12 Monterey, 13 Ventura, 14 Sonoma
#
#  Depuis la 0.2.6, le cœur d'Oktopios est 100 % pur Python :
#  installation directe via pip (crée la commande `okp`).
# ================================================

set -u

GREEN="\033[32m"; CYAN="\033[36m"
YELLOW="\033[33m"; RED="\033[31m"; RESET="\033[0m"; BOLD="\033[1m"

ok()   { echo -e "  ${GREEN}✓${RESET}  $1"; }
info() { echo -e "  ${YELLOW}→${RESET}  $1"; }
fail() { echo -e "  ${RED}✗  ERREUR: $1${RESET}"; exit 1; }
step() { echo -e "\n  ${BOLD}[$1/$2]${RESET} $3"; }

echo -e ""
echo -e "${CYAN}  ════════════════════════════════════════════${RESET}"
echo -e "${CYAN}   🐙  Oktopios - Installeur macOS${RESET}"
echo -e "${CYAN}  ════════════════════════════════════════════${RESET}"
echo -e ""

# 1. Python (Homebrew en secours)
step 1 3 "Vérification de Python..."
if ! command -v python3 &>/dev/null; then
    if command -v brew &>/dev/null; then
        info "Installation via Homebrew..."
        brew install python@3.12
    else
        fail "Installez Python depuis https://python.org ou Homebrew (https://brew.sh)"
    fi
fi
ok "Python $(python3 --version 2>&1 | awk '{print $2}')"

# 2. Installer Oktopios (pip --user)
step 2 3 "Installation d'Oktopios (pip)..."
if python3 -m pip install --user --upgrade oktopios >/dev/null 2>&1; then
    ok "Oktopios installé"
elif python3 -m pip install --user --upgrade --break-system-packages oktopios >/dev/null 2>&1; then
    ok "Oktopios installé (--break-system-packages)"
else
    fail "Échec de l'installation via pip. Essayez : python3 -m pip install --user oktopios"
fi

# 3. PATH (dossier des scripts utilisateur, ex. ~/Library/Python/3.x/bin)
step 3 3 "Configuration du PATH..."
USER_BIN="$(python3 -m site --user-base 2>/dev/null)/bin"
SHELL_RC="$HOME/.zshrc"
[ -n "${BASH_VERSION:-}" ] && SHELL_RC="$HOME/.bash_profile"
if [ -n "$USER_BIN" ] && ! echo "$PATH" | grep -q "$USER_BIN"; then
    if ! grep -q "$USER_BIN" "$SHELL_RC" 2>/dev/null; then
        {
            echo ""
            echo "# Oktopios"
            echo "export PATH=\"$USER_BIN:\$PATH\""
        } >> "$SHELL_RC"
    fi
    export PATH="$USER_BIN:$PATH"
    ok "PATH mis à jour dans $SHELL_RC"
else
    ok "PATH déjà configuré"
fi

echo ""
echo -e "  ${GREEN}════════════════════════════════════════════${RESET}"
echo -e "  ${GREEN}  ✅ Installation terminée !${RESET}"
echo -e "  ${GREEN}════════════════════════════════════════════${RESET}"
echo ""
if command -v okp &>/dev/null; then
    ok "okp disponible ($(okp --version 2>/dev/null || echo '?'))"
else
    info "Rechargez le terminal :  source $SHELL_RC"
fi
echo ""
echo -e "  Testez :"
echo -e "  ${CYAN}    okp --version${RESET}"
echo -e "  ${CYAN}    okp 'print(\"Bonjour Oktopios !\")'${RESET}"
echo -e "  ${CYAN}    okp --repl${RESET}"
echo -e "\n  Extras : ${CYAN}pip install oktopios[all]${RESET}  (data / recognition / ia / system)"
echo ""
