# Post LinkedIn — Oktopios v0.2.0

---

🐙 **Oktopios v0.2.0 — Namespace `Hash` : hachage cryptographique & Base64 natifs !**

Nouvelle version majeure pour **Oktopios**, le langage de programmation bio-inspiré interprété en Python.

Ce cycle apporte le namespace **`Hash`** — 10 fonctions de hachage et d'encodage, **100 % bibliothèque standard Python** (hashlib, hmac, base64), sans aucune dépendance supplémentaire.

```okp
inject Hash

// Hachage sécurisé
var h = Hash.sha256("mon-secret")

// Signature HMAC pour API
var sig = Hash.hmac("ma-clé", "payload")

// Encodage Base64 standard
var enc = Hash.b64encode("Bonjour Oktopios !")
print(Hash.b64decode(enc))    // Bonjour Oktopios !

// Base64 URL-safe (parfait pour JWT / tokens)
var tok = Hash.b64urlEncode("user:42:admin")

// Comparaison en temps constant (anti timing-attack)
print(Hash.compare(h, h))    // true
```

**Fonctions disponibles :**
✅ `Hash.md5` / `sha1` / `sha256` / `sha512`
✅ `Hash.hmac(key, msg, algo?)` — HMAC signé
✅ `Hash.b64encode` / `b64decode`
✅ `Hash.b64urlEncode` / `b64urlDecode`
✅ `Hash.compare` — comparaison résistante aux attaques temporelles

La suite grandit : **Set, Queue, Stack, Json, Http, Date, Regex, Map, List**… et maintenant **Hash**. 🧬

👉 `pip install oktopios==0.2.0`
🔗 https://github.com/ALISOULEMOUANWIYA/oktopios
📦 https://pypi.org/project/oktopios

---

🌍 **Oktopios v0.2.0 — `Hash` namespace: native cryptographic hashing & Base64 !**

New milestone for **Oktopios**, the bio-inspired programming language interpreted in Python.

This release ships the **`Hash`** namespace — 10 hashing and encoding functions, **using only Python's standard library** (hashlib, hmac, base64), with zero extra dependencies.

```okp
inject Hash

var h   = Hash.sha256("my-secret")
var sig = Hash.hmac("api-key", "payload")
var enc = Hash.b64encode("Hello Oktopios!")
var tok = Hash.b64urlEncode("user:42:admin")
print(Hash.compare(h, h))    // true
```

The standard library keeps growing: **Set, Queue, Stack, Json, Http, Date, Regex, Map, List** — and now **Hash**. 🔐

👉 `pip install oktopios==0.2.0`
🔗 https://github.com/ALISOULEMOUANWIYA/oktopios
📦 https://pypi.org/project/oktopios

---

#OpenSource #Oktopios #Python #ProgrammingLanguage #IA #Crypto #Security #Programming #BioInspired
