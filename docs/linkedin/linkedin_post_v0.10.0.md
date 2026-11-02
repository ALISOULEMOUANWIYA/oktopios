# Post LinkedIn — Oktopios v0.10.0

Image : `docs/media/linkedin_v0.10.0.png`

---

🇫🇷

🐙 **Oktopios v0.10.0 est là — nouveau namespace `Text` !**

Le langage de programmation bio-inspiré **Oktopios** gagne une boîte à outils complète pour manipuler du texte, sans aucune dépendance externe.

✨ 17 fonctions natives :
→ `Text.slugify` — URLs propres, accents gérés (« Élève à l'école » → `eleve-a-l-ecole`)
→ `Text.camel` / `pascal` / `snake` / `kebab` — conversions de casse intelligentes
→ `Text.levenshtein` / `similarity` — comparaison floue de chaînes
→ `Text.closest` — suggestions « vouliez-vous dire ? »
→ `Text.mask`, `wrap`, `initials`, `isPalindrome`, `wordCount`…

```okp
inject Text
print(Text.closest("pritn", ["print", "input"]))   // print
print(Text.mask("4970123412341234", 4))            // ************1234
```

📦 `pip install -U oktopios`
🔗 https://github.com/ALISOULEMOUANWIYA/oktopios

---

🇬🇧

🐙 **Oktopios v0.10.0 is out — new `Text` namespace!**

The bio-inspired **Oktopios** programming language now ships a full string-processing toolkit, with zero external dependencies.

✨ 17 built-in functions:
→ `Text.slugify` — clean URL slugs, accent-aware
→ `Text.camel` / `pascal` / `snake` / `kebab` — smart case conversion
→ `Text.levenshtein` / `similarity` — fuzzy string matching
→ `Text.closest` — "did you mean?" suggestions
→ `Text.mask`, `wrap`, `initials`, `isPalindrome`, `wordCount`…

📦 `pip install -U oktopios`
🔗 https://pypi.org/project/oktopios

#OpenSource #Oktopios #Python #ProgrammingLanguage #IA
