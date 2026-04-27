from colorama import Fore, Style  # Pour affichage coloré des erreurs (si utilisé ailleurs)
from .environment import Environment

class LambdaFunction:
    def __init__(self, expr, closure):
        self.expr = expr            # instance de LambdaExpr
        self.closure = closure      # environnement capturé

    def call(self, interpreter, arguments):
        env = Environment(enclosing=self.closure)

        # Injecte les arguments avec vérification des types
        for i in range(len(self.expr.params)):
            param = self.expr.params[i]

            if isinstance(param, tuple):
                param_token, param_type = param
            else:
                param_token = param
                param_type = None

            param_name = param_token.lexeme if hasattr(param_token, "lexeme") else str(param_token)
            arg_value = arguments[i]

            # 🔎 Vérification du type si précisé
            if param_type is not None:
                if not self._check_type(arg_value, param_type):
                    raise Exception(
                        Fore.CYAN +
                        f"[TypeError] Argument '{param_name}' attendu de type '{param_type}', mais reçu : {type(arg_value).__name__}" +
                        Style.RESET_ALL
                    )

            env.define(param_name, arg_value)

        # Évalue l'expression dans ce nouvel environnement
        previous_env = interpreter.env
        interpreter.env = env
        try:
            return interpreter.evaluate(self.expr.body)
        finally:
            interpreter.env = previous_env

    def _check_type(self, value, expected_type_name):
        expected_type = {
            "int": int,
            "float": float,
            "string": str,
            "char": str,
            "bool": bool,
            "void": type(None),  # pas vraiment utilisé ici
        }.get(expected_type_name)

        return isinstance(value, expected_type) if expected_type else True
