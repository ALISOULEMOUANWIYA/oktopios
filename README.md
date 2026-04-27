# 🐙 Oktopios

> Un langage de programmation moderne, expressif et orienté objet, interprété en Python.

---

## Installation

```bash
pip install oktopios
```

Ou depuis les sources :

```bash
git clone https://github.com/ALISOULEMOUANWIYA/oktopios
cd oktopios
```
### puis en suite Choisir l'installation selon votre plate-form
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

```
pip install -e .
```

## Utilisation rapide

```bash
# Exécuter un fichier
okp mon_programme.okp

# Code en ligne
okp 'print("Bonjour 🐙")'

# Mode interactif (REPL)
okp --repl

# Aide complète
okp --help
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
---
## Syntaxe de base d'Oktopios 🐙

```okp
// Variables et constantes
var age: int = 25
val nom: string = "Mouanwiya"

// Fonctions
fun saluer(prenom: string): string {
    return "Bonjour " + prenom + " !"
}
print(saluer(nom))

// Surcharge de fonctions
fun calcule(a: int, b: int): int { return a + b }
fun calcule(a: int, b: int, c: int): int { return (a + b) * c }

// Lambdas
val doubler = lambda(x: int) => x * 2
print(doubler(5))   // 10

// Boucles
loop (i = 0; i < 5; i += 1) {
    print(i)
}

// Classes
class Animal {
    var nom: string

    fun __construct(n: string) {
        this.nom = n
    }

    fun parler(): string {
        return this.nom + " dit bonjour"
    }
}

var chat = new Animal("Mimi")
print(chat.parler())

// Modules natifs
inject Math as math
inject String

print(Math.sqrt(16))           // 4.0
print(String.upper("hello"))   // HELLO
```

## matrix.new([lignes, colonnes]) → MatrixObject (sparse) Pour les graphes, réseaux, liens entre cellules, traversée BFS/DFS :
```
inject matrix
var m = matrix.new([3, 3])
matrix.set(m, [0, 0], 42)
matrix.link(m, [0, 0], m, [1, 1])
var chemin = matrix.traverse(m, [0, 0], "bfs")
```

## matrix.new([lignes, colonnes], true) → Matrix (dense) Pour les calculs mathématiques, addition, produit tensoriel, IA :
```
inject matrix
var A = matrix.new([2, 2], true)
var B = matrix.new([2, 2], true)
matrix.set(A, [0, 0], 1)
var C = matrix.add(A, B)
var T = matrix.tensor(A, B)
var R = matrix.contract(A, B, 0, 1)
```
## Fonctionnalités

- ✅ Variables typées (`var`, `val`)
- ✅ Fonctions avec surcharge (overloading)
- ✅ Lambdas et fonctions anonymes
- ✅ Classes, interfaces, classes abstraites
- ✅ Héritage, `override`, `super`
- ✅ Énumérations
- ✅ Modules natifs : `Math`, `String`, `Time`, `IO`, `List`, `Dict`...
- ✅ Boucles avancées : `loop`, `filterLoop`, `sortLoop`, `permuteLoop`...
- ✅ Gestion des exceptions (`try / catch / finally / throw`)
- ✅ REPL interactif
- ✅ Importation de fichiers `.okp`

## Commandes CLI

| Commande | Description |
|---|---|
| `okp fichier.okp` | Exécute un fichier |
| `okp 'code'` | Exécute du code inline |
| `okp --repl` | Lance le REPL |
| `okp --check fichier.okp` | Vérifie la syntaxe |
| `okp --version` | Affiche la version |
| `okp --keywords` | Liste les mots-clés |
| `okp --native` | Liste les fonctions natives |
| `okp --doc` | Documentation intégrée |
| `okp --init NomProjet` | Crée un projet |

## Licence

MIT © Mouanwiya Ali Soule

