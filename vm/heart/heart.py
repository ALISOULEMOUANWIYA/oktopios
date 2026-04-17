
from heart_io import HeartIO
from heart_net import HeartNet
from heart_core import HeartCore

class Heart:
    def __init__(self):
        self.io = HeartIO()
        self.net = HeartNet()
        self.core = HeartCore()

