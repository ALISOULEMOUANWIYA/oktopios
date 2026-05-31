# Oktopios 🐙 

Oktopios est un langage de programmation expérimental, moderne et expressif, interprété en Python. Il combine une syntaxe lisible, un modèle orienté objet, des fonctions avancées, des modules natifs et une architecture bio-inspirée appelée architecture pieuvrique.

L'objectif du projet est de construire un langage capable d'orchestrer des unités d'exécution locales comme des tentacules autour d'un cerveau central. Oktopios n'est donc pas seulement un langage de script : c'est une base pour explorer l'exécution distribuée interne, les matrices, l'adaptation IA et les systèmes modulaires.

## Vision 🐙 

Oktopios s'inspire de l'organisation d'une pieuvre :

- un cerveau central pour la gouvernance et l'orchestration ;
- plusieurs coeurs spécialisés pour l'exécution, la circulation des données et l'adaptation ;
- des tentacules capables d'exécuter localement des tâches ;
- un mécanisme d'intention pour diffuser des ordres ;
- une distribution aléatoire ou dynamique des tâches avec `tentRandom` ;
- une ouverture vers des modules IA adaptatifs comme Ollama, DeepSeek ou StarCoder.

Cette vision se traduit progressivement dans le langage avec les mots-clés :

```okp
tent
heart
core
ten
intention
tentRandom
```

## Installation 🐙 

### Depuis PyPI

```bash
pip install oktopios
```

Après installation :

```bash
okp --version
okp 'print("Bonjour Oktopios")'
```

### Depuis les sources 🐙 

```bash
git clone https://github.com/ALISOULEMOUANWIYA/oktopios.git
cd oktopios
pip install -e .
```

### Windows 🐙

```powershell
pip install oktopios
okp-setup
okp --version
```

Si la commande `okp` n'est pas reconnue, ouvrez un nouveau terminal ou ajoutez le dossier Scripts de Python au `PATH`.

### Linux et macOS 🐙

```bash
pip install oktopios
okp --version
```

Depuis le dépôt :

```bash
bash installers/linux/install.sh
# ou
bash installers/macos/install.sh
```

### Android avec Termux 🐙

Installez Termux depuis F-Droid, puis :

```bash
pkg install python git -y
pip install oktopios
okp --version
```

### iPhone ou iPad avec iSH 🐙

```sh
apk update
apk add python3 py3-pip
pip install oktopios
okp --version
```

## Utilisation rapide 🐙

```bash
# Exécuter un fichier
okp programme.okp

# Exécuter du code inline
okp 'print("Bonjour")'

# Lancer le REPL
okp --repl

# Afficher l'aide
okp --help
```

## Premier programme 🐙

```okp
val nom: string = "Oktopios"
print("Bonjour " + nom)
```

## Syntaxe de base 🐙 

### Variables 🐙 

```okp
val x: int = 10          // constante
var compteur: int = 0    // variable mutable
var message = "Salut"    // type inféré
```

### Fonctions 🐙 

```okp
fun add(a: int, b: int): int {
    return a + b
}

print(add(2, 3))
```

### Surcharge 🐙 

```okp
fun calcule(a: int, b: int): int {
    return a + b
}

fun calcule(a: int, b: int, c: int): int {
    return (a + b) * c
}
```

### Lambdas 🐙 

```okp
val doubler = lambda(x: int) => x * 2
print(doubler(5))
```

### Conditions 🐙 

```okp
if (compteur > 10) {
    print("grand")
} elif (compteur == 10) {
    print("égal")
} else {
    print("petit")
}
```

### Boucles 🐙 

```okp
for (var i: int = 0; i < 5; i += 1) {
    print(i)
}

var noms: string[] = ["Awa", "Mouanwiya", "Ali"]
for (nom in noms) {
    print(nom)
}
```

## Classes et objets 🐙 

```okp
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
```

Oktopios 🐙 prend aussi en charge progressivement :

- interfaces ;
- classes abstraites ;
- héritage ;
- `override` ;
- `super` ;
- énumérations ;
- méthodes statiques ;
- visibilité `public`, `private`, `protected`, `global`.

## Pattern matching avec `__matches__` 🐙 

`__matches__` permet de comparer une valeur contre plusieurs formes. Il peut retourner plusieurs résultats si plusieurs cas sont vrais.

```okp
val x = 20
val y = 20
var list: string[] = ["@Nabile", "@Soultan", "@Abdallah"]

val r = __matches__ x => {
    1                 => "one"
    2, 3              => "two or three"
    4|10              => "dans le range [4:10]"
    in list           => "dans la liste"
    like y            => f"x{x} = y{y}"
    between 18 and 30 => f"{x} appartient à [18:30]"
    is int            => "integer"
    else              => "other"
}

print(r)
```

Patterns supportés :

- valeurs simples : `1`, `"hello"` ;
- plusieurs valeurs : `2, 3` ;
- intervalle : `4|10` ;
- appartenance : `in list` ;
- ressemblance ou contenance : `like value` ;
- intervalle explicite : `between 18 and 30` ;
- regex : `matches "[a-z]+"` ;
- type : `is int`, `is string`, `is float`, `is bool` ;
- fallback : `else`.

## Architecture pieuvrique 🐙 

Oktopios introduit une architecture bio-inspirée pour organiser l'exécution.

```okp
tent class Brain {
    heart {
        var mode: string = "defense"
    }

    core {
        print("System Ready")
    }
}

ten class Arm1 {
    fun alert(msg: string) {
        print("Arm1 received " + msg)
    }
}

ten class Arm2 {
    fun alert(msg: string) {
        print("Arm2 received " + msg)
    }
}

intention alert("Danger")
tentRandom alert("Ping")
```

Dans ce modèle 🐙 :

- `tent class` déclare le cerveau central ;
- `heart` contient la configuration centrale ;
- `core` contient le noyau exécuté au démarrage ;
- `ten class` déclare une tentacule locale ;
- `intention` diffuse un appel à toutes les tentacules compatibles ;
- `tentRandom` envoie un appel à une tentacule compatible choisie au hasard.

Cette partie est en évolution. Le but est d'aller vers un vrai moteur interne de routage, d'adaptation et d'exécution distribuée.

## Matrices 🐙 

Oktopios possède un module `matrix` pour manipuler des structures denses ou clairsemées.

### Matrice clairsemée 🐙 

Utile pour les graphes, réseaux, liens entre cellules ou parcours BFS/DFS.

```okp
inject matrix

var m = matrix.new([3, 3])
matrix.set(m, [0, 0], 42)
matrix.link(m, [0, 0], m, [1, 1])
var chemin = matrix.traverse(m, [0, 0], "bfs")
```

### Matrice dense 🐙 

Utile pour les calculs mathématiques, l'IA et les opérations numériques.

```okp
inject matrix

var A = matrix.new([2, 2], true)
var B = matrix.new([2, 2], true)
matrix.set(A, [0, 0], 1)

var C = matrix.add(A, B)
var T = matrix.tensor(A, B)
var R = matrix.contract(A, B, 0, 1)
```

## Modules natifs 🐙 

Oktopios utilise `inject` pour charger des modules natifs.

```okp
inject Math
inject String
inject matrix

print(Math.sqrt(16))
print(String.upper("oktopios"))
```

Modules et familles de fonctionnalités disponibles ou en évolution :

- `Math` ;
- `String` ;
- collections ;
- matrices ;
- temps et entrées/sorties ;
- fonctions avancées ;
- coeur `heart` ;
- modules adaptatifs.

## Gestion des erreurs 🐙

```okp
try {
    throw "erreur volontaire"
} catch(e) {
    print("Attrapé : " + e)
} finally {
    print("Fin")
}
```

## Commandes CLI 🐙

| Commande | Description |
|---|---|
| `okp fichier.okp` | Exécute un fichier Oktopios |
| `okp 'code'` | Exécute du code inline |
| `okp --repl` | Lance le REPL |
| `okp --check fichier.okp` | Vérifie la syntaxe |
| `okp --version` | Affiche la version |
| `okp --keywords` | Liste les mots-clés |
| `okp --native` | Liste les fonctions natives |
| `okp --doc` | Affiche la documentation intégrée |
| `okp --init NomProjet` | Crée un projet Oktopios |

## Structure du projet 🐙

```text
vm/
  lexer.py                # tokenisation
  parser.py               # parsing vers AST
  ast_nodes.py            # modèle AST
  interpreter.py          # exécution
  environment.py          # environnements et portées
  runtime_instance.py     # instances objets
  native_funcs.py         # fonctions natives
  native_collections.py   # collections natives
  matrix.py               # matrices
  heart/                  # modules coeur
  modules/                # modules .okp
installers/               # scripts d'installation
tests/                    # tests et exemples
docs/                     # documentation
```

## État du projet 🐙

Oktopios est encore expérimental. Certaines fonctionnalités sont stables, d'autres sont en cours de conception ou d'intégration. Le langage évolue rapidement autour de trois axes :

- lisibilité de la syntaxe ;
- puissance du runtime objet et fonctionnel ;
- architecture pieuvrique pour l'orchestration, les matrices et l'adaptation IA.

## Licence

MIT © Mouanwiya Ali Soule