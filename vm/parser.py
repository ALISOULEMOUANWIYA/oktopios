
from . token_type import TokenType
from . ast_nodes import *
from  colorama import Fore, Style
from . parse_error import ParseError
from . symbole_table import SymbolTable

# Dans parser.py (ou accessible globalement)
#INJECTED_MODULES = set()  # ex: {"math", "io", "file"}
class Parser:
    def __init__(self, tokens, env=None, access_modifier="public"):
        self.tokens = tokens
        self.current = 0
        self.env = env
        self.access_modifier = access_modifier
        self.in_object_context = False  # remplace in_class_context
        # Ajout de cette ligne :
        self.global_functions = {}
        self.class_functions = {}  # { class_name: { function_name: [signatures] } }
        self.modules_loaded = set()  # pour les modules injecter
        self.modules_alias = set()  # pour les modules injecter
        self.modules_loaded_alias = set()  # pour les modules injecter
        self.modules_import_loaded = set()  # pour les modules importé appartire d'une fichier oktopios
        self.class_loaded = SymbolTable()  # pour tous les classes local et importé
        self.pointer_classe = None
        self.current_class = None
        self.interface_loaded = {}  # pour tous les interface local et importé
        self.enume_loaded = {}  # pour tous les enums local et importé
        self.value_matche_variable = None

    def parse(self):
        statements = []
        #self.in_object_context = False
        while not self.is_at_end():
            stmt = self.declaration()  # ✅ au lieu de self.statement()
            if stmt:
                statements.append(stmt)
        return Program(statements)

    def declaration(self):
        try:
            if self.match(TokenType.TENT):
                return self.tent_declaration()
            elif self.match(TokenType.TEN):
                return self.ten_declaration()
            elif self.match(TokenType.INTENTION):
                return self.intention_statement()
            elif self.match(TokenType.TENT_RANDOM):
                return self.tent_random_statement()
            elif self.match(TokenType.ABSTRACT):
                return self.parse_class_decl(type_class=TokenType.ABSTRACT)
            elif self.match(TokenType.CLASS):
                clss = self.parse_class_decl(type_class=TokenType.CLASS)
                #print("Debug : dans declaration TokenType.CLASS ", clss)
                return clss
            elif self.match(TokenType.INTERFACE):
                inter = self.parse_interface_decl()
                #print("Debug : dans declaration TokenType.INTERFACE ", inter)
                return inter
            elif self.match(TokenType.ENUM):
                enmm = self.parse_enum_decl()
                #print("Debug : dans declaration TokenType.ENUM ", enmm)
                return enmm
            elif self.match(TokenType.NEURON_LOOP):
                return self.parse_neuron_loop_decl()
            else:
                return self.statement()
        except ParseError as error:
            self.synchronize()
            return None

    # --------------------------
    # Déclaration de variable
    # --------------------------
    def var_decl(self, is_const=False, access_modifier="public", is_static=False):
        if self.check(TokenType.ID) or self.check(TokenType.MODE):
            id = self.advance()
        else:
            id = self.consume(TokenType.ID, Fore.CYAN + "Nom de variable attendu" + Style.RESET_ALL)
        name = id.value

        # --- Déclaration multiple, forme A : "x, y, a : int = 1, 2, 3" ---
        # (signal : une virgule arrive juste après le nom, avant tout ':' ou '=')
        if self.check(TokenType.COMMA):
            return self.multi_var_decl(name, None, False, is_const, access_modifier, is_static)

        if self.match(TokenType.COLON):
            type_ = self.consume_type()
        else:
            type_ = None
        value = None

        if self.match(TokenType.EQ):
            value = self.expression()
            # --- Déclaration multiple, forme B : "x = 1, y = 2, a = 3" ---
            # (signal : une virgule arrive APRÈS 'name = value', pas avant)
            if type_ is None and self.check(TokenType.COMMA):
                return self.multi_var_decl(name, value, True, is_const, access_modifier, is_static)

        # Vérification de cohérence
        if type_ is not None and isinstance(value, Literal):
            val_type = type(value.value).__name__
            if type_ == "string":
                val_type = "string"
            elif type_ == "bool":
                val_type = "bool"
            elif type_ == "int":
                val_type = "int"
            elif type_ == "float":
                val_type = "float"
            if type_ != val_type:
                #print(f"Debug : var_decl, name :{name}, type_ :{type_}, val_type :{val_type}, value :{value}, is_const :{is_const}, access_modifier :{access_modifier}, is_static :{is_static}")
                raise self.error(
                    self.peek(),
                    Fore.RED + f"Incompatibilité : '{name}' de type '{type_}' ne correspond pas à la valeur de type '{val_type}'." + Style.RESET_ALL
                )


        if isinstance(value , ListLiteral):
            type_ = list.__name__
        elif isinstance(value , DictLiteral):
            type_ = dict.__name__
        elif isinstance(value, (dict, list)):  # objets JSON natifs
            type_ = "json"
        elif isinstance(value , NewInstanceExpr):
            type_ = value.class_name


        #print("\nDebug : var_decl", "\nname = ",name, "\ntype_ = ",type_, "\nvalue = ",value, "\nis_const = ",is_const, "\naccess_modifier = ",access_modifier, "\nis_static = ",is_static)

        return VarDecl(name=name, type_=type_, value=value, is_constant=is_const, access_modifier=access_modifier, is_static=is_static)

    def multi_var_decl(self, first_name, first_value, first_has_value, is_const, access_modifier, is_static):
        """Gère les deux formes de déclaration multiple :
        - 'x, y, a : int = 1, 2, 3'  (type partagé, valeurs appariées par position)
        - 'x = 1, y = 2, a = 3'      (chaque variable a déjà sa propre valeur)
        `first_has_value` indique si first_value a déjà été parsé (forme B,
        détectée après coup) ou non (forme A, détectée avant tout '=')."""
        segment_names = [first_name]
        segment_values = [first_value if first_has_value else None]

        while self.match(TokenType.COMMA):
            seg_name_tok = self.consume(TokenType.ID, "Nom de variable attendu après ','")
            segment_names.append(seg_name_tok.value)
            if self.match(TokenType.EQ):
                segment_values.append(self.expression())
            else:
                segment_values.append(None)

        if self.check(TokenType.COLON):
            # --- FORME A : type partagé, valeurs après '=' séparées par des virgules ---
            if any(v is not None for v in segment_values):
                raise self.error(
                    self.peek(),
                    "Mélange invalide : utilisez soit 'x, y : type = v1, v2' soit 'x = v1, y = v2', pas les deux."
                )
            self.consume(TokenType.COLON, "Attendu ':' après la liste de noms")
            shared_type = self.consume_type()
            self.consume(TokenType.EQ, "Attendu '=' après le type dans une déclaration multiple")
            value_exprs = [self.expression()]
            while self.match(TokenType.COMMA):
                value_exprs.append(self.expression())

            if len(value_exprs) != len(segment_names):
                raise self.error(
                    self.peek(),
                    f"Nombre de valeurs ({len(value_exprs)}) ne correspond pas au nombre de "
                    f"variables ({len(segment_names)}) : {', '.join(segment_names)}"
                )

            decls = [
                VarDecl(name=n, type_=shared_type, value=v, is_constant=is_const,
                        access_modifier=access_modifier, is_static=is_static)
                for n, v in zip(segment_names, value_exprs)
            ]
            return MultiVarDecl(decls)

        # --- FORME B : chaque variable porte déjà sa propre valeur ---
        missing = [n for n, v in zip(segment_names, segment_values) if v is None]
        if missing:
            raise self.error(
                self.peek(),
                f"Valeur manquante pour : {', '.join(missing)} (forme attendue : 'x = 1, y = 2')"
            )

        decls = []
        for n, v in zip(segment_names, segment_values):
            t = None
            if isinstance(v, ListLiteral):
                t = list.__name__
            elif isinstance(v, DictLiteral):
                t = dict.__name__
            elif isinstance(v, NewInstanceExpr):
                t = v.class_name
            decls.append(VarDecl(name=n, type_=t, value=v, is_constant=is_const,
                                  access_modifier=access_modifier, is_static=is_static))
        return MultiVarDecl(decls)

    # --------------------------
    #dans le parser.py
    # Déclaration de classe avec héritage multiple
    # --------------------------
    def tent_declaration(self):
        self.consume(TokenType.CLASS, "Expected 'class' after tent.")
        return TentClass(self.parse_class_decl(type_class=TokenType.CLASS))

    def ten_declaration(self):
        self.consume(TokenType.CLASS, "Expected 'class' after ten.")
        return TenClass(self.parse_class_decl(type_class=TokenType.CLASS))

    def intention_statement(self):
        name = self.consume(TokenType.ID, "Expected intention name.").value
        args = self.parse_pieuvre_call_args()
        return IntentionStmt(name, args)

    def tent_random_statement(self):
        name = self.consume(TokenType.ID, "Expected tentRandom action name.").value
        args = self.parse_pieuvre_call_args()
        return TentRandomStmt(name, args)

    def parse_pieuvre_call_args(self):
        self.consume(TokenType.LPAREN, "Expected '(' after pieuvre action name.")
        args = []
        if not self.check(TokenType.RPAREN):
            args.append(self.expression())
            while self.match(TokenType.COMMA):
                args.append(self.expression())
        self.consume(TokenType.RPAREN, "Expected ')' after pieuvre action arguments.")
        return args

    def parse_id_list(self, keyword):
        """
        Accepte: extends Animal  OU  extends[Animal, Autre]
        """
        names = []
        if not self.check(TokenType.LBRACKET):
            name_token = self.consume(TokenType.ID, f"Nom attendu apres {keyword}")
            names.append(name_token.value)
            while self.match(TokenType.COMMA):
                name_token = self.consume(TokenType.ID, f"Nom attendu apres virgule")
                names.append(name_token.value)
            return names
        self.consume(TokenType.LBRACKET, f"Attendu [ apres {keyword}")
        while True:
            name_token = self.consume(TokenType.ID, f"Nom attendu apres {keyword}")
            names.append(name_token.value)
            if not self.match(TokenType.COMMA):
                break
        self.consume(TokenType.RBRACKET, f"Attendu ] apres la liste")
        return names

    def parse_class_decl(self, type_class=TokenType.CLASS):
        #print("ici dans parse_class_decl")
        previous_context = self.in_object_context
        self.in_object_context = True
        is_abstract = (type_class == TokenType.ABSTRACT)

        if is_abstract:
            self.consume(TokenType.CLASS, "Mot-clé 'class' attendu")

        # 🔹 Nom de la classe
        name_token = self.consume(TokenType.ID, "Nom de la classe attendu")
        class_name = name_token.value
        self.pointer_classe = class_name
        previous_class = self.current_class
        self.current_class = class_name
        self.class_loaded.create_class(class_name)

        # -----------------------
        # 🔸 Héritage (extends)
        # -----------------------
        superclasses = []
        if self.match(TokenType.EXTENDS):
            superclasses = self.parse_id_list("extends")


        # -----------------------
        # 🔸 Implémentation (implements)
        # -----------------------
        interfaces = []
        if self.match(TokenType.IMPLEMENTS):
            interfaces = self.parse_id_list("implements")

            # 💡 Vérification de duplication précoce
            if superclasses and superclasses[0] in interfaces:
                raise self.error(name_token,
                                 f"L'élément '{superclasses[0]}' est déjà déclaré comme superclasse. Il ne peut être implémenté.")

        # -----------------------
        # 🔸 Corps de la classe
        # -----------------------
        self.consume(TokenType.LBRACE, "Attendu '{' pour ouvrir le corps de la classe")

        members = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():

            # 💡 Réduction des répétitions pour l'accès (utilise la fonction match() qui avance)
            access_modifier = self.match(TokenType.PRIVATE, TokenType.PUBLIC, TokenType.PROTECTED, TokenType.GLOBAL)
            access_modifier = self.previous().value if access_modifier else "public"

            #print("access_modifier", access_modifier)

            # override / abstract / static (stocke le résultat du match)
            is_override = self.match(TokenType.OVERRIDE)
            is_abstract_fun = self.match(TokenType.ABSTRACT)
            is_invoke = self.match(TokenType.INVOKE)
            is_static_fun_or_var = self.match(TokenType.STATIC)


            # Pieuvre blocks
            if self.match(TokenType.HEART):
                heart_name = None
                if self.check(TokenType.STR):
                    heart_name = self.advance().value
                self.consume(TokenType.LBRACE, "Attendu '{' apres heart")
                # Scope le registre anti-doublon de fonctions par heart (et
                # non plus seulement par classe) : sans ça, deux hearts du
                # même 'tent class' ne pouvaient jamais définir une fonction
                # du même nom (ex: 'status'), même dans des hearts différents.
                previous_class_for_heart = self.current_class
                self.current_class = f"{class_name}::heart::{heart_name or f'_anon_{len(members)}'}"
                heart_body = self.block()
                self.current_class = previous_class_for_heart
                members.append(HeartBlock(heart_body, name=heart_name))
            elif self.match(TokenType.CORE):
                self.consume(TokenType.LBRACE, "Attendu '{' apres core")
                # Tous les core{} d'une même classe partagent le même registre
                # (ils partagent aussi le même environnement à l'exécution).
                previous_class_for_core = self.current_class
                self.current_class = f"{class_name}::core"
                core_body = self.block()
                self.current_class = previous_class_for_core
                members.append(CoreBlock(core_body))
            elif self.match(TokenType.DIRECTOR):
                self.consume(TokenType.LBRACE, "Attendu '{' apres director")
                previous_class_for_director = self.current_class
                self.current_class = f"{class_name}::director"
                director_body = self.block()
                self.current_class = previous_class_for_director
                members.append(DirectorBlock(director_body))
            elif self.match(TokenType.SUPEVISOR):
                supervisor_name = None
                if self.check(TokenType.STR):
                    supervisor_name = self.advance().value
                self.consume(TokenType.LBRACE, "Attendu '{' apres supervisor")
                previous_class_for_supervisor = self.current_class
                self.current_class = f"{class_name}::supervisor::{supervisor_name or f'_anon_{len(members)}'}"
                supervisor_body = self.block()
                self.current_class = previous_class_for_supervisor
                members.append(SupervisorBlock(supervisor_body, name=supervisor_name))
            elif self.match(TokenType.AGENT):
                agent_name = None
                if self.check(TokenType.STR):
                    agent_name = self.advance().value
                self.consume(TokenType.LBRACE, "Attendu '{' apres agent")
                previous_class_for_agent = self.current_class
                self.current_class = f"{class_name}::agent::{agent_name or f'_anon_{len(members)}'}"
                agent_body = self.block()
                self.current_class = previous_class_for_agent
                members.append(AgentBlock(agent_body, name=agent_name))
            elif self.match(TokenType.SECRETARY):
                self.consume(TokenType.LBRACE, "Attendu '{' apres secretary")
                previous_class_for_secretary = self.current_class
                self.current_class = f"{class_name}::secretary"
                secretary_body = self.block()
                self.current_class = previous_class_for_secretary
                members.append(SecretaryBlock(secretary_body))
            # Variables
            elif self.match(TokenType.VAR):
                varde = self.var_decl(False, access_modifier=access_modifier, is_static=is_static_fun_or_var)
                members.append(varde)
                self.class_loaded.add_member(class_name, varde)
            elif self.match(TokenType.VAL):
                valde =  self.var_decl(True, access_modifier=access_modifier, is_static=is_static_fun_or_var)
                members.append(valde)
                self.class_loaded.add_member(class_name, valde)
            # Fonctions
            elif self.match(TokenType.FUN):
                func_stmt = self.fun_decl_stmt(
                    visibility=access_modifier,
                    # Retirer 'is_abstract=is_abstract,'
                    is_abstract_fun=is_abstract_fun,
                    is_static=is_static_fun_or_var
                )
                func_stmt.is_override = is_override
                func_stmt.is_invoke = is_invoke
                members.append(func_stmt)
                self.class_loaded.add_method(class_name, func_stmt)
            else:
                raise self.error(self.peek(), "Déclaration invalide dans une classe")


        self.consume(TokenType.RBRACE, "Attendu '}' pour fermer le corps de la classe")
        self.in_object_context = False

        # -----------------------
        # 🔍 Finalisation de l'AST
        # -----------------------

        # ✅ Accepte plusieurs classes parentes (héritage multiple)
        superclass_final = superclasses if superclasses else None

        # ✅ Accepte plusieurs interfaces implémentées
        interfaces_final = interfaces if interfaces else None

        class_decl = ClassDeclaration(
            name=class_name,
            members=members,
            superclass=superclass_final,
            interfaces=interfaces_final,
            is_abstract=is_abstract
        )

        #print(self.class_loaded.classes[self.pointer_classe]["members"][0])
        self.current_class = previous_class
        return class_decl

    def parse_interface_decl(self):
        name_token = self.consume(TokenType.ID, "Nom de l'interface attendu")
        interface_name = name_token.value

        super_interfaces = []
        if self.match(TokenType.EXTENDS):
            # Utilisation de la nouvelle fonction utilitaire
            super_interfaces = self.parse_id_list("extends")
            #self.interface_loaded[interface_name] = super_interfaces

        self.consume(TokenType.LBRACE, "Attendu '{' pour ouvrir le corps de l'interface")

        methods = []
        #print(f"INTERFACE : {interface_name}")
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            if self.match(TokenType.FUN):
                func_decl = self.fun_decl_stmt(visibility="public", is_abstract_fun=True)
                methods.append(func_decl)
                #print(f"fun :{func_decl.name}")
                #self.interface_loaded[interface_name] = func_decl.name
            elif self.match(TokenType.VAL) or self.match(TokenType.VAR):
                prop_decl = self.var_decl(self.previous().type == TokenType.VAL, access_modifier="public", is_static=False)
                methods.append(prop_decl)
                #print(f"val | var :{prop_decl.name}")
                #self.interface_loaded[interface_name].append(prop_decl)
            elif self.match(TokenType.SEMICOLON):
                continue
            else:
                raise self.error(self.peek(),
                                 "Les interfaces ne peuvent contenir que des signatures de méthode abstraites ou des propriétés.")

        self.consume(TokenType.RBRACE, "Attendu '}' pour fermer l'interface")

        return InterfaceDeclaration(name=interface_name, methods=methods, super_interfaces=super_interfaces)

    def parse_enum_decl(self):
        name_token = self.consume(TokenType.ID, "Nom de l'enum attendu")
        enum_name = name_token.value
        self.consume(TokenType.LBRACE, "Attendu '{' pour ouvrir l'enum")

        previous_context = self.in_object_context
        self.in_object_context = True  # ✅ active le contexte objet

        # --- Lecture des constantes ---
        values = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            ident = self.consume(TokenType.ID, "Nom de constante attendu").value
            args = []
            if self.match(TokenType.LPAREN):
                if not self.check(TokenType.RPAREN):
                    while True:
                        args.append(self.expression())
                        if not self.match(TokenType.COMMA):
                            break
                self.consume(TokenType.RPAREN, "Attendu ')' après les arguments de la constante enum")
            values.append((ident, args))
            #self.enume_loaded[values] = (ident, args)

            if self.match(TokenType.SEMICOLON):
                break
            if not self.match(TokenType.COMMA):
                break

        # --- Lecture des champs / méthodes ---
        fields = []
        methods = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            visibility = self.match(TokenType.PRIVATE, TokenType.PUBLIC)
            visibility = self.previous().value if visibility else "public"
            if self.match(TokenType.VAL, TokenType.VAR):
                is_mutable = self.previous().type == TokenType.VAR
                name = self.consume(TokenType.ID, "Nom du champ attendu").value
                self.consume(TokenType.COLON, "':' attendu après le nom du champ")
                type_name = self.consume_type()
                var_decl = VarDecl(name=name, type_=type_name, value=None, is_constant=is_mutable, access_modifier=visibility, is_static=False)
                fields.append(var_decl)
                #self.enume_loaded[fields]= (var_decl)

            elif self.match(TokenType.FUN):
                funct = self.fun_decl_stmt(visibility=visibility)
                methods.append(funct)
                #self.enume_loaded[methods] = (funct)
            else:
                self.advance()

        self.consume(TokenType.RBRACE, "Attendu '}' pour fermer l'enum")

        self.in_object_context = previous_context  # ✅ on restaure le contexte précédent

        return EnumDeclaration(name=enum_name, values=values, fields=fields, methods=methods)

    def statement(self):
        if self.match(TokenType.ACTIVATE):
            class_name = self.consume(TokenType.ID, "Nom de classe attendu après 'activate'")
            return ActivateStmt(class_name.value)
        elif self.match(TokenType.BREAK):
            return BreakNode()
        elif self.match(TokenType.CONTINUE):
            return ContinueNode()
        elif self.check(TokenType.IF):
            return self.if_statement()
        elif self.check(TokenType.SWITCH):
            return self.switch_statement()
        elif self.check(TokenType.WHILE):
            return self.while_statement()
        elif self.check(TokenType.FOR):
            return self.for_stmt()
        elif self.check(TokenType.LOOP) or self.check(TokenType.FILTER_LOOP) or self.check(
                TokenType.FILTER_WHILE) or self.check(TokenType.SORT_LOOP) or self.check(
                TokenType.PERMUTE_LOOP) or self.check(TokenType.PERMUTE_WHILE) or self.check(
                TokenType.CIRCULAR_LOOP) or self.check(TokenType.SLEEPING_LOOP) or self.check(
                TokenType.SPIRAL) or self.check(TokenType.WAVE) or self.check(TokenType.SECTORS):
            return self.smart_loop()
        elif self.check(TokenType.ID) and self.check_next(TokenType.EQ):
            # print("Debug : statement assignment_stmt")
            return self.assignment_stmt()
        elif self.check(TokenType.TRY):
            return self.try_stmt()
        elif self.check(TokenType.ID) and self.check_next(TokenType.PLUSEQ, TokenType.MINUSEQ, TokenType.STAREQ,
                                                          TokenType.SLASHEQ):
            return self.augmented_assignment()
        elif self.check_next(TokenType.PLUSPLUS, TokenType.MINUSMINUS):
            return self.postfix()
        elif self.match(TokenType.FUN):  # ✅ AJOUTE CECI*
            # print("Debug : dans le parser statement Fun Parser")
            func = self.fun_decl_stmt()  # ⬅︎ appelle le parseur de fonction
            return func
        elif self.match(TokenType.RETURN):
            retn = self.return_stmt()
            return retn
        elif self.match(TokenType.VAR):
            return self.var_decl(False)
        elif self.match(TokenType.VAL):
            return self.var_decl(True)
        elif self.match(TokenType.LBRACKET):
            elements = []
            if not self.check(TokenType.RBRACKET):
                elements.append(self.expression())
                while self.match(TokenType.COMMA):
                    elements.append(self.expression())
            self.consume(TokenType.RBRACKET, Fore.CYAN + "Attendu ']' pour fermer la liste" + Style.RESET_ALL)
            return ListLiteral(elements)
        elif self.check(TokenType.THROW):
            return self.throw_stmt()
        elif self.match(TokenType.PRINT):
            return self.print_stmt()
        elif self.check(TokenType.ELSE) or self.check(TokenType.ELIF) or self.check(TokenType.RBRACE):
            # Ces tokens sont gérés dans les blocs (ex : if/else), pas comme statements principaux
            return None
        elif self.match(TokenType.IMPORT):
            return self.parse_import_stmt()
        elif self.match(TokenType.FROM):
            return self.parse_from_import()
        elif self.match(TokenType.USE):
            return self.parse_use()
        elif self.match(TokenType.INJECT):
            return self.inject_stmt()
        if self.match(TokenType.DELETE):
            return self.delete_statement()
        else:
            return self.expression_stmt()

    def return_stmt(self):
        keyword = self.previous()
        value = None
        if not self.check(TokenType.SEMICOLON) and not self.check(TokenType.RBRACE):
            value = self.expression()
        return ReturnStmt(keyword, value)

    def assignment_stmt(self, return_expr_only=False):
        name = self.consume(TokenType.ID, Fore.CYAN +"Attendu un nom de variable"+ Style.RESET_ALL)
        if self.check(TokenType.PLUS):
            self.consume(TokenType.PLUS, Fore.CYAN +"Attendu '++'"+ Style.RESET_ALL)
            value = self.expression()
        elif self.check(TokenType.MINUS):
            self.consume(TokenType.MINUS, Fore.CYAN +"Attendu '--'"+ Style.RESET_ALL)
            value = self.expression()
        else:
            self.consume(TokenType.EQ, Fore.CYAN +"Attendu '='"+ Style.RESET_ALL)
            value = self.expression()
        assign_expr = None

        if isinstance(value, Variable):
            assign_expr = Assignment(name=name.value, value=value, assign_type=TokenType.EQ)
        if isinstance(value, BinaryOp):
            assign_expr = Assignment(name=name.value, value=value, assign_type=TokenType.EQ)
        elif isinstance(value, DictLiteral):
            assign_expr = Assignment(name=name.value, value=value, assign_type=TokenType.COLON)
        elif isinstance(value, Literal):
            assign_expr = Assignment(name=name.value, value=value, assign_type=TokenType.COLON)
        elif isinstance(value, GetExpr):
            return SetExpr(value.object, value.index, value)
        if return_expr_only:
            return assign_expr
        return ExpressionStmt(assign_expr)

    def augmented_assignment(self, return_expr_only=False):
        name = self.consume(TokenType.ID, Fore.CYAN +"Attendu un nom de variable"+ Style.RESET_ALL)
        operator = self.advance()
        value = self.expression()

        assign_expr = AugmentedAssign(name=name.value, operator=operator, value=value)

        if return_expr_only:
            return assign_expr
        return ExpressionStmt(assign_expr)

    # parser.py
    def print_stmt(self):
        self.consume(TokenType.LPAREN, "'(' attendu après print")
        args, kwargs = self.parse_arguments()
        self.consume(TokenType.RPAREN, "')' attendu après les arguments de print")
        return PrintStmt(args, kwargs=kwargs)

    def parse_arguments(self):
        args = []
        kwargs = {}
        while not self.check(TokenType.RPAREN):
            # --- argument keyword : color=...
            if self.check(TokenType.ID) and self.peek_next().type == TokenType.EQ:
                key = self.consume(TokenType.ID, "Attendu un identifiant").value
                self.consume(TokenType.EQ, "Attendu '=' dans argument nommé")
                value = self.expression()
                kwargs[key] = value
            else:
                args.append(self.expression())

            if not self.match(TokenType.COMMA):
                break
        return args, kwargs

    def peek_next(self):
        if self.current + 1 < len(self.tokens):
            return self.tokens[self.current + 1]
        return Token(TokenType.EOF, "", self.peek().line, self.peek().column)

    def expression_until(self, stop_types):
        expr_tokens = []
        depth = 0  # Pour suivre parenthèses imbriquées
        tok = any
        while not self.is_at_end():
            tok = self.peek()
            if tok.type in stop_types and depth == 0:
                break
            if tok.type == TokenType.LPAREN:
                depth += 1
            elif tok.type == TokenType.RPAREN:
                depth -= 1
            expr_tokens.append(self.advance())
        # Crée un sous-parser si besoin, ou parse expr_tokens manuellement
        saved_tokens = self.tokens
        saved_current = self.current
        self.tokens = expr_tokens + [Token(TokenType.EOF, '', tok.line, tok.column)]
        self.current = 0
        try:
            expr = self.expression()
        finally:
            self.tokens = saved_tokens
            self.current = saved_current
        return expr

    def expression_current_line(self):
        start_line = self.peek().line
        expr_tokens = []
        depth = 0
        tok = self.peek()

        while not self.is_at_end():
            tok = self.peek()
            if depth == 0 and (tok.type == TokenType.RBRACE or tok.line != start_line):
                break
            if tok.type == TokenType.LPAREN:
                depth += 1
            elif tok.type == TokenType.RPAREN:
                depth -= 1
            expr_tokens.append(self.advance())

        if not expr_tokens:
            self.error(tok, Fore.CYAN + f"Expression attendue" + Style.RESET_ALL)

        saved_tokens = self.tokens
        saved_current = self.current
        self.tokens = expr_tokens + [Token(TokenType.EOF, '', tok.line, tok.column)]
        self.current = 0
        try:
            expr = self.expression()
        finally:
            self.tokens = saved_tokens
            self.current = saved_current
        return expr

    def try_stmt(self):
        self.consume(TokenType.TRY, Fore.CYAN +"Attendu 'try'"+ Style.RESET_ALL)
        self.consume(TokenType.LBRACE, Fore.CYAN +"Attendu '{' après 'try'"+ Style.RESET_ALL)
        try_block = self.block()

        catch_block = []
        finally_block = []
        has_catch = False
        has_finally = False
        error_var = None
        if self.match(TokenType.CATCH):
            has_catch = True
            #self.consume(TokenType.CATCH, "Attendu 'catch' après bloc 'try'")
            if self.match(TokenType.LPAREN):
                error_var = self.consume(TokenType.ID, "Attendu identifiant dans 'catch(err)'"+ Style.RESET_ALL).value
                self.consume(TokenType.RPAREN, "Attendu ')' après 'catch(err)'"+ Style.RESET_ALL)
            self.consume(TokenType.LBRACE, "Attendu '{' après 'catch'"+ Style.RESET_ALL)
            catch_block = self.block()


        if self.match(TokenType.FINALLY):
            has_finally = True
            self.consume(TokenType.LBRACE, Fore.CYAN +"Attendu '{' après 'finally'"+ Style.RESET_ALL)
            finally_block = self.block()

        if not has_catch and not has_finally:
            raise self.error(self.peek(), "Attendu 'catch' ou 'finally' après bloc 'try'")

        return TryCatchFinallyStmt(try_block=try_block, catch_block=catch_block ,finally_block=finally_block, error_var=error_var)

    def expression_stmt(self):
        expr = self.expression()
        return ExpressionStmt(expr)

    def throw_stmt(self):
        self.consume(TokenType.THROW, Fore.CYAN +"Attendu 'throw'")

        if self.match(TokenType.NEW):
            class_name = self.consume(TokenType.ID, Fore.CYAN +"Attendu nom de classe après 'new'").value
            self.consume(TokenType.LPAREN, Fore.CYAN +"Attendu '(' après nom de classe")
            args = []
            if not self.check(TokenType.RPAREN):
                args.append(self.expression())
                while self.match(TokenType.COMMA):
                    args.append(self.expression())
            self.consume(TokenType.RPAREN, Fore.CYAN +"Attendu ')' après arguments")
            return ThrowStmt(NewExpr(class_name, args))

        # throw simple
        expr = self.expression()
        return ThrowStmt(expr)

    def if_statement(self):
        self.consume(TokenType.IF, Fore.CYAN + "'if' attendu" + Style.RESET_ALL)
        self.consume(TokenType.LPAREN, Fore.CYAN + "'(' attendu après 'if'" + Style.RESET_ALL)
        condition = self.expression()
        self.consume(TokenType.RPAREN, Fore.CYAN + "')' attendu après la condition."+ Style.RESET_ALL+
                                                   Fore.YELLOW +"\nprobable que vous aviez mal saisi votre Condition" + Style.RESET_ALL)

        # ✅ Si le prochain token est une '{', on lit un bloc
        if self.check(TokenType.LBRACE):
            self.consume(TokenType.LBRACE, Fore.CYAN + "'{' attendu après ')'" + Style.RESET_ALL)
            then_branch = self.block()
        else:
            # ✅ Sinon, une seule instruction (comme "print(...)" ou "continue")
            then_branch = [self.statement()]

        elif_branches = []

        # ✅ Boucle pour accepter plusieurs elif
        while self.match(TokenType.ELIF):
            self.consume(TokenType.LPAREN, Fore.CYAN + "'(' attendu après 'elif'" + Style.RESET_ALL)
            elif_condition = self.expression()
            self.consume(TokenType.RPAREN, Fore.CYAN + "')' attendu après la condition de elif'" + Style.RESET_ALL)

            if self.check(TokenType.LBRACE):
                self.consume(TokenType.LBRACE, Fore.CYAN + "'{' attendu après ')' de elif" + Style.RESET_ALL)
                elif_body = self.block()
            else:
                elif_body = [self.statement()]

            elif_branches.append((elif_condition, elif_body))

        else_branch = None
        if self.match(TokenType.ELSE):
            if self.check(TokenType.LBRACE):
                self.consume(TokenType.LBRACE, Fore.CYAN + "'{' attendu après 'else'" + Style.RESET_ALL)
                else_branch = self.block()
            else:
                else_branch = [self.statement()]

        return IfStmt(condition, then_branch, elif_branches, else_branch)

#-----------------------------------------
    def expression(self):
        expr = self.parse_ternary()
        while self.match(TokenType.RANGE):
            operator = TokenType.RANGE
            if self.match(TokenType.GT, TokenType.LT):
                operator = self.previous().type
            end =self.parse_ternary()

            step = None
            if self.match(TokenType.RANGE):
                if self.match(TokenType.GT, TokenType.LT):
                    operator = self.previous().type
                step = self.parse_ternary()  # Le troisième nombre après le deuxième '|'
            expr = RangeExpr(expr, end, operator, step)
        return expr

    def parse_ternary(self):
        expr = self.parse_equality()
        if self.match(TokenType.QUESTION):
            then_expr = self.expression()
            self.consume(TokenType.COLON, Fore.CYAN +"':' attendu dans l'expression ternaire"+ Style.RESET_ALL)
            else_expr = self.expression()
            return TernaryExpr(expr, then_expr, else_expr)
        return expr

    def parse_equality(self):
        expr = self.parse_comparison()
        #if self.match(TokenType.NOT):
        #    if self.match(TokenType.IN):
        #        operator = TokenType.NOT_IN
        #        right = self.parse_term()
        #        return BinaryOp(expr, operator, right)

        while self.match(TokenType.IN):
            operator = self.previous()
            expr = self.value_matche_variable if self.value_matche_variable != None else expr
            right = self.parse_comparison()
            expr = BinaryOp(left=expr, operator=operator, right=right)
        return expr

    def parse_comparison(self):
        expr = self.parse_term()
        # --- gestion spéciale : IS EMPTY / IS NOT EMPTY ---
        if self.match(TokenType.BETWEEN):
            lower = self.parse_term()
            self.consume(TokenType.AND, "Oups 'and' apres lower bound.")
            upper = self.parse_term()
            expr = self.value_matche_variable if self.value_matche_variable != None else expr
            return BetweenExpr(expr, lower, upper)
        if self.match(TokenType.IS):
            # --- IS TYPE ---
            if self.match(
                    TokenType.INT,
                    TokenType.STRING,
                    TokenType.FLOAT,
                    TokenType.BOOL
            ):
                type_token = self.previous()
                expr = self.value_matche_variable if self.value_matche_variable != None else expr
                return IsTypeExpr(expr, type_token)
            elif self.match(TokenType.NOT):
                if self.match(TokenType.IS_EMPTY):
                    expr = self.value_matche_variable if self.value_matche_variable != None else expr
                    return IsEmptyExpr(expr, negate=True)
            elif self.match(TokenType.IS_EMPTY):
                expr = self.value_matche_variable if self.value_matche_variable != None else expr
                return IsEmptyExpr(expr, negate=False)
            else:
                # cas normal : x is y
                operator = self.previous()
                right = self.parse_term()
                expr = self.value_matche_variable if self.value_matche_variable != None else expr
                return BinaryOp(expr, operator, right)

        # --- gestion spéciale :  NOT ... ---
        if self.match(TokenType.NOT):
            if self.match(TokenType.IN):
                operator = TokenType.NOT_IN
                right = self.parse_term()
                expr = self.value_matche_variable if self.value_matche_variable != None else expr
                return BinaryOp(expr, operator, right)
            if self.match(TokenType.IS_EMPTY):
                expr = self.value_matche_variable if self.value_matche_variable != None else expr
                return IsEmptyExpr(expr, negate=True)
            if self.match(TokenType.IS_LIKE):
                operator = TokenType.NOT_LIKE
                right = self.parse_term()
                expr = self.value_matche_variable if self.value_matche_variable != None else expr
                return BinaryOp(left=expr, operator=operator, right=right)
            if self.match(TokenType.MATCHES):
                pattern = self.parse_term()
                expr = self.value_matche_variable if self.value_matche_variable != None else expr
                return MatchesExpr(expr, pattern)

        if self.match(TokenType.MATCHES):
            pattern = self.parse_term()
            expr = self.value_matche_variable if self.value_matche_variable != None else expr
            return MatchesExpr(expr, pattern)

        # --- valeur __matches_db__ NomDB [threshold N] [autocreate CATEGORIE]
        #     [insert CATEGORIE | update | delete | reflexion | select] { motif } [set { ... }] ---
        if self.match(TokenType.IS_MATCHES_DB):
            db_name_token = self.consume(TokenType.ID, "Nom de la base attendu après '__matches_db__'")
            threshold_expr = None
            if self.match(TokenType.THRESHOLD):
                threshold_expr = self.parse_term()
            autocreate_category = None
            if self.match(TokenType.AUTOCREATE):
                autocreate_token = self.consume(TokenType.ID, "Nom de catégorie attendu après 'autocreate'")
                autocreate_category = autocreate_token.value

            # --- Verbe de la requête : select (défaut) / insert / update / delete / reflexion ---
            verb = "select"
            if self.match(TokenType.DELETE):
                verb = "delete"
            elif self.check(TokenType.ID) and self.peek().value in ("insert", "update", "reflexion", "select"):
                verb_token = self.advance()
                verb = verb_token.value
                if verb == "insert":
                    cat_token = self.consume(TokenType.ID, "Nom de catégorie attendu après 'insert'")
                    autocreate_category = cat_token.value  # 'insert' réutilise le mécanisme d'autocreate

            self.consume(TokenType.LBRACE, "'{' attendu après le nom de la base dans __matches_db__")
            motif = self.parse_db_motif()
            self.consume(TokenType.RBRACE, "'}' attendu pour fermer le motif __matches_db__")

            set_clause = None
            if verb == "update":
                set_kw = self.consume(TokenType.ID, "'set' attendu après le motif d'un update __matches_db__")
                if set_kw.value != "set":
                    self.error(set_kw, "'set { ... }' attendu après le motif d'un update __matches_db__")
                set_clause = self.parse_set_clause()

            expr = self.value_matche_variable if self.value_matche_variable != None else expr
            return MatchesDbExpr(expr, db_name_token.value, motif, threshold=threshold_expr,
                                  autocreate=autocreate_category, verb=verb, set_clause=set_clause)

        # opérateurs classiques
        while self.match(
                TokenType.GT,
                TokenType.GE,
                TokenType.LT,
                TokenType.LE,
                TokenType.EQEQ,
                TokenType.NE,
                TokenType.IS_LIKE,
                TokenType.OR
        ):
            operator = self.previous()
            right = self.parse_term()
            expr = self.value_matche_variable if self.value_matche_variable != None else expr
            expr = BinaryOp(expr, operator, right)

        return expr

    def parse_match_expr(self):
        value = self.expression()
        self.consume(
            TokenType.ARROW, Fore.YELLOW +f"Oups "+ Style.RESET_ALL +
                             Fore.RED +f"'=>'"+ Style.RESET_ALL +
                             Fore.LIGHTWHITE_EX +f" apres match value"+ Style.RESET_ALL
        )
        self.consume(TokenType.LBRACE, "Oups '{' apres match expression.")
        cases = []
        else_branch = None

        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            if self.match(TokenType.ELSE):
                self.consume(TokenType.ARROW, "Oups '=>' apres 'else'")
                else_branch = self.expression_current_line()
                break

            # Patterns
            patterns = []
            # Premier pattern
            patterns.append(self.parse_match_pattern())

            while self.match(TokenType.COMMA):
                patterns.append(self.parse_match_pattern())
            while self.match(TokenType.AND):
                patterns.append(self.expression())

            self.consume(TokenType.ARROW, "Oups '=>' apres match case")

            body = self.expression_current_line()
            cases.append(MatchCase(patterns, body))

        self.consume(TokenType.RBRACE, "Oups '}' apres match block")

        if else_branch is None:
            self.error(self.peek(), "Match expression must have an else branch.")

        return MatchExpr(value, cases, else_branch)

    def parse_match_pattern(self):
        if self.match(TokenType.IN):
            base_pattern = InPattern(self.expression())
        elif self.match(TokenType.IS_LIKE):
            base_pattern = LikePattern(self.expression())
        elif self.match(TokenType.BETWEEN):
            lower = self.parse_term()
            self.consume(TokenType.AND, "Oups 'and' apres lower bound.")
            upper = self.parse_term()
            base_pattern = BetweenPattern(lower, upper)
        elif self.match(TokenType.MATCHES):
            base_pattern = RegexPattern(self.parse_term())
        elif self.match(TokenType.IS):
            if self.match(TokenType.INT, TokenType.STRING, TokenType.FLOAT, TokenType.BOOL):
                base_pattern = TypePattern(self.previous())
            else:
                self.error(self.peek(), "Type attendu apres 'is' dans match case")
        else:
            expr = self.expression()
            if isinstance(expr, RangeExpr):
                base_pattern = RangePattern(expr.start, expr.end, expr.step)
            else:
                base_pattern = ValuePattern(expr)

        # --- Guard support ---
        if self.match(TokenType.IF):
            guard_expr = self.expression()
            return GuardedPattern(base_pattern, guard_expr)

        return base_pattern

    # ------------------------------------------------------------------
    # __matches_db__ : motif { champ: pattern, ... }
    # ------------------------------------------------------------------
    def parse_db_motif(self):
        pairs = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            field_expr = self.expression()
            self.consume(TokenType.COLON, "':' attendu après le champ dans le motif __matches_db__")
            if self.match(TokenType.ARROW):
                ref_token = self.consume(TokenType.ID, "Nom de référence attendu après '=>' dans le motif")
                pattern = DbRefPattern(ref_token.value)
            else:
                pattern = self.parse_match_pattern()
            pairs.append((field_expr, pattern))
            self.match(TokenType.COMMA)
        return pairs

    # ------------------------------------------------------------------
    # update ... set { champ: nouvelle_valeur, ... }
    # ------------------------------------------------------------------
    def parse_set_clause(self):
        self.consume(TokenType.LBRACE, "'{' attendu après 'set'")
        pairs = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            key_expr = self.expression()
            self.consume(TokenType.COLON, "':' attendu après la clé dans set")
            value_expr = self.expression()
            pairs.append((key_expr, value_expr))
            self.match(TokenType.COMMA)
        self.consume(TokenType.RBRACE, "'}' attendu pour fermer set")
        return pairs

    # ------------------------------------------------------------------
    # neuron_loop NomDB { neuro_X{ enter{...} memory{...} elementor{...} out_X{...} } }
    # ------------------------------------------------------------------
    def parse_neuron_loop_decl(self):
        token = self.previous()
        name_token = self.consume(TokenType.ID, "Nom de la base attendu après 'neuron_loop'")
        self.consume(TokenType.LBRACE, "'{' attendu après le nom de la base neuron_loop")
        neurons = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            neurons.append(self.parse_neuron_block())
            self.match(TokenType.COMMA)
        self.consume(TokenType.RBRACE, "'}' attendu pour fermer neuron_loop")
        return NeuronLoopDecl(name=name_token.value, neurons=neurons, line=token.line, column=token.column)

    def parse_neuron_block(self):
        name_token = self.consume(TokenType.ID, "Nom de neurone attendu (ex: neuro_000000000001)")
        self.consume(TokenType.LBRACE, "'{' attendu après le nom du neurone")
        enter, memory, elementor, out_blocks = {}, {}, {}, {}
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            section_token = self.consume(TokenType.ID, "Section attendue (enter/memory/elementor/out_X) dans le neurone")
            section_name = section_token.value
            if section_name == "enter":
                enter, _ = self.parse_port_block()
            elif section_name == "memory":
                memory = self.parse_category_container()
            elif section_name == "elementor":
                elementor = self.parse_category_container()
            elif section_name.startswith("out"):
                ports, target = self.parse_port_block()
                out_blocks[section_name] = {"ports": ports, "target": target}
            else:
                self.error(section_token, f"Section inconnue '{section_name}' dans un bloc neuron_loop")
            self.match(TokenType.COMMA)
        self.consume(TokenType.RBRACE, "'}' attendu pour fermer le neurone")
        return NeuronBlock(name=name_token.value, enter=enter, memory=memory, elementor=elementor, out_blocks=out_blocks)

    def parse_port_block(self):
        """enter{ alpha: 1  beta: 2 ... } / out_6{ target: neuro_2  alpha: 6 ... }
        — virgules optionnelles. 'target' déclare la synapse vers le neurone suivant."""
        self.consume(TokenType.LBRACE, "'{' attendu pour ouvrir un bloc de ports")
        ports = {}
        target = None
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            key_token = self.consume(TokenType.ID, "Nom de catégorie ou 'target' attendu")
            self.consume(TokenType.COLON, "':' attendu après le nom de catégorie")
            if key_token.value == "target":
                target_token = self.consume(TokenType.ID, "Nom de neurone cible attendu après 'target:'")
                target = target_token.value
            else:
                ports[key_token.value] = self.parse_term()
            self.match(TokenType.COMMA)
        self.consume(TokenType.RBRACE, "'}' attendu pour fermer le bloc de ports")
        return ports, target

    def parse_category_container(self):
        """memory{ alpha{...} beta{...} ... } ou elementor{ ... }"""
        self.consume(TokenType.LBRACE, "'{' attendu pour ouvrir memory/elementor")
        categories = {}
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            cat_token = self.consume(TokenType.ID, "Nom de catégorie attendu (alpha/beta/gamma/ohm/dzeta)")
            categories[cat_token.value] = self.parse_category_block()
            self.match(TokenType.COMMA)
        self.consume(TokenType.RBRACE, "'}' attendu pour fermer memory/elementor")
        return categories

    def parse_category_block(self):
        """alpha{ ref_el_1{ id: 1 => data: {...} } ref_el_2{...} }"""
        self.consume(TokenType.LBRACE, "'{' attendu pour ouvrir une catégorie")
        entries = {}
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            entry = self.parse_ref_entry()
            entries[entry.name] = entry
            self.match(TokenType.COMMA)
        self.consume(TokenType.RBRACE, "'}' attendu pour fermer une catégorie")
        return entries

    def parse_ref_entry(self):
        """ref_el_1{ id: 1 => data: { ... } }"""
        name_token = self.consume(TokenType.ID, "Nom de référence attendu (ex: ref_el_1)")
        self.consume(TokenType.LBRACE, "'{' attendu après le nom de la référence")

        id_field = self.consume(TokenType.ID, "Champ 'id' attendu dans une référence")
        if id_field.value != "id":
            self.error(id_field, "Champ 'id' attendu en premier dans une référence")
        self.consume(TokenType.COLON, "':' attendu après 'id'")
        id_expr = self.parse_term()

        self.consume(TokenType.ARROW, "'=>' attendu après l'id de la référence")
        data_field = self.consume(TokenType.ID, "Champ 'data' attendu après '=>'")
        if data_field.value != "data":
            self.error(data_field, "Champ 'data' attendu après '=>'")
        self.consume(TokenType.COLON, "':' attendu après 'data'")
        data_pairs = self.parse_neuron_data_dict()

        self.consume(TokenType.RBRACE, "'}' attendu pour fermer la référence")
        return RefEntry(name=name_token.value, id_expr=id_expr, data_pairs=data_pairs)

    def parse_neuron_data_dict(self):
        """{ "date": [], "odeur": => beta_2, ... }"""
        self.consume(TokenType.LBRACE, "'{' attendu pour ouvrir le bloc data")
        pairs = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            key_expr = self.expression()
            self.consume(TokenType.COLON, "':' attendu après la clé dans data")
            if self.match(TokenType.ARROW):
                ref_token = self.consume(TokenType.ID, "Nom de référence attendu après '=>'")
                value_node = RefValue(ref_token.value)
            else:
                value_node = self.expression()
            pairs.append((key_expr, value_node))
            self.match(TokenType.COMMA)
        self.consume(TokenType.RBRACE, "'}' attendu pour fermer le bloc data")
        return pairs

    def parse_term(self):
        expr = self.parse_factor()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous()
            right = self.parse_factor()
            #print(f"ici deja somme DONC {right}")
            expr = BinaryOp(left=expr, operator=operator, right=right)

        return expr

    def parse_factor(self):
        expr = self.parse_unary()
        while self.match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            operator = self.previous()
            right = self.parse_unary()
            expr = BinaryOp(left=expr, operator=operator, right=right)

        return expr

    def parse_unary(self):
        if self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            operand = self.parse_unary()
            return UnaryExpr(operator, operand)
        # Tu peux gérer les opérateurs unaires plus tard (ex : -x)
        expr = self.parse_primary()
        #print(f"ici deja expe DONC {expr}")
        return self.parse_postfix(expr)  # ← appel indispensable pour supporter noms[0]

    def parse_primary(self):
        if self.match(TokenType.NEW):
            class_name_token = self.consume(TokenType.ID, "Nom de classe attendu après 'new'")
            self.consume(TokenType.LPAREN, "Attendu '(' après le nom de classe")

            args = []
            if not self.check(TokenType.RPAREN):
                while True:
                    args.append(self.expression())  # parser un argument
                    if self.match(TokenType.COMMA):
                        continue
                    else:
                        break

            self.consume(TokenType.RPAREN, "Attendu ')' pour fermer l'instanciation")
            return NewInstanceExpr(class_name_token.value, args)
        elif self.match(TokenType.FUN):
            return self.fun_expr()
        elif self.match(TokenType.LAMBDA):
            return self.lambda_expr()
        elif self.match(TokenType.THIS):
            if not self.in_object_context:
                self.error(self.peek(), "Mot-clé 'thi' utilisé en dehors d'une classe")
            expr = ThisExpr(self.previous())
            # 🔹 retourner l'expression complète après toutes les cascade
            return expr
        elif self.match(TokenType.SUPER):
            # supporte:
            #   super.method(...)
            #   super[Parent1, Parent2].method(...)
            parent_names = None
            token = self.peek()
            if self.match(TokenType.LBRACKET):
                parent_names = []
                # au moins un ID attendu
                parent_token = self.consume(TokenType.ID, "Nom de super-classe attendu dans super[...]")
                parent_names.append(parent_token.value)
                while self.match(TokenType.COMMA):
                    parent_token = self.consume(TokenType.ID, "Nom de super-classe attendu dans super[...]")
                    parent_names.append(parent_token.value)
                self.consume(TokenType.RBRACKET, "Attendu ']' pour fermer la liste de superclasses")

            # ensuite on exige .method(...)
            self.consume(TokenType.DOT, "Attendu '.' après 'super' ou 'super[...]'")
            #name_token = self.consume(TokenType.ID, "Nom de méthode attendu après 'super.'")
            if self.check(TokenType.CONSTRUCT):
                name_token = self.consume(TokenType.CONSTRUCT, Fore.CYAN + "Nom de constructeur attendu après 'super[...].'" + Style.RESET_ALL)
            else:
                name_token = self.consume(TokenType.ID, Fore.CYAN + "Nom de méthode attendu après 'super[...].'" + Style.RESET_ALL)
            #name = name_token.value
            method_name = name_token.value

            # arguments (obligatoire parenthèses)
            self.consume(TokenType.LPAREN, "Attendu '(' après le nom de méthode")
            args = []
            if not self.check(TokenType.RPAREN):
                args.append(self.expression())
                while self.match(TokenType.COMMA):
                    args.append(self.expression())
            self.consume(TokenType.RPAREN, Fore.CYAN + "')' attendu après les arguments" + Style.RESET_ALL)

            return SuperCallExpr(parent_names=parent_names, method_name=method_name, arguments=args, line=token.line, column=token.column)
        elif self.match(TokenType.SUPER_FORCE):
            parent_names = None
            token = self.peek()
            if self.match(TokenType.LBRACKET):
                parent_names = []
                # au moins un ID attendu
                parent_token = self.consume(TokenType.ID, "[Erreur] Nom de classe attendu après super_force[")
                parent_names.append(parent_token.value)
                while self.match(TokenType.COMMA):
                    parent_token = self.consume(TokenType.ID, "[Erreur] Nom de classe attendu après super_force[")
                    parent_names.append(parent_token.value)
                self.consume(TokenType.RBRACKET, "[Erreur] ']' manquant après super_force[...]")

            # ensuite on exige .method(...)
            self.consume(TokenType.DOT, "Attendu '.' après 'super_force' ou 'super_force[...]'")
            #name_token = self.consume(TokenType.ID, "[Erreur] Nom de méthode attendu après super_force[...]'")
            if self.check(TokenType.CONSTRUCT):
                name_token = self.consume(TokenType.CONSTRUCT, Fore.CYAN + "Nom de constructeur attendu après 'super_force[...].'" + Style.RESET_ALL)
            else:
                name_token = self.consume(TokenType.ID, Fore.CYAN + "Nom de méthode attendu après 'super_force[...].'" + Style.RESET_ALL)

            method_name = name_token.value

            # arguments (obligatoire parenthèses)
            self.consume(TokenType.LPAREN, "Attendu '(' après le nom de méthode")
            args = []
            if not self.check(TokenType.RPAREN):
                args.append(self.expression())
                while self.match(TokenType.COMMA):
                    args.append(self.expression())
            self.consume(TokenType.RPAREN, Fore.CYAN + "')' attendu après les arguments" + Style.RESET_ALL)

            return SuperForceCallExpr(parents=parent_names, method_name=method_name, arguments=args, line=token.line, column=token.column)

            #return SuperForceCallExpr(parents, method_name, args, token.line, token.column)
        elif self.match(TokenType.IS_MATCHES):
            return self.parse_match_expr()
        elif self.match(TokenType.LPAREN):
            expr = self.expression()
            #print("expr Parentaise", expr)
            self.consume(TokenType.RPAREN, Fore.CYAN +"')' attendu "+ Style.RESET_ALL)
            return expr
        elif self.match(TokenType.LBRACKET):  # ← nouveau cas
            #print("Debug : dans le parser LBRACKET")
            elements = []
            if not self.check(TokenType.RBRACKET):
                elements.append(self.expression())
                while self.match(TokenType.COMMA):
                    elements.append(self.expression())
            self.consume(TokenType.RBRACKET, Fore.CYAN +"Attendu ']' pour fermer le tableau"+ Style.RESET_ALL)
            return ListLiteral(elements)
        elif self.match(TokenType.LBRACE):
            #print("Debug : dans le parser LBRACE")
            #self.consume(TokenType.LBRACE, Fore.CYAN +"Attendu '{' pour ouvrir le dictionnaire"+ Style.RESET_ALL)
            return self.parse_dict()  # ça retourne DictLiteral
        elif self.match(TokenType.NUMBER, TokenType.STR, TokenType.BOOLVAL, TokenType.NULLVAL):
            _tok = self.previous()
            if _tok.type == TokenType.BOOLVAL:
                return Literal(_tok.value == "true")
            if _tok.type == TokenType.NULLVAL:
                return Literal(None)
            return Literal(_tok.value)
        elif self.match(TokenType.FSTRING):
            raw_value = self.previous().value
            return FStringStmt(raw_value)
        elif self.match(TokenType.ID):
            token = self.previous()
            expr = Variable(self.previous().value, token.line, token.column)
            #print("Debug : dans parse_primary  ID = ", expr)
            return expr
        else:
            self.error(self.peek(), Fore.CYAN +f"Expressions invalide"+ Style.RESET_ALL)
            return None

    def parse_postfix(self, expr):
        while True:
            if self.match(TokenType.DOT):
                name_token = self.consume(TokenType.ID, "Nom de membre attendu après '.'")
                member_name = name_token.value
                if self.match(TokenType.LPAREN):  # Appel de méthode
                    args = []
                    if not self.check(TokenType.RPAREN):
                        args.append(self.expression())
                        while self.match(TokenType.COMMA):
                            args.append(self.expression())
                    self.consume(TokenType.RPAREN, "')' attendu après les arguments")
                    token = self.previous()

                    # --- Nouvelle logique : fonction natif, globale ou instance ? ---
                    # (isinstance(expr, Variable) est requis : seul un identifiant nommé
                    #  peut être un nom de module/classe connu. Le résultat d'un appel
                    #  chaîné — x.foo().bar() — n'a pas de '.name' et doit directement
                    #  emprunter le chemin générique MethodCall ci-dessous.)
                    if not isinstance(expr, ThisExpr) and isinstance(expr, Variable):
                        if (expr.name in self.modules_loaded) or (expr.name in self.modules_alias):
                            # print("Debug : dans le parser Appel de fonction natif", expr.name)
                            # 🔸 Appel de fonction d’un module injecté
                            expr =  ModuleFuncCall(
                                module=expr.name,
                                func=name_token.value,
                                arguments=args,
                                line=token.line,
                                column=token.column
                            )
                        # 🔸 Est-il importé depuis une classe definit ou une fonction global ?
                        elif expr.name in self.modules_import_loaded:
                            # 🔸 Appel d'un fonction depuis une classe importé d'ou un instance
                            if (len(self.class_loaded.classes) > 0 ) and (expr.name in self.class_loaded.classes[self.pointer_classe]["method"]):
                                # print("Debug : is MethodCall ? ", expr.name)
                                # 🔸 Méthode d’une instance
                                expr =  MethodCall(
                                    obj=expr,
                                    method=name_token.value,
                                    arguments=args,
                                    line=token.line,
                                    column=token.column
                                )
                            else:
                                expr =  ModuleFuncCall(
                                    module=expr.name,
                                    func=name_token.value,
                                    arguments=args,
                                    line=token.line,
                                    column=token.column
                                )
                        else:
                            #print(f"1) ===================================== {expr}")
                            expr = MethodCall(obj=expr, method=member_name, arguments=args, line=token.line, column=token.column)
                    else:
                        # 🔸 Méthode d'une instance variable (ou résultat d'un appel chaîné)
                        #print(f"2) ===================================== {expr}")
                        expr = MethodCall(obj=expr, method=member_name, arguments=args, line=token.line, column=token.column)
                else:  # accès champ
                    attr = AttributeAccess(expr, member_name)
                    # Si suivi de "=" → assignation d'attribut (this.x = val)
                    if self.match(TokenType.EQ):
                        value_expr = self.expression()
                        return AttributeAssignment(expr, member_name, value_expr)
                    # Si suivi de += -= *= /= → assignation augmentée d'attribut
                    elif self.check(TokenType.PLUSEQ) or self.check(TokenType.MINUSEQ) or \
                         self.check(TokenType.STAREQ) or self.check(TokenType.SLASHEQ):
                        op = self.advance()
                        value_expr = self.expression()
                        # a.x += v  ==  a.x = a.x + v
                        op_map = {
                            TokenType.PLUSEQ:  TokenType.PLUS,
                            TokenType.MINUSEQ: TokenType.MINUS,
                            TokenType.STAREQ:  TokenType.STAR,
                            TokenType.SLASHEQ: TokenType.SLASH,
                        }
                        rhs = BinaryOp(left=attr, operator=op, right=value_expr)
                        return AttributeAssignment(expr, member_name, rhs)
                    expr = attr
            elif self.match(TokenType.LBRACKET):
                index = self.expression()
                self.consume(TokenType.RBRACKET, Fore.CYAN +"Attendu ']' après l'index")
                # Vérifie si c’est une affectation indexée
                if self.match(TokenType.EQ):
                    value_expr = self.expression()
                    expr = IndexAssignment(obj=expr, index=index, value=value_expr)
                else:
                    expr = IndexAccess(obj=expr, index=index)
            # 🔹 Si pas de point → appel fonction globale
            elif self.match(TokenType.LPAREN):
                #print("Debug : dans le parser parse_primary LPAREN")
                args = []
                if not self.check(TokenType.RPAREN):
                    args.append(self.expression())
                    while self.match(TokenType.COMMA):
                        args.append(self.expression())
                self.consume(TokenType.RPAREN, "')' attendu après les arguments")

                # print("ici 1 creation de FuncCall dans le parser")
                # print(f"Debug : dans le parser dans parse_primary FuncCall name: {expr.name}  et args : {args}")
                expr = FuncCall(name=expr.name, arguments=args)
            else:
                break
        return expr

#----------------------------------------------
    def parse_dict(self):
        pairs = []
        if not self.check(TokenType.RBRACE):
            while True:
                key = self.expression()  # clé
                self.consume(TokenType.COLON, "':' attendu après la clé du dictionnaire")
                value = self.expression()  # valeur
                pairs.append((key, value))
                if not self.match(TokenType.COMMA):
                    break
        self.consume(TokenType.RBRACE, "'}' attendu après le dictionnaire")
        #print("Debug pairs : ",pairs)
        return DictLiteral(pairs)

    def parse_mapUpdate(self):
        pairs = []

        # 🔒 Ouverture du dictionnaire
        self.consume(TokenType.LBRACE, "'{' attendu pour ouvrir le dictionnaire")

        # 🔍 Lecture des paires clé:valeur
        if not self.check(TokenType.RBRACE):
            while True:
                key = self.expression()
                self.consume(TokenType.COLON, "':' attendu après la clé du dictionnaire")
                value = self.expression()
                pairs.append((key, value))
                # Si pas de virgule, on sort
                if not self.match(TokenType.COMMA):
                    break

        # 🔚 Fermeture du dictionnaire
        self.consume(TokenType.RBRACE, "'}' attendu après le dictionnaire")
        return DictLiteral(pairs)

    def parse_braced_expression(self):
        # Si c’est vide : {}
        if self.check(TokenType.RBRACE):
            self.advance()

            return DictLiteral({})

        # On regarde le premier élément pour deviner le type
        save_pos = self.current
        key_expr = self.expression()

        # S’il y a un ':' → dictionnaire
        if self.match(TokenType.COLON):
            # Retour à la position du début car parse_dict relit proprement
            self.current = save_pos - 1
            return self.parse_dict()

        # Sinon, c’est probablement un set
        # On reconstruit la liste d’éléments
        elements = [key_expr]
        while self.match(TokenType.COMMA):
            elements.append(self.expression())

        self.consume(TokenType.RBRACKET,
                     Fore.CYAN + "']' attendu à la fin de l’ensemble ou du dictionnaire" + Style.RESET_ALL)
        return SetLiteral(elements)

    def fun_expr(self):
        name = None  # 🔒 Fonction anonyme
        is_short = None  # 🔒 Fonction lambda
        self.consume(TokenType.LPAREN, Fore.CYAN + "'(' attendu après 'fun'" + Style.RESET_ALL)
        params = []
        if not self.check(TokenType.RPAREN):
            while True:
                is_mutable = False
                if self.match(TokenType.VAR):
                    is_mutable = True
                elif self.match(TokenType.VAL):
                    is_mutable = False
                param_name = self.consume(TokenType.ID, "Nom de paramètre attendu").value
                self.consume(TokenType.COLON, "':' attendu après le nom du paramètre")
                param_type = self.consume_type()
                default_value = None
                if self.match(TokenType.EQ):
                    default_value = self.expression()
                params.append((param_name, param_type, is_mutable, default_value))
                if not self.match(TokenType.COMMA):
                    break
        self.consume(TokenType.RPAREN, "')' attendu après les paramètres")
        return_type = None
        if self.match(TokenType.COLON):
            return_type = self.consume_type()

        self.consume(TokenType.LBRACE, "'{' attendu pour le corps de la fonction")
        body = self.block()

        if name is None:
            return AnonymousFunction(params, return_type, body)
        else:
            return FunDecl(name, params, return_type, body)

    def consume_type(self):
        if self.match(TokenType.INT):
            type_name = "int"
        elif self.match(TokenType.FLOAT):
            type_name = "float"
        elif self.match(TokenType.STRING):
            type_name = "string"
        elif self.match(TokenType.STR):
            type_name = "str"
        elif self.match(TokenType.CHAR):
            type_name = "char"
        elif self.match(TokenType.BOOL):
            type_name = "bool"
        elif self.match(TokenType.VOID):
            type_name = "void"
        elif self.match(TokenType.FUN):
            type_name = "fun"

        # ✅ AJOUT : reconnaissance des types définis par l'utilisateur
        elif self.match(TokenType.ID):
            type_name = self.previous().value

        else:
            raise self.error(self.peek(), "Attendu un type (int, float, string, bool, void, ou type personnalisé)")

        if self.match(TokenType.LBRACKET):
            self.consume(TokenType.RBRACKET, Fore.CYAN + "Attendu ']' après '[' dans le type tableau" + Style.RESET_ALL)
            type_name += "[]"

        return type_name

    def match(self, *types):
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False

    def consume(self, type_, message):
        if self.check(type_):
            return self.advance()
        self.error(self.peek(), message)

    def check(self, type_):
        if self.is_at_end():
            return False
        return self.peek().type == type_

    def check_next(self, *types):
        if self.current + 1 >= len(self.tokens):
            return False
        return self.tokens[self.current + 1].type in types

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self):
        return self.peek().type == TokenType.EOF

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def error(self, token, message):
        line_info = f"ligne {token.line}, colonne {token.column}" if token else "position inconnue"
        raise Exception(Fore.RED + f"{message} ({line_info})" + Style.RESET_ALL)

    def switch_statement(self):
        self.consume(TokenType.SWITCH, Fore.CYAN +"'switch' attendu"+ Style.RESET_ALL)
        self.consume(TokenType.LPAREN, Fore.CYAN +"'(' attendu après 'switch'"+ Style.RESET_ALL)
        expr = self.expression()
        self.consume(TokenType.RPAREN, Fore.CYAN +"')' attendu après l'expression du switch"+ Style.RESET_ALL)
        self.consume(TokenType.LBRACE, Fore.CYAN +"'{' attendu pour ouvrir le bloc de switch"+ Style.RESET_ALL)

        cases = []
        default_block = None

        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            if self.match(TokenType.CASE):
                if self.match(TokenType.LPAREN):
                    #self.consume(TokenType.LPAREN, Fore.CYAN + "'(' attendu après 'CASE'" + Style.RESET_ALL)
                    value = self.expression()
                    self.consume(TokenType.RPAREN, Fore.CYAN + "')' attendu après l'expression du CASE" + Style.RESET_ALL)
                    self.consume(TokenType.LBRACE, Fore.CYAN + "'{' attendu pour ouvrir le bloc de CASE" + Style.RESET_ALL)
                    block = self.block()
                    cases.append((value, block))
                else :
                    value = self.expression()
                    self.consume(TokenType.LBRACE, Fore.CYAN +"'{' attendu après case"+ Style.RESET_ALL)
                    block = self.block()
                    cases.append((value, block))
            elif self.match(TokenType.DEFAULT):
                self.consume(TokenType.LBRACE, Fore.CYAN +"'{' attendu après default"+ Style.RESET_ALL)
                default_block = self.block()
            else:
                self.error(self.peek(), "Attendu 'case' ou 'default' dans un switch")

        self.consume(TokenType.RBRACE, Fore.CYAN +"'}' attendu à la fin du switch"+ Style.RESET_ALL)
        return SwitchStmt(expression=expr, cases=cases, default_block=default_block)

    def while_statement(self):
        self.consume(TokenType.WHILE, Fore.CYAN +"'while' attendu"+ Style.RESET_ALL)
        self.consume(TokenType.LPAREN, Fore.CYAN +"'(' attendu après 'while'"+ Style.RESET_ALL)
        condition = self.expression()
        self.consume(TokenType.RPAREN, Fore.CYAN +"')' attendu après la condition"+ Style.RESET_ALL)
        if self.check(TokenType.LBRACE):
            self.consume(TokenType.LBRACE, "'{' attendu")
            body = self.block()
        else:
            body = [self.statement()]
        return WhileStmt(condition, body)

    def for_stmt(self):
        self.consume(TokenType.FOR, Fore.CYAN +"Attendu 'for'"+ Style.RESET_ALL)
        self.consume(TokenType.LPAREN, Fore.CYAN +"Attendu '(' après 'for'"+ Style.RESET_ALL)

        # Détection de la forme `for (item in iterable)`
        if self.check(TokenType.ID) and self.check_next(TokenType.IN):
            var_name = self.consume(TokenType.ID, Fore.CYAN +"Attendu un nom de variable"+ Style.RESET_ALL)
            self.consume(TokenType.IN, Fore.CYAN +"Attendu 'in'"+ Style.RESET_ALL)
            iterable_expr = self.expression()

            #if not isinstance(iterable_expr, RangeExpr) and not isinstance(iterable_expr, ListLiteral) and not isinstance(iterable_expr, Literal) and not isinstance(iterable_expr, Variable):
            #    raise self.error(self.peek(), f"Expression {iterable_expr} iterable invalide dans la boucle for.")

            self.consume(TokenType.RPAREN, Fore.CYAN +"Attendu ')' après expression iterable"+ Style.RESET_ALL)
            if self.check(TokenType.LBRACE):
                self.consume(TokenType.LBRACE, "'{' attendu")
                body = self.block()
            else:
                body = [self.statement()]  # Une seule instruction

            return ForEachStmt(var_name.value, iterable_expr, body)

        initializer = None
        if self.match(TokenType.VAR):
            initializer = self.var_decl(False)
        elif self.match(TokenType.VAL):
            initializer = self.var_decl(True)
        elif self.check(TokenType.ID):
            # Permet aussi les affectations normales sans var (ex: i = 0)
            initializer = self.assignment_stmt(return_expr_only=False)
        if self.check(TokenType.SEMICOLON):
            self.consume(TokenType.SEMICOLON, Fore.CYAN +"Attendu ';' après initialisation"+ Style.RESET_ALL)
        else:
            self.consume(TokenType.COMMA, Fore.CYAN +"Attendu ',' après initialisation"+ Style.RESET_ALL)

        condition = self.expression()

        if self.check(TokenType.SEMICOLON):
            self.consume(TokenType.SEMICOLON, Fore.CYAN +"Attendu ';' après initialisation"+ Style.RESET_ALL)
        else:
            self.consume(TokenType.COMMA, Fore.CYAN +"Attendu ',' après initialisation"+ Style.RESET_ALL)

        # --- incrément ---
        if self.check(TokenType.ID) and self.check_next(TokenType.PLUSPLUS, TokenType.MINUSMINUS):
            increment = self.postfix()
        elif self.check(TokenType.ID) and self.check_next(TokenType.PLUSEQ, TokenType.MINUSEQ):
            increment = self.augmented_assignment(True)
        else:
            increment = self.assignment_stmt(True)

        self.consume(TokenType.RPAREN, Fore.CYAN +"Attendu ')' après incrément"+ Style.RESET_ALL)
        self.consume(TokenType.LBRACE, Fore.CYAN +"'{' attendu pour délimiter le bloc de la for"+ Style.RESET_ALL)

        body = self.block()  # Liste de statements

        if increment:
            body.append(ExpressionStmt(increment))

        if not condition:
            condition = Literal(True)

        loop = WhileStmt(condition, body)

        if initializer:
            return BlockStmt([initializer, loop])
        else:
            return loop

    def postfix(self):
        expr = self.parse_primary()

        # form: variable ++
        if isinstance(expr, Variable):
            if self.match(TokenType.PLUSPLUS):
                return PostfixIncrement(expr.name)
            if self.match(TokenType.MINUSMINUS):
                return PostfixDecrement(expr.name)

        return expr

    # parser.py (méthode smart_loop)
    def smart_loop(self):

        # --- Reconnaître le type de boucle (mot-clé) ---
        if self.match(TokenType.LOOP):
            loop_kind = "loop"
        elif self.match(TokenType.FILTER_LOOP):
            loop_kind = "filterLoop"
        elif self.match(TokenType.FILTER_WHILE):
            loop_kind = "filterWhile"
        elif self.match(TokenType.SORT_LOOP):
            loop_kind = "sortLoop"
        elif self.match(TokenType.PERMUTE_LOOP):
            loop_kind = "permuteLoop"
        elif self.match(TokenType.PERMUTE_WHILE):
            loop_kind = "permuteWhile"
        elif self.match(TokenType.CIRCULAR_LOOP):
            loop_kind = "circularLoop"
        elif self.match(TokenType.CIRCULAR_WHILE):
            loop_kind = "circularWhile"
        elif self.match(TokenType.SLEEPING_LOOP):
            loop_kind = "sleepingLoop"
        elif self.match(TokenType.SPIRAL):
            loop_kind = "spiral"
        elif self.match(TokenType.WAVE):
            loop_kind = "wave"
        elif self.match(TokenType.SECTORS):
            loop_kind = "sectors"
        else:
            raise self.error(self.peek(), "Type de boucle attendu (loop, filterLoop, sortLoop, ...).")

        NEW_STYLE_KINDS = ("spiral", "wave", "sectors")

        var_name = None
        iterator = None

        if loop_kind in NEW_STYLE_KINDS:
            # Pas de parenthèses englobant "var in iterateur" pour ces 3
            # boucles (syntaxe voulue : 'spiral cell in matrix { ... }') —
            # seul le motif (x, y) destructuré utilise des parenthèses, et
            # uniquement autour de lui-même.
            if self.match(TokenType.LPAREN):
                first_name = self.consume(TokenType.ID, "Attendu un identifiant dans (x, y)").value
                self.consume(TokenType.COMMA, "Attendu ',' dans le motif (x, y)")
                second_name = self.consume(TokenType.ID, "Attendu un second identifiant dans (x, y)").value
                self.consume(TokenType.RPAREN, "Attendu ')' pour fermer (x, y)")
                var_name = (first_name, second_name)
            else:
                var_name = self.consume(TokenType.ID, "Attendu un identifiant").value
            self.consume(TokenType.IN, "Attendu 'in' dans la déclaration de boucle")
            iterator = self.expression()
        else:
            # --- ( ... ) pattern/iterator (forme historique) ---
            self.consume(TokenType.LPAREN, "Attendu '(' après le type de boucle")
            # pattern principal | accepte identifiant simple ou parenthèse de destructuration
            # Ici on implémente la forme simple : IDENT [in expr]
            if self.check(TokenType.ID):
                var_name = self.consume(TokenType.ID, "Attendu un identifiant").value
                if self.match(TokenType.IN):
                    iterator = self.expression()
            else:
                # possibilité d'étendre : (i, j in 0|10, ...) -> à implémenter si besoin
                raise self.error(self.peek(), "Attendu un identifiant dans la déclaration de boucle.")

            self.consume(TokenType.RPAREN, "Attendu ')' après la déclaration de boucle")

        # --- Modificateur optionnel (après ':' par exemple) ---
        modifier_condition = None
        modifier_name = None
        modifier_expr = None
        modifier_extra = None
        modifier_mode = None
        modifier_check = None
        modifier_where_permutloop = None
        modifier_until_expr = None
        bare_modifiers = None

        if loop_kind in NEW_STYLE_KINDS:
            # Modificateurs SANS ':' ni parenthèses, chaînables : from X Y,
            # count N, rows N, cols N, amplitude N, by X, parallel (drapeau).
            bare_modifiers = {}
            while True:
                if self.match(TokenType.FROM):
                    origin = self.consume(TokenType.ID, "Attendu 'center' ou 'top_left' après 'from'").value
                    direction = "clockwise"
                    if self.check(TokenType.ID) and self.peek().value in ("clockwise", "counterclockwise"):
                        direction = self.advance().value
                    bare_modifiers["from"] = {"origin": origin, "direction": direction}
                elif self.match(TokenType.COUNT):
                    bare_modifiers["count"] = self.expression()
                elif self.match(TokenType.ROWS):
                    bare_modifiers["rows"] = self.expression()
                elif self.match(TokenType.COLS):
                    bare_modifiers["cols"] = self.expression()
                elif self.match(TokenType.AMPLITUDE):
                    bare_modifiers["amplitude"] = self.expression()
                elif self.match(TokenType.PARALLEL):
                    bare_modifiers["parallel"] = True
                elif self.match(TokenType.BY):
                    bare_modifiers["by"] = self.consume(TokenType.ID, "Attendu 'row' ou 'column' après 'by'").value
                else:
                    break

        # si tu veux autoriser le modificateur sans ':', enlève la check sur COLON
        # ==== debu de reciperaton des parametre : bloc ou instruction unique ==
        if loop_kind not in NEW_STYLE_KINDS and self.match(TokenType.COLON):
            # le prochain token doit être un mot-clé modificateur
            if self.match(TokenType.WHERE):
                modifier_name = "where"
                self.consume(TokenType.LPAREN, "Attendu '(' après where")
                modifier_expr = self.expression()
                self.consume(TokenType.RPAREN, "Attendu ')' après expression where")
            elif  self.match(TokenType.WHENEVER):
                modifier_name = "whenever"
                self.consume(TokenType.LPAREN, "Attendu '(' après using")

                # récupérer une liste de paramètres simples : using(a, b, c)
                params = []
                while not self.check(TokenType.RPAREN):
                    # si identifiant attendu
                    if not self.check(TokenType.ID):
                        raise self.error(self.peek(), "Identifiant attendu dans whenever(...)")
                    p = self.expression()
                    params.append(p)
                    if not self.match(TokenType.COMMA, TokenType.AND, TokenType.OR):
                        break

                self.consume(TokenType.RPAREN, "Attendu ')' après whenever(...)")

                # stocke juste la liste de noms (strings)
                modifier_expr = params
                if self.match(TokenType.CHECK):
                    self.consume(TokenType.LPAREN, "Attendu '(' après using")

                    # récupérer une liste de paramètres simples : using(a, b, c)
                    params = []
                    while not self.check(TokenType.RPAREN):
                        # si identifiant attendu
                        if not self.check(TokenType.ID):
                            raise self.error(self.peek(), "Identifiant attendu dans check(...)")
                        p = self.expression()
                        params.append(p)
                        if not self.match(TokenType.COMMA, TokenType.AND, TokenType.OR):
                            break
                    self.consume(TokenType.RPAREN, "Attendu ')' après expression check")
                    modifier_check = params
            elif self.match(TokenType.BY):
                modifier_name = "by"
                self.consume(TokenType.LPAREN, "Attendu '(' après by")
                modifier_expr = self.expression()
                self.consume(TokenType.RPAREN, "Attendu ')' après expression by")
                # optional order asc/desc
                if self.match(TokenType.ORDER):
                    if self.match(TokenType.ASC):
                        modifier_extra = "asc"
                    elif self.match(TokenType.DESC):
                        modifier_extra = "desc"
                    else:
                        raise self.error(self.peek(), "Attendu 'asc' ou 'desc' après 'order'")

            elif self.match(TokenType.USING):
                modifier_name = "using"
                self.consume(TokenType.LPAREN, "Attendu '(' après using")
                # récupérer une liste de paramètres simples : using(a, b, c)
                params = []
                simple_identifiers_only = True
                while not self.check(TokenType.RPAREN):
                    # si identifiant attendu
                    if not self.check(TokenType.ID):
                        raise self.error(self.peek(), "Identifiant attendu dans using(...)")
                    p = self.consume(TokenType.ID, "Paramètre attendu")
                    params.append(p.value)
                    if not self.match(TokenType.COMMA, TokenType.AND):
                        break
                self.consume(TokenType.RPAREN, "Attendu ')' après using(...)")
                # stocke juste la liste de noms (strings)
                modifier_expr = params

                # --- MODE(random / chaos / cycle / reverse / stable / noise) ---
                if self.match(TokenType.MODE):
                    self.consume(TokenType.LPAREN, "Attendu '(' après mode")
                    if not self.check(TokenType.ID):
                        raise self.error(self.peek(), "Identifiant attendu dans mode(...)")
                    mode_name = self.consume(TokenType.ID, "Nom du mode attendu").value
                    self.consume(TokenType.RPAREN, "Attendu ')' après mode(...)")

                    modifier_mode = mode_name  # ex: "chaos", "stable"

                # stocke juste la liste de noms (strings)
                if self.match(TokenType.WHERE):
                    self.consume(TokenType.LPAREN, "Attendu '(' après using")
                    # récupérer une liste de paramètres simples : where(...)
                    params_where = []
                    while not self.check(TokenType.RPAREN):
                        p = self.expression()
                        params_where.append(p)
                        if not self.match(TokenType.COMMA, TokenType.AND, TokenType.OR):
                            break
                    self.consume(TokenType.RPAREN, "Attendu ')' après expression where")
                    modifier_where_permutloop = params_where



            elif self.match(TokenType.STEP):
                modifier_name = "step"
                self.consume(TokenType.LPAREN, "Attendu '(' après step")
                modifier_expr = self.expression()  # ex: i += 1 ou une assignation
                self.consume(TokenType.RPAREN, "Attendu ')' après step")
                if self.match(TokenType.UNTIL):
                    # Bug trouvé en testant : ça écrasait modifier_name/modifier_expr
                    # ('step' disparaissait totalement de stmt.modifiers dès qu'un
                    # 'until' suivait). On garde maintenant les deux séparément.
                    self.consume(TokenType.LPAREN, "Attendu '(' après until")
                    modifier_until_expr = self.expression()
                    self.consume(TokenType.RPAREN, "Attendu ')' après until")
            elif self.match(TokenType.WAIT_UNTIL):
                modifier_name = "waitUntil"
                self.consume(TokenType.LPAREN, "Attendu '(' après waitUntil")
                modifier_expr = self.expression()
                self.consume(TokenType.RPAREN, "Attendu ')' après waitUntil")
            else:
                raise self.error(self.peek(), "Modificateur de boucle inconnu après ':'")
        # ==== fin des parametrage : bloc ou instruction unique ==

        # ==== dubut du Corps : bloc ou instruction unique ==
        if self.check(TokenType.LBRACE):
            self.consume(TokenType.LBRACE, "Attendu '{' pour le corps de la boucle")
            body = self.block()
        else:
            # version courte (une instruction)
            body = [self.statement()]
        # ==== fin du Corps : bloc ou instruction unique ==

        # Construire l'AST : utilise SmartLoopStmt (alias de LoopStmt)
        stmt = SmartLoopStmt(
            kind=loop_kind,
            var_name=var_name,  # 👈 ici
            initializer=None,
            condition=None,
            increment=None,
            iterator=iterator,
            modifiers=bare_modifiers if bare_modifiers is not None else ({modifier_name: modifier_expr} if modifier_name else {}),
            filters=[],
            actions=[],
            step=None,
            body=body
        )

        # pour by/order on peut ajouter modifier_extra dans modifiers
        if modifier_extra:
            stmt.modifiers["order"] = modifier_extra
        if modifier_mode:
            stmt.modifiers["mode"] = modifier_mode
        if modifier_check:
            stmt.modifiers["check"] = modifier_check
        if modifier_where_permutloop is not None:
            stmt.modifiers["where"] = modifier_where_permutloop
        if modifier_until_expr is not None:
            stmt.modifiers["until"] = modifier_until_expr


        return stmt

    def block(self):
        statements = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            stmt = self.declaration()
            if stmt is not None:
                statements.append(stmt)
        self.consume(TokenType.RBRACE, Fore.CYAN +"'}' attendu à la fin du bloc"+ Style.RESET_ALL)
        return statements

    def synchronize(self):
        self.advance()
        while not self.is_at_end() and self.peek().type not in (
                TokenType.VAR,
                TokenType.IF,
                TokenType.PRINT,
                TokenType.ELSE
        ):
            self.advance()

    def fun_decl_stmt(
        self,
        visibility="public",
        is_abstract_fun=False,
        is_static=False
    ):
        token = self.previous()
        if self.check(TokenType.CONSTRUCT):
            name_token = self.consume(TokenType.CONSTRUCT, Fore.CYAN + "Nom de fonction attendu" + Style.RESET_ALL)
        elif self.check(TokenType.DESTRUCT):
            name_token = self.consume(TokenType.DESTRUCT, Fore.CYAN + "Nom de fonction attendu" + Style.RESET_ALL)
        else:
            name_token = self.consume(TokenType.ID, Fore.CYAN + "Nom de fonction attendu" + Style.RESET_ALL)
        name = name_token.value

        self.consume(TokenType.LPAREN, Fore.CYAN + "'(' attendu après le nom de la fonction" + Style.RESET_ALL)

        # Lecture des paramètres
        params = []
        if not self.check(TokenType.RPAREN):
            while True:
                is_mutable = False
                if self.match(TokenType.VAR):
                    is_mutable = True
                elif self.match(TokenType.VAL):
                    is_mutable = False

                param_name = self.consume(TokenType.ID,
                                          Fore.CYAN + "Nom de paramètre attendu" + Style.RESET_ALL).value
                self.consume(TokenType.COLON, Fore.CYAN + "':' attendu après le nom du paramètre" + Style.RESET_ALL)
                param_type = self.consume_type()

                default_value = None
                if self.match(TokenType.EQ):
                    default_value = self.expression()

                params.append((param_name, param_type, is_mutable, default_value))

                if not self.match(TokenType.COMMA):
                    break

        self.consume(TokenType.RPAREN, Fore.CYAN + "')' attendu après les paramètres" + Style.RESET_ALL)

        param_types = tuple(param_type for (_, param_type, _, _) in params)

        # Détermination du registre
        if self.current_class is None:
            registry = self.global_functions
        else:
            if self.current_class not in self.class_functions:
                self.class_functions[self.current_class] = {}
            registry = self.class_functions[self.current_class]

        if name not in registry:
            registry[name] = []

        signature = (param_types, is_static)

        if signature in registry[name]:
            raise Exception(
                f"Erreur: Fonction '{name}' déjà déclarée avec la même signature "
                f"\ndonc redondance de fonction '{name}' à la ligne {name_token.line}, colonne {name_token.column}"
            )

        # Type de retour optionnel
        if self.match(TokenType.COLON):

            return_type = self.consume_type()
        else:
            return_type = None

        # --------------------------------------------------------------------------------------------------
        # 🎯 LOGIQUE CLÉ : Si méthode marquée ABSTRAITE OU si la signature est suivie d'un ';' (pas de corps)
        # --------------------------------------------------------------------------------------------------
        # Si c’est une méthode abstraite (signature suivie de ';') — pas de corps
        # On définit 'is_abstract_fun' comme VRAI si le mot-clé est présent OU si on trouve un point-virgule (méthode sans corps)
        is_abstract_method = is_abstract_fun or self.match(TokenType.SEMICOLON)

        if is_abstract_method:
            #print("is_abstract_method", is_abstract_method)
            return FunDecl(
                name,
                params,
                return_type,
                None,
                visibility=visibility,
                is_abstract=True,  # Forcer à VRAI si is_abstract_method est VRAI
                is_static=is_static,
                line=token.line,
                column=token.column
            )

        # Expression courte (Logique inchangée)
        if self.match(TokenType.EQ):
            expr = self.expression()
            #print("ici fonction courte")
            fake_return_token = Token(TokenType.RETURN, "return", line=0, column=0)
            return_stmt = ReturnStmt(fake_return_token, expr)
            # Support des mots-clés supplémentaires
            func_decl = FunDecl(
                name,
                params,
                return_type,
                [return_stmt],
                visibility=visibility,
                is_static=is_static,
                is_abstract=False,
                line=token.line,
                column=token.column
            )

            func_decl.is_override = hasattr(self, "is_override") and self.is_override
            func_decl.is_invoke = hasattr(self, "is_invoke") and self.is_invoke

            registry[name].append(signature)
            return func_decl


        # Bloc normal (Logique inchangée)
        self.consume(TokenType.LBRACE,
                     Fore.CYAN + "'{' attendu pour ouvrir le corps de la fonction" + Style.RESET_ALL)
        body = self.block()

        # Support des mots-clés supplémentaires
        #print("is_static_method", is_static)
        func_decl = FunDecl(
            name,
            params,
            return_type,
            body,
            visibility=visibility,
            is_static=is_static,
            is_abstract=False,
            line=token.line,
            column=token.column
        )


        func_decl.is_override = hasattr(self, "is_override") and self.is_override
        func_decl.is_invoke = hasattr(self, "is_invoke") and self.is_invoke

        registry[name].append(signature)
        return func_decl

    def lambda_expr(self):
        self.consume(TokenType.LPAREN, "Parenthèse attendue après 'lambda'")
        params = []

        if not self.check(TokenType.RPAREN):
            while True:
                name = self.consume(TokenType.ID, "Nom de paramètre attendu").value
                param_type = None
                if self.match(TokenType.COLON):
                    param_type = self.consume_type()
                params.append((name, param_type))
                if not self.match(TokenType.COMMA):
                    break

        self.consume(TokenType.RPAREN, "')' attendu après les paramètres")

        # 🔹 Accepter optionnellement un type de retour
        return_type = None
        if self.match(TokenType.COLON):  # ex: `): int =>`
            return_type = self.consume_type()

        self.consume(TokenType.ARROW, "'=>' attendu après les paramètres")
        body_expr = self.expression()

        return LambdaExpr(params, body_expr, return_type)

    def parse_import_stmt(self):
        name_token = self.consume(TokenType.ID, "Nom de module attendu après 'import'")
        module_name = name_token.value

        if self.match(TokenType.STAR):
            return ImportStmt(module=module_name, names=["*"])


        # Cas avec alias : import utils as u
        if self.match(TokenType.AS):
            alias = self.consume(TokenType.ID, "Alias attendu après 'as'").value
            # Enregistrer le module dans la liste des modules chargés
            self.modules_import_loaded.add(alias)
            return ImportStmt(module=module_name, names=[(module_name, alias)])

        # Cas simple : import utils
        return ImportStmt(module=module_name, names=["*"])

    def parse_from_import(self):
        # on a consommé 'from' avant d'appeler
        module_name = self.consume(TokenType.ID, "Nom de module attendu après 'from'").value
        self.consume(TokenType.IMPORT, "Attendu 'import' après 'from . <module>'")
        if self.match(TokenType.STAR):
            return FromImportStmt(module=module_name, names=["*"])
        names = []
        while True:
            name = self.consume(TokenType.ID, "Nom de symbol à importer attendu").value
            alias = None

            # supporte "as alias"
            if self.match(TokenType.AS):
                alias = self.consume(TokenType.ID, "Oups alias").value

            names.append((name, alias) if alias else name)
            if not self.match(TokenType.COMMA):
                break
        # Enregistrer le module dans la liste des modules chargés
        self.modules_import_loaded.add(module_name)
        #self.modules_from_import_loaded.add(module_name)
        return FromImportStmt(module=module_name, names=names)

    # à revenir
    def parse_use(self):
        # use "path/to/file.okp"
        path_token = self.consume(TokenType.STR, "Chemin attendu après 'use'")
        return UseStmt(path_token.value)

    def inject_stmt(self):
        modules_with_alias = []

        # Lecture du premier module
        module_name = self.consume(TokenType.ID, "Nom de module attendu après 'inject'").value
        alias = None

        if self.match(TokenType.AS):  # gestion du alias
            alias = self.consume(TokenType.ID, "Nom d'alias attendu après 'as'").value

        self.modules_loaded.add(module_name)
        self.modules_alias.add(alias)
        self.modules_loaded_alias.add((module_name, alias))

        # Gestion des modules suivants séparés par des virgules
        while self.match(TokenType.COMMA):
            module_name = self.consume(TokenType.ID, "Nom de module attendu après ','").value
            alias = None
            if self.match(TokenType.AS):
                alias = self.consume(TokenType.ID, "Nom d'alias attendu après 'as'").value
            self.modules_loaded.add(module_name)
            self.modules_alias.add(alias)
            self.modules_loaded_alias.add((module_name, alias))

        return InjectStmt(self.modules_loaded_alias)

    def delete_statement(self):
        name_token = self.consume(TokenType.ID, "Nom de variable attendu après 'delete'")
        return DeleteStmt(name=name_token.value)
