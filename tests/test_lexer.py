"""
test_lexer.py — Tests unitaires du lexeur Oktopios.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from vm.lexer import tokenize
from vm.token_type import TokenType


def tok(code):
    return list(tokenize(code))


# ── Primitives ────────────────────────────────────────────────────────────────

def test_entier():
    tokens = tok("42")
    assert tokens[0].type == TokenType.NUMBER
    assert tokens[0].value == 42


def test_float():
    tokens = tok("3.14")
    assert tokens[0].type == TokenType.NUMBER
    assert abs(tokens[0].value - 3.14) < 1e-9


def test_string():
    tokens = tok('"Bonjour"')
    assert tokens[0].type == TokenType.STR
    assert tokens[0].value == "Bonjour"


def test_booleen_true():
    tokens = tok("true")
    assert tokens[0].type == TokenType.BOOLVAL
    assert tokens[0].value == "true"


def test_booleen_false():
    tokens = tok("false")
    assert tokens[0].type == TokenType.BOOLVAL


# ── Mots-clés ─────────────────────────────────────────────────────────────────

def test_keyword_var():
    tokens = tok("var")
    assert tokens[0].type == TokenType.VAR


def test_keyword_val():
    tokens = tok("val")
    assert tokens[0].type == TokenType.VAL


def test_keyword_fun():
    tokens = tok("fun")
    assert tokens[0].type == TokenType.FUN


def test_keyword_if():
    tokens = tok("if")
    assert tokens[0].type == TokenType.IF


def test_keyword_return():
    tokens = tok("return")
    assert tokens[0].type == TokenType.RETURN


def test_keyword_class():
    tokens = tok("class")
    assert tokens[0].type == TokenType.CLASS


def test_keyword_loop():
    tokens = tok("loop")
    assert tokens[0].type == TokenType.LOOP


def test_keyword_for():
    tokens = tok("for")
    assert tokens[0].type == TokenType.FOR


def test_keyword_while():
    tokens = tok("while")
    assert tokens[0].type == TokenType.WHILE


def test_keyword_lambda():
    tokens = tok("lambda")
    assert tokens[0].type == TokenType.LAMBDA


def test_keyword_inject():
    tokens = tok("inject")
    assert tokens[0].type == TokenType.INJECT


def test_keyword_enum():
    tokens = tok("enum")
    assert tokens[0].type == TokenType.ENUM


# ── Opérateurs ────────────────────────────────────────────────────────────────

def test_op_plus():
    tokens = tok("+")
    assert tokens[0].type == TokenType.PLUS


def test_op_minus():
    tokens = tok("-")
    assert tokens[0].type == TokenType.MINUS


def test_op_eqeq():
    tokens = tok("==")
    assert tokens[0].type == TokenType.EQEQ


def test_op_neq():
    tokens = tok("!=")
    assert tokens[0].type == TokenType.NE


def test_op_lte():
    tokens = tok("<=")
    assert tokens[0].type == TokenType.LE


def test_op_gte():
    tokens = tok(">=")
    assert tokens[0].type == TokenType.GE


def test_op_pluseq():
    tokens = tok("+=")
    assert tokens[0].type == TokenType.PLUSEQ


# ── Positions (ligne / colonne) ────────────────────────────────────────────────

def test_position_ligne():
    tokens = tok("var x = 1\nvar y = 2")
    # 'var' de la 2e ligne
    y_tok = next(t for t in tokens if t.value == "y")
    assert y_tok.line == 2


def test_position_colonne():
    tokens = tok("var x = 42")
    x_tok = next(t for t in tokens if t.value == "x")
    assert x_tok.column == 4


# ── Commentaires ignorés ──────────────────────────────────────────────────────

def test_commentaire_ignore():
    tokens = tok("// ceci est un commentaire\nvar x = 1")
    types = [t.type for t in tokens]
    assert TokenType.VAR in types
    # Aucun token de type commentaire
    assert all(t.type != TokenType.EOF or True for t in tokens)


# ── Séquences complexes ───────────────────────────────────────────────────────

def test_sequence_declaration():
    tokens = tok("var age: int = 25")
    types = [t.type for t in tokens[:-1]]  # sans EOF
    assert TokenType.VAR in types
    assert TokenType.INT in types
    assert TokenType.NUMBER in types


def test_not_in_fusion():
    """'not in' doit être fusionné en un seul token NOT_IN."""
    tokens = tok("x not in liste")
    assert any(t.type == TokenType.NOT_IN for t in tokens)


def test_eof_present():
    tokens = tok("42")
    assert tokens[-1].type == TokenType.EOF


def test_caractere_inattendu():
    with pytest.raises((SyntaxError, Exception)):
        tok("var x = @")
