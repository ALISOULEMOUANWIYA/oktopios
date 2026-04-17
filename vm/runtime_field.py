class RuntimeField:
    def __init__(self, name, value, is_constant=False, is_private=False):
        self.name = name
        self.value = value
        self.is_constant = is_constant
        self.is_private = is_private
