from .environment import Environment
from .return_Value import ReturnValue
from colorama import Fore, Style
from .ast_nodes import FunDecl  # ou l'import adapté


class UserFunction:
    def __init__(self, declaration, closure, instance=None):
        self.instance = instance
        self.closure = closure

        # Si c’est une lambda ou fonction native Python → pas de params / body
        if callable(declaration) and not isinstance(declaration, FunDecl):
            self.native = declaration
            self.declaration = None
        else:
            self.declaration = declaration
            self.native = None

    def __call__(self, *args, interpreter):
        """Permet d’appeler directement la fonction importée depuis un module."""
        return self.call(interpreter, args)

    def call(self, interpreter, args, line=None, column=None):
        if self.native:
            # Appel direct de la fonction lambda/native
            return self.native(interpreter, args)

        # Sinon, comportement normal pour FunDecl
        env = Environment(enclosing=self.closure)
        prev_env = interpreter.env
        prev_return_type = interpreter.current_return_type
        prev_instance = getattr(interpreter, "current_instance", None)
        try:
            interpreter.env = env
            if self.instance is not None:
                env.define("this", self.instance, is_constant=True)


            for i, (name, _type, is_mutable, default_value) in enumerate(self.declaration.params):
                if i < len(args):
                    value = args[i]
                elif default_value is not None:
                    value = interpreter.evaluate(default_value)
                else:
                    raise Exception(f"[Erreur] Argument manquant pour {name}")
                env.define(name, value, is_constant=not is_mutable)

            interpreter.current_return_type = getattr(self.declaration, "return_type", None)
            interpreter.current_instance = self.instance

            try:
                interpreter.execute_block(self.declaration.body, env)
                return None
            except ReturnValue as rv:
                return rv.value
        finally:
            interpreter.env = prev_env
            interpreter.current_return_type = prev_return_type
            interpreter.current_instance = prev_instance
