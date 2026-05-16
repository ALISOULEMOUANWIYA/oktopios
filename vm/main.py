"""
main.py — Point d'entrée du langage Oktopios
Usage :
    okp fichier.okp          → Exécute un fichier
    okp 'print("Bonjour")'   → Exécute du code inline
    okp --repl               → Lance le REPL interactif
    okp --help               → Aide
    okp --version            → Version
"""

import sys
import os
import json
import time
from colorama import Fore, Style, init as colorama_init
from tabulate import tabulate

from .lexer import tokenize, TYPE_ALIASES
from .parser import Parser
from .interpreter import Interpreter
from .native_funcs import NativeFuncs

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _chemin_metadata(nom_fichier):
    """Renvoie le chemin absolu vers un fichier dans metadata/."""
    racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(racine, "metadata", nom_fichier)


def _lire_metadata(nom_fichier):
    chemin = _chemin_metadata(nom_fichier)
    if not os.path.isfile(chemin):
        return None
    with open(chemin, "r", encoding="utf-8") as f:
        return f.read()



def _executer_code(code, chemin_source="<inline>"):
    """Tokenise, parse et interprète du code Oktopios."""
    start_time = time.perf_counter()  # Mesure précise du temps
    exit_code = 0
    error_msg = None

    try:
        tokens = list(tokenize(code))
        ast = Parser(tokens).parse()
        Interpreter().interpret(ast)
    except SyntaxError as e:
        error_msg = f"[Erreur syntaxique] {e}"
        print(Fore.RED + error_msg + Style.RESET_ALL)
        exit_code = 1
        sys.exit(exit_code)
    except Exception as e:
        error_msg = f"[Erreur] {e}"
        print(Fore.RED + error_msg + Style.RESET_ALL)
        exit_code = 1
        sys.exit(exit_code)
    finally:
        end_time = time.perf_counter()
        execution_time = end_time - start_time

        # Formatage du temps selon sa durée
        if execution_time < 0.001:
            time_str = f"{execution_time * 1000:.2f} µs"
        elif execution_time < 1:
            time_str = f"{execution_time * 1000:.2f} ms"
        else:
            time_str = f"{execution_time:.3f} s"

        # Affichage du résultat
        print(
            Fore.LIGHTCYAN_EX + f"\n[Process finished with exit code {exit_code}]"
            + Style.RESET_ALL
            + Fore.LIGHTGREEN_EX + " -> "
            + Style.RESET_ALL
            + Fore.LIGHTMAGENTA_EX + f"{time_str}"
            + Style.RESET_ALL
        )

        # Optionnel : afficher aussi en cas d'erreur
        if exit_code != 0:
            print(Fore.YELLOW + f"[!] L'exécution a échoué : {error_msg}" + Style.RESET_ALL)
            sys.exit(exit_code)


# ─── Commandes ────────────────────────────────────────────────────────────────

def cmd_version():
    version = _lire_metadata("version.txt")
    if version:
        print(Fore.YELLOW + f"Oktopios version {version.strip()}" + Style.RESET_ALL)
    else:
        print(Fore.YELLOW + "Oktopios version 0.0.1" + Style.RESET_ALL)


def cmd_aide():
    print("""
╭────────────────────────────────────────────╮
│        🐙 Aide pour le langage Oktopios    │
╰────────────────────────────────────────────╯

📦 Commandes générales :
  okp fichier.okp                   → Exécute un fichier Oktopios
  okp 'code'                        → Exécute une commande en ligne
  okp --help            ou -h       → Affiche cette aide
  okp --version         ou -v       → Affiche la version du langage
  okp --keywords        ou -kw      → Liste les mots-clés disponibles
  okp --doc             ou -d       → Affiche la documentation intégrée
  okp --init NomProjet              → Crée une structure de projet Oktopios

🧠 Analyse et REPL :
  okp --check fichier.okp  ou -ch   → Vérifie la syntaxe d'un fichier
  okp --repl               ou --rl  → Lance l'interface interactive REPL

📘 Fonctions natives :
  okp --native         ou -nt       → Liste les fonctions natives
  okp --native-json    ou -nj       → Renvoie les fonctions natives en JSON
  okp --native-markdown ou -nm      → Génère la doc native en Markdown

🧪 Types :
  okp --types          ou -tp       → Affiche les types disponibles
  okp --types-used fichier.okp      → Types utilisés dans un fichier
  okp --types-detail   ou -td       → Variables et leurs types

🔹 Exemples :
  okp monfichier.okp
  okp 'print("Bonjour")'
  okp --native
  okp --types-used monfichier.okp

🐙 https://oktopios.dev (à venir)
""")


def cmd_keywords():
    kw = _lire_metadata("keywords.txt")
    if kw:
        print(Fore.YELLOW + "Mots-clés Oktopios :\n" + kw + Style.RESET_ALL)
    else:
        from .lexer import KEYWORDS
        mots = sorted(KEYWORDS.keys())
        print(Fore.YELLOW + "Mots-clés Oktopios :\n" + "  " + "\n  ".join(mots) + Style.RESET_ALL)


def cmd_repl():
    print(Fore.CYAN + "🐙 Bienvenue dans le REPL d'Oktopios — tapez 'exit' pour quitter." + Style.RESET_ALL)
    print(Fore.CYAN + "   Tapez 'exit' ou 'quit' pour quitter." + Style.RESET_ALL)
    interpreter = Interpreter()  # Un seul interpréteur persistant
    while True:
        try:
            line = input(Fore.YELLOW + "okp> " + Style.RESET_ALL)
            if line.strip().lower() in ("exit", "quit"):
                print(Fore.GREEN + "👋 À bientôt !" + Style.RESET_ALL)
                break
            if not line.strip():
                continue
            tokens = list(tokenize(line))
            # Transmettre les modules déjà injectés au parser
            parser = Parser(tokens)
            parser.modules_loaded = set(interpreter.modules_loaded)
            if hasattr(interpreter, 'modules_loaded_alias'):
                for alias in interpreter.modules_loaded_alias.values():
                    if alias:
                        parser.modules_alias.add(alias)
            ast = parser.parse()
            interpreter.interpret(ast)
        except KeyboardInterrupt:
            print(Fore.RED + "\nInterruption (Ctrl+C). Sortie du REPL." + Style.RESET_ALL)
            break
        except Exception as e:
            print(Fore.RED + f"[Erreur REPL] {e}" + Style.RESET_ALL)


def cmd_check(args):
    path = next((a for a in args if a.endswith(".okp")), None)
    if not path:
        # Essayer de checker du code inline
        code = " ".join(args)
    else:
        if not os.path.isfile(path):
            print(Fore.RED + f"❌ Fichier introuvable : {path}" + Style.RESET_ALL)
            sys.exit(1)
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
    try:
        tokens = list(tokenize(code))
        Parser(tokens).parse()
        print(Fore.GREEN + "✅ Syntaxe OK." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"❌ Erreur de syntaxe : {e}" + Style.RESET_ALL)
        sys.exit(1)


def cmd_types():
    print(Fore.YELLOW + "Types supportés dans Oktopios :" + Style.RESET_ALL)
    for alias, real_type in TYPE_ALIASES.items():
        if alias != real_type:
            print(Fore.YELLOW + f"  {alias} (alias de {real_type})" + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + f"  {alias}" + Style.RESET_ALL)


def cmd_types_used(args):
    path = next((a for a in args if a.endswith(".okp")), None)
    if not path or not os.path.isfile(path):
        print(Fore.RED + "❌ Fournissez un fichier .okp valide." + Style.RESET_ALL)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()
    tokens = list(tokenize(code))
    ast = Parser(tokens).parse()
    types_utilises = set()

    def parcourir(node):
        if hasattr(node, "__dict__"):
            for value in node.__dict__.values():
                if isinstance(value, list):
                    for item in value:
                        parcourir(item)
                else:
                    parcourir(value)
        elif isinstance(node, str) and node in TYPE_ALIASES:
            types_utilises.add(node)

    parcourir(ast)
    print(Fore.YELLOW + "Types utilisés :" + Style.RESET_ALL)
    for t in sorted(types_utilises):
        alias = TYPE_ALIASES.get(t, t)
        suffix = f" (alias de {alias})" if alias != t else ""
        print(Fore.YELLOW + f"  {t}{suffix}" + Style.RESET_ALL)


def cmd_types_detail(args):
    path = next((a for a in args if a.endswith(".okp")), None)
    if not path or not os.path.isfile(path):
        print(Fore.RED + "❌ Fournissez un fichier .okp valide." + Style.RESET_ALL)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()
    tokens = list(tokenize(code))
    ast = Parser(tokens).parse()
    interpreter = Interpreter()
    interpreter.interpret(ast)
    if hasattr(interpreter, "variables") and interpreter.variables:
        print(Fore.YELLOW + "Variables détectées :" + Style.RESET_ALL)
        for nom, info in interpreter.variables.items():
            type_str = info.get("type", "inconnu") if isinstance(info, dict) else type(info).__name__
            print(f"  {nom} : {type_str}")
    else:
        print(Fore.YELLOW + "Aucune variable détectée." + Style.RESET_ALL)


def cmd_types_json(args):
    path = next((a for a in args if a.endswith(".okp")), None)
    if not path or not os.path.isfile(path):
        print(Fore.RED + "❌ Fournissez un fichier .okp valide." + Style.RESET_ALL)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()
    tokens = list(tokenize(code))
    ast = Parser(tokens).parse()
    interpreter = Interpreter()
    interpreter.interpret(ast)
    print(json.dumps({
        "variables": getattr(interpreter, "variables", {}),
        "functions": getattr(interpreter, "functions", {})
    }, indent=2, ensure_ascii=False))


def cmd_native():
    funcs = NativeFuncs.get_all() if hasattr(NativeFuncs, "get_all") else NativeFuncs
    table = []
    if isinstance(funcs, dict):
        for module, methods in funcs.items():
            if isinstance(methods, dict):
                for name, meta in methods.items():
                    if isinstance(meta, dict):
                        table.append([f"{module}.{name}", meta.get("args",""), meta.get("description",""), meta.get("example","")])
    print(Fore.LIGHTGREEN_EX + tabulate(
        table,
        headers=["Fonction", "Arguments", "Description", "Exemple"],
        tablefmt="fancy_grid"
    ) + Style.RESET_ALL)


def cmd_native_json():
    funcs = NativeFuncs.get_all() if hasattr(NativeFuncs, "get_all") else NativeFuncs
    # Supprimer les lambdas non-sérialisables
    def safe(obj):
        if callable(obj):
            return "<fonction native>"
        if isinstance(obj, dict):
            return {k: safe(v) for k, v in obj.items()}
        return obj
    print(json.dumps(safe(funcs), indent=2, ensure_ascii=False))


def cmd_native_markdown():
    funcs = NativeFuncs.get_all() if hasattr(NativeFuncs, "get_all") else {}
    output_path = "native_functions.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# 📘 Fonctions Natives Oktopios\n\n")
        if isinstance(funcs, dict):
            for module, methods in funcs.items():
                if isinstance(methods, dict):
                    f.write(f"## Module `{module}`\n\n")
                    for name, meta in methods.items():
                        if isinstance(meta, dict):
                            f.write(f"### `{module}.{name}`\n")
                            f.write(f"- **Arguments** : `{meta.get('args','')}`\n")
                            f.write(f"- **Description** : {meta.get('description','')}\n")
                            f.write(f"- **Exemple** : `{meta.get('example','')}`\n\n")
    print(Fore.LIGHTCYAN_EX + f"✅ Fichier `{output_path}` généré." + Style.RESET_ALL)


def cmd_doc():
    doc = _lire_metadata("doc.md")
    if doc:
        print(Fore.LIGHTYELLOW_EX + doc + Style.RESET_ALL)
    else:
        print("""
📘 Guide rapide Oktopios

🔸 Variables :
    var nom: int = 42
    val titre = "Bonjour"

🔸 Fonctions :
    fun saluer(nom: string) {
        print("Salut " + nom)
    }

🔸 Conditions :
    if x > 0 {
        print("Positif")
    } else {
        print("Négatif")
    }

🔸 Boucles :
    loop (i = 0; i < 5; i += 1) {
        print(i)
    }

🔸 Classes :
    class Animal {
        var nom: string
        fun __construct(n: string) {
            this.nom = n
        }
    }

🐙 okp --keywords  → mots-clés
   okp --native    → fonctions natives
   okp --version   → version
""")


def cmd_init(nom_projet):
    from pathlib import Path
    dossier = Path(nom_projet)
    if dossier.exists():
        print(Fore.RED + f"❌ Le dossier '{nom_projet}' existe déjà." + Style.RESET_ALL)
        sys.exit(1)
    (dossier / ".oktopios").mkdir(parents=True)
    (dossier / "main.okp").write_text(
        'print("Bienvenue dans Oktopios 🐙 !")\n', encoding="utf-8"
    )
    (dossier / "README.md").write_text(
        f"# {nom_projet}\n\nProjet généré avec 🐙 Oktopios.\n\n- Exécutez avec `okp main.okp`\n",
        encoding="utf-8"
    )
    (dossier / ".oktopios" / "config.toml").write_text(
        "# Configuration du projet Oktopios\n", encoding="utf-8"
    )
    print(Fore.GREEN + f"✅ Projet '{nom_projet}' créé dans : {dossier.resolve()}" + Style.RESET_ALL)


def cmd_executer_fichier(path):
    if not os.path.isfile(path):
        print(Fore.RED + f"❌ Fichier introuvable : {path}" + Style.RESET_ALL)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()
    _executer_code(code, chemin_source=path)


# ─── Routeur principal ────────────────────────────────────────────────────────

def main():
    colorama_init()
    os.system("")  # Active ANSI sur Windows
    sys.stdout.reconfigure(encoding="utf-8")

    args = sys.argv[1:]

    # Aucun argument → REPL
    if not args:
        cmd_repl()
        return

    cmd = args[0]

    if cmd in ("--help", "-h"):
        cmd_aide()
    elif cmd in ("--version", "-v"):
        cmd_version()
    elif cmd in ("--keywords", "-kw"):
        cmd_keywords()
    elif cmd in ("--repl", "--rl"):
        cmd_repl()
    elif cmd in ("--check", "-ch"):
        cmd_check(args[1:])
    elif cmd in ("--types", "-tp"):
        cmd_types()
    elif cmd in ("--types-used", "-tu"):
        cmd_types_used(args[1:])
    elif cmd in ("--types-detail", "-td"):
        cmd_types_detail(args[1:])
    elif cmd in ("--types-json", "-tj"):
        cmd_types_json(args[1:])
    elif cmd in ("--native", "-nt"):
        cmd_native()
    elif cmd in ("--native-json", "-nj"):
        cmd_native_json()
    elif cmd in ("--native-markdown", "-nm"):
        cmd_native_markdown()
    elif cmd in ("--doc", "-d"):
        cmd_doc()
    elif cmd == "--init":
        if len(args) < 2:
            print(Fore.RED + "❌ Usage : okp --init NomDuProjet" + Style.RESET_ALL)
            sys.exit(1)
        cmd_init(args[1])
    elif cmd.endswith(".okp"):
        cmd_executer_fichier(cmd)
    else:
        # Code inline : okp 'print("Bonjour")'
        code = " ".join(args)
        _executer_code(code)


if __name__ == "__main__":
    main()
