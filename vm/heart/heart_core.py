class HeartCore:
    def __init__(self):
        self.memory = {}
        self.long_term = {}
        self.signal_bus = {}
        self.events = {}

    def status(self):
        return "🐙 OKTOPIOS_CORE: VIVANT"

    def clock(self):
        import time
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def log(self, msg):
        print(f"[LOG {self.clock()}] {msg}")

    # Mémoire
    def mem(self, key, val=None):
        if val is not None:
            self.memory[key] = val
        return self.memory.get(key)

    # Signaux
    def emit(self, key, value):
        self.signal_bus[key] = value

    def receive(self, key):
        return self.signal_bus.get(key, None)

    # Événements
    def on(self, trigger, callback):
        self.events[trigger] = callback

    def trigger(self, trigger):
        if trigger in self.events:
            return self.events[trigger]()
        return f"[!] Aucun événement : {trigger}"
