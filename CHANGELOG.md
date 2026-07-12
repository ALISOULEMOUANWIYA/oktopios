# Changelog

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