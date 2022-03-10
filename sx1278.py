from machine import Pin, SPI
from utime import sleep


class SX1278:

    regFifo = 0x00
    regOpMode = 0x01
    regPAConfig = 0x09
    regLNA = 0x0C
    regFifoAddrPtr = 0x0D
    regFifoTxBaseAddr = 0x0E
    regFifoRxBaseAddr = 0x0F
    regFifoRxCurrentAddr = 0x10
    regRxNbBytes = 0x13
    regPktSNRValue = 0x19
    regPktRSSIValue = 0x1A
    regModemConfig1 = 0x1D
    regModemConfig2 = 0x1E
    regModemConfig3 = 0x26
    regPayloadLength = 0x22
    regMaxPayloadLength = 0x23
    regDioMapping1 = 0x40
    regDioMapping2 = 0x41
    regVersion = 0x42

    MODE_SLEEP = 0x80
    MODE_STBY = 0x81
    MODE_FSTX = 0x82
    MODE_TX = 0x83
    MODE_FSRX = 0x84
    MODE_RXCONT = 0x85
    MODE_RXSINGLE = 0x86
    MODE_CAD = 0x87

    def __init__(self, nss, dio0, reset):
        self.spi = SPI(2, baudrate=8000000, polarity=0, phase=0, bits=8, firstbit=SPI.MSB, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
        self.nss = Pin(nss, Pin.OUT)
        self.dio0 = Pin(dio0, Pin.IN)
        self.reset = Pin(reset, Pin.OUT)
        self.nss(1)
        self.reset(1)

    def write_reg(self, reg, data):
        if self.spi is not None:
            self.nss(0)
            self.spi.write(bytearray([(reg | 0x80), data]))
            self.nss(1)
            sleep(0.001)

    def write_fifo(self, buffer: bytes):
        if self.spi is not None:
            buf_ba = bytearray([0x10, ])
            buf_ba.extend(buffer)
            self.nss(0)
            self.spi.write(buf_ba)
            self.nss(1)
            sleep(0.001)


    def read_reg(self, reg):
        wb = bytearray([reg, 0xBB])
        rb = bytearray([0xAA, 0xAA])
        if self.spi is not None:
            self.nss(0)
            self.spi.write_readinto(wb, rb)
            self.nss(1)
            sleep(0.001)
            return rb

    def set_mode(self, mode):
        self.write_reg(self.regOpMode, mode)

    def setup(self):
        self.set_mode(self.MODE_SLEEP)
        self.write_reg(self.regLNA, 0x23)  # Max LNA gain + boost
        self.write_reg(0x11, 0x48)  # RxDone, TxDone IRQ EN
        self.write_reg(self.regModemConfig1, 0b01101000)  # 62.5 kHz, 4/8 CR, Explicit header
        self.write_reg(self.regModemConfig2, 0xC0)  # SF 12
        self.write_reg(self.regModemConfig3, 0x08)  # Low datarate optimize On

    def transmit(self, buffer: bytes):
        self.set_mode(self.MODE_STBY)
        self.write_fifo(buffer)
        print("sending ", buffer)
        self.set_mode(self.MODE_TX)
        while self.read_reg(self.regOpMode)[1] == self.MODE_TX:
            sleep(0.5)
            pass
        print("sent!")

        