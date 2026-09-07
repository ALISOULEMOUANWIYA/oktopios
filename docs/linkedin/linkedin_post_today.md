# LinkedIn Post — Oktopios v0.3.0 — Namespace `Url`

## 🇫🇷 Français

🐙 **Oktopios v0.3.0 est disponible !**

Aujourd'hui, Oktopios s'enrichit du namespace **`Url`** — 13 fonctions pour manipuler les URLs directement depuis votre code `.okp`, sans aucune dépendance externe (100 % `urllib.parse`, stdlib Python).

**Ce que vous pouvez faire :**
• `Url.parse(url)` → décompose une URL en map de composantes
• `Url.build(parts)` → reconstruit une URL depuis ses parties
• `Url.join(base, url)` → résout une URL relative (RFC 3986)
• `Url.encode` / `Url.decode` → percent-encoding
• `Url.encodeQuery` / `Url.decodeQuery` → query strings ↔ maps
• `Url.scheme`, `Url.host`, `Url.port`, `Url.path`, `Url.query`, `Url.fragment` → accès direct aux composantes

```okp
inject Url

var p = Url.parse("https://api.example.com:8080/v1/search?q=okp&lang=fr")
print(p.host)      // api.example.com
print(p.port)      // 8080
print(p.path)      // /v1/search

var qs = Url.encodeQuery({ q: "oktopios", lang: "fr", page: 1 })
print(qs)          // q=oktopios&lang=fr&page=1

print(Url.join("https://example.com/a/b/", "../c"))  // https://example.com/a/c
```

Combiné avec `Http`, `Json` et `Regex`, Oktopios dispose maintenant d'une vraie boîte à outils pour travailler avec le Web — en quelques lignes, lisibles et expressives.

📦 Mise à jour : `pip install --upgrade oktopios`
🔗 GitHub : https://github.com/ALISOULEMOUANWIYA/oktopios
📚 PyPI : https://pypi.org/project/oktopios

#OpenSource #Oktopios #Python #ProgrammingLanguage #IA

---

## 🇬🇧 English

🐙 **Oktopios v0.3.0 is out!**

Today Oktopios gains the **`Url`** namespace — 13 functions to parse, build, encode and resolve URLs directly from your `.okp` code, with zero extra dependencies (pure `urllib.parse`, Python stdlib).

**What you can do:**
• `Url.parse(url)` → decompose a URL into a component map
• `Url.build(parts)` → reconstruct a URL from its parts
• `Url.join(base, url)` → resolve a relative URL (RFC 3986)
• `Url.encode` / `Url.decode` → percent-encoding
• `Url.encodeQuery` / `Url.decodeQuery` → query strings ↔ maps
• `Url.scheme`, `Url.host`, `Url.port`, `Url.path`, `Url.query`, `Url.fragment` → direct component access

```okp
inject Url

var p = Url.parse("https://api.example.com:8080/v1/search?q=okp&lang=fr")
print(p.host)      // api.example.com
print(p.port)      // 8080
print(p.path)      // /v1/search

var qs = Url.encodeQuery({ q: "oktopios", lang: "fr", page: 1 })
print(qs)          // q=oktopios&lang=fr&page=1

print(Url.join("https://example.com/a/b/", "../c"))  // https://example.com/a/c
```

Combined with `Http`, `Json`, and `Regex`, Oktopios now has a complete web toolkit — concise, readable, expressive.

📦 Update: `pip install --upgrade oktopios`
🔗 GitHub: https://github.com/ALISOULEMOUANWIYA/oktopios
📚 PyPI: https://pypi.org/project/oktopios

#OpenSource #Oktopios #Python #ProgrammingLanguage #IA

---

_Image: `docs/linkedin/linkedin_url_v030.png` (1200×630 px)_
