from colorama import Fore, Style

class Instance:
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}

    def get(self, name):
        if name in self.fields:
            return self.fields[name]
        raise RuntimeError(Fore.CYAN + f"Champ '{name}' non défini"+ Style.RESET_ALL)

    def set(self, name, value):
        self.fields[name] = value

    def __str__(self):
        return f"<instance {self.klass}>"
