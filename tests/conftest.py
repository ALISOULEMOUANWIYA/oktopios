"""
conftest.py — Fixtures partagées pour les tests Oktopios.
"""
import sys
import os
import pytest

# Ajouter la racine du repo (parent de vm/) au path : vm/ est un package
# (il a un __init__.py), donc les imports relatifs internes ('from . ast_nodes
# import *') ne fonctionnent QUE si vm est importé comme package — importer
# 'interpreter' tout seul (sys.path pointant directement sur vm/) casse ces
# imports relatifs. C'était le bug qui empêchait toute la suite de tourner.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def run_okp(code: str):
    """Exécute du code Oktopios et retourne stdout capturé."""
    from vm.lexer import tokenize
    from vm.parser import Parser
    from vm.interpreter import Interpreter
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
