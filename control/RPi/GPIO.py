# Dummy package
BOARD = 1
OUT = 1
IN = 1
HIGH = 1
LOW = 0
BCM = None
PUD_UP = 1


def setmode(*args, **kwargs):
    pass


def setup(*args, **kwargs):
    pass


def output(*args, **kwargs):
    pass


def input(*args, **kwargs):
    pass


def cleanup(*args, **kwargs):
    pass


def setwarnings(*args, **kwargs):
    pass


class PWM():
    def __init__(self, pin, dc):
        self.pin = pin
        self.dc = dc
        self.state = 0

    def start(self, a):
        self.state = 1

    def stop(self):
        self.state = 0
