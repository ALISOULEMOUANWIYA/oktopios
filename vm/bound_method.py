from .environment import Environment

class BoundMethod:
    def __init__(self, instance, method):
        self.instance = instance
        self.method = method

    def call(self, interpreter, args):
        # injecter "this" (self.instance) dans l’environnement
        env = Environment(parent=self.method.closure)
        env.define("this", self.instance)
        return interpreter.execute_block(self.method.body, env)
