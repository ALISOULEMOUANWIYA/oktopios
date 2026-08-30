# 🐙 Oktopios — Guide d'installation par plateforme

## 🪟 Windows

### Méthode 1 — Script automatique (recommandé)
```powershell
# Dans PowerShell (en tant qu'administrateur)
powershell -ExecutionPolicy Bypass -File installers\windows\install.ps1
```

### Méthode 2 — Double-clic
Double-cliquez sur `installers\windows\install.bat`

### Méthode 3 — pip
```powershell
pip install oktopios
```

Après installation, ouvrez un **nouveau** PowerShell :
```powershell
okp --version
okp "print('Bonjour Oktopios !')"
```

---

## 🐧 Linux (Ubuntu, Debian, Fedora, Arch...)

```bash
bash installers/linux/install.sh
source ~/.bashrc
okp --version
```

---

## 🍎 macOS

```bash
bash installers/macos/install.sh
source ~/.zshrc
okp --version
```

---

## 🤖 Android — Termux

**Installer Termux** depuis [F-Droid](https://f-droid.org/packages/com.termux/)
*(pas depuis le Play Store — version obsolète)*

Depuis la 0.2.6, le cœur d'Oktopios est pur Python : le plus simple est pip.

Dans Termux :
```bash
pkg install python -y
pip install oktopios
okp --version
```

Alternative — installeur automatique (gère Python et les replis pip) :
```bash
pkg install python git -y && \
git clone https://github.com/ALISOULEMOUANWIYA/oktopios && \
cd oktopios && bash installers/android-termux/termux-install.sh
```

---

## 📱 iPhone / iPad — iSH Shell

**Installer iSH Shell** depuis l'[App Store](https://apps.apple.com/app/ish-shell/id1436902243) (gratuit)

iSH émule un terminal Linux Alpine sur iOS. Depuis la 0.2.6, le cœur d'Oktopios
est pur Python : l'installation la plus simple passe directement par pip.

Puis dans iSH :
```sh
# Mise à jour Alpine + Python
apk update && apk add python3 py3-pip

# Installer Oktopios (pur Python, aucune compilation)
pip install oktopios

# Tester
okp --version
```

> Alpine récent applique PEP 668 : si `pip` affiche
> « externally-managed-environment », ajoutez `--break-system-packages` :
> `pip install --break-system-packages oktopios`

Alternative — installeur automatique (gère Python, PEP 668 et le repli pour les
très anciens Python) :
```sh
apk add git
git clone https://github.com/ALISOULEMOUANWIYA/oktopios
cd oktopios
sh installers/ios-ish/ios-install.sh
```

---

## ✅ Test universel après installation

```okp
okp --version
okp --help
okp 'print("🐙 Bonjour Oktopios !")'
okp --repl
```

---

## 🔄 Désinstallation

### Windows
```powershell
Remove-Item -Recurse "$env:LOCALAPPDATA\Oktopios"
# Puis supprimer manuellement de PATH dans : Paramètres → Variables d'environnement
```

### Linux / macOS
```bash
rm -rf ~/.local/lib/oktopios ~/.local/bin/okp
```

### Termux
```bash
pip uninstall oktopios
```

### iSH
```sh
pip uninstall oktopios
```
