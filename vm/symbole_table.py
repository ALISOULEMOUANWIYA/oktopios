
class SymbolTable:
    def __init__(self):
        self.classes = {}

    def create_class(self, name):
        if name in self.classes:
            raise Exception(f"Class '{name}' already defined")

        self.classes[name] = {
            "members": [],
            "method": []
        }

    def add_member(self, class_name, member):
        self.classes[class_name]["members"].append(member)

    def add_method(self, class_name, method):
        self.classes[class_name]["method"].append(method)