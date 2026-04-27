from .runtime_instance import RuntimeInstance_for_enum
from .user_function import UserFunction

class RuntimeEnum:
    def __init__(self, name, values, fields=None, methods=None, interpreter=None):
        self.name = name
        self.values = {}
        self.fields = fields or []
        self.methods = methods or []
        self.interpreter = interpreter

        # Création des instances enum
        for index, (const_name, args) in enumerate(values):
            inst = RuntimeInstance_for_enum(self, const_name, interpreter=interpreter, ordinal=index)
            self.values[const_name] = inst

            # Appel de init() si défini
            init_method = next((m for m in self.methods if m.name == "init"), None)
            if init_method:
                call_env = interpreter.env.fork()
                call_env.define("this", inst)
                if args:
                    interpreter.call_function(init_method, args, call_env)

    # Version hybride pour méthodes statiques
    def get_method_bound(self, name, caller_instance=None, arg_types=None, line=None, column=None):
        if name == "values":
            # juste les noms
            return UserFunction(lambda _, args: [v.enum_value_name for v in self.values.values()], closure=None)
        if name == "valueOf":
            #return UserFunction(lambda _, args: self.values.get(args[0]), closure=None)
            return UserFunction(
                lambda _, args: self.values.get(args[0]).enum_value_name if args and args[0] in self.values else None,
                closure=None)
        return None

    def get(self, key):
        if key in self.values:
            return self.values[key]
        raise Exception(f"[Enum] '{key}' n’existe pas dans {self.name}")

    def __repr__(self):
        return f"enum {self.name} {{ {', '.join(self.values.keys())} }}"
