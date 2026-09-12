# Post LinkedIn — Oktopios v0.3.1 🐙

*Joindre l'image : `linkedin_v0.3.1_Log.png` (générer avec `python generate_linkedin_image.py`)*

---

## 🇫🇷 Français

🐙 **Oktopios v0.3.1 est disponible !**

Nouveau namespace : **`Log`** — journalisation structurée, colorée et horodatée, directement dans vos scripts Oktopios.

**12 fonctions, zéro dépendance externe :**

```
inject Log

Log.debug("Connexion à la base de données...")
Log.info("Serveur démarré sur le port 8080")
Log.warn("Mémoire disponible faible")
Log.error("Timeout lors de la requête HTTP")
Log.fatal("Corruption détectée !")

// Persistance dans un fichier
Log.configure(file = "app.log", level = "INFO")

// Format personnalisé
Log.configure(fmt = "{level} | {ts} | {msg}")
```

5 niveaux hiérarchiques (DEBUG → FATAL), colorisation ANSI automatique via colorama (déjà inclus), écriture dans un fichier sans codes ANSI, et format personnalisable.

🔗 GitHub : https://github.com/ALISOULEMOUANWIYA/oktopios
📦 PyPI : https://pypi.org/project/oktopios

```bash
pip install --upgrade oktopios
```

---

## 🇬🇧 English

🐙 **Oktopios v0.3.1 is out!**

New namespace: **`Log`** — structured, colorized, timestamped logging, right in your Oktopios scripts.

**12 functions, zero extra dependencies:**

```
inject Log

Log.debug("Connecting to database...")
Log.info("Server started on port 8080")
Log.warn("Low memory")
Log.error("HTTP request timeout")
Log.fatal("Data corruption detected!")

// Persist to file
Log.configure(file = "app.log", level = "INFO")
```

5 hierarchical levels (DEBUG → FATAL), automatic ANSI colorization via colorama (already bundled), clean file output without ANSI codes, and a fully customizable format string.

🔗 GitHub: https://github.com/ALISOULEMOUANWIYA/oktopios
📦 PyPI: https://pypi.org/project/oktopios

```bash
pip install --upgrade oktopios
```

---

**Hashtags :**
#OpenSource #Oktopios #Python #ProgrammingLanguage #IA #Programming #Developer #Bioinspired

---

*Pour publier : aller sur https://www.linkedin.com/in/ali-mouanwiya-b330941b7, cliquer "Démarrer une publication", coller le texte, joindre l'image linkedin_v0.3.1_Log.png.*
