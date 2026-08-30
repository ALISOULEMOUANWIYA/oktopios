# Changelog

## [0.2.6] — Compatibilité élargie (Python 3.8+, Termux/Android)

### Changé

- **`requires-python` abaissé de `>=3.10` à `>=3.8`** — le cœur d'Oktopios
  n'utilise aucune fonctionnalité réservée à 3.9/3.10+. Oktopios s'installe
  désormais sur des Python plus anciens (utile sur Termux/Android et les
  environnements figés).
- **`psutil` déplacé des dépendances de base vers l'extra `[system]`.** C'était
  la seule dépendance de base à contenir une extension C (compilation requise,
  qui échouait souvent sur Termux). Le cœur est maintenant **100 % pur Python**
  (`colorama`, `tabulate`) et s'installe sans compilateur, partout.
  `System.uptime` / `System.memory_info` nécessitent `pip install oktopios[system]`
  (sinon ils renvoient `null`, comportement déjà géré). `[all]` inclut `[system]`.

### Ajouté

- Matrice CI étendue aux Python **3.8** et **3.9** (en plus de 3.10/3.11/3.12).
- Documentation Termux mise à jour (installation pure-Python + repli
  `--ignore-requires-python` pour les très anciens Python).

---

## [0.2.5] — Namespace `Fmt` — formatage humain de valeurs

### Ajouté

**Namespace `Fmt` — 9 fonctions de formatage (stdlib uniquement, aucune dépendance)**

Toutes les fonctions utilisent la bibliothèque standard Python —
aucun `pip install` supplémentaire n'est requis.

- `Fmt.number(n, decimals?, sep?)` — formate un nombre avec séparateur de milliers et décimales (`1234567.8` → `"1,234,567.80"`)
- `Fmt.percent(n, decimals?)` — formate en pourcentage (`0.753` → `"75.3 %"`)
- `Fmt.currency(n, symbol?, decimals?)` — formate en monnaie (`9.5` → `"$ 9.50"`, symbole configurable)
- `Fmt.bytes(n)` — taille en octets lisible (`1536000` → `"1.46 MB"`, supporte B/KB/MB/GB/TB/PB/EB)
- `Fmt.duration(seconds)` — durée en secondes lisible (`3665` → `"1h 1m 5s"`, inclut les jours)
- `Fmt.plural(n, singular, plural?)` — pluralisation naturelle (`Fmt.plural(3, "chat")` → `"3 chats"`)
- `Fmt.pad(s, width, char?, align?)` — alignement dans une largeur (l=gauche, r=droite, c=centré)
- `Fmt.truncate(s, width, suffix?)` — troncature avec suffixe (`"Bonjour le monde"` → `"Bonj…"`)
- `Fmt.ordinal(n)` — ordinal anglais (`3` → `"3rd"`, `11` → `"11th"`)

```okp
inject Fmt

// Nombres
print(Fmt.number(1234567.89))         // 1,234,567.89
print(Fmt.number(1234567, 0))         // 1,234,567
print(Fmt.number(9999.5, 2, " "))     // 9 999.50  (espace comme séparateur)

// Pourcentages et monnaies
print(Fmt.percent(0.753))             // 75.3 %
print(Fmt.percent(0.0045, 2))         // 0.45 %
print(Fmt.currency(1234.5))           // $ 1,234.50
print(Fmt.currency(50, "€", 2))       // € 50.00

// Tailles et durées
print(Fmt.bytes(1024))                // 1.00 KB
print(Fmt.bytes(1536000))             // 1.46 MB
print(Fmt.bytes(2147483648))          // 2.00 GB
print(Fmt.duration(45))               // 45s
print(Fmt.duration(3665))             // 1h 1m 5s
print(Fmt.duration(90061))            // 1j 1h 1m 1s

// Pluralisation
print(Fmt.plural(1, "fichier"))       // 1 fichier
print(Fmt.plural(3, "fichier"))       // 3 fichiers
print(Fmt.plural(0, "erreur"))        // 0 erreurs
print(Fmt.plural(2, "cheval", "chevaux"))  // 2 chevaux

// Alignement et troncature
print(Fmt.pad("ok", 10))              // "ok        " (gauche par défaut)
print(Fmt.pad("ok", 10, " ", "r"))    // "        ok"
print(Fmt.pad("ok", 10, "-", "c"))    // "----ok----"
print(Fmt.truncate("Bonjour tout le monde", 10))  // "Bonjour t…"
print(Fmt.truncate("court", 10))      // "court"

// Ordinal (anglais)
print(Fmt.ordinal(1))   // 1st
print(Fmt.ordinal(2))   // 2nd
print(Fmt.ordinal(3))   // 3rd
print(Fmt.ordinal(11))  // 11th
print(Fmt.ordinal(21))  // 21st

// Exemple combiné : rapport de performance
var score = 0.876
var total = 1048576
var elapsed = 7384

print("Score : " + Fmt.percent(score))
print("Données traitées : " + Fmt.bytes(total))
print("Durée : " + Fmt.duration(elapsed))
print(Fmt.plural(42, "erreur") + " trouvée(s)")
```

### Corrigé

- Chaînes contenant un backslash non-échappement (typiquement un chemin
  Windows `"C:\Users\..."`) : le lexer plantait avec `UnicodeDecodeError`
  car `\U` était lu comme un début d'échappement unicode invalide. La chaîne
  est désormais conservée telle quelle en cas d'échappement invalide.

---

## [0.2.4] — Namespace `Table` — rendu de tableaux formatés en texte

### Ajouté

**Namespace `Table` — 8 fonctions de rendu tabulaire (utilise `tabulate`, déjà inclus)**

Le namespace `Table` permet d'afficher n'importe quelle donnée (liste de maps, liste
de listes) sous forme de tableau texte formaté, avec plus de 16 styles disponibles.
Il complète naturellement le namespace `Csv` : lisez avec `Csv.read`, affichez avec `Table`.

- `Table.render(data, style?, headers?)` — formate les données en chaîne de tableau (retourne `string`)
- `Table.print(data, style?, headers?)` — affiche directement le tableau dans le terminal
- `Table.styles()` — liste des styles disponibles : `plain`, `simple`, `grid`, `github`, `pipe`, `rst`, `html`, `tsv` …
- `Table.fromCsv(path, style?, delimiter?)` — lit un CSV et retourne la chaîne de tableau formatée
- `Table.column(data, key)` — extrait une colonne par son nom (string) ou son index (int)
- `Table.rowCount(data)` — nombre de lignes de données
- `Table.colCount(data)` — nombre de colonnes (détecté depuis la première ligne)
- `Table.transpose(data)` — transpose lignes ↔ colonnes (liste de listes)

**Styles disponibles** : `plain`, `simple` (défaut), `github`, `grid`, `simple_grid`,
`rounded_grid`, `heavy_grid`, `pipe`, `orgtbl`, `presto`, `pretty`, `psql`,
`rst`, `mediawiki`, `html`, `tsv`.

```okp
inject Table
inject Csv

// Depuis une liste de maps (les clés deviennent les en-têtes)
var lignes = Csv.read("ventes.csv")
Table.print(lignes)
// ┌────────────┬───────────┬────────┐  (style "simple" par défaut)
// produit       quantite    prix
// -----------  ----------  ------
// Pomme         120         1.5
// Banane        85          0.9

// Choisir un style
var texte = Table.render(lignes, "grid")
print(texte)

// Depuis une liste de listes
var matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
Table.print(matrix, "rounded_grid", ["A", "B", "C"])

// Lire un CSV et afficher directement
var vue = Table.fromCsv("rapport.csv", "github")
print(vue)

// Extraire une colonne
var prix = Table.column(lignes, "prix")
print(prix)   // [1.5, 0.9, ...]

// Statistiques rapides sur une colonne
inject Stats
print(Stats.mean(Table.column(lignes, "quantite")))

// Transposer une matrice
var t = Table.transpose([[1, 2], [3, 4], [5, 6]])
Table.print(t)

// Lister les styles disponibles
print(Table.styles())
```

---

## [0.2.3] — Namespace `Csv` — lecture et écriture CSV native

### Ajouté

**Namespace `Csv` — 7 fonctions de manipulation CSV (stdlib uniquement, aucune dépendance)**

Toutes les fonctions utilisent la bibliothèque standard Python (`csv`) —
aucun `pip install` supplémentaire n'est requis.

**Lecture**
- `Csv.read(path, delimiter?, has_header?)` — lit un fichier CSV ; retourne une liste de maps si `has_header=true` (défaut), sinon une liste de listes
- `Csv.head(path, n?, delimiter?)` — retourne les `n` premières lignes brutes (défaut : 5)
- `Csv.columns(path, delimiter?)` — retourne la liste des noms de colonnes (première ligne)
- `Csv.count(path, delimiter?, skip_header?)` — nombre de lignes de données (hors en-tête)

**Écriture**
- `Csv.write(path, data, delimiter?, header?)` — écrit une liste de maps ou de listes dans un fichier CSV

**Conversion en mémoire**
- `Csv.parse(text, delimiter?, has_header?)` — analyse une chaîne CSV, sans fichier
- `Csv.stringify(data, delimiter?, header?)` — convertit des données en chaîne CSV

```okp
inject Csv

// Lire un CSV avec en-têtes → liste de maps
var lignes = Csv.read("ventes.csv")
print(Csv.count("ventes.csv"))   // ex: 150

// Écrire un CSV
var data = [{nom: "Alice", score: 42}, {nom: "Bob", score: 37}]
Csv.write("resultats.csv", data)

// Convertir en texte sans fichier
var texte = Csv.stringify(data)
print(texte)
// nom,score
// Alice,42
// Bob,37
```

---

## [0.2.2] — Namespace `Path` — manipulation de chemins de fichiers

### Ajouté

**Namespace `Path` — 16 fonctions de manipulation de chemins (stdlib uniquement, aucune dépendance)**

Toutes les fonctions utilisent la bibliothèque standard Python (`os.path`) —
aucun `pip install` supplémentaire n'est requis.

**Composition et décomposition**
- `Path.join(a, b, ...)` — joint plusieurs parties en un chemin cross-platform
- `Path.dirname(p)` — répertoire parent (`"a/b/c.txt"` → `"a/b"`)
- `Path.basename(p)` — nom de fichier avec extension (`"a/b/c.txt"` → `"c.txt"`)
- `Path.stem(p)` — nom de fichier SANS extension (`"a/b/c.txt"` → `"c"`)
- `Path.ext(p)` — extension avec le point (`"a/b/c.txt"` → `".txt"`)
- `Path.split(p)` — liste `[répertoire, fichier]`
- `Path.splitExt(p)` — liste `[racine, extension]`

**Résolution et normalisation**
- `Path.abs(p)` — chemin absolu résolu depuis le répertoire courant
- `Path.normalize(p)` — normalise `..`, `.` et les séparateurs doubles
- `Path.expand(p)` — développe `~` et les variables d'environnement
- `Path.relpath(p, start?)` — chemin relatif de `p` depuis `start`

**Informations et tests**
- `Path.exists(p)` — vrai si le chemin existe (fichier ou dossier)
- `Path.isFile(p)` — vrai si c'est un fichier régulier
- `Path.isDir(p)` — vrai si c'est un répertoire
- `Path.isAbs(p)` — vrai si le chemin est absolu
- `Path.size(p)` — taille du fichier en octets (`-1` si introuvable)

**Navigation**
- `Path.cwd()` — répertoire de travail courant
- `Path.home()` — répertoire personnel de l'utilisateur (`~`)
- `Path.listdir(p?)` — liste les entrées d'un répertoire (défaut : `.`)

```okp
inject Path

var p = Path.join("projets", "oktopios", "main.okp")
print(p)              // projets/oktopios/main.okp  (ou \\ sur Windows)

print(Path.dirname(p))    // projets/oktopios
print(Path.basename(p))   // main.okp
print(Path.stem(p))       // main
print(Path.ext(p))        // .okp

var abs = Path.abs("config.json")
print(abs)            // chemin absolu complet

print(Path.exists("README.md"))   // true / false
print(Path.isFile("README.md"))   // true
print(Path.isDir("vm"))           // true

var entries = Path.listdir("vm")
print(entries)        // ["interpreter.py", "lexer.py", ...]

print(Path.home())    // /home/alice  (ou C:\Users\alice sur Windows)
print(Path.cwd())     // répertoire de travail courant

// Développement de ~ et variables d'environnement
print(Path.expand("~/projets"))          // /home/alice/projets
print(Path.expand("$HOME/projets"))      // /home/alice/projets
```

---

## [0.2.1] — Namespace `Stats` — statistiques descriptives natives

### Ajouté

**Namespace `Stats` — 20 fonctions de statistiques descriptives (stdlib uniquement, aucune dépendance)**

Toutes les fonctions utilisent la bibliothèque standard Python (`statistics`, `math`) —
aucun `pip install` supplémentaire n'est requis.

**Mesures de tendance centrale**
- `Stats.mean(lst)` — moyenne arithmétique
- `Stats.median(lst)` — médiane (valeur centrale)
- `Stats.modeOf(lst)` — valeur la plus fréquente (mode) — nommé `modeOf` car `mode` est un mot réservé du langage
- `Stats.geomean(lst)` — moyenne géométrique (valeurs > 0 requises)
- `Stats.harmean(lst)` — moyenne harmonique (valeurs > 0 requises)

**Mesures de dispersion**
- `Stats.variance(lst, pop?)` — variance échantillon (défaut) ou population (`pop=true`)
- `Stats.stddev(lst, pop?)` — écart-type échantillon (défaut) ou population
- `Stats.range(lst)` — étendue (max − min)
- `Stats.iqr(lst)` — écart interquartile (Q3 − Q1)
- `Stats.mad(lst)` — écart absolu médian (robuste aux valeurs aberrantes)

**Quantiles et centiles**
- `Stats.quartiles(lst)` — liste `[Q1, Q2, Q3]`
- `Stats.percentile(lst, p)` — p-ème centile (0–100), interpolation linéaire

**Normalisation et scores**
- `Stats.normalize(lst)` — normalisation min-max vers `[0, 1]`
- `Stats.zscore(lst)` — liste des z-scores (écarts centrés réduits)

**Relations entre deux séries**
- `Stats.covariance(a, b)` — covariance échantillon entre deux listes de même taille
- `Stats.correlation(a, b)` — coefficient de corrélation de Pearson (∈ `[−1, 1]`)

**Utilitaires**
- `Stats.sum(lst)`, `Stats.min(lst)`, `Stats.max(lst)`, `Stats.size(lst)` — agrégats de base (`size` au lieu de `count` qui est réservé)
- `Stats.describe(lst)` — résumé complet : `{ count, sum, min, max, range, mean, median, variance, stddev, q1, q3, iqr }`

```okp
inject Stats

var data = [4, 7, 13, 2, 1, 9, 3, 6, 8, 5]

print(Stats.mean(data))       // 5.8
print(Stats.median(data))     // 5.5
print(Stats.stddev(data))     // 3.458...
print(Stats.iqr(data))        // 5.5
print(Stats.percentile(data, 90))  // 9.1

var norm = Stats.normalize(data)
print(norm)   // [0.25, 0.5, 1.0, 0.083..., 0.0, 0.666..., 0.166..., 0.416..., 0.583..., 0.333...]

var zs = Stats.zscore(data)
print(zs)     // liste des z-scores centrés réduits

// Corrélation entre deux séries
var x = [1, 2, 3, 4, 5]
var y = [2, 4, 5, 4, 5]
print(Stats.correlation(x, y))  // ~0.9

// Résumé complet
var desc = Stats.describe(data)
print(desc.mean)    // 5.8
print(desc.stddev)  // 3.458...
print(desc.iqr)     // 5.5
```

---

## [0.2.0] — Namespace `Hash` — hachage cryptographique & encodage Base64

### Ajouté

**Namespace `Hash` — 10 fonctions de hachage et d'encodage (stdlib uniquement, aucune dépendance)**

Toutes les fonctions utilisent la bibliothèque standard Python (`hashlib`, `hmac`, `base64`) —
aucun `pip install` supplémentaire n'est requis.

- `Hash.md5(s)` — digest MD5 hexadécimal de la chaîne `s`
- `Hash.sha1(s)` — digest SHA-1 hexadécimal
- `Hash.sha256(s)` — digest SHA-256 hexadécimal (recommandé pour usage général)
- `Hash.sha512(s)` — digest SHA-512 hexadécimal
- `Hash.hmac(key, msg, algo?)` — HMAC signé avec `key`, algorithme configurable (défaut `"sha256"`)
- `Hash.b64encode(s)` — encodage Base64 standard (RFC 4648 §4)
- `Hash.b64decode(s)` — décodage Base64 standard
- `Hash.b64urlEncode(s)` — encodage Base64 URL-safe (RFC 4648 §5, idéal pour JWT et URLs)
- `Hash.b64urlDecode(s)` — décodage Base64 URL-safe (gère le padding automatiquement)
- `Hash.compare(h1, h2)` — comparaison en temps constant (résistante aux attaques temporelles)

```okp
// Hachage de mot de passe (salt à gérer côté application)
var pwd = "s3cr3t"
print(Hash.sha256(pwd))
// → "secret" hashed : e.g. 2bb80d537b1da3e38bd30361aa855686bde0eacd7162fef6a25fe97bf527a25b

// HMAC pour signature d'API
var sig = Hash.hmac("my-key", "payload-data")
print(sig)  // → signature hexadécimale HMAC-SHA256

// Encodage Base64 — transmission de données binaires
var encoded = Hash.b64encode("Bonjour Oktopios !")
print(encoded)            // Qm9uam91ciBPa3RvcGlvcyAh
print(Hash.b64decode(encoded))  // Bonjour Oktopios !

// URL-safe Base64 pour tokens JWT
var token = Hash.b64urlEncode("user:42:admin")
print(token)              // dXNlcjo0MjphZG1pbg==
print(Hash.b64urlDecode(token))  // user:42:admin

// Comparaison sécurisée de hachages (anti timing-attack)
var h1 = Hash.sha256("secret")
var h2 = Hash.sha256("secret")
print(Hash.compare(h1, h2))  // true
```

---

## [0.1.9] — Namespaces `Queue` & `Stack` — structures de données natives

### Ajouté

**Namespace `Queue` — file d'attente FIFO (10 fonctions)**

Représentation interne : `OktopiosMap { "_t": "Q", "_d": [items] }`.
La Queue est **mutable** : `enqueue` et `dequeue` modifient l'objet en place.

- `Queue.create(liste?)` — crée une file vide ou depuis une liste existante
- `Queue.fromList(liste)` — alias explicite pour la conversion depuis une liste
- `Queue.enqueue(q, val)` — ajoute `val` en fin de file (O(1) amorti)
- `Queue.dequeue(q)` — retire et retourne l'élément de tête (FIFO) ; erreur si vide
- `Queue.peek(q)` — retourne l'élément de tête **sans le retirer** ; erreur si vide
- `Queue.size(q)` — nombre d'éléments dans la file
- `Queue.isEmpty(q)` — retourne `true` si la file est vide
- `Queue.contains(q, val)` — retourne `true` si `val` est dans la file
- `Queue.toList(q)` — convertit la file en liste Oktopios (tête en premier)
- `Queue.clear(q)` — vide la file

**Namespace `Stack` — pile LIFO (10 fonctions)**

Représentation interne : `OktopiosMap { "_t": "S", "_d": [items] }`.
La Stack est **mutable** : `push` et `pop` modifient l'objet en place. Le sommet correspond au dernier élément de la liste interne.

- `Stack.create(liste?)` — crée une pile vide ou depuis une liste existante
- `Stack.fromList(liste)` — alias explicite pour la conversion depuis une liste
- `Stack.push(s, val)` — empile `val` au sommet (O(1))
- `Stack.pop(s)` — dépile et retourne l'élément du sommet (LIFO) ; erreur si vide
- `Stack.peek(s)` — retourne l'élément du sommet **sans le retirer** ; erreur si vide
- `Stack.size(s)` — nombre d'éléments dans la pile
- `Stack.isEmpty(s)` — retourne `true` si la pile est vide
- `Stack.contains(s, val)` — retourne `true` si `val` est dans la pile
- `Stack.toList(s)` — convertit la pile en liste Oktopios (sommet en premier)
- `Stack.clear(s)` — vide la pile

```okp
// Queue — traitement en file
var q = Queue.create()
Queue.enqueue(q, "Alice")
Queue.enqueue(q, "Bob")
Queue.enqueue(q, "Charlie")
print(Queue.peek(q))        // Alice
print(Queue.dequeue(q))     // Alice
print(Queue.size(q))        // 2
print(Queue.toList(q))      // [Bob, Charlie]

// Stack — pile d'appels / undo-redo
var s = Stack.create([1, 2, 3])
Stack.push(s, 99)
print(Stack.peek(s))        // 99
print(Stack.pop(s))         // 99
print(Stack.toList(s))      // [3, 2, 1]  (sommet en premier)
print(Stack.contains(s, 2)) // true
```

---

## [0.1.8] — Namespace `Set` — ensembles mathématiques natifs

### Ajouté

**Namespace `Set` — 15 fonctions pour les ensembles (valeurs uniques, non ordonnées)**

Représentation interne : `OktopiosMap { élément -> true }` — toutes les opérations
sont **pures** (immutables) et retournent un nouveau Set sans modifier l'original.

- `Set.create(liste?)` — crée un ensemble vide ou depuis une liste (les doublons sont ignorés)
- `Set.fromList(liste)` — alias explicite de `create` pour la conversion depuis une liste
- `Set.has(s, x)` — retourne `true` si `x` est dans l'ensemble (`O(1)`)
- `Set.size(s)` — nombre d'éléments dans l'ensemble
- `Set.isEmpty(s)` — retourne `true` si l'ensemble est vide
- `Set.toList(s)` — convertit le Set en liste Oktopios
- `Set.add(s, x)` — retourne un nouveau Set avec `x` ajouté
- `Set.remove(s, x)` — retourne un nouveau Set sans `x`
- `Set.clear(s)` — retourne un Set vide
- `Set.union(a, b)` — union : tous les éléments de `a` ou `b`
- `Set.intersect(a, b)` — intersection : éléments présents dans `a` **et** `b`
- `Set.diff(a, b)` — différence : éléments de `a` qui ne sont pas dans `b`
- `Set.symDiff(a, b)` — différence symétrique : éléments exclusifs à `a` ou `b`
- `Set.isSubset(a, b)` — retourne `true` si `a ⊆ b`
- `Set.isSuperset(a, b)` — retourne `true` si `a ⊇ b`
- `Set.isDisjoint(a, b)` — retourne `true` si `a` et `b` n'ont aucun élément en commun
- `Set.equals(a, b)` — retourne `true` si les deux ensembles contiennent les mêmes éléments

```okp
var a = Set.create([1, 2, 3, 2, 1])   // {1, 2, 3} — doublons éliminés
var b = Set.create([2, 3, 4])
print(Set.size(a))                     // 3
print(Set.has(a, 2))                   // true
print(Set.union(a, b))                 // {1, 2, 3, 4}
print(Set.intersect(a, b))             // {2, 3}
print(Set.diff(a, b))                  // {1}
print(Set.symDiff(a, b))               // {1, 4}
print(Set.isSubset(Set.create([2, 3]), a))  // true
var c = Set.add(a, 99)
print(Set.toList(c))                   // [1, 2, 3, 99]
```

---

## [0.1.7] — Namespace `Http` — requêtes HTTP natives

### Ajouté

**Namespace `Http` — 10 fonctions pour interagir avec des APIs web**
- `Http.get(url, headers?, timeout?)` — requête GET ; retourne un map `{ status, ok, body, headers }`
- `Http.post(url, body?, headers?, json?, timeout?)` — requête POST (corps texte ou JSON)
- `Http.put(url, body?, headers?, json?, timeout?)` — requête PUT (corps texte ou JSON)
- `Http.patch(url, body?, headers?, json?, timeout?)` — requête PATCH (corps texte ou JSON)
- `Http.delete(url, headers?, timeout?)` — requête DELETE
- `Http.status(response)` — code HTTP entier extrait de la réponse (ex. `200`, `404`)
- `Http.ok(response)` — booléen, `true` si le statut est entre 200 et 299
- `Http.body(response)` — corps de la réponse sous forme de chaîne brute
- `Http.json(response)` — désérialise le corps comme JSON (retourne une valeur Oktopios)
- `Http.headers(response)` — en-têtes de la réponse sous forme d'un map Oktopios

Le namespace `Http` est complémentaire à `Json` : envoyez et recevez du JSON via HTTP
en combinant les deux namespaces. Nécessite `pip install requests` (ou `pip install oktopios[ia]`).

```okp
var resp = Http.get("https://api.github.com/repos/ALISOULEMOUANWIYA/oktopios")
print(Http.status(resp))                         // 200
var data = Http.json(resp)
print(Json.get(data, "stargazers_count", 0))     // nombre d'étoiles
```

---

## [0.1.6] — Namespace `Json` — manipulation JSON en mémoire

### Ajouté

**Namespace `Json` — 12 fonctions de manipulation JSON**
- `Json.parse(s)` — désérialise une chaîne JSON en valeur Oktopios (map, liste, primitif)
- `Json.stringify(v)` — sérialise une valeur Oktopios en chaîne JSON compacte
- `Json.pretty(v)` — sérialise avec indentation 2 espaces (pretty-print)
- `Json.get(obj, path, default?)` — lit une valeur à un chemin pointé `"a.b.c"` dans un objet imbriqué
- `Json.set(obj, path, val)` — retourne un nouvel objet avec la valeur modifiée au chemin donné
- `Json.has(obj, path)` — vérifie si le chemin `"a.b.c"` existe dans l'objet
- `Json.merge(a, b)` — merge profond de deux objets JSON (b écrase a en cas de conflit)
- `Json.fromFile(path)` — charge un fichier JSON et le retourne comme valeur Oktopios
- `Json.toFile(path, v, indent?)` — écrit une valeur Oktopios dans un fichier JSON (indentation 2 par défaut)
- `Json.isValid(s)` — retourne `true` si la chaîne est du JSON valide, `false` sinon
- `Json.keys(obj)` — retourne les clés de premier niveau d'un objet JSON

Le namespace `Json` est complémentaire à `DataImport` : là où `DataImport` lit/écrit des
fichiers entiers, `Json` manipule des valeurs JSON en mémoire (parse, chemin pointé, merge profond).

---

## [0.1.5] — Namespace `Date` — arithmétique et manipulation de dates

### Ajouté

**Namespace `Date` — 16 fonctions de manipulation de dates**
- `Date.parse(s, fmt?)` — parse une chaîne de date avec le format donné (défaut `%Y-%m-%d`), retourne ISO `YYYY-MM-DD`
- `Date.format(d, fmt?)` — formate une date vers un format arbitraire (défaut `DD/MM/YYYY`)
- `Date.add(d, n, unit?)` — ajoute `n` unités à une date ; unités : `"days"`, `"weeks"`, `"months"`, `"years"`
- `Date.diff(d1, d2, unit?)` — différence entre deux dates dans l'unité voulue (`"days"` par défaut, aussi `"weeks"`, `"hours"`, `"minutes"`, `"seconds"`)
- `Date.compare(d1, d2)` — retourne `-1`, `0` ou `1` selon que `d1` est avant, égal ou après `d2`
- `Date.isBefore(d1, d2)` — retourne `true` si `d1` est strictement avant `d2`
- `Date.isAfter(d1, d2)` — retourne `true` si `d1` est strictement après `d2`
- `Date.isEqual(d1, d2)` — retourne `true` si les deux dates sont identiques
- `Date.weekday(d)` — retourne l'indice du jour de la semaine (`0` = Lundi, `6` = Dimanche)
- `Date.weekdayName(d, lang?)` — retourne le nom du jour en anglais (par défaut) ou en français (`"fr"`)
- `Date.isLeapYear(year)` — retourne `true` si l'année est bissextile
- `Date.daysInMonth(year, month)` — retourne le nombre de jours dans un mois donné
- `Date.toTimestamp(d)` — convertit une date en timestamp Unix (entier)
- `Date.fromTimestamp(ts)` — convertit un timestamp Unix en date ISO `YYYY-MM-DD`

Tous les formats courants sont acceptés en entrée : `YYYY-MM-DD`, `DD/MM/YYYY`, `MM/DD/YYYY`, `DD-MM-YYYY`, `YYYYMMDD`, etc.

---

## [0.1.4] — Namespace `Regex` — expressions régulières natives

### Ajouté

**Namespace `Regex` — 10 fonctions d'expressions régulières**
- `Regex.test(pattern, s)` — test booléen : le pattern correspond-il quelque part dans `s` ?
- `Regex.match(pattern, s)` — test booléen de correspondance complète (fullmatch)
- `Regex.search(pattern, s)` — retourne la première correspondance (chaîne) ou `null`
- `Regex.findAll(pattern, s)` — retourne toutes les correspondances sous forme de liste
- `Regex.replace(pattern, repl, s)` — remplace toutes les correspondances par `repl`
- `Regex.replaceN(pattern, repl, s, n)` — remplace exactement `n` occurrences (0 = toutes)
- `Regex.split(pattern, s)` — découpe `s` selon le pattern, retourne une liste
- `Regex.groups(pattern, s)` — liste ordonnée des groupes de capture de la première correspondance
- `Regex.namedGroups(pattern, s)` — map des groupes nommés `(?P<nom>...)` de la première correspondance
- `Regex.count(pattern, s)` — nombre total de correspondances dans `s`
- `Regex.escape(s)` — échappe les caractères spéciaux pour usage sécurisé dans un pattern

---


## [0.1.3] — Namespace `Map` & correction doublon IAModule

### Ajouté

**Namespace `Map` — utilitaires fonctionnels sur les maps**
- `Map.keys(m)`, `Map.values(m)`, `Map.entries(m)` — accès aux clés, valeurs et paires
- `Map.size(m)`, `Map.isEmpty(m)`, `Map.has(m, key)` — introspection
- `Map.get(m, key, default?)` — lecture sécurisée avec valeur par défaut optionnelle
- `Map.set(m, key, val)`, `Map.remove(m, key)` — modifications sans mutation (retournent une nouvelle map)
- `Map.merge(a, b)` — fusion de deux maps (b écrase a en cas de conflit)
- `Map.pick(m, keys)`, `Map.omit(m, keys)` — extraction / exclusion de sous-ensembles de clés
- `Map.fromList(lst)` — conversion d'une liste de paires `[clé, valeur]` en map
- `Map.toList(m)` — conversion inverse en liste de paires
- `Map.findKey(m, val)` — recherche de la première clé ayant une valeur donnée
- `Map.invert(m)` — inversion clés↔valeurs

### Corrigé

- **Doublon IAModule** dans `native_funcs.py` : des lignes de code orphelines étaient
  présentes après la fermeture du dictionnaire `NativeFuncs`, causant une `SyntaxError`
  au chargement du module. Supprimées.

---

## [0.1.2] — Namespace `List` fonctionnel & types enrichis

### Ajouté

**Namespace `List` — utilitaires fonctionnels**
- `List.head(lst)`, `List.tail(lst)`, `List.last(lst)`, `List.init(lst)` — accès aux extrémités
- `List.take(lst, n)`, `List.drop(lst, n)`, `List.get(lst, i)` — extraction de sous-listes
- `List.flatten(lst)` — aplatissement récursif de listes imbriquées
- `List.unique(lst)` — suppression des doublons (ordre préservé)
- `List.zip(a, b)` — association de deux listes en liste de paires
- `List.unzip(lst)` — décompression d'une liste de paires en deux listes
- `List.chunk(lst, n)` — découpe en sous-listes de taille n
- `List.sorted(lst, rev?)` — copie triée (optionnellement inversée)
- `List.reversed(lst)` — copie inversée
- `List.concat(a, b)` — concaténation de deux listes
- `List.enumerate(lst)` — liste de paires `[index, valeur]`
- `List.rotate(lst, n)` — rotation circulaire de n positions
- `List.sum(lst)`, `List.product(lst)`, `List.max(lst)`, `List.min(lst)`, `List.avg(lst)` — agrégations
- `List.contains(lst, x)`, `List.indexOf(lst, x)`, `List.count(lst, x)` — recherche
- `List.intersect(a, b)`, `List.subtract(a, b)`, `List.union(a, b)` — opérations ensemblistes

**Namespace `Type` enrichi**
- `Type.type(x)` — retourne désormais le nom de type Oktopios (`int`, `float`, `bool`, `string`, `list`, `map`, `null`) au lieu du nom Python interne
- `Type.isInt(x)`, `Type.isFloat(x)`, `Type.isBool(x)`, `Type.isString(x)` — prédicats de type
- `Type.isList(x)`, `Type.isMap(x)`, `Type.isNull(x)`, `Type.isNum(x)` — prédicats de type

---

## [0.1.1] — Bibliothèque standard enrichie & corrections de ressources

### Ajouté

**Constantes et fonctions Math**
- `Math.pi`, `Math.e`, `Math.tau`, `Math.inf` — constantes mathématiques natives
- `Math.sum(liste)`, `Math.avg(liste)` — somme et moyenne d'une liste
- `Math.sign(x)` — signe d'un nombre (-1, 0, 1)
- `Math.clamp(x, lo, hi)` — clamp d'une valeur entre deux bornes
- `Math.gcd(a, b)`, `Math.lcm(a, b)` — PGCD et PPCM
- `Math.hypot(x, y)`, `Math.atan2(y, x)` — géométrie vectorielle
- `Math.log2(x)` — logarithme base 2
- `Math.isnan(x)`, `Math.isinf(x)` — tests de valeurs spéciales

**Fonctions String**
- `String.lstrip(s)`, `String.rstrip(s)` — suppression d'espaces ciblée
- `String.title(s)` — mise en titre (première lettre de chaque mot)
- `String.count(s, sub)` — nombre d'occurrences d'une sous-chaîne
- `String.repeat(s, n)` — répétition de chaîne
- `String.padStart(s, width, char)` / `String.padEnd(s, width, char)` — alignement/rembourrage
- `String.indexOf(s, sub)`, `String.lastIndexOf(s, sub)` — recherche de position
- `String.replaceAll(s, a, b)` — alias de replace pour clarté
- `String.isAlpha(s)`, `String.isDigit(s)`, `String.isAlNum(s)` — tests de type
- `String.join(sep, liste)` — jonction d'une liste en chaîne
- `String.format(template, ...)` — formatage de chaîne à la Python

**Fonctions Random**
- `Random.choice(liste)` — élément aléatoire dans une liste
- `Random.shuffle(liste)` — liste mélangée (non destructif)
- `Random.sample(liste, k)` — échantillon sans remise
- `Random.seed(n)` — graine pour reproductibilité
- `Random.uuid()` — identifiant unique aléatoire

**Fonctions Time**
- `Time.now()` — alias de `time()` pour plus de clarté
- `Time.today()` — date du jour au format `YYYY-MM-DD`
- `Time.strftime(fmt)` — format de date personnalisé
- `Time.year()`, `Time.month()`, `Time.day()` — composantes de date
- `Time.hour()`, `Time.minute()`, `Time.second()` — composantes d'heure

**Fonctions File**
- `File.basename(path)`, `File.dirname(path)` — navigation dans les chemins
- `File.extension(path)` — extension du fichier
- `File.abspath(path)` — chemin absolu
- `File.join(*parts)` — construction de chemin cross-platform

### Corrigé

- **Fuite de descripteurs de fichiers** (`File.read`, `File.write`, `File.append`,
  `File.readlines`, `File.hashfile`) : les fichiers n'étaient pas fermés après
  usage. Remplacés par des fonctions helpers utilisant `with ... as f:`.
  `File.hashfile` lit désormais les gros fichiers par blocs de 64 Ko.

---

## [0.1.0] — Architecture bio-inspirée, multi-agents et moteur adaptatif

Première version qui sort du rythme `0.0.x` : trop de fonctionnalités neuves
et de corrections de fond pour rester un simple patch.

### ⚠️ Changements cassants

- **6 nouveaux mots réservés** : `null`, `count`, `rows`, `cols`, `amplitude`,
  `parallel`. Si un script existant utilisait un de ces noms comme variable
  ou fonction, il ne compile plus. Vérifiez vos anciens `.okp` avant de
  mettre à jour :
  ```bash
  grep -lE '\b(null|count|rows|cols|amplitude|parallel)\b' votre_script.okp
  ```
- Les déclarations typées sans valeur ont désormais une valeur par défaut
  au lieu de `null` partout : `0` (int), `false` (bool), `0.0` (float),
  `[]` (tableaux), `{}` (dict). Si du code s'appuyait sur l'ancien
  comportement (`null` systématique), son comportement change.

### Ajouté

**Mémoire associative (`neuron_loop` / `__matches_db__`)**
- Déclaration `neuron_loop NomDB { ... }` (catégories alpha/beta/gamma/ohm/dzêta)
- `__matches_db__` avec 5 verbes : `select` (défaut), `insert`/`autocreate`,
  `update ... set {...}`, `delete`, `reflexion`
- Seuil de déclenchement (`threshold`), propagation synaptique entre neurones
  liés (`target:`), limites de capacité (7 divisions × 8 sous-divisions ×
  7000 éléments), verrou par base (bases différentes = vraiment parallèles)
- Persistance disque : `MatchesDB.save`/`load`

**Architecture multi-agents**
- `heart{}` (isolé par cœur) / `core{}` (noyau partagé, parent des hearts)
- `director{}` / `supervisor{}` / `agent{}` / `secretary{}` +
  `MultiAgent.run(tache)` (descente director→supervisor→agent→secretary,
  montée jusqu'au rapport final)
- `Tentacle.create()` (création dynamique), `intention`/`tentRandom`
  (dispatch), `Scheduler.run`/`runConcurrent` (vrais threads, verrous fins)
- `Monitor.snapshot`/`log`/`history` (observabilité)

**Moteur adaptatif**
- `AdaptiveEngine.run(situation, options)` : IAModule → analyse → décision
  → action (`agir()` dans `core{}`/`director{}`) → feedback → apprentissage
  (mémorisé dans un `neuron_loop` dédié, rappelable via `.recall()`)
- `IAModule.ollama/deepseek/starcoder` — DeepSeek et StarCoder routent vers
  Ollama local par défaut (gratuit, sans clé) ; `IAModule.callWithFallback`
  (cascade de secours) ; `IAModule.ollamaStream` (streaming avec callback)

**Connecteurs de données**
- `DataImport` : lecture/écriture json/excel/sql(sqlite)/mysql
- `Recognize` : empreintes faciale (histogramme) et vocale (MFCC), hors-ligne

**Boucles spéciales**
- `spiral` (parcours hélicoïdal, `from center/top_left`, sens horaire/anti-horaire)
- `wave` (zig-zag par ligne/colonne `by row`/`by column`, ou `amplitude N` sur liste plate)
- `sectors` (découpage `count N`, ou matriciel `rows N cols N`, option `parallel`)
- `circularLoop`/`sortLoop`/`filterLoop`/`permuteLoop`/`filterWhile` testés et 2 bugs corrigés

**Langage**
- Littéral `null`
- Déclarations multiples : `var x, y, a : int = 1, 2, 3` et `var x = 1, y = 2`
- 