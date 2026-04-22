#!/bin/sh
# ================================================
#  Oktopios v0.0.1 - Installeur iPhone/iOS (iSH)
#  Usage: sh ios-install.sh
#
#  Prérequis : Application iSH Shell (App Store gratuit)
#  https://apps.apple.com/app/ish-shell/id1436902243
#
#  iSH émule Linux Alpine sur iPhone/iPad
# ================================================

OKP_VERSION="0.0.1"
INSTALL_DIR="$HOME/.oktopios"
BIN_DIR="/usr/local/bin"

echo ""
echo "  ============================================"
echo "   🐙  Oktopios v${OKP_VERSION} - iPhone/iPad (iSH)"
echo "  ============================================"
echo ""

# 1. Mise à jour Alpine
echo "  [1/5] Mise a jour du systeme..."
apk update -q 2>/dev/null || true
echo "  OK"

# 2. Installer Python via Alpine
echo "  [2/5] Installation de Python3..."
if ! command -v python3 >/dev/null 2>&1; then
    apk add python3 py3-pip -q
fi
echo "  OK - Python $(python3 --version 2>&1 | awk '{print $2}')"

# 3. Installer git
echo "  [3/5] Installation de git..."
if ! command -v git >/dev/null 2>&1; then
    apk add git -q
fi
echo "  OK"

# 4. Installer Oktopios
echo "  [4/5] Installation d'Oktopios..."
mkdir -p "$INSTALL_DIR"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if [ -f "$PROJECT_DIR/vm/main.py" ]; then
    cp -r "$PROJECT_DIR"/. "$INSTALL_DIR/"
    echo "  OK - Fichiers copies"
else
    echo "  -> Telechargement depuis GitHub..."
    git clone --depth 1 https://github.com/ALISOULEMOUANWIYA/oktopios "$INSTALL_DIR" 2>/dev/null || \
    pip3 install oktopios --quiet
    echo "  OK"
fi

# Dépendances minimales (Alpine)
pip3 install colorama tabulate --quiet 2>/dev/null || true

# 5. Créer le lanceur
echo "  [5/5] Creation du lanceur okp..."
cat > "/usr/local/bin/okp" << WRAPPER
#!/bin/sh
python3 "$INSTALL_DIR/vm/main.py" "\$@"
WRAPPER
chmod +x "/usr/local/bin/okp"
echo "  OK"

# Ajouter au profil
if ! grep -q "Oktopios" "$HOME/.profile" 2>/dev/null; then
    echo "" >> "$HOME/.profile"
    echo "# Oktopios" >> "$HOME/.profile"
    echo "export PATH=\"/usr/local/bin:\$PATH\"" >> "$HOME/.profile"
fi

echo ""
echo "  ============================================"
echo "   Installation terminee sur iPhone/iPad !"
echo "  ============================================"
echo ""
echo "  Testez avec :"
echo "    okp --version"
echo "    okp 'print(\"Bonjour depuis iPhone !\")'"
echo "    okp --repl"
echo ""

# Test immédiat
okp 'print("Oktopios fonctionne sur iPhone !")' 2>/dev/null && \
    echo "  Test OK !" || echo "  Tapez: source ~/.profile puis: okp --version"
