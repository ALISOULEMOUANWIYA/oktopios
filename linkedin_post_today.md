# Post LinkedIn — Oktopios v0.1.1
*Généré automatiquement le 2026-07-06*

---

## 🇫🇷 Version française

🐙 **Oktopios v0.1.1 est disponible !**

Cette version enrichit considérablement la bibliothèque standard du langage :

**Math** : constantes natives (`Math.pi`, `Math.e`, `Math.tau`), nouvelles fonctions (`clamp`, `gcd`, `lcm`, `hypot`, `atan2`, `sign`, `sum`, `avg`, `log2`, `isnan`)

**String** : `padStart`, `padEnd`, `repeat`, `count`, `title`, `join`, `format`, `isAlpha`, `isDigit`, `lastIndexOf`

**Random** : `choice`, `shuffle`, `sample`, `uuid`, `seed` pour des tirages reproductibles

**Time** : `today()`, `strftime(fmt)`, `year()`, `month()`, `day()`, `hour()`, `minute()`, `second()`

**File** : `basename`, `dirname`, `extension`, `abspath`, `join` — et surtout : correction de la fuite de descripteurs de fichiers (tous les `File.read`, `File.write`, etc. utilisent desormais `with ... as f:`)

100 tests passent ✅

```
pip install --upgrade oktopios
```

#OpenSource #Oktopios #Python #ProgrammingLanguage #IA

---

## 🇬🇧 English version

🐙 **Oktopios v0.1.1 is out!**

This release significantly expands the standard library:

**Math**: native constants (`Math.pi`, `Math.e`, `Math.tau`), new functions (`clamp`, `gcd`, `lcm`, `hypot`, `atan2`, `sign`, `sum`, `avg`, `log2`, `isnan`)

**String**: `padStart`, `padEnd`, `repeat`, `count`, `title`, `join`, `format`, `isAlpha`, `isDigit`, `lastIndexOf`

**Random**: `choice`, `shuffle`, `sample`, `uuid`, `seed` for reproducible draws

**Time**: `today()`, `strftime(fmt)`, `year()`, `month()`, `day()`, `hour()`, `minute()`, `second()`

**File**: `basename`, `dirname`, `extension`, `abspath`, `join` — and: file handle leak fix (all `File.read`, `File.write`, etc. now use `with ... as f:`)

100 tests passing ✅

```
pip install --upgrade oktopios
```

#OpenSource #Oktopios #Python #ProgrammingLanguage #IA

---

Image: oktopios_v0.1.1_linkedin.png (1200x630 px)
GitHub: https://github.com/ALISOULEMOUANWIYA/oktopios
PyPI:   https://pypi.org/project/oktopios
