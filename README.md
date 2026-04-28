# 🐙 Oktopios

> Un langage de programmation moderne, expressif et orienté objet, interprété en Python.

---

## Installation Général 

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
$env:PATH += ";$env:APPDATA\Python\Python312\Scripts"
okp --version
okp "print('Bonjour Oktopios !')"
```

---
## 🐧 Linux (Ubuntu, Debian, Fedora, Arch...)

### Méthode 1 — pip
```bash
pip install oktopios
```

### Méthode 2 
```bash
bash installers/linux/install.sh
source ~/.bashrc
okp --version
```

---

## 🍎 macOS
### Méthode 1 — pip
```bash
pip install oktopios
```

### Méthode 2 
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
### Méthode 1 — pip
```bash
pip install oktopios
```
### Méthode 2
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
### Méthode 1 — pip
```sh
apk update && apk add python3 py3-pip
pip install oktopios
```

### Méthode 2
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

## matrix([lignes, colonnes]) → MatrixObject (sparse) Pour les graphes, réseaux, liens entre cellules, traversée BFS/DFS :
```okp
inject matrix
var m = matrix.new([3, 3])
matrix.set(m, [0, 0], 42)
matrix.link(m, [0, 0], m, [1, 1])
var chemin = matrix.traverse(m, [0, 0], "bfs")
```

## matrix([lignes, colonnes], true) → Matrix (dense) Pour les calculs mathématiques, addition, produit tensoriel, IA :
```okp
inject Matrix
var A = Matrix([2, 2], true)
var B = Matrix.new([2, 2], true)
Matrix.set(A, [0, 0], 1)
var C = Matrix.add(A, B)
var T = Matrix.tensor(A, B)
var R = Matrix.contract(A, B, 0, 1)
```

## Exemple :
```okp
val doubler = lambda(x) => x * 2
val composer = lambda(f, g) => lambda(x) => f(g(x))
val doubler_apres_incr = composer(doubler, lambda(x) => x + 1)
print(doubler_apres_incr(4))  // 10

inject LinkedList
inject TreeSet
inject LinkedHashSet
inject TreeMap

var ll = LinkedList([1, 2])
var ts = TreeSet([2, 3])
var lhs = LinkedHashSet([10, 20])
var tm = TreeMap({"A": 1, "B": 2})

// =====================================================
// RACCOURCIS D’OPÉRATEURS POUR LES COLLECTIONS NATIVES
// =====================================================
ll += [3, 4]
ts += [0, 1]
lhs += [30, 23]
tm += {"C": 1, "D": 2}

// =====================================================
// TEST DES FONCTIONS NATIVES DIRECTES
// =====================================================
// --- LinkedList ---
LinkedList.llAdd(ll, 99)
LinkedList.llRemove(ll, 2)
var llList = LinkedList.llList(ll)

// --- TreeSet ---
TreeSet.tsAdd(ts, 42)
TreeSet.tsRemove(ts, 0)
var tsList = TreeSet.tsList(ts)

// --- LinkedHashSet ---
LinkedHashSet.lhsAdd(lhs, 77)
LinkedHashSet.lhsRemove(lhs, 23)
var lhsList = LinkedHashSet.lhsList(lhs)

// --- TreeMap ---
TreeMap.tmPut(tm, "E", 5)
TreeMap.tmRemove(tm, "A")
var tmKeys = TreeMap.tmKeys(tm)
var tmVals = TreeMap.tmVals(tm)

// =====================================================
// AFFICHAGE FINAL DES RÉSULTATS
// =====================================================
print("LinkedList → " + llList)
print("TreeSet → " + tsList)
print("LinkedHashSet → " + lhsList)
print("TreeMap Keys → " + tmKeys)
print("TreeMap Values → " + tmVals)


inject Math
print(Math.sqrt(9))

inject Matrix
var A = Matrix([2, 2], true)
var B = Matrix([2, 2], true)
Matrix.set(A, [0, 0], 1)
var C = Matrix.add(A, B)
var T = Matrix.tensor(A, B)
var R = Matrix.contract(A, B, 0, 1)

var m = Matrix([3, 3])
Matrix.set(m, [0, 0], 42)
Matrix.link(m, [0, 0], m, [1, 1])
var chemin = Matrix.traverse(m, [0, 0], "bfs")

print(C)
print(T)
print(R)
print(chemin)
```

## Résultat
```
10
LinkedList : [1, 3, 4, 99]
TreeSet : [1, 2, 3, 42]
LinkedHashSet : [10, 20, 30, 77]
TreeMap Keys : ['B', 'C', 'D', 'E']
TreeMap Values : [2, 1, 2, 5]
3.0
Matrix[2, 2]:
  (0, 0) -> 6
  (0, 1) -> 8
  (1, 0) -> 10
  (1, 1) -> 12
Matrix[2, 2, 2, 2]:
  (0, 0, 0, 0) -> 5
  (0, 0, 0, 1) -> 6
  (0, 0, 1, 0) -> 7
  (0, 0, 1, 1) -> 8
  (0, 1, 0, 0) -> 10
  (0, 1, 0, 1) -> 12
  (0, 1, 1, 0) -> 14
  (0, 1, 1, 1) -> 16
  (1, 0, 0, 0) -> 15
  (1, 0, 0, 1) -> 18
  (1, 0, 1, 0) -> 21
  (1, 0, 1, 1) -> 24
  (1, 1, 0, 0) -> 20
  (1, 1, 0, 1) -> 24
  (1, 1, 1, 0) -> 28
  (1, 1, 1, 1) -> 32
Matrix[2, 2]:
  (0, 0) -> 23
  (0, 1) -> 31
  (1, 0) -> 34
  (1, 1) -> 46
[Cell([0, 0], val=42), Cell([1, 1], val=10)]
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

