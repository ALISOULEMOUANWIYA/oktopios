from colorama import Fore, Style

class Environment:
    def __init__(self, parent=None, enclosing=None, conflict_manager=None):
        self.values = {}
        self.constants = {}
        self.parent = parent
        self.imported_modules = {}   # <— ajouté
        self.imported_symbols = {}   # <— ajouté
        self.enclosing = enclosing
        self.conflict_manager = conflict_manager or (parent.conflict_manager if parent else None)

    def __contains__(self, name):
        return name in self.values

    def define(self, name, value=None, arity=None, is_constant=False, source="local"):
        # Vérification de conflit
        if self.conflict_manager:
            self.conflict_manager.register_symbol(name, source)

        key = f"{name}/{arity}" if arity is not None else name
        self.values[key] = value
        #print(value)
        if is_constant:
            self.constants[name] = is_constant

    #def assign(self, name, value):
    #    if name in self.constants and self.constants[name]:
    #        raise RuntimeError(Fore.CYAN + f"Impossible de modifier la valeur constante '{name}'"+ Style.RESET_ALL)
    #    self.values[name] = value

    def assign(self, name, value):
        if name in self.constants and self.constants[name]:
            raise RuntimeError(Fore.CYAN + f"Impossible de modifier la valeur constante '{name}'"+ Style.RESET_ALL)
        # D'abord chercher dans l’environnement local
        if name in self.values:
            self.values[name] = value
            return

        # Sinon, propager au parent
        if self.enclosing:
            self.enclosing.assign(name, value)
            return

        raise RuntimeError(f"[Erreur] Variable inconnue (assign) : {name}")

    def get(self, name, arity=None, suppress_errors=False):
        # 🔹 Cas avec arité explicite
        if arity is not None:
            full_name = f"{name}/{arity}"
            if full_name in self.values:
                return self.values[full_name]
            elif self.enclosing:
                return self.enclosing.get(name, arity, suppress_errors)

        # 🔹 Recherche exacte
        if name in self.values:
            return self.values[name]

        # 🔹 Recherche par correspondance (ex: hello → hello/0)
        for key, val in self.values.items():
            if key.startswith(f"{name}/"):
                return val

        # 🔹 Si non trouvé, chercher dans l'environnement parent
        if self.enclosing:
            return self.enclosing.get(name, None, suppress_errors)

        # 🔹 Sinon erreur
        if not suppress_errors:
            msg = f"[Erreur] Variable ou fonction inconnue : {name}"
            if arity is not None:
                msg += f"/{arity}"
            raise Exception(msg)

        return None

    def exists(self, name):
        if name in self.values:
            return True
        elif self.enclosing:
            return self.enclosing.exists(name)
        return False

    def is_global_scope(self):
        return self.parent is None

    # --- Imports explicites ---
    def import_module(self, module_name, alias=None, module_proxy=None):
        name = alias or module_name.split(".")[-1]
        #print("Debug : dans environement > import_module : ", name)
        if name in self.imported_modules:
            raise Exception(f"[Conflit d'importation] Le module '{name}' est déjà importé.")
        self.imported_modules[name] = module_proxy
        self.define(name, module_proxy, source="import")

    def import_symbol(self, module_name, symbol_name, alias_name, value):
        if alias_name in self.imported_symbols or alias_name in self.values:
            raise Exception(f"[Conflit d'importation] Le symbole '{alias_name}' est déjà utilisé.")
        self.imported_symbols[alias_name] = (module_name, symbol_name)
        self.define(alias_name, value, source="from_import")

    # --- Résolution d’un symbole importé ---
    def resolve_imported(self, name):
        if name in self.imported_symbols:
            return self.values.get(name)
        if name in self.imported_modules:
            return self.imported_modules[name]
        return None

    def cleanup(self):
        for key, val in list(self.values.items()):
            if hasattr(val, "__destruct__"):
                try:
                    destructor = getattr(val, "__destruct__")
                    if callable(destructor):
                        destructor()
                except Exception as e:
                    print(
                        Fore.RED + f"[Warning] Erreur lors de l’appel du destructeur de '{key}': {e}" + Style.RESET_ALL)
