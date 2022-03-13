from sx1278 import SX1278
from utime import sleep
import utime as time
from ubinascii import hexlify
from machine import Pin
import machine
import DisasterRadio

print("I'm alive!")
sleep(0.5)

dr = DisasterRadio.DR()
lora_id = hex(dr.lora.read_reg(dr.lora.regVersion))
print("my ID: ", hexlify(machine.unique_id()[2:]))
print("LoRa chip ID: ", lora_id)
led = Pin(12, Pin.OUT)

while 1:
    led(dr.lora.cad())
    # dr.send_heartbeat()
    # dr.heartbeat_cycle()

