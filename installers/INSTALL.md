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

Puis dans Termux :
```bash
bash installers/android-termux/termux-install.sh
okp --version
```

Ou en une seule commande :
```bash
pkg install python git -y && \
git clone https://github.com/ALISOULEMOUANWIYA/oktopios && \
cd oktopios && bash installers/android-termux/termux-install.sh
```

---

## 📱 iPhone / iPad — iSH Shell

**Installer iSH Shell** depuis l'[App Store](https://apps.apple.com/app/ish-shell/id1436902243) (gratuit)

iSH émule un terminal Linux Alpine sur iOS.

Puis dans iSH :
```sh
# Mise à jour Alpine
apk update && apk add git python3 py3-pip

# Cloner et installer
git clone https://github.com/ALISOULEMOUANWIYA/oktopios
cd oktopios
sh installers/ios-ish/ios-install.sh

# Tester
okp --version
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
rm -rf ~/.oktopios $PREFIX/bin/okp
```

### iSH
```sh
rm -rf ~/.oktopios /usr/local/bin/okp
```
