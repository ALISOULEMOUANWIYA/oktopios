# 🫀 Cœurs de la pieuvre

class HeartIO:
    def __init__(self):
        pass

    def print(self, *args):
        print(*args)

    def read(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Erreur IO lecture : {e}")

    def write(self, path, content):
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            raise Exception(f"Erreur IO écriture : {e}")
