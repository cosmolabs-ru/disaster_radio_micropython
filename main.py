from sx1278 import SX1278
from utime import sleep
from ubinascii import hexlify

print("I'm alive!")
sleep(0.5)
lora = SX1278(5, 2, 14)

lora.setup()
lora_id = hex(lora.read_reg(lora.regVersion))
print("LoRa chip ID: ", lora_id)


lora.set_mode(lora.MODE_RXCONT)  # go to RX_CONTINUOUS mode
while 1:
    # lora.transmit(b'Hello world!')
    # sleep(1)
    lora.write_reg(lora.regFifoAddrPtr, 0)
    lora.write_reg(lora.regFifoRxBaseAddr, 0)
    print("Waiting to receive...")
    while not lora.dio0.value():  # wait 4 IRQ
        pass
    lora.write_reg(lora.regIrqFlags, 0x40)  # reset irq flag
    rx_len = lora.read_reg(lora.regRxNbBytes)
    print("Received bytes: ", rx_len)
    print("RxCurrentAddr: ", lora.read_reg(lora.regFifoRxCurrentAddr))
    lora.write_reg(lora.regFifoAddrPtr, lora.read_reg(lora.regFifoRxCurrentAddr))
    print("Payload: ", lora.read_fifo(rx_len))

