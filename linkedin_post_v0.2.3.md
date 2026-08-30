# LinkedIn Post — Oktopios v0.2.3

---

🐙 **Oktopios v0.2.3 est disponible !**

Nouveau namespace natif : **`Csv`** — lecture, écriture et conversion CSV directement dans votre code Oktopios, sans aucune dépendance externe (stdlib Python uniquement).

**7 fonctions, zéro `pip install` :**

```okp
inject Csv

// Lire un fichier CSV avec en-têtes → liste de maps
var ventes = Csv.read("ventes.csv")
print(Csv.count("ventes.csv"))     // ex : 150 lignes

// Inspecter la structure
print(Csv.columns("ventes.csv"))   // ["produit", "quantite", "prix"]
print(Csv.head("ventes.csv", 3))   // premières 3 lignes brutes

// Écrire / convertir
Csv.write("sortie.csv", ventes)
var texte = Csv.stringify(ventes)
var data   = Csv.parse(texte)      // aller-retour sans fichier
```

✅ `Csv.read` / `Csv.write` — fichier ↔ données  
✅ `Csv.parse` / `Csv.stringify` — texte ↔ données (sans fichier)  
✅ `Csv.head` — aperçu rapide  
✅ `Csv.columns` — noms des colonnes  
✅ `Csv.count` — nombre de lignes de données  

Oktopios continue de s'enrichir de namespaces utiles, tous construits sur la bibliothèque standard Python. Après `Path`, `Stats`, `Hash`, `Set`, `Http`, `Regex`, `Date`, `Json`… voici `Csv` !

🔗 GitHub : https://github.com/ALISOULEMOUANWIYA/oktopios  
📦 PyPI : https://pypi.org/project/oktopios  

#OpenSource #Oktopios #Python #ProgrammingLanguage #IA #CSV #Dev

---

🐙 **Oktopios v0.2.3 is out!**

New built-in namespace: **`Csv`** — read, write and convert CSV data natively in Oktopios, with zero external dependencies (Python stdlib only).

**7 functions, zero `pip install`:**

- `Csv.read(path)` — file → list of maps (with headers) or list of lists  
- `Csv.write(path, data)` — data → CSV file  
- `Csv.parse(text)` — CSV string → data (no file needed)  
- `Csv.stringify(data)` — data → CSV string  
- `Csv.head(path, n)` — first N rows preview  
- `Csv.columns(path)` — column names from the header row  
- `Csv.count(path)` — number of data rows  

Every namespace in Oktopios is built on Python's standard library — no hidden dependencies, no surprises. CSV joins Path, Stats, Hash, Set, Http, Regex, Date, Json and more.

🔗 GitHub: https://github.com/ALISOULEMOUANWIYA/oktopios  
📦 PyPI: https://pypi.org/project/oktopios  

#OpenSource #Oktopios #Python #ProgrammingLanguage #IA #CSV #Dev
