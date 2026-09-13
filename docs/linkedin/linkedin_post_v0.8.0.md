# Post LinkedIn — Oktopios v0.8.0

## Texte du post (bilingue FR/EN)

---

🐙 **Oktopios v0.8.0 est là — Namespace `Template` intégré !**

Nouvelle version du langage de programmation bio-inspiré **Oktopios** : le namespace `Template` est désormais natif, sans aucune dépendance externe.

Syntaxe intuitive inspirée de Mustache/Twig :
- `{{variable}}` pour substituer une valeur
- `{{variable|valeur_par_défaut}}` pour un repli automatique

**7 fonctions disponibles :**
→ `Template.render(tpl, vars)` — rendu en mémoire
→ `Template.partial(tpl, vars)` — rendu partiel multi-passes
→ `Template.fromFile(path, vars)` — charger un fichier gabarit
→ `Template.toFile(tpl, path, vars)` — écrire le résultat dans un fichier
→ `Template.fileToFile(tplPath, outPath, vars)` — pipeline fichier → fichier
→ `Template.vars(tpl)` — inspecter les variables d'un gabarit
→ `Template.strip(tpl)` / `Template.escape(s)` — utilitaires

**Exemple concret :**
```okp
inject Template
var html = "<h1>Bonjour {{prenom}} !</h1><p>Code : {{code|N/A}}</p>"
var out = Template.render(html, { prenom: "Alice", code: "OKTO-2026" })
File.write("email.html", out)
```

Aucun `pip install` supplémentaire : 100 % bibliothèque standard Python. Parfait pour générer des emails, des rapports, du HTML ou des fichiers de configuration directement depuis vos scripts `.okp`.

📦 `pip install --upgrade oktopios`
🔗 https://pypi.org/project/oktopios
💻 https://github.com/ALISOULEMOUANWIYA/oktopios

---

🐙 **Oktopios v0.8.0 is out — built-in `Template` namespace!**

New release of the bio-inspired **Oktopios** programming language: the `Template` namespace is now native, with zero external dependencies.

Intuitive Mustache/Twig-inspired syntax:
- `{{variable}}` to substitute a value
- `{{variable|default}}` for automatic fallback

**7 functions included:**
→ `Template.render(tpl, vars)` — render in memory
→ `Template.partial(tpl, vars)` — multi-pass partial rendering
→ `Template.fromFile(path, vars)` — load and render a template file
→ `Template.toFile(tpl, path, vars)` — write rendered output to a file
→ `Template.fileToFile(tplPath, outPath, vars)` — file-to-file pipeline
→ `Template.vars(tpl)` — inspect which variables a template uses
→ `Template.strip(tpl)` / `Template.escape(s)` — utilities

**Quick example:**
```okp
inject Template
var html = "<h1>Hello {{name}}!</h1><p>Code: {{code|N/A}}</p>"
var out = Template.render(html, { name: "Alice", code: "OKTO-2026" })
File.write("email.html", out)
```

No extra `pip install` needed: 100% Python standard library. Perfect for generating emails, reports, HTML, or config files directly from your `.okp` scripts.

📦 `pip install --upgrade oktopios`
🔗 https://pypi.org/project/oktopios
💻 https://github.com/ALISOULEMOUANWIYA/oktopios

---

#OpenSource #Oktopios #Python #ProgrammingLanguage #IA #BioInspired #Gabarit #Template #DevFR #Dev

---

## Instructions pour publier

1. Exécuter le script image :
   ```
   cd C:\Users\mouan\PycharmProjects\Oktopios\version.0.0.1
   python generate_linkedin_image.py
   ```
   → génère `linkedin_oktopios_v0.8.0.png`

2. Aller sur https://www.linkedin.com/in/ali-mouanwiya-b330941b7
3. Cliquer "Démarrer un post"
4. Copier-coller le texte ci-dessus
5. Joindre l'image `linkedin_oktopios_v0.8.0.png`
6. Publier !

## Commandes Git/PyPI (ou double-cliquer release_0.8.0.bat)

```bash
cd C:\Users\mouan\PycharmProjects\Oktopios\version.0.0.1
git pull origin main
git add -A
git commit -m "feat: namespace Template — gabarits de chaines natifs (v0.8.0)"
git push origin main
python -m build
python -m twine upload dist/*
```
