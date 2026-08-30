#!/usr/bin/env bash
# ================================================
#  Oktopios - Installeur Linux universel (via pip)
#  Usage: bash install.sh
#  Testé sur: Ubuntu, Debian, Fedora, Arch, Alpine
#
#  Depuis la 0.2.6, le cœur d'Oktopios est 100 % pur Python :
#  l'installation passe directement par pip et crée la commande
#  `okp` (entry-point). Plus de copie de fichiers ni de wrapper.
# ================================================

set -u

BOLD="\033[1m"; GREEN="\033[32m"; CYAN="\033[36m"
YELLOW="\033[33m"; RED="\033[31m"; RESET="\033[0m"

ok()   { echo -e "  ${GREEN}✓${RESET}  $1"; }
info() { echo -e "  ${YELLOW}→${RESET}  $1"; }
fail() { echo -e "  ${RED}✗  ERREUR: $1${RESET}"; exit 1; }
step() { echo -e "\n  ${BOLD}[$1/$2]${RESET} $3"; }

echo -e ""
echo -e "${CYAN}  ════════════════════════════════════════════${RESET}"
echo -e "${CYAN}   🐙  Oktopios - Installeur Linux${RESET}"
echo -e "${CYAN}  ════════════════════════════════════════════${RESET}"
echo -e ""

# ── 1. Python + pip ───────────────────────────────────────────────────────────
step 1 3 "Vérification de Python..."
if ! command -v python3 &>/dev/null; then
    info "Python3 non trouvé. Tentative d'installation..."
    if   command -v apt-get &>/dev/null; then sudo apt-get install -y python3 python3-pip -q
    elif command -v dnf     &>/dev/null; then sudo dnf install -y python3 python3-pip -q
    elif command -v pacman  &>/dev/null; then sudo pacman -S --noconfirm python python-pip
    elif command -v apk     &>/dev/null; then apk add python3 py3-pip
    else fail "Installez Python 3.8+ depuis https://python.org"
    fi
fi
if ! python3 -m pip --version &>/dev/null; then
    info "pip absent — installation..."
    if   command -v apt-get &>/dev/null; then sudo apt-get install -y python3-pip -q 2>/dev/null || true
    elif command -v dnf     &>/dev/null; then sudo dnf install -y python3-pip -q 2>/dev/null || true
    elif command -v pacman  &>/dev/null; then sudo pacman -S --noconfirm python-pip 2>/dev/null || true
    fi
    python3 -m ensurepip --upgrade 2>/dev/null || true
fi
ok "Python $(python3 --version 2>&1 | awk '{print $2}')"

# ── 2. Installer Oktopios (pip --user) ────────────────────────────────────────
step 2 3 "Installation d'Oktopios (pip)..."
if python3 -m pip install --user --upgrade oktopios >/dev/null 2>&1; then
    ok "Oktopios installé"
elif python3 -m pip install --user --upgrade --break-system-packages oktopios >/dev/null 2>&1; then
    ok "Oktopios installé (--break-system-packages)"
elif python3 -m pip install --user --upgrade --break-system-packages --ignore-requires-python oktopios >/dev/null 2>&1; then
    ok "Oktopios installé (Python ancien, contrainte de version ignorée)"
else
    fail "Échec de l'installation via pip. Essayez : python3 -m pip install --user oktopios"
fi

# ── 3. PATH (dossier des scripts utilisateur) ─────────────────────────────────
step 3 3 "Configuration du PATH..."
USER_BIN="$(python3 -m site --user-base 2>/dev/null)/bin"
case "$SHELL" in
    */zsh)  SHELL_RC="$HOME/.zshrc" ;;
    */fish) SHELL_RC="$HOME/.config/fish/config.fish" ;;
    *)      SHELL_RC="$HOME/.bashrc" ;;
esac
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
    info "Rechargez votre terminal :  source $SHELL_RC"
fi
echo ""
echo -e "  Testez :"
echo -e "  ${CYAN}    okp --version${RESET}"
echo -e "  ${CYAN}    okp 'print(\"Bonjour Oktopios !\")'${RESET}"
echo -e "  ${CYAN}    okp --repl${RESET}"
echo -e "\n  Extras : ${CYAN}pip install oktopios[all]${RESET}  (data / recognition / ia / system)"
echo ""
