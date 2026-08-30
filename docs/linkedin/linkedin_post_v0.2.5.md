# LinkedIn Post — Oktopios v0.2.5

---

🐙 **Oktopios v0.2.5 est disponible !**

Nouvelle version du langage bio-inspiré avec le namespace **`Fmt`** — formatage humain de valeurs, sans aucune dépendance externe.

9 fonctions disponibles dès maintenant :

```
Fmt.number(1234567.89)     → "1,234,567.89"
Fmt.percent(0.753)         → "75.3 %"
Fmt.currency(9.5, "€")     → "€ 9.50"
Fmt.bytes(1536000)         → "1.46 MB"
Fmt.duration(3665)         → "1h 1m 5s"
Fmt.plural(3, "chat")      → "3 chats"
Fmt.truncate(s, 10)        → "Bonjour t…"
Fmt.ordinal(11)            → "11th"
Fmt.pad("ok", 10, "-","c") → "----ok----"
```

Afficher des données de façon lisible n'a jamais été aussi simple dans Oktopios 🎯

---

🐙 **Oktopios v0.2.5 is out!**

New release of the bio-inspired language featuring the **`Fmt`** namespace — human-friendly value formatting, zero external dependencies.

9 functions available right now, covering numbers, percentages, currencies, file sizes, durations, pluralization, padding, truncation, and ordinals — all using Python's standard library only.

```okp
inject Fmt

print(Fmt.bytes(2147483648))   // 2.00 GB
print(Fmt.duration(90061))     // 1j 1h 1m 1s
print(Fmt.percent(0.0045, 2))  // 0.45 %
print(Fmt.plural(1, "error"))  // 1 error
```

🔗 GitHub: https://github.com/ALISOULEMOUANWIYA/oktopios
📦 PyPI: https://pypi.org/project/oktopios
Install: `pip install oktopios`

#OpenSource #Oktopios #Python #ProgrammingLanguage #IA #BioInspired #DevTools
