# Post LinkedIn — Oktopios v0.1.5

## 🇫🇷 Français

🐙 **Oktopios v0.1.5 est disponible !**

Cette mise à jour apporte le namespace **`Date`** — 16 fonctions natives pour manipuler les dates directement dans le langage, sans importer de bibliothèque externe.

```okp
var naissance = "1990-07-15"
var age_jours = Date.diff(naissance, Time.today(), "days")
print("Vous avez vécu " + age_jours + " jours !")

var prochaine_reunion = Date.add(Time.today(), 14, "days")
print("Prochaine réunion : " + Date.format(prochaine_reunion, "%d %B %Y"))

print(Date.weekdayName("2025-12-25", "fr"))  // → "Jeudi"
print(Date.isLeapYear(2024))                  // → true
print(Date.daysInMonth(2024, 2))              // → 29
```

Toutes les fonctions : `parse`, `format`, `add`, `diff`, `compare`, `isBefore`, `isAfter`, `isEqual`, `weekday`, `weekdayName`, `isLeapYear`, `daysInMonth`, `toTimestamp`, `fromTimestamp`.

📦 `pip install oktopios==0.1.5`
🔗 https://github.com/ALISOULEMOUANWIYA/oktopios
🐍 https://pypi.org/project/oktopios

#OpenSource #Oktopios #Python #ProgrammingLanguage #IA

---

## 🇬🇧 English

🐙 **Oktopios v0.1.5 is out!**

This release brings the **`Date`** namespace — 16 built-in functions for date manipulation, no external library needed.

```okp
var birthday = "1990-07-15"
var age_days = Date.diff(birthday, Time.today(), "days")
print("You have lived " + age_days + " days!")

var next_meeting = Date.add(Time.today(), 14, "days")
print("Next meeting: " + Date.format(next_meeting, "%d %B %Y"))

print(Date.weekdayName("2025-12-25"))  // → "Thursday"
print(Date.isLeapYear(2024))            // → true
print(Date.daysInMonth(2024, 2))        // → 29
```

Full function list: `parse`, `format`, `add`, `diff`, `compare`, `isBefore`, `isAfter`, `isEqual`, `weekday`, `weekdayName`, `isLeapYear`, `daysInMonth`, `toTimestamp`, `fromTimestamp`.

📦 `pip install oktopios==0.1.5`
🔗 https://github.com/ALISOULEMOUANWIYA/oktopios
🐍 https://pypi.org/project/oktopios

#OpenSource #Oktopios #Python #ProgrammingLanguage #IA
