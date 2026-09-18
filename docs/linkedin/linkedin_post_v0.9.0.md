# Post LinkedIn — Oktopios v0.9.0

---

## 🇫🇷 Français

🐙 **Oktopios v0.9.0 est là — Namespace `Zip` natif !**

La nouvelle version d'Oktopios introduit le namespace **`Zip`** : créez, lisez et manipulez des archives ZIP directement depuis vos scripts `.okp`, sans aucune dépendance externe (stdlib Python uniquement).

**9 fonctions disponibles :**

```okp
inject Zip

// Créer une archive
Zip.create("rapport.zip", ["data.csv", "README.md"])

// Lire sans extraire
var contenu = Zip.read("rapport.zip", "README.md")

// Lister le contenu
print(Zip.list("rapport.zip"))

// Extraire tout
Zip.extract("rapport.zip", "sortie/")

// Ajouter / supprimer
Zip.add("rapport.zip", "nouveau.txt")
Zip.remove("rapport.zip", "ancien.txt")
```

✅ 149 tests passent — 0 dépendance ajoutée
📦 `pip install oktopios==0.9.0`
🔗 https://github.com/ALISOULEMOUANWIYA/oktopios

#OpenSource #Oktopios #Python #ProgrammingLanguage #IA

---

## 🇬🇧 English

🐙 **Oktopios v0.9.0 is out — Native `Zip` Namespace!**

The latest release of Oktopios brings the **`Zip`** namespace: create, read, and manage ZIP archives directly from your `.okp` scripts — no external dependencies, pure Python stdlib.

**9 built-in functions:**

```okp
inject Zip

// Create an archive
Zip.create("report.zip", ["data.csv", "README.md"])

// Read without extracting
var content = Zip.read("report.zip", "README.md")

// List contents
print(Zip.list("report.zip"))

// Extract everything
Zip.extract("report.zip", "output/")

// Add / remove entries
Zip.add("report.zip", "new_file.txt")
Zip.remove("report.zip", "old_file.txt")
```

✅ 149 tests passing — 0 new dependencies
📦 `pip install oktopios==0.9.0`
🔗 https://github.com/ALISOULEMOUANWIYA/oktopios

#OpenSource #Oktopios #Python #ProgrammingLanguage #IA

---

*Image jointe : `linkedin_v0.9.0.png` (1200×630 px)*
