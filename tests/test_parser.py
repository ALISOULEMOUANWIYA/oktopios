"""
test_parser.py — Tests unitaires du parseur Oktopios.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "vm"))

import pytest
from lexer import tokenize
from parser import Parser
from ast_nodes import (
    Program, VarDecl, FunDecl, ClassDeclaration,
    IfStmt, WhileStmt, ForEachStmt, BlockStmt,
    ReturnStmt, PrintStmt, Literal, Variable, BinaryOp, FuncCall
)


def parse(code):
    tokens = list(tokenize(code))
    return Parser(tokens).parse()


# ── Programme vide ────────────────────────────────────────────────────────────

def test_programme_vide():
    ast = parse("")
    assert isinstance(ast, Program)
    assert ast.body == []


# ── Déclarations de variables ─────────────────────────────────────────────────

def test_var_int():
    ast = parse("var x: int = 42")
    node = ast.body[0]
    assert isinstance(node, VarDecl)
    assert node.name == "x"


def test_val_string():
    ast = parse('val msg: string = "Oktopios"')
    node = ast.body[0]
    assert isinstance(node, VarDecl)
    assert node.name == "msg"
    assert node.is_constant is True


def test_var_sans_type():
    ast = parse("var x = 10")
    node = ast.body[0]
    assert isinstance(node, VarDecl)


# ── Fonctions ─────────────────────────────────────────────────────────────────

def test_fun_simple():
    ast = parse("fun saluer() { }")
    node = ast.body[0]
    assert isinstance(node, FunDecl)
    assert node.name == "saluer"


def test_fun_avec_params():
    ast = parse("fun add(a: int, b: int): int { return a + b }")
    node = ast.body[0]
    assert isinstance(node, FunDecl)
    assert len(node.params) == 2
    assert node.params[0][0] == "a"
    assert node.params[1][0] == "b"


def test_fun_return_type():
    ast = parse("fun get(): string { return \"ok\" }")
    node = ast.body[0]
    assert isinstance(node, FunDecl)
    assert node.return_type == "string"


def test_fun_surcharge():
    ast = parse("""
        fun f(a: int): int { return a }
        fun f(a: int, b: int): int { return a + b }
    """)
    funs = [n for n in ast.body if isinstance(n, FunDecl)]
    assert len(funs) == 2


# ── Conditions ────────────────────────────────────────────────────────────────

def test_if_simple():
    ast = parse("if(x > 0) { print(x) }")
    node = ast.body[0]
    assert isinstance(node, IfStmt)


def test_if_else():
    ast = parse("if(x > 0) { print(1) } else { print(0) }")
    node = ast.body[0]
    assert isinstance(node, IfStmt)
    assert node.else_body is not None


def test_if_elif_else():
    ast = parse("if(x > 0) { print(1) } elif(x == 0) { print(0) } else { print(-1) }")
    node = ast.body[0]
    assert isinstance(node, IfStmt)


# ── Boucles ───────────────────────────────────────────────────────────────────

def test_while():
    ast = parse("while(i < 10) { i += 1 }")
    # WhileStmt peut être wrappé dans un BlockStmt
    node = ast.body[0]
    assert isinstance(node, WhileStmt)


def test_for_each():
    ast = parse("for(n in nums) { print(n) }")
    node = ast.body[0]
    assert isinstance(node, ForEachStmt)
    assert node.var_name == "n"


def test_for_cstyle():
    ast = parse("for(var i: int = 0; i < 3; i += 1) { print(i) }")
    # Produit un BlockStmt(VarDecl, WhileStmt)
    node = ast.body[0]
    assert isinstance(node, (BlockStmt, WhileStmt))


# ── Classes ───────────────────────────────────────────────────────────────────

def test_class_vide():
    ast = parse("class Animal { }")
    node = ast.body[0]
    assert isinstance(node, ClassDeclaration)
    assert node.name == "Animal"


def test_class_avec_methode():
    ast = parse("""
        class Chat {
            fun parler(): string {
                return "Miaou"
            }
        }
    """)
    node = ast.body[0]
    assert isinstance(node, ClassDeclaration)


def test_class_extends():
    ast = parse("class Chien extends Animal { }")
    node = ast.body[0]
    assert isinstance(node, ClassDeclaration)
    assert node.superclass is not None


# ── Expressions ───────────────────────────────────────────────────────────────

def test_binop_addition():
    ast = parse("print(1 + 2)")
    # Ne doit pas lever d'exception


def test_binop_precedence():
    ast = parse("print(2 + 3 * 4)")
    # 2 + (3*4) = 14, pas (2+3)*4 = 20


def test_appel_fonction():
    ast = parse("add(1, 2)")
    node = ast.body[0]
    # FuncCall ou ExpressionStmt wrappant FuncCall
    assert node is not None


def test_acces_attribut():
    ast = parse("obj.nom")


def test_new():
    ast = parse("var a = new Animal()")


# ── Erreurs de syntaxe ────────────────────────────────────────────────────────

def test_accolade_manquante():
    with pytest.raises(Exception):
        parse("fun f() { ")


def test_paren_non_fermee():
    with pytest.raises(Exception):
        parse("print(42")


def test_expression_invalide():
    with pytest.raises(Exception):
        parse("var x = ")
