# LinkedIn Post — Oktopios v0.1.7 🐙

> **Image à joindre :** `oktopios_v0.1.7_linkedin.png`

---

🐙 **Oktopios v0.1.7 — Namespace `Http` : le web dans votre langage !**
**Oktopios v0.1.7 — `Http` namespace: the web inside your language!**

---

🇫🇷 **Français**

Aujourd'hui, **Oktopios** fait un grand pas vers le monde réel : le nouveau namespace **`Http`** permet de communiquer avec n'importe quelle API web directement depuis vos scripts `.okp` 🌐

**10 fonctions natives :**
▸ `Http.get(url)` — requête GET
▸ `Http.post(url, json: data)` — requête POST avec corps JSON
▸ `Http.put` / `Http.patch` / `Http.delete`
▸ `Http.status(r)` — code HTTP (200, 404…)
▸ `Http.ok(r)` — booléen de succès
▸ `Http.body(r)` — corps brut
▸ `Http.json(r)` — désérialise le JSON en valeur Oktopios
▸ `Http.headers(r)` — en-têtes comme map

Et ça s'enchaîne parfaitement avec le namespace **`Json`** (v0.1.6) !

```okp
var r = Http.get("https://api.github.com/repos/ALISOULEMOUANWIYA/oktopios")
print(Http.status(r))                          // 200
var data = Http.json(r)
print(Json.get(data, "stargazers_count", 0))   // ⭐
```

Tous les **111 tests passent** ✅ — installez avec `pip install oktopios[ia]`

---

🇬🇧 **English**

**Oktopios v0.1.7** is out with the brand-new `Http` namespace — make HTTP requests natively from `.okp` scripts! GET, POST, PUT, PATCH, DELETE — responses come back as Oktopios maps with `status`, `ok`, `body`, `headers`. Pair it with the `Json` namespace and you have a full web-client built into the language.

👉 `pip install oktopios[ia]`
👉 GitHub: https://github.com/ALISOULEMOUANWIYA/oktopios
👉 PyPI: https://pypi.org/project/oktopios

---

#OpenSource #Oktopios #Python #ProgrammingLanguage #IA #HTTP #WebDev #BioInspired
