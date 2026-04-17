# module_proxy.py
class ModuleProxy:
    def __init__(self, module_interp, module_name, alias=None):
        self._module_interp = module_interp
        self._module_name = module_name
        self._alias = alias

    def __repr__(self):
        return f"<Module {self._module_name}>"

    def __getattr__(self, item):
        # priorité : tenter module env .get(name)
        env = getattr(self._module_interp, "env", None)
        if env:
            # essaie différents noms / API pour récupérer la valeur exportée
            get_try = None
            for attr in ("get", "get_value", "values", "store", "_values", "symbols"):
                if hasattr(env, attr):
                    get_try = attr
                    break
            # si env a méthode get(name, suppress_errors=True)
            if hasattr(env, "get"):
                try:
                    val = env.get(item, suppress_errors=True)
                    if val is not None:
                        return val
                except Exception:
                    pass
            # fallback : essayer un dictionnaire `values` ou `store`
            for field in ("values", "store", "_values", "symbols"):
                if hasattr(env, field):
                    d = getattr(env, field)
                    try:
                        return d[item]
                    except Exception:
                        pass
        # fallback: essayer dans l'interpreter directement
        if hasattr(self._module_interp, item):
            return getattr(self._module_interp, item)
        raise AttributeError(f"Module '{self._module_name}' n'a pas d'attribut '{item}'")


    def get(self, symbol_name):
        #print("Debug : dans module_proxy > get symbol_name : ", symbol_name)
        return self._module_interp.env.get(symbol_name)
