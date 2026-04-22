#!/usr/bin/env bash
# ================================================
#  Oktopios v0.0.1 - Installeur macOS
#  Usage: bash install.sh
#  Testé sur: macOS 12 Monterey, 13 Ventura, 14 Sonoma
# ================================================

set -e

OKP_VERSION="0.0.1"
INSTALL_DIR="$HOME/.local/lib/oktopios"
BIN_DIR="$HOME/.local/bin"
GREEN="\033[32m"; CYAN="\033[36m"
YELLOW="\033[33m"; RED="\033[31m"; RESET="\033[0m"; BOLD="\033[1m"

ok()   { echo -e "  ${GREEN}✓${RESET}  $1"; }
info() { echo -e "  ${YELLOW}→${RESET}  $1"; }
fail() { echo -e "  ${RED}✗  ERREUR: $1${RESET}"; exit 1; }
step() { echo -e "\n  ${BOLD}[$1/$2]${RESET} $3"; }

echo -e ""
echo -e "${CYAN}  ════════════════════════════════════════════${RESET}"
echo -e "${CYAN}   🐙  Oktopios v${OKP_VERSION} - Installeur macOS${RESET}"
echo -e "${CYAN}  ════════════════════════════════════════════${RESET}"
echo -e ""

# 1. Vérifier Python
step 1 5 "Vérification de Python 3.10+..."
if ! command -v python3 &>/dev/null; then
    info "Python3 non trouvé."
    if command -v brew &>/dev/null; then
        info "Installation via Homebrew..."
        brew install python@3.12
    else
        fail "Installez Python depuis https://python.org ou installez Homebrew: https://brew.sh"
    fi
fi

PYVER=$(python3 --version 2>&1 | awk '{print $2}')
PYMAJ=$(echo "$PYVER" | cut -d. -f1)
PYMIN=$(echo "$PYVER" | cut -d. -f2)
if [ "$PYMAJ" -lt 3 ] || { [ "$PYMAJ" -eq 3 ] && [ "$PYMIN" -lt 10 ]; }; then
    fail "Python 3.10+ requis (détecté: $PYVER). Mettez à jour via: brew install python@3.12"
fi
ok "Python $PYVER"

# 2. Créer les dossiers
step 2 5 "Création des dossiers..."
mkdir -p "$INSTALL_DIR" "$BIN_DIR"
ok "Dossiers créés"

# 3. Copier les fichiers
step 3 5 "Installation des fichiers Oktopios..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if [ -f "$PROJECT_DIR/vm/main.py" ]; then
    cp -r "$PROJECT_DIR"/. "$INSTALL_DIR/"
    ok "Fichiers copiés dans $INSTALL_DIR"
else
    info "Installation via pip..."
    python3 -m pip install oktopios --quiet --user
    ok "Installé via pip"
fi

# 4. Dépendances
step 4 5 "Installation des dépendances..."
python3 -m pip install colorama tabulate psutil --quiet --user 2>/dev/null || \
python3 -m pip install colorama tabulate --quiet --user
ok "colorama, tabulate installés"

# Créer wrapper okp
cat > "$BIN_DIR/okp" << WRAPPER
#!/usr/bin/env bash
python3 "$INSTALL_DIR/vm/main.py" "\$@"
WRAPPER
chmod +x "$BIN_DIR/okp"
ok "Lanceur okp créé"

# 5. PATH
step 5 5 "Configuration du PATH..."
SHELL_RC="$HOME/.zshrc"
[ -n "$BASH_VERSION" ] && SHELL_RC="$HOME/.bash_profile"

PATH_LINE='export PATH="$HOME/.local/bin:$PATH"'
if ! grep -q '.local/bin' "$SHELL_RC" 2>/dev/null; then
    echo "" >> "$SHELL_RC"
    echo "# Oktopios" >> "$SHELL_RC"
    echo "$PATH_LINE" >> "$SHELL_RC"
    ok "PATH ajouté dans $SHELL_RC"
else
    ok "PATH déjà configuré"
fi

echo ""
echo -e "  ${GREEN}════════════════════════════════════════════${RESET}"
echo -e "  ${GREEN}  ✅ Installation terminée !${RESET}"
echo -e "  ${GREEN}════════════════════════════════════════════${RESET}"
echo ""
echo -e "  Rechargez le terminal :"
echo -e "  ${CYAN}    source $SHELL_RC${RESET}"
echo ""
echo -e "  Testez :"
echo -e "  ${CYAN}    okp --version${RESET}"
echo -e "  ${CYAN}    okp 'print(\"Bonjour Oktopios !\")'${RESET}"
echo -e "  ${CYAN}    okp --repl${RESET}"
echo ""
echo -e "  Tip Homebrew: vous pouvez aussi utiliser"
echo -e "  ${CYAN}    pip install oktopios${RESET}"
echo ""
