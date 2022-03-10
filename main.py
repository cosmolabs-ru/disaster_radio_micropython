from sx1278 import SX1278
from utime import sleep

print("I'm alive!")
sleep(0.5)
lora = SX1278(5, 2, 14)

lora.setup()
lora_id = hex(lora.read_reg(lora.regVersion)[1])
print("LoRa chip ID: ", lora_id)

while 1:
    lora.transmit("Hello world!".encode('ascii'))
    sleep(1)
