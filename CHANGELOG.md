# Changelog

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