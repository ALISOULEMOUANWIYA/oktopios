# runtime_instance.py
import copy
from .user_function import UserFunction
from .return_Value import ReturnValue
from collections import Counter
from .ast_nodes import Field, FieldMethode
from colorama import Fore, Style
from .runtime_object_instance import RuntimeObjectInstance
from .ast_nodes import OktopiosMap

DEBUG = False  # mettre True pour traces détaillées


class RuntimeInstance(RuntimeObjectInstance):
    def __init__(self, klass, constructor_args=None, interpreter=None):
        """
        klass: ClassDeclaration (ou RuntimeClass) — attendu résolu (superclass -> ClassDeclaration ou list)
        constructor_args: liste d'Expr (non évalués) ou liste de valeurs déjà évaluées selon usage.
        interpreter: objet Interpreter (nécessaire pour évaluer les args si fournis en AST,
                     et pour résoudre noms de superclasses s'ils sont fournis en str)
        """

        # informations de base
        self.klass = klass
        # instances fields (non-static)
        self.fields = {}            # name -> Field
        # methods mapping (instance-level fallback keys "name" and "name/arity")
        self.fieldsMeth = {}        # key -> FieldMethode
        # super instances (par nom de classe)
        self.super_instances = {}   # name -> RuntimeInstance
        # signature table: (name, tuple(types)) -> FieldMethode
        self.method_signatures = {} # (nom, tuple(types)) -> FieldMethode

        # tables statiques (attachées à la déclaration de classe)
        # On stocke statics sur la déclaration (klass) si disponible
        #if not hasattr(self.klass, "static_fields"):
        #    self.klass.static_fields = {}
        #if not hasattr(self.klass, "static_methods"):
        #    self.klass.static_methods = {}

        # kind: "class" (par défaut), "abstract", "interface", "enum"
        kind = getattr(klass, "kind", "class")

        #if DEBUG:
        #    print()
        #    print(Fore.YELLOW + f"--- Instanciation de la classe {getattr(klass,'name','<anon>')} (kind={kind}) ---" + Style.RESET_ALL)

        # -------------------------------------------------------------------------------------------------------------------------
        # 🔄 CORRECTION (1) : Permettre l'instanciation des classes abstraites/interfaces si ce sont des parents (constructor_args=None)
        # -------------------------------------------------------------------------------------------------------------------------
        # --- 0) gestion des enums et interfaces / abstract non-instanciable ---
        # Interfaces & abstract ne doivent pas être instanciés directement, sauf pour l'héritage (constructor_args=None).
        if constructor_args is not None:
            if kind == "interface":
                raise Exception(Fore.RED + f"[Erreur] Impossible d'instancier une interface '{klass.name}'." + Style.RESET_ALL)
            if kind == "abstract":
                raise Exception(Fore.RED + f"[Erreur] Impossible d'instancier la classe abstraite '{klass.name}'." + Style.RESET_ALL)

        # --- 1) Instanciation des superclasses (tolérante aux noms non résolus) ---
        parent = getattr(klass, "superclass", None)
        if parent:
            parents = parent if isinstance(parent, list) else [parent]
            for p in parents:
                parent_decl = None
                if isinstance(p, str):
                    # résoudre via interpreter si fourni
                    if interpreter is not None:
                        # ----------------------------------------------------------------
                        # 🔄 VÉRIFIER TOUTES LES TABLES DE CLASSES (LOGIQUE PRÉCÉDENTE CONSERVÉE)
                        # ----------------------------------------------------------------
                        if hasattr(interpreter, "classes"):
                            parent_decl = interpreter.classes.get(p)
                        if parent_decl is None and hasattr(interpreter, "abstract_classes"):
                            parent_decl = interpreter.abstract_classes.get(p)
                        if parent_decl is None and hasattr(interpreter, "interfaces"):
                            parent_decl = interpreter.interfaces.get(p)
                        # ----------------------------------------------------------------

                        if parent_decl is None:
                            raise Exception(
                                Fore.RED + f"[Erreur] Superclasse ou Interface '{p}' introuvable pour la classe '{getattr(klass, 'name', '<anon>')}'" + Style.RESET_ALL)
                    else:
                        raise Exception(
                            Fore.RED + f"[Erreur] Superclasse '{p}' référence un nom non résolu (fournir interpreter ou résoudre avant)." + Style.RESET_ALL)
                else:
                    # on copie la déclaration du parent pour éviter effets de bord
                    parent_decl = p

                parent_name = getattr(parent_decl, "name", None)
                if parent_name in self.super_instances:
                    continue
                # instancier récursivement la super-instance (sans constructor args)
                #if DEBUG:
                #    print(f"  ↳ Création de la super-instance {parent_name}")
                self.super_instances[parent_name] = RuntimeInstance(parent_decl, constructor_args=None, interpreter=interpreter)

        # --- 2) Initialisation des champs (Field) définis localement dans klass (non-static) ---
        from .ast_nodes import VarDecl
        for m in getattr(klass, "members", []):
            if isinstance(m, VarDecl):
                # si variable marquée static (attribut statique) : la stocker dans klass.static_fields
                #if getattr(m, "is_static", False):
                #    # évaluer valeur si AST et interpreter donné
                #    if getattr(m, "value", None) is not None and interpreter is not None and not isinstance(m.value, (int, float, str, bool, list)):
                #        val = interpreter.evaluate(m.value)
                #    else:
                #        val = getattr(m, "value", None)
                #    self.klass.static_fields[m.name] = val
                #    if DEBUG:
                #        print(Fore.MAGENTA + f"  [static field] {klass.name}.{m.name} = {val}" + Style.RESET_ALL)
                #    continue

                field = Field(m)
                if field.value is not None and interpreter is not None and not isinstance(field.value, (int, float, str, bool, list)):
                    field.value = interpreter.evaluate(field.value)
                self.fields[m.name] = field


        # --- 3) Enregistrement des méthodes locales (avec prise en charge de static/abstract/override/invoke) ---
        for methode_decl in getattr(klass, "methods", []):
            arity = len(getattr(methode_decl, "params", []))
            param_types = tuple(p[1] for p in methode_decl.params) if getattr(methode_decl, "params", None) else tuple()
            key_arity = f"{methode_decl.name}/{arity}"

            # si méthode statique => ranger dans klass.static_methods
            if getattr(methode_decl, "is_static", False):
                # priorité sur static_methods par nom et par arité (si besoin)
                self.klass.static_methods[f"{methode_decl.name}/{arity}"] = methode_decl
                self.klass.static_methods[methode_decl.name] = methode_decl
                #if DEBUG:
                #    print(Fore.MAGENTA + f"  [static method] {klass.name}.{methode_decl.name}/{arity}" + Style.RESET_ALL)
                continue

            # création du FieldMethode
            field_m = FieldMethode(methode_decl)

            # empêche redéfinition stricte (même signature) locale
            if (methode_decl.name, param_types) in self.method_signatures:
                raise Exception(Fore.CYAN + f"[Erreur] Redéfinition interdite : méthode '{methode_decl.name}' avec mêmes types {param_types}" + Style.RESET_ALL)

            # enregistrement prioritaire local (override local écrase héritée)
            self.method_signatures[(methode_decl.name, param_types)] = field_m
            self.fieldsMeth[key_arity] = field_m
            # enregistrement nom simple (fallback)
            self.fieldsMeth[methode_decl.name] = field_m

            #if DEBUG:
            #    print(f"  ➕ Ajout méthode {methode_decl.name}/{arity} types={param_types}, nom simple: {methode_decl.name} dans {klass.name}")

        # --- 4) Fusion (héritage multiple) : copier les membres hérités sans écraser les locaux ---

        # 4a) Fusion des CHAMPS (Fields) non-statiques (Logique inchangée)
        def merge_fields(instance_to_merge):
            # On utilise le dictionnaire des champs déjà résolu sur l'instance parente
            for name, field in instance_to_merge.fields.items():
                if name not in self.fields:
                    # Copier le champ pour éviter que les modifications d'une instance n'affectent l'autre
                    self.fields[
                        name] = field  # Utiliser copy.deepcopy(field) si la sémantique de votre langage l'exige

            # Récursivité sur les parents du parent pour s'assurer que même les champs éloignés sont inclus
            for sup_inst in instance_to_merge.super_instances.values():
                merge_fields(sup_inst)

        # -------------------------------------------------------------------------------------------------------------------------
        # 🔄 CORRECTION (2) : Fusion des méthodes par signature avec reconstruction des fallbacks pour garantir la recherche simple.
        # -------------------------------------------------------------------------------------------------------------------------
        # 4b) Fusion des MÉTHODES (Methodes)
        def merge_methods(instance_to_merge):
            # 1. Fusion par signature exacte (méthodes virtuelles/surchargées)
            for (p_name, p_types), p_field in instance_to_merge.method_signatures.items():
                # Si l'enfant n'a pas cette signature exacte, on l'hérite
                if (p_name, p_types) not in self.method_signatures:
                    self.method_signatures[(p_name, p_types)] = p_field

                    # 2. Re-création/Mise à jour des fallbacks pour cette méthode nouvellement héritée (drive, fly)
                    #    Ceci est crucial pour que les appels simples (name/arity) fonctionnent sur les méthodes héritées.
                    arity = len(p_types)
                    key_arity = f"{p_name}/{arity}"

                    # Copier par arité si absent
                    if key_arity not in self.fieldsMeth:
                        self.fieldsMeth[key_arity] = p_field

                    # Copier nom simple si absent
                    if p_name not in self.fieldsMeth:
                        self.fieldsMeth[p_name] = p_field

            # Récursivité sur les parents du parent
            for sup_inst in instance_to_merge.super_instances.values():
                merge_methods(sup_inst)

        # 🚨 Démarrage de la fusion à partir des parents directs de la classe courante (FlyingCar)
        # L'ordre dans lequel les parents sont fusionnés est important (gestion du Diamant)
        for parent_inst in list(self.super_instances.values()):
            merge_fields(parent_inst)
            merge_methods(parent_inst)
            #if DEBUG:
            #    print(
            #        Fore.CYAN + f"  🔗 Fusion récursive des membres hérités de {parent_inst.klass.name}" + Style.RESET_ALL)

        #if DEBUG:
        #    print(
        #        Fore.CYAN + f"✅ Méthodes connues de {klass.name}: {list(self.method_signatures.keys())}" + Style.RESET_ALL)

        # --- 5) Vérification d'override (toutes les méthodes marquées override existent dans au moins un parent) ---
        # ... (Logique inchangée) ...
        for (name, param_types), field_m in list(self.method_signatures.items()):
            decl = field_m.methodeName
            if getattr(decl, "is_override", False):
                found_in_super = False
                inspected_supers = []

                def check_in_supers(super_instances):
                    nonlocal found_in_super
                    for super_inst in super_instances.values():
                        inspected_supers.append(super_inst.klass.name)
                        for (s_name, s_types), s_field in super_inst.method_signatures.items():
                            if s_name == name and len(s_types) == len(param_types):
                                found_in_super = True
                                return
                        check_in_supers(super_inst.super_instances)
                        if found_in_super:
                            return

                check_in_supers(self.super_instances)
                if not found_in_super:
                    raise Exception(Fore.RED + f"[Erreur] La méthode '{name}' est marquée override mais n'existe pas dans les superclasses {inspected_supers}." + Style.RESET_ALL)

        # --- 5b) Vérification d'implémentation des méthodes abstraites héritées ---
        # ... (Logique inchangée) ...
        # Si une superclasse contient des méthodes marquées 'is_abstract', l'enfant concret doit les implémenter.
        # On vérifie seulement si la classe courante n'est pas abstraite elle-même.
        if kind != "abstract":
            abstract_missed = []
            def collect_abstracts(super_instances):
                res = []
                for s in super_instances.values():
                    for (mname, mtypes), mfield in s.method_signatures.items():
                        decl = mfield.methodeName
                        if getattr(decl, "is_abstract", False):
                            res.append((mname, mtypes))
                    res.extend(collect_abstracts(s.super_instances))
                return res

            all_abstracts = collect_abstracts(self.super_instances)
            for (mname, mtypes) in all_abstracts:
                if (mname, mtypes) not in self.method_signatures:
                    # fallback: accept same arity name match if types unknown (len match)
                    found = False
                    for (nm, types) in self.method_signatures.keys():
                        if nm == mname and len(types) == len(mtypes):
                            found = True
                            break
                    if not found:
                        abstract_missed.append((mname, mtypes))

            if abstract_missed:
                names = [f"{n}{tuple(t)}" for n, t in abstract_missed]
                raise Exception(Fore.RED + f"[Erreur] La classe '{klass.name}' n'implémente pas les méthodes abstraites héritées : {names}" + Style.RESET_ALL)

        # --- 6) Appel du constructeur (init) si args fournis ---
        # ... (Logique inchangée) ...
        #if constructor_args:
        #    args_vals = []
        #    if interpreter is not None:
        #        args_vals = [
        #            interpreter.evaluate(a) if not isinstance(a, (int, float, str, bool, list)) else a
        #            for a in constructor_args
        #        ]
        #    else:
        #        args_vals = constructor_args

        #    init_field = self.fieldsMeth.get("__construct")
        #    if init_field:
        #        user_func = UserFunction(init_field.methodeName, getattr(self.klass, "closure", None), instance=self)
        #        user_func.call(interpreter=interpreter, args=args_vals)


    # ----------------------------
    # Accès aux champs (instance)
    # ----------------------------
    def get_field(self, name, current_class=None):
        field = self.fields.get(name)


        if not field:
            raise Exception(f"[Erreur] Champ inconnu: {name}")
        if getattr(field, "access_modifier", "public") == "private" and current_class != self.klass.name:
            raise Exception(f"[Erreur] Accès illégal au champ privé '{name}'")
        if getattr(field, "access_modifier", "public") == "protected" and current_class != self.klass.name:
            raise Exception(f"[Erreur] Accès illégal au champ protected '{name}'")
        return field.value


    def get_attr(self, name, from_this=False):
        return self.get_field(name, current_class=self.klass.name if from_this else None)

    def set_field(self, name, value, current_class=None):
        field = self.fields.get(name)
        if not field:
            raise Exception(f"[Erreur] Champ inconnu: {name}")
        if getattr(field, "is_constant", False):
            raise Exception(f"[Erreur] Impossible de modifier la constante '{name}'")
        if getattr(field, "access_modifier", "public") == "private" and current_class != self.klass.name:
            raise Exception(f"[Erreur] Accès illégal au champ privé '{name}'")
        if getattr(field, "access_modifier", "public") == "protected" and current_class != self.klass.name:
            raise Exception(f"[Erreur] Accès illégal au champ protected '{name}'")
        field.value = value

    def set_attr(self, name, value, from_this=False):
        self.set_field(name, value, current_class=self.klass.name if from_this else None)

    # ----------------------------
    # Recherche et binding d'une méthode
    # ----------------------------
    def get_method_bound(self, method_name, caller_instance=None, arg_count=None, arg_types=None, line=None,
                         column=None):
        """
        Recherche d'une méthode (locale ou héritée) avec prise en charge de :
          - méthodes statiques (sur klass.static_methods)
          - correspondance exacte par signature (nom + types)
          - fallback par arité (nom/arity)
          - fallback par nom simple
        Retourne un UserFunction bound (instance=self) pour méthodes d'instance.
        """
        # 0) Vérifier static method sur la déclaration (appel via Classe.metho() doit résoudre ailleurs)
        # Note: ici on gère la recherche d'instance ; les appels statiques peuvent être résolus via la table interpreter/classes.
        # Mais on propose aussi une résolution locale via klass.static_methods.
        # (Si tu veux appeler une static via instance, on privilégie instance methods first.)
        # -> On ne renvoie pas de bound static ici (garder UserFunction mais instance=None pour static)
        # (Ton interpréteur devrait repérer et appeler static via la table klass.static_methods)

        arg_info = f"({', '.join(arg_types)})" if arg_types else f"/{arg_count}" if arg_count is not None else ""

        #if DEBUG:
        #    print(Fore.YELLOW + f"--- [DEBUG] Recherche finale de '{method_name}{arg_info}' sur '{self.klass.name}' ---" + Style.RESET_ALL)

        method_decl = None
        field_m = None
        found_key = None

        # 1) Exact match (signature: name + types)
        if arg_types:
            key = (method_name, tuple(arg_types))
            field_m = self.method_signatures.get(key)
            if field_m:
                method_decl = field_m.methodeName
                found_key = f"Signature {key}"

        # 2) Fallback par arité
        if method_decl is None and arg_count is not None:
            key_arity = f"{method_name}/{arg_count}"
            field_m = self.fieldsMeth.get(key_arity)
            if field_m:
                method_decl = field_m.methodeName
                found_key = f"Arity {key_arity}"

        # 3) Fallback par nom simple
        if method_decl is None:
            field_m = self.fieldsMeth.get(method_name)
            if field_m:
                method_decl = field_m.methodeName
                found_key = f"Nom Simple {method_name}"

        # 4) Si toujours rien -> erreur
        if not method_decl:
            received = "(" + ", ".join(arg_types or []) + ")"
            line_info = f"ligne {line}, colonne {column}" if line and column else "ligne ?"
            #print("method_name", method_name,  "self.klass", self.klass.members)
            raise Exception(Fore.RED + f"[Erreur {line_info}] Méthode '{method_name}{received}' introuvable dans '{self.klass.name}'." + Style.RESET_ALL)

        # Vérification visibilité
        visibility = getattr(method_decl, "visibility", "public")
        if visibility == "private" and caller_instance != self:
            raise Exception(f"[Erreur] Accès illégal à la méthode privée '{method_name}'")
        if visibility == "protected" and caller_instance != self:
            raise Exception(f"[Erreur] Accès illégal à la méthode protégée '{method_name}'")

        # Vérifier si la déclaration trouvée est abstraite -> impossible d'appeler une méthode abstract
        if getattr(method_decl, "is_abstract", False):
            raise Exception(f"[Erreur] Méthode abstraite '{method_name}' introuvable pour exécution dans '{self.klass.name}'")

        #if DEBUG:
        #    decl_id = id(method_decl)
        #    print(Fore.GREEN + f"[DEBUG] ✅ Méthode trouvée par {found_key} dans {self.klass.name}. Décl. ID: {decl_id}" + Style.RESET_ALL)
        #    if hasattr(method_decl, "body") and method_decl.body:
        #        print(Fore.CYAN + f"[DEBUG-FINAL] Déclaration utilisée: {method_decl.name} (première instruction: {type(method_decl.body[0]).__name__})" + Style.RESET_ALL)

        # Retour d'un UserFunction bound à cette instance
        return UserFunction(method_decl, getattr(self.klass, "closure", None), instance=self)

    # ----------------------------
    # retrouver super par nom (récursif)
    # ----------------------------
    def get_super_by_name(self, name):
        if not hasattr(self, "super_instances") or not self.super_instances:
            return None
        for klass_name, super_inst in self.super_instances.items():
            if super_inst.klass.name == name:
                return super_inst
            found = super_inst.get_super_by_name(name)
            if found:
                return found
        return None

    # ----------------------------
    # Appel de méthodes sur les parents (super)
    # ----------------------------
    def call_super(self, method_name, interpreter, args, parent_names=None, caller_instance=None):
        if not self.super_instances:
            raise Exception("[Erreur] Pas de superclasse à appeler")

        # déterminer parents à appeler
        if parent_names is None:
            if len(self.super_instances) == 1:
                parents_to_call = list(self.super_instances.values())
            else:
                raise Exception("[Erreur] Héritage multiple : veuillez préciser les parents dans super[...].method(...)")
        else:
            parents_to_call = []
            for pname in parent_names:
                inst = self.super_instances.get(pname)
                if not inst:
                    raise Exception(f"[Erreur] Parent '{pname}' introuvable pour la classe '{self.klass.name}'")
                parents_to_call.append(inst)

        seen = set()
        results = []
        for parent_inst in parents_to_call:
            if parent_inst.klass.name in seen:
                continue
            seen.add(parent_inst.klass.name)

            bound = parent_inst.get_method_bound(method_name, caller_instance=self)
            if not bound:
                raise Exception(f"[Erreur] Méthode '{method_name}' introuvable dans le parent '{parent_inst.klass.name}'")

            res = bound.call(interpreter, args)
            results.append(res)

        return results[0] if len(results) == 1 else results

    def __str__(self):
        return f"<instance of {getattr(self.klass, 'name', 'anonymous')}>"

class RuntimeInstance_for_enum(RuntimeObjectInstance):
    def __init__(self, enum_type, value_name, interpreter=None, ordinal=None):
        self.enum_type = enum_type
        self.enum_value_name = value_name
        self.fields = {"name": value_name, "ordinal": ordinal}
        self.interpreter = interpreter
        self.ordinal_value = ordinal

        # Initialisation de tous les champs définis dans l'enum
        for field in enum_type.fields:
            self.fields[field.name] = None

    def get_attr(self, name):
        # Priorité : champ de l'instance
        if name in self.fields:
            return self.fields[name]

        # Méthodes de l'enum
        method = next((m for m in self.enum_type.methods if m.name == name), None)
        if method:
            return UserFunction(method, closure=None, instance=self)

        raise Exception(f"[EnumInstance] '{name}' introuvable dans {self.enum_type.name}")

    def set_attr(self, name, value, interpreter=None):
        # Si le champ existe dans l'instance ou dans les fields de l'enum
        self.fields[name] = value

    def set_field(self, name, value):
        # autoriser la création dynamique de champs (ex: this.description)
        self.fields[name] = value

    def get_field(self, name):
        if name == "name":
            return self.enum_value_name
        if name == "ordinal":
            return self.ordinal_value
        if name in self.fields:
            return self.fields[name]
        for field in self.enum_type.fields:
            if field.name == name:
                return None
        raise Exception(f"[EnumInstance] Champ '{name}' inconnu dans {self.enum_type.name}")

    def get_method_bound(self, name, caller_instance=None, arg_types=None, line=None, column=None):
        # Méthodes prédéfinies
        if name == "name":
            return UserFunction(lambda _, args: self.enum_value_name, closure=None, instance=self)
        if name == "ordinal":
            return UserFunction(lambda _, args: self.ordinal_value, closure=None, instance=self)
        if name == "toString":
            return UserFunction(lambda _, args: self.enum_value_name, closure=None, instance=self)
        if name == "values":
            return UserFunction(lambda _, args: list(self.enum_type.values.values()), closure=None, instance=self)
        if name == "valueOf":
            return UserFunction(lambda _, args: self.enum_type.get(args[0]), closure=None, instance=self)
        if name == "set_attr":
            return UserFunction(lambda _, args: self.set_attr(args[0], args[1]), closure=None, instance=self)
        if name == "get_attr":
            return UserFunction(lambda _, args: self.get_attr(args[0]), closure=None, instance=self)
        if name == "compareTo":
            return UserFunction(lambda _, args: self.ordinal_value - args[0].ordinal_value, closure=None, instance=self)
        if name == "equals":
            return UserFunction(lambda _, args: self == args[0], closure=None, instance=self)
        if name == "hashCode":
            return UserFunction(lambda _, args: hash((self.enum_type.name, self.enum_value_name)), closure=None,
                                instance=self)

        # Méthodes définies dans l'enum
        for method in self.enum_type.methods:
            if method.name == name:
                return UserFunction(method, closure=None, instance=self)

        return None

    def call_method(self, name, args, interpreter):
        for method in self.enum_type.methods:
            if method.name == name:
                call_env = interpreter.env.fork()
                call_env.define("this", self)
                return interpreter.call_function(method, args, call_env)
        raise Exception(f"[EnumInstance] Méthode '{name}' non trouvée dans {self.enum_type.name}")

    def __repr__(self):
        return f"{self.enum_type.name}.{self.enum_value_name}"

    def __eq__(self, other):
        return (
            isinstance(other, RuntimeInstance_for_enum)
            and self.enum_type == other.enum_type
            and self.enum_value_name == other.enum_value_name
        )


