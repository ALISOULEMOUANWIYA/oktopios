# LinkedIn Post — Oktopios v0.2.2

## Texte du post (bilingue FR/EN)

---

🐙 **Oktopios v0.2.2 est sorti !** Nouveau namespace natif : `Path`

Avec cette version, Oktopios intègre un namespace complet pour manipuler les chemins de fichiers, sans aucune dépendance externe — stdlib Python uniquement.

**19 fonctions cross-platform :**

🔧 Composition & décomposition
```
Path.join("a", "b", "c.okp")  // "a/b/c.okp"
Path.dirname(p)    → répertoire parent
Path.basename(p)   → nom de fichier avec extension
Path.stem(p)       → nom sans extension
Path.ext(p)        → extension (ex: ".okp")
Path.split(p)      → [répertoire, fichier]
```

📍 Résolution & navigation
```
Path.abs(p)        → chemin absolu
Path.normalize(p)  → résout .., ., séparateurs doubles
Path.expand(p)     → développe ~ et $VARIABLES
Path.cwd()         → répertoire courant
Path.home()        → dossier utilisateur
Path.relpath(p)    → chemin relatif
```

✅ Tests & informations
```
Path.exists(p)     → fichier ou dossier existant ?
Path.isFile(p)     → fichier régulier ?
Path.isDir(p)      → répertoire ?
Path.isAbs(p)      → chemin absolu ?
Path.size(p)       → taille en octets
Path.listdir(p)    → liste du répertoire
```

Exemple complet :
```okp
inject Path

var p = Path.join("projets", "oktopios", "main.okp")
print(Path.stem(p))    // "main"
print(Path.ext(p))     // ".okp"
print(Path.exists(p))  // true / false
print(Path.home())     // /home/alice
```

Cette version consolide aussi les namespaces `Hash` (v0.2.0) et `Stats` (v0.2.1) publiés précédemment.

🔗 GitHub : https://github.com/ALISOULEMOUANWIYA/oktopios
📦 PyPI   : pip install oktopios==0.2.2

---

🐙 **Oktopios v0.2.2 is out!** New native namespace: `Path`

This release adds a complete file path manipulation namespace — no external dependencies, pure Python stdlib.

**19 cross-platform functions** covering path composition, resolution, testing, and navigation. Works identically on Linux, macOS, and Windows.

```okp
inject Path

var p = Path.join("projects", "oktopios", "main.okp")
print(Path.stem(p))     // "main"
print(Path.ext(p))      // ".okp"
print(Path.isFile(p))   // true / false
print(Path.listdir("vm"))  // ["interpreter.py", "lexer.py", ...]
print(Path.home())      // /home/alice (or C:\Users\alice on Windows)
```

This also bundles `Hash` (v0.2.0) and `Stats` (v0.2.1) from previous sessions.

🔗 GitHub: https://github.com/ALISOULEMOUANWIYA/oktopios
📦 PyPI:   pip install oktopios==0.2.2

#OpenSource #Oktopios #Python #ProgrammingLanguage #IA #BioInspired #Interpreter

---

## Image à joindre
`oktopios_v0.2.2_linkedin.png` (dans le même dossier)

## Instructions de publication
1. Aller sur https://www.linkedin.com/in/ali-mouanwiya-b330941b7
2. Cliquer "Démarrer un post"
3. Coller le texte ci-dessus (section FR+EN)
4. Joindre l'image `oktopios_v0.2.2_linkedin.png`
5. Publier
