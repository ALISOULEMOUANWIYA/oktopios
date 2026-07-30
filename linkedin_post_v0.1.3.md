# LinkedIn Post — Oktopios v0.1.3

## Texte du post (bilingue FR/EN)

---

🐙 **Oktopios v0.1.3 est disponible !**
_(Oktopios v0.1.3 is out!)_

Cette version apporte le **namespace `Map`** — 16 nouvelles fonctions natives pour manipuler les maps (dictionnaires) de façon fonctionnelle et immutable, directement dans le langage.
_(This release ships the `Map` namespace — 16 built-in functions for functional, immutable map operations, right inside the language.)_

```
Map.keys(m)          → liste des clés
Map.values(m)        → liste des valeurs
Map.entries(m)       → liste de paires [clé, valeur]
Map.has(m, "key")    → booléen
Map.get(m, "k", def) → lecture sécurisée
Map.set(m, k, v)     → nouvelle map avec k=v
Map.merge(a, b)      → fusion (b écrase a)
Map.pick(m, keys)    → sous-ensemble de clés
Map.omit(m, keys)    → exclusion de clés
Map.invert(m)        → inversion clés↔valeurs
Map.fromList(lst)    → [[k,v]...] → map
Map.toList(m)        → map → [[k,v]...]
Map.findKey(m, val)  → première clé par valeur
... et plus encore
```

Comme toujours : aucune mutation, chaque opération retourne une nouvelle map.
_(As always: no mutation — every operation returns a new map.)_

✅ 100 tests passent
✅ Python ≥ 3.10
✅ `pip install oktopios`

---

🔗 PyPI : https://pypi.org/project/oktopios
🔗 GitHub : https://github.com/ALISOULEMOUANWIYA/oktopios

#OpenSource #Oktopios #Python #ProgrammingLanguage #IA #BioInspired #FunctionalProgramming

---

## Image
`oktopios_v0.1.3_linkedin.png` (1200×630px) — présente dans le dossier du projet.

## Notes
- Le commit v0.1.3 a été créé localement (SHA: 6dde082).
- **Action requise** : supprimer les fichiers lock Windows (.git/ORIG_HEAD.lock, .git/index.lock, .git/objects/maintenance.lock) puis exécuter :
  ```
  git push origin main
  python -m build
  python -m twine upload dist/*
  ```
