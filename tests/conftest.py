"""
conftest.py — Fixtures partagées pour les tests Oktopios.
"""
import sys
import os
import pytest

# Ajouter le dossier vm/ au path pour tous les tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "vm"))


def run_okp(code: str):
    """Exécute du code Oktopios et retourne stdout capturé."""
    from lexer import tokenize
    from parser import Parser
    from interpreter import Interpreter
    tokens = list(tokenize(code))
    ast = Parser(tokens).parse()
    interp = Interpreter()
    interp.interpret(ast)
    return interp


def run_okp_output(code: str, capsys) -> str:
    """Exécute du code Oktopios et retourne la sortie stdout."""
    run_okp(code)
    captured = capsys.readouterr()
    return captured.out.strip()
