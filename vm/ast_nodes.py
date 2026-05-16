# dans ast_nodes.py
from . lexer import Token
from  typing import List, Union, Optional, Dict, Any
from  dataclasses import dataclass, field


# --------------------
# ---- Expressions ----
@dataclass
class Expr:
    pass


@dataclass
class Variable(Expr):
    name: str
    line: str  # 🔹 Ajouter la ligne du code source
    column: str  # 🔹 Ajouter la ligne du code source


@dataclass
class ClassDeclaration:
    def __init__(self, name, members, superclass=None, interfaces=None, is_abstract=False):
        self.name = name
        self.members = members
        self.superclass = superclass or []
        self.interfaces = interfaces or []
        self.is_abstract = is_abstract

        # ⚙️ Séparation automatique des membres
        self.methods = []
        self.variables = []

        for m in members:
            if isinstance(m, FunDecl):
                m.parent = self  # ⚡ assignation du parent
                self.methods.append(m)
            else:
                self.variables.append(m)


@dataclass
class InterfaceDeclaration:
    def __init__(self, name, methods, super_interfaces=None):
        self.name = name
        self.methods = methods
        self.super_interfaces = super_interfaces or []

        for m in methods:
            m.parent = self  # ⚡ assignation parent pour règles 'invoke'


@dataclass
class TentClass:
    def __init__(self, class_decl):
        self.class_decl = class_decl
        self.name = class_decl.name
        self.body = class_decl.members


@dataclass
class TenClass:
    def __init__(self, class_decl):
        self.class_decl = class_decl
        self.name = class_decl.name
        self.body = class_decl.members


@dataclass
class HeartBlock:
    def __init__(self, body):
        self.body = body


@dataclass
class CoreBlock:
    def __init__(self, body):
        self.body = body


@dataclass
class IntentionStmt:
    def __init__(self, name, args):
        self.name = name
        self.args = args


@dataclass
class TentRandomStmt:
    def __init__(self, name, args):
        self.name = name
        self.args = args


@dataclass
class EnumDeclaration:
    def __init__(self, name, values, fields=None, methods=None):
        self.name = name  # Nom de l'enum (ex: Level)
        self.values = values  # Liste [(nom_const, [args])]
        self.fields = fields or []  # Liste de FieldDecl
        self.methods = methods or []  # Liste de FunDecl
        self.type = "enum"


@dataclass
class Field:
    def __init__(self, decl, value=None):
        self.decl = decl  # VarDecl ou None
        self.value = value if value is not None else getattr(decl, "value", None)

    @property
    def is_constant(self):
        return getattr(self.decl, "is_constant", False)

    @property
    def access_modifier(self):
        return getattr(self.decl, "access_modifier", "public")

    def __repr__(self):
        return f"Field(value={self.value}, const={self.is_constant}, access={self.access_modifier})"


@dataclass
class FieldMethode:
    def __init__(self, methodeName):
        self.methodeName = methodeName  # VarDecl ou None

    @property
    def visibility(self):
        return getattr(self.methodeName, "visibility", "public")

    def __repr__(self):
        return f"Field Methode (access={self.visibility})"


@dataclass
class NewInstanceExpr:
    def __init__(self, class_name, arguments=None):
        self.class_name = class_name  # str : nom de la classe
        self.arguments = arguments or []  # list : expressions pour le constructeur

    def __str__(self):
        return f"NewInstanceExpr({self.class_name}, args={self.arguments})"


@dataclass
class Instance:
    def __init__(self, klass):
        self.klass = klass
        self.fields = {
            name: Field(var_decl)
            for name, var_decl in klass.variables.items()
        }

        # 🔹 Méthodes liées à l'instance
        from . user_function import UserFunction
        self.methods = {}
        for method_decl in getattr(klass, "methods", []):
            self.methods[method_decl.name] = UserFunction(
                method_decl,
                closure=getattr(klass, "closure", None),
                instance=self  # 🔹 permet 'this'
            )


@dataclass
class GetAttrExpr:
    def __init__(self, object_expr, name):
        self.object_expr = object_expr
        self.name = name


@dataclass
class MethodCallExpr:
    def __init__(self, object_expr, method_name, arguments):
        self.object_expr = object_expr
        self.method_name = method_name
        self.arguments = arguments


@dataclass
class Stmt:
    pass


@dataclass
class VarDecl(Stmt):
    def __init__(self, name, type_, value, is_constant=False, access_modifier="public", is_static=False):
        self.name = name
        self.type_ = type_
        self.value = value
        self.is_constant = is_constant
        self.access_modifier = access_modifier  # "public", "private", "protected", "global"
        self.is_static = is_static

    def __str__(self):
        init_part = f" = {self.value}" if self.value is not None else ""
        return f"{self.access_modifier} {'val' if self.is_constant else 'var'} {self.name}: {self.type_}{init_part}"


@dataclass
class IndexAccess:
    def __init__(self, obj, index):
        self.obj = obj
        self.index = index


@dataclass
class IndexAssignment:
    def __init__(self, obj, index, value):
        self.obj = obj
        self.index = index
        self.value = value


@dataclass
class IndexThisAssignment:
    def __init__(self, expr_this, expr_name, index, value):
        self.expr_this = expr_this
        self.expr_name = expr_name
        self.index = index
        self.value = value


@dataclass
class Assignment:
    def __init__(self, name, value, assign_type):
        self.name = name  # str
        self.assign_type = assign_type
        self.value = value  # Expression

    def __repr__(self):
        return f"Assignment(name={self.name}, value={self.value})"


@dataclass
class AugmentedAssign(Stmt):
    def __init__(self, name, operator, value):
        self.name = name
        self.operator = operator
        self.value = value

    def __repr__(self):
        return f"AugmentedAssign(name={self.name}, operator={self.operator}, value={self.value})"


# ast_node.py
@dataclass
class PrintStmt(Stmt):
    expressions: List[Expr]
    kwargs: Dict[str, Expr] = field(default_factory=dict)  # stocke color, bg, style, etc.

    def __repr__(self):
        return f"PrintStmt(expressions={self.expressions!r}, kwargs={self.kwargs!r})"


# ast_node.py
@dataclass
class FStringStmt(Expr):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"FString(value={self.value!r})"


@dataclass
class Program:
    body: List[Stmt]


@dataclass
class BinaryOp(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator  # TokenType.IN ou NOTIN
        self.right = right

    def __repr__(self):
        return f"BinaryOp({self.left}, {self.operator}, {self.right})"


class Pattern:
    pass


class ValuePattern(Pattern):
    def __init__(self, expr):
        self.expr = expr


class RangePattern(Pattern):
    def __init__(self, start, end, step=None):
        self.start = start
        self.end = end
        self.step = step


class TypePattern(Pattern):
    def __init__(self, type_token):
        self.type_token = type_token


class BetweenPattern(Pattern):
    def __init__(self, lower, upper):
        self.lower = lower
        self.upper = upper


class RegexPattern(Pattern):
    def __init__(self, pattern_expr):
        self.pattern_expr = pattern_expr


class GuardedPattern(Pattern):
    def __init__(self, pattern, guard_expr):
        self.pattern = pattern
        self.guard_expr = guard_expr


class LikePattern(Pattern):
    def __init__(self, pattern):
        self.pattern = pattern


class InPattern(Pattern):
    def __init__(self, pattern):
        self.pattern = pattern


@dataclass
class UnaryExpr(Expr):
    operator: Token
    operand: Expr


@dataclass
class IsEmptyExpr:
    def __init__(self, expr, negate=False):
        self.expr = expr
        self.negate = negate

    def accept(self, visitor):
        return visitor.visit_IsEmptyExpr(self)


@dataclass
class BetweenExpr:
    def __init__(self, expr, lower, upper):
        self.expr = expr
        self.lower = lower
        self.upper = upper

    def accept(self, visitor):
        return visitor.visit_BetweenExpr(self)


@dataclass
class IsTypeExpr:
    def __init__(self, expr, type_token):
        self.expr = expr
        self.type_token = type_token

    def accept(self, visitor):
        return visitor.visit_IsTypeExpr(self)


@dataclass
class MatchCase:
    def __init__(self, patterns, body):
        self.patterns = patterns  # liste d'expressions
        self.body = body


@dataclass
class MatchesExpr:
    def __init__(self, expr, pattern):
        self.expr = expr
        self.pattern = pattern

    def accept(self, visitor):
        return visitor.visit_MatchesExpr(self)


@dataclass
class MatchExpr:
    def __init__(self, value, cases, else_branch):
        self.value = value
        self.cases = cases
        self.else_branch = else_branch

    def accept(self, visitor):
        return visitor.visit_MatchExpr(self)


@dataclass
class IfStmt(Stmt):
    def __init__(self, condition, then_branch, elif_branches, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.elif_branches = elif_branches  # Liste de tuples : (condition, block)
        self.else_branch = else_branch


@dataclass
class BreakNode:
    pass


@dataclass
class ContinueNode:
    pass


@dataclass
class TernaryExpr(Expr):
    def __init__(self, condition, then_expr, else_expr):
        self.condition = condition
        self.then_expr = then_expr
        self.else_expr = else_expr

    def __repr__(self):
        return f"TernaryExpr(cond={self.condition}, then={self.then_expr}, else={self.else_expr})"


@dataclass
class SwitchStmt:
    def __init__(self, expression, cases, default_block):
        self.expression = expression  # Expression de contrôle (ex: une variable)
        self.cases = cases  # Liste de tuples (valeur, bloc de statements)
        self.default_block = default_block  # Bloc de statements par défaut (ou None)

    def __repr__(self):
        return f"SwitchStmt(expr={self.expression}, cases={self.cases}, default={self.default_block})"


@dataclass
class WhileStmt:
    def __init__(self, condition, body):
        self.condition = condition  # Expression
        self.body = body  # Liste de statements

    def __repr__(self):
        return f"WhileStmt(condition={self.condition}, body={self.body})"


@dataclass
class PostfixIncrement(Expr):
    name: str


@dataclass
class PostfixDecrement(Expr):
    name: str


@dataclass
class ForEachStmt(Stmt):
    def __init__(self, var_name, iterable_expr, body):
        self.var_name = var_name
        self.iterable_expr = iterable_expr
        self.body = body


@dataclass
class RangeExpr(Expr):
    from . token_type import TokenType
    def __init__(self, start, end, operator=TokenType.RANGE, step=None):
        self.start = start
        self.end = end
        self.operator = operator
        self.step = step


@dataclass
class Literal(Expr):
    value: Union[int, float, str, bool]


@dataclass
class ListLiteral(Expr):
    def __init__(self, elements, line=None, column=None):
        self.elements = elements
        self.line = line  # 🔹 Ajouter la ligne du code source
        self.column = column  # 🔹 Ajouter la ligne du code source


@dataclass
class OktopiosList(list):
    def __init__(self, elements=None):
        super().__init__(elements)
        self.elements = elements or []

    def callMethod(self, method_name, args):
        if method_name == "add":
            self.add(args[0])
        elif method_name == "removeAtIndex":
            self.removeAtIndex(args[0])
        elif method_name == "remove":
            self.remove(args[0])
        elif method_name == "length":
            return self.length()
        elif method_name == "get":
            return self.get(args[0])
        elif method_name == "clear":
            self.clear()
        else:
            raise Exception(f"[Erreur] Méthode inconnue '{method_name}' pour OktopiosList")

    def add(self, value):
        self.elements.append(value)
        return None

    def get(self, index):
        return self.elements[index]

    def removeAtIndex(self, index):
        if 0 <= index < len(self.elements):
            del self.elements[index]
        else:
            raise Exception(f"[Erreur] Index hors limite : {index}")

    def remove(self, value):
        self.elements.remove(value)

    def length(self):
        return len(self.elements)

    def set(self, index, value):
        self.elements[index] = value

    def clear(self):
        self.elements.clear()

    def __str__(self):
        return str(self.elements)


# ---- NativeTypes.py ou directement dans interpreter.py ----
@dataclass
class OktopiosMap(dict):
    def __init__(self, entries=None):
        super().__init__(entries or {})
        self.entries = entries

    # --- Méthodes natives de base ---
    def get(self, key):
        return self.entries.get(key)

    def set(self, key, value):
        self.entries[key] = value

    def keys(self):
        return list(self.entries.keys())

    def values(self):
        return list(self.entries.values())

    def items(self):
        return list(self.entries.items())

    def clear(self):
        self.entries.clear()

    def remove(self, key):
        if key in self.entries:
            self.entries.pop(key)

    def length(self):
        return len(self.items())

    def callMethod(self, method_name, args):
        if method_name == "get":
            return self.get(args[0])
        elif method_name == "set":
            self.set(args[0], args[1])
        elif method_name == "remove":
            self.remove(args[0])
        elif method_name == "keys":
            return self.keys()
        elif method_name == "values":
            return self.values()
        elif method_name == "items":
            # print("debug 1 : length", len(self.entries))
            return self.items()
        elif method_name == "clear":
            return self.clear()
        elif method_name == "length":
            return self.length()
        else:
            raise Exception(f"[Erreur] Méthode inconnue '{method_name}' pour OktopiosMap")

    # --- Pour un affichage lisible ---
    def __repr__(self):
        return repr(self.entries)


@dataclass
class MapUpdateCall:
    def __init__(self, target, updates, line=None, column=None):
        self.target = target  # Expression ou Variable à mettre à jour
        self.updates = updates  # DictLiteral contenant les paires clé/valeur
        self.line = line  # Optionnel : ligne du code source
        self.column = column  # Optionnel : colonne du code source


@dataclass
class SetLiteral:
    def __init__(self, elements):
        self.elements = elements

    def __repr__(self):
        return f"SetLiteral({self.elements})"


@dataclass
class DictLiteral(dict):
    def __init__(self, pairs):
        super().__init__()
        self.pairs = pairs

    def set(self, key, value):
        self.pairs[key] = value


@dataclass
class BlockStmt:
    def __init__(self, statements):
        self.statements = statements


@dataclass
class ExpressionStmt:
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f"ExpressionStmt({self.expression})"


@dataclass
class ReturnStmt(Stmt):
    def __init__(self, keyword, value):
        self.keyword = keyword  # Token
        self.value = value  # Expression ou None


@dataclass
class TryCatchFinallyStmt(Stmt):
    def __init__(self, try_block, catch_block, finally_block, error_var=None):
        self.try_block = try_block
        self.catch_block = catch_block
        self.finally_block = finally_block
        self.error_var = error_var  # 💡 nom de la variable utilisée dans catch

    def __repr__(self):
        return f"SwitchStmt(trye={self.try_block}, catch_block={self.catch_block}), finally={self.finally_block}, err={self.error_var})"


@dataclass
class ThrowStmt(Stmt):
    def __init__(self, expr):
        self.expr = expr


@dataclass
class DeleteStmt(Stmt):
    def __init__(self, name):
        self.name = name


@dataclass
class FunDecl:
    def __init__(
            self,
            name,
            params,
            return_type,
            body,
            visibility="public",
            is_abstract=False,
            is_override=False,
            is_static=False,
            is_short=False,
            is_invoke=False,
            parent=None,
            line=None,
            column=None
    ):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body
        self.visibility = visibility
        self.is_abstract = is_abstract
        self.is_override = is_override
        self.is_static = is_static
        self.is_short = is_short
        self.is_invoke = is_invoke  # Important pour les interfaces
        self.parent = parent  # ⚡ Référence vers la classe ou interface parente
        self.line = line
        self.column = column


@dataclass
class FunctionDeclaration(Stmt):
    def __init__(self, name, params, return_type, body, is_short, visibility="public"):
        self.name = name
        self.params = params  # liste de (nom, type)
        self.return_type = return_type
        self.body = body  # liste d'instructions
        self.is_short = is_short
        self.visibility = visibility  # <- ajout


@dataclass
class AnonymousFunction:
    def __init__(self, params, return_type, body):
        self.params = params  # liste de tuples (name, type, is_mutable, default_value)
        self.return_type = return_type
        self.body = body  # liste d'instructions


@dataclass
class LambdaExpr(Expr):
    def __init__(self, params, body, return_type=None):
        self.params = params  # liste de noms de paramètres (strings)
        self.body = body  # expression
        self.return_type = return_type


@dataclass
class OktopiosException(Exception):
    def __init__(self, value):
        self.value = value


@dataclass
class NewExpr(Expr):
    def __init__(self, class_name, arguments):
        self.class_name = class_name
        self.arguments = arguments


@dataclass
class GetExpr(Expr):
    def __init__(self, object, index):
        self.object = object  # ex: "noms"
        self.index = index  # ex: 0


@dataclass
class SetExpr(Expr):
    def __init__(self, object, index, value):
        self.object = object  # ex: une Variable ou une autre expr (arr)
        self.index = index  # l'expression de l’index (ex: 2 ou i)
        self.value = value  # la valeur à assigner


@dataclass
class ThisExpr(Expr):
    def __init__(self, keyword):
        self.keyword = keyword  # Le token 'this'


@dataclass
class SuperCallExpr(Expr):
    """
    Représente : super.method(...)  ou  super[ParentA,ParentB].method(...)
    parent_names : None (pour super implicite) ou list[str] (noms de classes parents spécifiés)
    method_name : str
    arguments : list[Expr]
    """

    def __init__(self, parent_names, method_name, arguments, line, column):
        self.parent_names = parent_names  # None ou liste de strings
        self.method_name = method_name
        self.arguments = arguments
        self.line = line
        self.column = column


@dataclass
class SuperForceCallExpr:
    def __init__(self, parents, method_name, arguments, line, column):
        self.parents = parents  # liste de noms de classes (chaînes)
        self.method_name = method_name
        self.arguments = arguments  # liste d’expressions
        self.line = line
        self.column = column


@dataclass
class AttributeAccess(Expr):
    def __init__(self, obj_expr, name):
        self.obj_expr = obj_expr  # Expression, ex: ThisExpr
        self.name = name  # Nom de l'attribut


@dataclass
class AttributeAssignment(Stmt):
    def __init__(self, obj_expr, name, value):
        self.obj_expr = obj_expr  # Expression, ex: ThisExpr
        self.name = name  # Nom de l'attribut
        self.value = value  # Expression assignée


@dataclass
class CallExpr(Expr):
    def __init__(self, callee, arguments):
        self.callee = callee  # L'expression à appeler
        self.arguments = arguments  # Liste d'expressions


@dataclass
class FuncCall:
    def __init__(self, name, arguments, dists=None):
        self.name = name
        self.arguments = arguments
        self.dists = dists


@dataclass
class MethodCall:
    def __init__(self, obj, method, arguments, line=None, column=None):
        self.obj = obj
        self.method = method
        self.arguments = arguments
        self.line = line  # 🔹 Ajouter la ligne du code source
        self.column = column  # 🔹 Ajouter la ligne du code source

    def __repr__(self):
        return f"MethodCall(obj={self.obj}, method={self.method}, args={self.arguments})"


@dataclass
class ModuleFuncCall:
    def __init__(self, module, func, arguments, line=None, column=None):
        self.module = module
        self.func = func
        self.arguments = arguments
        self.line = line  # 🔹 Ajouter la ligne du code source
        self.column = column  # 🔹 Ajouter la ligne du code source

    def __repr__(self):
        return f"ModuleFuncCall(obj={self.module}, method={self.func}, args={self.arguments})"


@dataclass
class ActivateStmt(Stmt):
    def __init__(self, class_name):
        self.class_name = class_name

    def __repr__(self):
        return f"ActivateStmt(class={self.class_name})"


@dataclass
class Importa:
    module: str
    alias: Optional[str] = None


@dataclass
class FromImport:
    module: str
    names: List[str]  # ["a","b"] ou ["*"]


@dataclass
class ImportStmt:
    def __init__(self, module, names):
        self.module = module  # ex: "utils"
        self.names = names  # liste de str ou tuples ("nom", "alias")


@dataclass
class FromImportStmt:
    def __init__(self, module, names):
        self.module = module  # ex: "utils"
        self.names = names  # liste de str ou tuples ("nom", "alias")


@dataclass
class UseStmt:
    path: str


@dataclass
class InjectStmt(Stmt):
    def __init__(self, modules_with_alias):
        # modules_with_alias est une liste de tuples (module, alias)
        # Exemple : [("math", "m"), ("time", "t"), ("String", None)]
        self.modules_with_alias = modules_with_alias

    def __repr__(self):
        return f"InjectStmt({self.modules_with_alias})"


@dataclass
class RuntimeType:
    def __init__(self, name, base_types=None, is_abstract=False, is_interface=False):
        self.name = name
        self.base_types = base_types or []
        self.is_abstract = is_abstract
        self.is_interface = is_interface

    def is_assignable_from(self, other):
        if self.name == other.name:
            return True
        for base in other.base_types:
            if self.is_assignable_from(base):
                return True
        return False


@dataclass
class LoopStmt(Stmt):
    kind: str
    var_name: Optional[str] = None  # 👈 ajoute cette ligne
    initializer: Optional[Stmt] = None
    condition: Optional[Expr] = None
    increment: Optional[Stmt] = None
    iterator: Optional[Expr] = None
    modifiers: Dict[str, Any] = field(default_factory=dict)
    filters: List[Expr] = field(default_factory=list)
    actions: List[Any] = field(default_factory=list)
    step: Optional[Expr] = None
    body: List[Stmt] = field(default_factory=list)

    def __repr__(self):
        return (f"LoopStmt(kind={self.kind!r}, var={self.var_name!r}, init={self.initializer!r}, "
                f"cond={self.condition!r}, incr={self.increment!r}, iter={self.iterator!r}, "
                f"mods={self.modifiers!r}, filters={self.filters!r}, actions={self.actions!r}, "
                f"step={self.step!r}, body={self.body!r})")


# SmartLoopStmt : simple alias/concrete class to keep parser names consistent
@dataclass
class SmartLoopStmt(LoopStmt):
    """Wrapper pour les boucles "intelligentes" - identique à LoopStmt, utilisé par parser.smart_loop"""
    pass

