from sx1278 import SX1278
from utime import sleep
import utime as time
from ubinascii import hexlify
from machine import Pin
import network
import ubinascii
import machine
import DisasterRadio
# from webserver import WebServer
from nanoweb import HttpError, Nanoweb, send_file
import uasyncio as asyncio

print("I'm alive!")
sleep(0.5)
dr = DisasterRadio.DR()
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="EFIR_"+ubinascii.hexlify(dr.id).decode().upper(), password="12345678")
ap.ifconfig(('192.168.4.1', '255.255.255.0', '10.10.10.0', '8.8.8.8'))
lora_id = hex(dr.lora.read_reg(dr.lora.regVersion))
print("my ID: ", hexlify(machine.unique_id()[2:]).decode().upper())
print("LoRa chip ID: ", lora_id)
led = Pin(12, Pin.OUT)
loop = asyncio.get_event_loop()
naw = Nanoweb(80)
naw.assets_extensions += ('ico',)


@naw.route("/")
async def index(request):
    await request.write("HTTP/1.1 200 OK\r\n\r\n")
    await request.write('<html><body><h1>Hello, world! (<a href="/table">table</a>)</h1></html>\n')


async def run_server():
    while 1:
        await naw.run()

async def heartbeat():
    while 1:
        await dr.heartbeat_cycle()


loop.create_task(naw.run())
loop.create_task(heartbeat())
loop.run_forever()
