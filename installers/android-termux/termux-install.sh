#!/data/data/com.termux/files/usr/bin/bash
# ================================================
#  Oktopios v0.0.1 - Installeur Android (Termux)
#  Usage: bash termux-install.sh
#
#  Termux : https://f-droid.org/packages/com.termux/
#  (Utilisez la version F-Droid, pas celle du Play Store)
# ================================================

OKP_VERSION="0.0.1"
PREFIX="${PREFIX:-/data/data/com.termux/files/usr}"
HOME_DIR="${HOME:-/data/data/com.termux/files/home}"
INSTALL_DIR="$HOME_DIR/.oktopios"
BIN_DIR="$PREFIX/bin"

GREEN="\033[32m"; CYAN="\033[36m"
YELLOW="\033[33m"; RED="\033[31m"; RESET="\033[0m"; BOLD="\033[1m"

ok()   { echo -e "  ${GREEN}✓${RESET}  $1"; }
info() { echo -e "  ${YELLOW}→${RESET}  $1"; }
fail() { echo -e "  ${RED}✗  ERREUR: $1${RESET}"; exit 1; }

echo -e ""
echo -e "${CYAN}  ════════════════════════════════════════════${RESET}"
echo -e "${CYAN}   🐙  Oktopios v${OKP_VERSION} - Termux (Android)${RESET}"
echo -e "${CYAN}  ════════════════════════════════════════════${RESET}"
echo -e ""

# 1. Mise à jour des paquets Termux
echo -e "  ${BOLD}[1/5]${RESET} Mise à jour de Termux..."
pkg update -y -q 2>/dev/null || apt-get update -y -q
ok "Termux à jour"

# 2. Installer Python
echo -e "\n  ${BOLD}[2/5]${RESET} Installation de Python..."
if ! command -v python3 &>/dev/null; then
    pkg install python -y -q
fi
ok "Python $(python3 --version | awk '{print $2}')"

# 3. Installer git (pour cloner si besoin)
echo -e "\n  ${BOLD}[3/5]${RESET} Installation de git..."
if ! command -v git &>/dev/null; then
    pkg install git -y -q
fi
ok "git disponible"

# 4. Installer Oktopios
echo -e "\n  ${BOLD}[4/5]${RESET} Installation d'Oktopios..."
mkdir -p "$INSTALL_DIR"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if [ -f "$PROJECT_DIR/vm/main.py" ]; then
    cp -r "$PROJECT_DIR"/. "$INSTALL_DIR/"
    ok "Fichiers copiés"
else
    # Télécharger depuis GitHub
    info "Téléchargement depuis GitHub..."
    git clone --depth 1 https://github.com/ALISOULEMOUANWIYA/oktopios "$INSTALL_DIR" 2>/dev/null || \
    pip install oktopios --quiet
    ok "Oktopios téléchargé"
fi

# Installer dépendances pip
pip install colorama tabulate --quiet
ok "Dépendances installées"

# 5. Créer le lanceur
echo -e "\n  ${BOLD}[5/5]${RESET} Création du lanceur okp..."
cat > "$BIN_DIR/okp" << WRAPPER
#!/data/data/com.termux/files/usr/bin/bash
python3 "$INSTALL_DIR/vm/main.py" "\$@"
WRAPPER
chmod +x "$BIN_DIR/okp"
ok "Commande okp créée"

# Ajouter alias dans .bashrc
if ! grep -q "alias okp" "$HOME_DIR/.bashrc" 2>/dev/null; then
    echo "" >> "$HOME_DIR/.bashrc"
    echo "# Oktopios" >> "$HOME_DIR/.bashrc"
    echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$HOME_DIR/.bashrc"
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
echo -e "  Pour créer un projet :"
echo -e "  ${CYAN}    okp --init MonProjet${RESET}"
echo -e "  ${CYAN}    cd MonProjet && okp main.okp${RESET}"
echo ""

# Tester immédiatement
echo -e "  Test rapide..."
"$BIN_DIR/okp" 'print("🐙 Oktopios fonctionne sur Android !")' 2>/dev/null && \
    ok "Test réussi !" || info "Redémarrez Termux et tapez: okp --version"
