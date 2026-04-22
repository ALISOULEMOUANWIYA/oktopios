#!/usr/bin/env bash
# ================================================
#  Oktopios v0.0.1 - Installeur Linux universel
#  Usage: bash install.sh
#  Testé sur: Ubuntu, Debian, Fedora, Arch, Alpine
# ================================================

set -e

OKP_VERSION="0.0.1"
INSTALL_DIR="$HOME/.local/lib/oktopios"
BIN_DIR="$HOME/.local/bin"
BOLD="\033[1m"
GREEN="\033[32m"
CYAN="\033[36m"
YELLOW="\033[33m"
RED="\033[31m"
RESET="\033[0m"

header() {
    echo -e ""
    echo -e "${CYAN}  ════════════════════════════════════════════${RESET}"
    echo -e "${CYAN}   🐙  Oktopios v${OKP_VERSION} - Installeur Linux${RESET}"
    echo -e "${CYAN}  ════════════════════════════════════════════${RESET}"
    echo -e ""
}

ok()   { echo -e "  ${GREEN}✓${RESET}  $1"; }
info() { echo -e "  ${YELLOW}→${RESET}  $1"; }
fail() { echo -e "  ${RED}✗  ERREUR: $1${RESET}"; exit 1; }
step() { echo -e "\n  ${BOLD}[$1/$2]${RESET} $3"; }

header

# 1. Vérifier Python 3.10+
step 1 5 "Vérification de Python..."
if ! command -v python3 &>/dev/null; then
    info "Python3 non trouvé. Tentative d'installation..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get install -y python3 python3-pip 2>/dev/null || fail "Installation Python échouée"
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y python3 python3-pip 2>/dev/null || fail "Installation Python échouée"
    elif command -v pacman &>/dev/null; then
        sudo pacman -S --noconfirm python python-pip 2>/dev/null || fail "Installation Python échouée"
    elif command -v apk &>/dev/null; then
        apk add python3 py3-pip 2>/dev/null || fail "Installation Python échouée"
    else
        fail "Installez Python 3.10+ manuellement depuis https://python.org"
    fi
fi

PYVER=$(python3 --version 2>&1 | awk '{print $2}')
PYMAJ=$(echo "$PYVER" | cut -d. -f1)
PYMIN=$(echo "$PYVER" | cut -d. -f2)
if [ "$PYMAJ" -lt 3 ] || { [ "$PYMAJ" -eq 3 ] && [ "$PYMIN" -lt 10 ]; }; then
    fail "Python 3.10+ requis (détecté: $PYVER)"
fi
ok "Python $PYVER"

# 2. Créer les dossiers
step 2 5 "Création des dossiers..."
mkdir -p "$INSTALL_DIR" "$BIN_DIR"
ok "Dossiers créés dans $INSTALL_DIR"

# 3. Copier les fichiers
step 3 5 "Copie des fichiers Oktopios..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if [ -f "$PROJECT_DIR/vm/main.py" ]; then
    cp -r "$PROJECT_DIR"/. "$INSTALL_DIR/"
    ok "Fichiers copiés"
else
    info "Installation via pip..."
    python3 -m pip install oktopios --quiet --user
    ok "Installé via pip"
    # Créer wrapper pip
    cat > "$BIN_DIR/okp" << 'WRAPPER'
#!/usr/bin/env bash
python3 -m oktopios "$@"
WRAPPER
    chmod +x "$BIN_DIR/okp"
    finish
fi

# 4. Installer les dépendances
step 4 5 "Installation des dépendances..."
python3 -m pip install colorama tabulate psutil --quiet --user 2>/dev/null || \
python3 -m pip install colorama tabulate --quiet --user
ok "Dépendances installées"

# Créer le wrapper okp
cat > "$BIN_DIR/okp" << WRAPPER
#!/usr/bin/env bash
python3 "$INSTALL_DIR/vm/main.py" "\$@"
WRAPPER
chmod +x "$BIN_DIR/okp"

# 5. Configurer le PATH
step 5 5 "Configuration du PATH..."
SHELL_RC=""
case "$SHELL" in
    */bash) SHELL_RC="$HOME/.bashrc" ;;
    */zsh)  SHELL_RC="$HOME/.zshrc"  ;;
    */fish) SHELL_RC="$HOME/.config/fish/config.fish" ;;
    *)      SHELL_RC="$HOME/.profile" ;;
esac

PATH_LINE='export PATH="$HOME/.local/bin:$PATH"'
if ! grep -q '.local/bin' "$SHELL_RC" 2>/dev/null; then
    echo "" >> "$SHELL_RC"
    echo "# Oktopios" >> "$SHELL_RC"
    echo "$PATH_LINE" >> "$SHELL_RC"
    ok "PATH ajouté dans $SHELL_RC"
else
    ok "PATH déjà configuré"
fi

finish() {
    echo ""
    echo -e "  ${GREEN}════════════════════════════════════════════${RESET}"
    echo -e "  ${GREEN}  ✅ Installation terminée avec succès !${RESET}"
    echo -e "  ${GREEN}════════════════════════════════════════════${RESET}"
    echo ""
    echo -e "  Rechargez votre terminal :"
    echo -e "  ${CYAN}    source $SHELL_RC${RESET}"
    echo ""
    echo -e "  Puis testez :"
    echo -e "  ${CYAN}    okp --version${RESET}"
    echo -e "  ${CYAN}    okp 'print(\"Bonjour Oktopios !\")'${RESET}"
    echo -e "  ${CYAN}    okp --repl${RESET}"
    echo ""
}

finish
