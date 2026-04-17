# 📘 Documentation Oktopios v0.0.1

## Variables

```okp
var x: int = 10          // variable mutable, typée
var y = 3.14             // type inféré (float)
val PI: float = 3.14159  // constante, ne peut pas être réassignée
var msg: string = "Salut"
var flag: bool = true
```

## Fonctions

```okp
// Déclaration simple
fun saluer(nom: string) {
    print("Bonjour " + nom)
}
saluer("Ali")

// Avec type de retour
fun addition(a: int, b: int): int {
    return a + b
}
print(addition(3, 4))   // 7

// Valeur par défaut
fun accueillir(prenom: string = "ami") {
    print("Salut " + prenom)
}
accueillir()          // Salut ami
accueillir("Nina")    // Salut Nina

// Expression courte
fun carre(n: int): int = n * n

// Surcharge (même nom, paramètres différents)
fun calcule(a: int, b: int): int { return a + b }
fun calcule(a: int, b: int, c: int): int { return (a + b) * c }
print(calcule(2, 3))      // 5
print(calcule(2, 3, 4))   // 20

// Fonctions imbriquées
fun externe() {
    var msg = "Salut"
    fun interne() { print(msg) }
    interne()
}
```

## Lambdas

```okp
val doubler = lambda(x: int) => x * 2
print(doubler(5))   // 10

var adder = lambda(a: int, b: int) => a + b
print(adder(3, 4))  // 7

// Composition de fonctions
val composer = lambda(f, g) => lambda(x) => f(g(x))
val incr = lambda(x: int) => x + 1
val doubleApresIncr = composer(doubler, incr)
print(doubleApresIncr(4))   // 10
```

## Conditions

```okp
var n: int = 42

if n > 0 {
    print("Positif")
} elif n == 0 {
    print("Zéro")
} else {
    print("Négatif")
}

// Switch
switch (n) {
    case 1 { print("Un") }
    case 42 { print("La réponse !") }
    default { print("Autre") }
}
```

## Boucles

```okp
// Boucle classique
loop (i = 0; i < 5; i += 1) {
    print(i)
}

// While
var i = 0
while i < 3 {
    print(i)
    i += 1
}

// For-each
var noms: string[] = ["Ali", "Nina", "Sam"]
for (nom in noms) {
    print(nom)
}

// Boucle filtrante
var nums: int[] = [1, 2, 3, 4, 5, 6]
filterLoop (x in nums) where (x % 2 == 0) {
    print(x)   // 2, 4, 6
}

// Boucle triante
sortLoop (x in nums) order asc {
    print(x)
}

// Boucle avec when (switch intégré)
loop (i = 0; i < 5; i += 1) when (i) {
    is 1 => { print("Un") }
    is 3 => { print("Trois") }
    default => { print(i) }
}
```

## Classes

```okp
class Animal {
    var nom: string
    var age: int

    fun __construct(n: string, a: int) {
        this.nom = n
        this.age = a
    }

    fun parler(): string {
        return this.nom + " parle !"
    }

    fun __destruct() {
        print("Animal " + this.nom + " libéré")
    }
}

var chien = new Animal("Rex", 3)
print(chien.parler())
print(chien.nom)
```

## Héritage

```okp
class Chien extends Animal {
    var race: string

    fun __construct(n: string, a: int, r: string) {
        super(n, a)
        this.race = r
    }

    override fun parler(): string {
        return this.nom + " aboie !"
    }
}

var rex = new Chien("Rex", 3, "Labrador")
print(rex.parler())   // Rex aboie !
```

## Classes abstraites et interfaces

```okp
interface IAnimal {
    fun parler(): string
    fun bouger(): void
}

abstract class Vertebre {
    var nom: string
    abstract fun respirer(): void
}

class Humain extends Vertebre implements IAnimal {
    fun __construct(n: string) { this.nom = n }

    invoke fun parler(): string { return "Je parle" }
    invoke fun bouger(): void { print("Je marche") }
    override fun respirer(): void { print("Je respire") }
}
```

## Énumérations

```okp
enum Couleur {
    ROUGE,
    VERT,
    BLEU
}

var c = Couleur.ROUGE
if c == Couleur.ROUGE {
    print("C'est rouge !")
}
```

## Gestion des erreurs

```okp
try {
    var x: int = 10 / 0
} catch (err) {
    print("Erreur : " + err)
} finally {
    print("Toujours exécuté")
}

// Lever une exception
fun diviser(a: int, b: int): float {
    if b == 0 { throw "Division par zéro !" }
    return a / b
}
```

## Modules natifs

```okp
inject Math
inject String
inject Time
inject IO

print(Math.sqrt(16))           // 4.0
print(Math.abs(-5))            // 5
print(Math.floor(3.7))         // 3
print(Math.pow(2, 10))         // 1024.0

print(String.upper("hello"))   // HELLO
print(String.lower("MONDE"))   // monde
print(String.length("okp"))    // 3
print(String.contains("oktopios", "okto"))  // true

print(Time.date())             // 2025-xx-xx xx:xx:xx

// Alias
inject Math as math
print(math.sin(0))    // 0.0
```

## Importation de fichiers

```okp
// Dans helpers.okp :
//   fun aide() { print("Je suis un helper") }

import "helpers.okp"
aide()

// Importation avec alias
import "helpers.okp" as h
h.aide()
```

## f-strings

```okp
var nom = "Oktopios"
var version = 1
print(f"Bienvenue dans {nom} v{version} !")
```

## Modificateurs d'accès

```okp
class Compte {
    private var solde: float
    public var proprietaire: string

    fun __construct(nom: string, montant: float) {
        this.proprietaire = nom
        this.solde = montant
    }

    public fun getSolde(): float {
        return this.solde
    }
}
```
