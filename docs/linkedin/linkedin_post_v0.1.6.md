# Post LinkedIn — Oktopios v0.1.6

## 🇫🇷 Français

🐙 **Oktopios v0.1.6 est là — le namespace `Json` arrive !**

Nouvelle version pour Oktopios, le langage de programmation bio-inspiré expérimental écrit en Python.

Cette semaine, j'ai ajouté le namespace **`Json`** : 11 fonctions pour manipuler du JSON directement en mémoire, sans passer par des fichiers.

**Ce que vous pouvez faire :**

```okp
inject Json

var data = {"score": 99, "active": true}
var s    = Json.stringify(data)   // → chaîne JSON compacte
var obj  = Json.parse(s)          // → map Oktopios
Json.get(obj, "score")            // → 99
Json.has(obj, "active")           // → true
Json.set(obj, "score", 100)       // → nouvel objet immuable
Json.merge(a, b)                  // → deep merge
Json.isValid("[1,2,3]")           // → true
Json.fromFile("config.json")      // → charge un fichier
Json.toFile("out.json", obj)      // → écrit un fichier
```

Le namespace `Json` complète `DataImport` : là où `DataImport` lit/écrit des fichiers entiers, `Json` manipule des valeurs en mémoire avec des chemins pointés (`"a.b.c"`).

🔗 GitHub : https://github.com/ALISOULEMOUANWIYA/oktopios
📦 PyPI : `pip install oktopios==0.1.6`

---

## 🇬🇧 English

🐙 **Oktopios v0.1.6 — the `Json` namespace is here!**

New release for Oktopios, an experimental bio-inspired programming language interpreted in Python.

This week I added the **`Json`** namespace: 11 functions for in-memory JSON manipulation, no files needed.

**What you can do:**

```okp
inject Json

var data = {"score": 99, "active": true}
var s    = Json.stringify(data)   // → compact JSON string
var obj  = Json.parse(s)          // → Oktopios map
Json.get(obj, "score")            // → 99
Json.has(obj, "active")           // → true
Json.set(obj, "score", 100)       // → new immutable object
Json.merge(a, b)                  // → deep merge
Json.isValid("[1,2,3]")           // → true
Json.fromFile("config.json")      // → load from file
Json.toFile("out.json", obj)      // → write to file
```

The `Json` namespace complements `DataImport`: while `DataImport` reads/writes whole files, `Json` works on in-memory values with dot-path access (`"a.b.c"`).

🔗 GitHub: https://github.com/ALISOULEMOUANWIYA/oktopios
📦 PyPI: `pip install oktopios==0.1.6`

---

**Hashtags:**
#OpenSource #Oktopios #Python #ProgrammingLanguage #IA #Json #BioInspired #Programming #Dev #Innovation
