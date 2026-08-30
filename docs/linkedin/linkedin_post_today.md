# LinkedIn post — Oktopios v0.2.4

---

🐙 **Oktopios v0.2.4 est disponible !** — Namespace `Table` : affichez vos données en tableaux formatés

Après le namespace `Csv` (v0.2.3), voici son complément naturel : **`Table`**, qui transforme n'importe quelle liste de maps ou de listes en un tableau texte lisible, avec **16 styles** au choix — et zéro nouvelle dépendance (tabulate est déjà inclus).

```okp
inject Table, Csv

var lignes = Csv.read("ventes.csv")
Table.print(lignes)

// produit      quantite    prix
// ----------  ----------  ------
// Pomme              120     1.5
// Banane              85     0.9

Table.print(lignes, "grid")   // bordures ASCII complètes
Table.print(lignes, "github") // format GitHub Markdown
Table.print(lignes, "html")   // rendu HTML
```

**8 fonctions disponibles :**
- `Table.render(data, style?, headers?)` — rendu en chaîne
- `Table.print(data, style?, headers?)` — affichage direct
- `Table.styles()` — liste les 16 styles disponibles
- `Table.fromCsv(path, style?, delimiter?)` — CSV → table en une ligne
- `Table.column(data, key)` — extrait une colonne par nom ou index
- `Table.rowCount(data)` / `Table.colCount(data)` — dimensions
- `Table.transpose(data)` — transpose lignes ↔ colonnes

Combiné à `Csv`, `Stats` et `List`, `Table` rend Oktopios encore plus puissant pour l'exploration de données en ligne de commande.

🔗 GitHub : https://github.com/ALISOULEMOUANWIYA/oktopios
📦 PyPI : https://pypi.org/project/oktopios

#OpenSource #Oktopios #Python #ProgrammingLanguage #IA

---

🐙 **Oktopios v0.2.4 is out!** — `Table` namespace: display your data as formatted tables

Following the `Csv` namespace (v0.2.3), here's its natural companion: **`Table`**, which turns any list of maps or lists into a readable text table with **16 built-in styles** — and zero new dependencies (tabulate is already bundled).

8 functions: `render`, `print`, `styles`, `fromCsv`, `column`, `rowCount`, `colCount`, `transpose`.

Combined with `Csv`, `Stats`, and `List`, the `Table` namespace makes Oktopios a capable tool for data exploration directly from the command line.

🔗 GitHub: https://github.com/ALISOULEMOUANWIYA/oktopios
📦 PyPI: https://pypi.org/project/oktopios

#OpenSource #Oktopios #Python #ProgrammingLanguage #IA
