# Post LinkedIn — Oktopios v0.11.0

🐙 Oktopios v0.11.0 — « Vouliez-vous dire… ? »

🇫🇷 Les fautes de frappe font partie de la vie d'un développeur. Avec cette version, Oktopios vous aide à les corriger au lieu de simplement vous dire que quelque chose est « inconnu ».

Quand un nom est introuvable, l'interpréteur propose désormais le candidat le plus proche (distance de Levenshtein) :
✅ Variable inconnue : compter → Vouliez-vous dire 'compteur' ?
✅ Fonction mal tapée : pritn → Vouliez-vous dire 'print' ?
✅ Fonction de namespace : Text.slugfy → Vouliez-vous dire 'slugify' ?
✅ Namespace oublié : « ajoutez 'inject Text' en début de fichier »
✅ Aucune suggestion si rien n'est assez proche — zéro bruit

Au passage, la release inclut aussi le namespace Text (slugify, camel/snake/kebab, Levenshtein, masquage…). 157 tests, zéro dépendance ajoutée.

🇬🇧 Typos are part of every developer's day. Oktopios v0.11.0 now helps you fix them: whenever a variable, function or namespace member can't be found, the interpreter suggests the closest match ("Did you mean 'compteur'?"), and reminds you when you forgot to `inject` a native namespace. No suggestion is shown when nothing is close enough. This release also ships the new Text namespace. 157 tests, no new dependencies.

📦 pip install --upgrade oktopios
💻 https://github.com/ALISOULEMOUANWIYA/oktopios

#OpenSource #Oktopios #Python #ProgrammingLanguage #IA #DeveloperExperience
