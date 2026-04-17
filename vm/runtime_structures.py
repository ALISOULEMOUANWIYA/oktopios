class OktopiosMap(dict):
    def __init__(self, entries=None):
        self.entries = entries or {}

    # --- Méthodes natives de base ---
    def Get(self, key):
        return self.entries.get(key)

    def Set(self, key, value):
        self.entries[key] = value

    def Keys(self):
        return list(self.entries.keys())

    def Values(self):
        return list(self.entries.values())

    def items(self):
        #print("debug 2 : length", len(self.entries.items()))
        return list(self.entries.items())

    def Clear(self):
        self.entries.clear()

    def Length(self):
        return len(self.entries)

    def callMethod(self, method_name, args):
        if method_name == "get":
            return self.Get(args[0])
        elif method_name == "set":
            self.Set(args[0], args[1])
        elif method_name == "remove":
            self.Remove(args[0])
        elif method_name == "keys":
            return self.keys()
        elif method_name == "values":
            return self.values()
        elif method_name == "items":
            #print("debug 1 : length", len(self.entries))
            return self.items()
        elif method_name == "clear":
            return self.Clear()
        elif method_name == "length":
            return self.Length()
        else:
            raise Exception(f"[Erreur] Méthode inconnue '{method_name}' pour OktopiosMap")

    # --- Pour un affichage lisible ---
    def __repr__(self):
        return repr(self.entries)
