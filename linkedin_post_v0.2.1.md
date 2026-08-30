# Post LinkedIn — Oktopios v0.2.1

## 🇫🇷 Français

🐙 **Oktopios v0.2.1 — Namespace `Stats` : statistiques descriptives natives !**

Je viens de publier une nouvelle version d'**Oktopios**, mon langage de programmation bio-inspiré et interprété en Python.

Cette version introduit le namespace **`Stats`** — 20 fonctions de statistiques descriptives qui utilisent uniquement la bibliothèque standard Python (zéro dépendance externe) :

📊 **Tendance centrale** — `mean`, `median`, `modeOf`, `geomean`, `harmean`
📉 **Dispersion** — `variance`, `stddev`, `range`, `iqr`, `mad`
🔢 **Quantiles** — `percentile`, `quartiles`, `normalize`, `zscore`
🔗 **Relations** — `covariance`, `correlation` (Pearson)
📋 **Résumé complet** — `describe` retourne count, mean, median, stddev, q1, q3, iqr en un seul appel

```okp
inject Stats

var data = [4, 7, 13, 2, 1, 9, 3, 6, 8, 5]
print(Stats.mean(data))           // 5.8
print(Stats.stddev(data))         // 3.458...
print(Stats.iqr(data))            // 5.5
print(Stats.percentile(data, 90)) // 9.1

// Corrélation entre deux séries
var x = [1, 2, 3, 4, 5]
var y = [2, 4, 5, 4, 5]
print(Stats.correlation(x, y))    // ~0.9

// Résumé complet
var d = Stats.describe(data)
print(d["mean"])    // 5.8
print(d["stddev"])  // 3.458...
```

👉 `pip install oktopios` pour essayer !

---

## 🇬🇧 English

🐙 **Oktopios v0.2.1 — `Stats` namespace: native descriptive statistics!**

Just released a new version of **Oktopios**, my bio-inspired programming language interpreted in Python.

This version introduces the **`Stats`** namespace — 20 descriptive statistics functions using only the Python standard library (zero external dependencies):

📊 **Central tendency** — `mean`, `median`, `modeOf`, `geomean`, `harmean`
📉 **Dispersion** — `variance`, `stddev`, `range`, `iqr`, `mad`
🔢 **Quantiles** — `percentile`, `quartiles`, `normalize`, `zscore`
🔗 **Relationships** — `covariance`, `correlation` (Pearson)
📋 **Full summary** — `describe` returns count, mean, median, stddev, q1, q3, iqr in one call

The Stats namespace complements the existing `Math`, `List`, and `DataImport` namespaces, making Oktopios a capable language for data analysis workflows.

👉 `pip install oktopios` to try it!
📦 PyPI: https://pypi.org/project/oktopios
⭐ GitHub: https://github.com/ALISOULEMOUANWIYA/oktopios

---

**Hashtags:**
#OpenSource #Oktopios #Python #ProgrammingLanguage #IA #Statistics #DataScience #BioInspired
