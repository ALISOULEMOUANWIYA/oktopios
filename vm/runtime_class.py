from .user_function import UserFunction
from .ast_nodes import Field, VarDecl

class RuntimeClass:
    def __init__(self, class_decl, interpreter):
        self.decl = class_decl
        self.name = class_decl.name
        self.interpreter = interpreter

        # Assure l'existence d'un dictionnaire partagé pour les static fields/methods
        if not hasattr(self.decl, "static_fields"):
            # construire la table à partir des VarDecl marqués static (valeur initiale)
            self.decl.static_fields = {}
            for m in getattr(class_decl, "members", []):
                if isinstance(m, VarDecl) and getattr(m, "is_static", False):
                    field = Field(m)
                    # évaluer la valeur initiale si nécessaire
                    if field.value is not None and interpreter is not None and not isinstance(field.value, (int, float, str, bool, list)):
                        field.value = interpreter.evaluate(field.value)
                    self.decl.static_fields[m.name] = field



        # Méthodes statiques (partagées également sur la déclaration)
        for m in class_decl.members:
            if getattr(m, "is_static", False):
                self.decl.static_methods[m.name] = m

        # Ici on se contente de référencer les tables partagées (pas de copie)
        self.static_methods = self.decl.static_methods
        self.fields = self.decl.static_fields

    # get/set statics
    def get_static_field(self, name):
        field = self.fields.get(name)
        if not field:
            raise Exception(f"[Erreur] Champ inconnu: {name}")
        return field.value

    def set_static_field(self, name, value):
        field = self.fields.get(name)
        if not field:
            raise Exception(f"[Erreur] Champ inconnu: {name}")
        if getattr(field, "is_constant", False):
            raise Exception(f"[Erreur] Impossible de modifier la constante '{name}'")
        field.value = value

    def get_static_method_bound(self, name, arg_count=None, line=None, column=None):
        if not self.static_methods:
            raise Exception(f"[Erreur] Classe '{self.name}' n'a aucune méthode statique.")
        # arité -> key_arity
        if arg_count is not None:
            key_arity = f"{name}/{arg_count}"
            if key_arity in self.static_methods:
                return UserFunction(self.static_methods[key_arity],
                                    getattr(self.decl, "closure", None),
                                    instance=None)
        if name in self.static_methods:
            return UserFunction(self.static_methods[name],
                                getattr(self.decl, "closure", None),
                                instance=None)
        # héritage statique (si class_decl.superclass contient des ClassDeclaration)
        if hasattr(self.decl, "superclass") and self.decl.superclass:
            for parent in self.decl.superclass:
                parent_static = getattr(parent, "static_methods", {})
                if name in parent_static:
                    return UserFunction(parent_static[name],
                                        getattr(parent, "closure", None),
                                        instance=None)
        raise Exception(f"Méthode statique '{name}()' introuvable dans '{self.name}'.")

    def __repr__(self):
        return f"<RuntimeClass {self.name}>"
