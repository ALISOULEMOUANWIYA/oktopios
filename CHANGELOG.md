# Changelog

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
- Valeurs par défaut selon le type pour les déclarations sans valeur

### Corrigé

- Constructeur sans paramètre jamais appelé (`new X()`)
- Héritage de constructeur cassé (classe enfant sans `__construct` perdait les arguments)
- Chaînage de méthodes (`a.b().c()`) qui plantait après le premier niveau
- Ambiguïté `None`/introuvable dans la résolution de variables/fonctions
- Bug d'encodage : tout accent dans une chaîne devenait illisible (`Attrapé` → `AttrapÃ©`)
- Paramètres de fonction à valeur par défaut bloqués par une vérification d'arité trop stricte
- `circularLoop` ré-itérait en plus après son `until` (return manquant)
- `step()`/`until()` s'écrasaient l'un l'autre dans le parser
- Suite `pytest` ne tournait pas du tout (bug d'import) → 100/100 tests passent désormais
- Sorties `print()` concurrentes qui s'entremêlaient (pas de verrou sur stdout)
- `IAModule.*` plantait en traceback Python brut si `requests` n'était pas installé

### Dépendances

Les nouvelles dépendances sont **optionnelles** (`pip install oktopios[all]`
pour tout avoir, ou `[data]`/`[recognition]`/`[ia]` séparément) — l'install
de base reste légère.
