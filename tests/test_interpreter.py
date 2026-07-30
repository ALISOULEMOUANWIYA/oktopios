"""
test_interpreter.py — Tests d'intégration de l'interpréteur Oktopios.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from vm.lexer import tokenize
from vm.parser import Parser
from vm.interpreter import Interpreter


def run(code: str, capsys=None):
    tokens = list(tokenize(code))
    ast = Parser(tokens).parse()
    Interpreter().interpret(ast)
    if capsys:
        return capsys.readouterr().out.strip()
    return None


def out(code: str, capsys) -> str:
    return run(code, capsys)


# ── Valeurs primitives ────────────────────────────────────────────────────────

def test_print_entier(capsys):
    assert out("print(42)", capsys) == "42"


def test_print_float(capsys):
    assert out("print(3.14)", capsys) == "3.14"


def test_print_string(capsys):
    assert out('print("Bonjour")', capsys) == "Bonjour"


def test_print_bool_true(capsys):
    assert out("print(true)", capsys) == "true"


def test_print_bool_false(capsys):
    assert out("print(false)", capsys) == "false"


# ── Arithmétique ──────────────────────────────────────────────────────────────

def test_addition(capsys):
    assert out("print(3 + 4)", capsys) == "7"


def test_soustraction(capsys):
    assert out("print(10 - 3)", capsys) == "7"


def test_multiplication(capsys):
    assert out("print(3 * 4)", capsys) == "12"


def test_division(capsys):
    result = out("print(10 / 4)", capsys)
    assert float(result) == pytest.approx(2.5)


def test_modulo(capsys):
    assert out("print(10 % 3)", capsys) == "1"


def test_priorite_ops(capsys):
    assert out("print(2 + 3 * 4)", capsys) == "14"


def test_parentheses(capsys):
    assert out("print((2 + 3) * 4)", capsys) == "20"


# ── Variables ─────────────────────────────────────────────────────────────────

def test_var_int(capsys):
    assert out("var x: int = 99\nprint(x)", capsys) == "99"


def test_var_reassign(capsys):
    assert out("var x = 1\nx = 2\nprint(x)", capsys) == "2"


def test_val_immutable():
    with pytest.raises(Exception):
        run("val x = 5\nx = 6")


def test_var_string(capsys):
    assert out('var s = "ok"\nprint(s)', capsys) == "ok"


def test_concat_string(capsys):
    assert out('print("Hello" + " " + "World")', capsys) == "Hello World"


# ── Fonctions ─────────────────────────────────────────────────────────────────

def test_fun_call(capsys):
    code = "fun double(n: int): int { return n * 2 }\nprint(double(5))"
    assert out(code, capsys) == "10"


def test_fun_default_param(capsys):
    code = 'fun salut(nom: string = "ami") { print(nom) }\nsalut()'
    assert out(code, capsys) == "ami"


def test_fun_default_override(capsys):
    code = 'fun salut(nom: string = "ami") { print(nom) }\nsalut("Ali")'
    assert out(code, capsys) == "Ali"


def test_fun_surcharge(capsys):
    code = """
fun f(a: int): int { return a }
fun f(a: int, b: int): int { return a + b }
print(f(5))
print(f(3, 4))
"""
    lines = out(code, capsys).split("\n")
    assert lines[0] == "5"
    assert lines[1] == "7"


def test_recursion(capsys):
    code = """
fun fact(n: int): int {
    if(n <= 1) { return 1 }
    return n * fact(n - 1)
}
print(fact(6))
"""
    assert out(code, capsys) == "720"


def test_fun_imbriquee(capsys):
    code = """
fun externe() {
    var msg: string = "Salut"
    fun interne() { print(msg) }
    interne()
}
externe()
"""
    assert out(code, capsys) == "Salut"


# ── Lambda ────────────────────────────────────────────────────────────────────

def test_lambda_simple(capsys):
    assert out("val double = lambda(n: int) => n * 2\nprint(double(5))", capsys) == "10"


def test_lambda_multi_param(capsys):
    assert out("val add = lambda(a: int, b: int) => a + b\nprint(add(3, 4))", capsys) == "7"


# ── Conditions ────────────────────────────────────────────────────────────────

def test_if_vrai(capsys):
    assert out("if(true) { print(1) }", capsys) == "1"


def test_if_faux(capsys):
    assert out("if(false) { print(1) } else { print(0) }", capsys) == "0"


def test_if_elif(capsys):
    code = "var n = 5\nif(n > 10) { print(\"grand\") } elif(n == 5) { print(\"cinq\") } else { print(\"autre\") }"
    assert out(code, capsys) == "cinq"


def test_comparaison_egalite(capsys):
    assert out("print(3 == 3)", capsys) == "true"


def test_comparaison_inegalite(capsys):
    assert out("print(3 != 4)", capsys) == "true"


# ── Boucles ───────────────────────────────────────────────────────────────────

def test_while(capsys):
    code = "var i = 0\nwhile(i < 3) { print(i)\ni += 1 }"
    lines = out(code, capsys).split("\n")
    assert lines == ["0", "1", "2"]


def test_for_cstyle(capsys):
    code = "for(var i: int = 0; i < 3; i += 1) { print(i) }"
    lines = out(code, capsys).split("\n")
    assert lines == ["0", "1", "2"]


def test_for_each(capsys):
    code = "var nums: int[] = [1, 2, 3]\nfor(n in nums) { print(n) }"
    lines = out(code, capsys).split("\n")
    assert lines == ["1", "2", "3"]


def test_break(capsys):
    code = "var i = 0\nwhile(i < 10) { if(i == 3) { break }\nprint(i)\ni += 1 }"
    lines = out(code, capsys).split("\n")
    assert "3" not in lines
    assert lines[-1] == "2"


# ── Classes ───────────────────────────────────────────────────────────────────

def test_class_instanciation(capsys):
    code = """
class Point {
    var x: int
    var y: int
    fun __construct(px: int, py: int) {
        this.x = px
        this.y = py
    }
    fun afficher(): string {
        return "(" + this.x + ", " + this.y + ")"
    }
}
var p = new Point(3, 4)
print(p.afficher())
"""
    assert out(code, capsys) == "(3, 4)"


def test_class_heritage(capsys):
    code = """
class Animal {
    var nom: string
    fun __construct(n: string) { this.nom = n }
    fun parler(): string { return this.nom + " parle" }
}
class Chien extends Animal {
    override fun parler(): string { return this.nom + " aboie" }
}
var rex = new Chien("Rex")
print(rex.parler())
"""
    assert out(code, capsys) == "Rex aboie"


# ── Modules natifs ────────────────────────────────────────────────────────────

def test_math_sqrt(capsys):
    assert out("inject Math\nprint(Math.sqrt(16))", capsys) == "4.0"


def test_math_abs(capsys):
    assert out("inject Math\nprint(Math.abs(-7))", capsys) == "7"


def test_string_upper(capsys):
    assert out('inject String\nprint(String.upper("hello"))', capsys) == "HELLO"


def test_string_lower(capsys):
    assert out('inject String\nprint(String.lower("MONDE"))', capsys) == "monde"


def test_string_length(capsys):
    assert out('inject String\nprint(String.length("okp"))', capsys) == "3"


# ── Gestion d'erreurs ─────────────────────────────────────────────────────────

def test_variable_inconnue():
    with pytest.raises(Exception):
        run("print(variableInexistante)")


def test_division_par_zero():
    with pytest.raises(Exception):
        run("print(1 / 0)")


def test_try_catch(capsys):
    code = """
try {
    throw "Erreur test"
} catch(e) {
    print("Attrapé")
}
"""
    assert out(code, capsys) == "Attrapé"


# ── Namespace Json ─────────────────────────────────────────────────────────────
# Note: le lexer Oktopios ne supporte pas \" dans les chaînes.
# On utilise la stratégie map Oktopios → stringify → parse pour les tests.

def test_json_is_valid_array(capsys):
    """[1,2,3] est du JSON valide."""
    code = 'inject Json\nprint(Json.isValid("[1,2,3]"))'
    assert out(code, capsys) == "true"


def test_json_is_valid_false(capsys):
    """Une chaîne non-JSON retourne false."""
    code = 'inject Json\nprint(Json.isValid("not json"))'
    assert out(code, capsys) == "false"


def test_json_stringify_is_valid(capsys):
    """stringify d'un entier produit du JSON valide."""
    code = 'inject Json\nprint(Json.isValid(Json.stringify(42)))'
    assert out(code, capsys) == "true"


def test_json_stringify_map_roundtrip(capsys):
    """Un map Oktopios peut être stringify puis re-parsé, et Json.get fonctionne."""
    code = """inject Json
var m = {"score": 99, "ok": true}
var s = Json.stringify(m)
var parsed = Json.parse(s)
print(Json.get(parsed, "score"))"""
    assert out(code, capsys) == "99"


def test_json_has_true(capsys):
    """Json.has retourne true si la clé existe."""
    code = """inject Json
var m = {"x": 1}
var s = Json.stringify(m)
var obj = Json.parse(s)
print(Json.has(obj, "x"))"""
    assert out(code, capsys) == "true"


def test_json_has_false(capsys):
    """Json.has retourne false si la clé est absente."""
    code = """inject Json
var m = {"x": 1}
var s = Json.stringify(m)
var obj = Json.parse(s)
print(Json.has(obj, "missing"))"""
    assert out(code, capsys) == "false"


def test_json_set(capsys):
    """Json.set met à jour une valeur et retourne un nouvel objet."""
    code = """inject Json
var m = {"x": 1}
var s = Json.stringify(m)
var obj = Json.parse(s)
var obj2 = Json.set(obj, "x", 99)
print(Json.get(obj2, "x"))"""
    assert out(code, capsys) == "99"


def test_json_merge(capsys):
    """Json.merge fusionne deux objets."""
    code = """inject Json
var a = {"x": 1}
var b = {"y": 2}
var sa = Json.stringify(a)
var sb = Json.stringify(b)
var merged = Json.merge(Json.parse(sa), Json.parse(sb))
print(Json.has(merged, "x"))
print(Json.has(merged, "y"))"""
    lines = out(code, capsys).split("\n")
    assert lines[0] == "true"
    assert lines[1] == "true"


def test_json_keys(capsys):
    """Json.keys retourne les clés de premier niveau."""
    code = """inject Json
inject List
var m = {"a": 1, "b": 2}
var obj = Json.parse(Json.stringify(m))
var k = Json.keys(obj)
print(List.contains(k, "a"))
print(List.contains(k, "b"))"""
    lines = out(code, capsys).split("\n")
    assert lines[0] == "true"
    assert lines[1] == "true"


def test_json_get_default(capsys):
    """Json.get retourne null si la clé est absente sans default."""
    code = """inject Json
var m = {"z": 7}
var obj = Json.parse(Json.stringify(m))
print(Json.get(obj, "missing", "fallback"))"""
    assert out(code, capsys) == "fallback"


def test_json_file_roundtrip(capsys, tmp_path):
    """Json.toFile puis Json.fromFile reconstituent le même objet."""
    import os
    filepath = str(tmp_path / "test.json")
    code = f"""inject Json
var m = {{"val": 42}}
Json.toFile("{filepath}", m)
var loaded = Json.fromFile("{filepath}")
print(Json.get(loaded, "val"))"""
    assert out(code, capsys) == "42"
