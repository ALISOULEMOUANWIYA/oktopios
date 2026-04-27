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

ok()   { echo -e "  ${GREEN}✓${RESET}  $1"; }
info() { echo -e "  ${YELLOW}→${RESET}  $1"; }
fail() { echo -e "  ${RED}✗  ERREUR: $1${RESET}"; exit 1; }
step() { echo -e "\n  ${BOLD}[$1/$2]${RESET} $3"; }

finish() {
    echo ""
    echo -e "  ${GREEN}════════════════════════════════════════════${RESET}"
    echo -e "  ${GREEN}  ✅ Installation terminée avec succès !${RESET}"
    echo -e "  ${GREEN}════════════════════════════════════════════${RESET}"
    echo ""
    echo -e "  Rechargez votre terminal :"
    echo -e "  ${CYAN}    source ~/.bashrc${RESET}"
    echo ""
    echo -e "  Puis testez :"
    echo -e "  ${CYAN}    okp --version${RESET}"
    echo -e "  ${CYAN}    okp 'print(\"Bonjour Oktopios !\")'${RESET}"
    echo -e "  ${CYAN}    okp --repl${RESET}"
    echo ""
}

echo -e ""
echo -e "${CYAN}  ════════════════════════════════════════════${RESET}"
echo -e "${CYAN}   🐙  Oktopios v${OKP_VERSION} - Installeur Linux${RESET}"
echo -e "${CYAN}  ════════════════════════════════════════════${RESET}"
echo -e ""

# ── 1. Python ─────────────────────────────────────────────────────────────────
step 1 5 "Vérification de Python..."

if ! command -v python3 &>/dev/null; then
    info "Python3 non trouvé. Tentative d'installation..."
    if   command -v apt-get &>/dev/null; then sudo apt-get install -y python3 python3-pip -q
    elif command -v dnf     &>/dev/null; then sudo dnf install -y python3 python3-pip -q
    elif command -v pacman  &>/dev/null; then sudo pacman -S --noconfirm python python-pip
    elif command -v apk     &>/dev/null; then apk add python3 py3-pip
    else fail "Installez Python 3.10+ depuis https://python.org"
    fi
fi

if ! python3 -m pip --version &>/dev/null 2>&1; then
    info "pip absent — installation..."
    if   command -v apt-get &>/dev/null; then sudo apt-get install -y python3-pip -q 2>/dev/null || true
    elif command -v dnf     &>/dev/null; then sudo dnf install -y python3-pip -q 2>/dev/null || true
    elif command -v pacman  &>/dev/null; then sudo pacman -S --noconfirm python-pip 2>/dev/null || true
    fi
    python3 -m ensurepip --upgrade 2>/dev/null || true
fi

PYVER=$(python3 --version 2>&1 | awk '{print $2}')
ok "Python $PYVER"

# ── 2. Dossiers ───────────────────────────────────────────────────────────────
step 2 5 "Création des dossiers..."
mkdir -p "$INSTALL_DIR" "$BIN_DIR"
ok "Dossiers créés dans $INSTALL_DIR"

# ── 3. Copie des fichiers ─────────────────────────────────────────────────────
step 3 5 "Copie des fichiers Oktopios..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALLERS_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_DIR="$(dirname "$INSTALLERS_DIR")"

if [ ! -f "$PROJECT_DIR/vm/main.py" ] && [ -f "vm/main.py" ]; then
    PROJECT_DIR="$(pwd)"
fi
if [ ! -f "$PROJECT_DIR/vm/main.py" ]; then
    SEARCH="$(pwd)"
    for _ in 1 2 3 4; do
        if [ -f "$SEARCH/vm/main.py" ]; then PROJECT_DIR="$SEARCH"; break; fi
        SEARCH="$(dirname "$SEARCH")"
    done
fi

if [ ! -f "$PROJECT_DIR/vm/main.py" ]; then
    fail "Projet introuvable. Lancez depuis le dossier oktopios-0.0.1 :\n  cd oktopios-0.0.1\n  bash installers/linux/install.sh"
fi

if command -v rsync &>/dev/null; then
    rsync -a --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' "$PROJECT_DIR/" "$INSTALL_DIR/"
else
    cp -r "$PROJECT_DIR"/. "$INSTALL_DIR/" 2>/dev/null || true
    rm -rf "$INSTALL_DIR/.git" 2>/dev/null || true
    find "$INSTALL_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
fi
ok "Fichiers copiés"

# ── 4. Dépendances ────────────────────────────────────────────────────────────
step 4 5 "Installation des dépendances..."
python3 -m pip install colorama tabulate psutil --quiet --user 2>/dev/null || \
python3 -m pip install colorama tabulate psutil --quiet --user --break-system-packages 2>/dev/null || \
python3 -m pip install colorama tabulate --quiet --user --break-system-packages 2>/dev/null || \
sudo apt-get install -y python3-colorama -q 2>/dev/null || true
ok "Dépendances installées"

cat > "$BIN_DIR/okp" << 'WRAPPER'
#!/usr/bin/env bash
python3 "$HOME/.local/lib/oktopios/vm/main.py" "$@"
WRAPPER
chmod +x "$BIN_DIR/okp"

# ── 5. PATH ───────────────────────────────────────────────────────────────────
step 5 5 "Configuration du PATH..."

case "$SHELL" in
    */zsh)  SHELL_RC="$HOME/.zshrc" ;;
    */fish) SHELL_RC="$HOME/.config/fish/config.fish" ;;
    *)      SHELL_RC="$HOME/.bashrc" ;;
esac

if ! grep -q '.local/bin' "$SHELL_RC" 2>/dev/null; then
    echo "" >> "$SHELL_RC"
    echo "# Oktopios" >> "$SHELL_RC"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
    ok "PATH ajouté dans $SHELL_RC"
else
    ok "PATH déjà configuré"
fi

finish
