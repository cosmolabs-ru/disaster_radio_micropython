from sx1278 import SX1278
from utime import sleep
from ubinascii import hexlify


class DR:
    def __init__(self):
        self.lora = lora = SX1278(5, 2, 14)
        self.lora.setup()
