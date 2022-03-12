from sx1278 import SX1278
from utime import sleep
from ubinascii import hexlify

print("I'm alive!")
sleep(0.5)
lora = SX1278(5, 2, 14)

lora.setup()
lora_id = hex(lora.read_reg(lora.regVersion))
print("LoRa chip ID: ", lora_id)

# lora.rx_cont_init()
while 1:
    # lora.transmit(b'Hello world!')
    # sleep(1)
    print(lora.rx_single())

