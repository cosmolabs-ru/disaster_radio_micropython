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
    regIrqFlags = 0x12
    regRxNbBytes = 0x13
    regPktSNRValue = 0x19
    regPktRSSIValue = 0x1A
    regModemConfig1 = 0x1D
    regModemConfig2 = 0x1E
    regSymbTimeoutLSB = 0x1F
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
        self.reset(0)
        sleep(0.1)
        self.reset(1)
        sleep(0.1)

    def write_reg(self, reg, data):
        if self.spi is not None:
            self.nss(0)
            self.spi.write(bytearray([(reg | 0x80), data]))
            self.nss(1)
            sleep(0.001)

    def write_fifo(self, buffer: bytes):
        if self.spi is not None:
            buf_ba = bytearray([0x80, ])
            buf_ba.extend(buffer)
            self.nss(0)
            self.spi.write(buf_ba)
            self.nss(1)
            sleep(0.001)

    def read_fifo(self, rx_len: int):
        if self.spi is not None:
            buf_ba = bytearray([0x00, ])
            buf_ba.extend(bytearray(rx_len))
            rb = bytearray(rx_len+1)
            self.nss(0)
            self.spi.write_readinto(buf_ba, rb)
            self.nss(1)
            sleep(0.001)
            return rb[1:]

    def read_reg(self, reg):
        wb = bytearray([reg, 0xBB])
        rb = bytearray([0xAA, 0xAA])
        if self.spi is not None:
            self.nss(0)
            self.spi.write_readinto(wb, rb)
            self.nss(1)
            sleep(0.001)
            return rb[1]

    def set_mode(self, mode):
        self.write_reg(self.regOpMode, mode)

    def setup(self):
        self.set_mode(self.MODE_SLEEP)
        self.write_reg(self.regPAConfig, 0xFF)  # PA_BOOST pin, max output power
        self.write_reg(self.regLNA, 0x23)  # Max LNA gain + boost
        self.write_reg(self.regDioMapping1, 0x00)  # default IRQ mapping: RxDone, TxDone on DIO0
        self.write_reg(self.regSymbTimeoutLSB, 0xFF)  # RXSINGLE RxTimeout: 1024 symbols
        self.write_reg(self.regModemConfig1, 0b01101000)  # 62.5 kHz, 4/8 CR, Explicit header
        self.write_reg(self.regModemConfig2, 0xC3)  # SF 12 + SymbTimeout |= 0xC0
        self.write_reg(self.regModemConfig3, 0x08)  # Low datarate optimize On

    def transmit(self, buffer: bytes):
        self.set_mode(self.MODE_STBY)
        self.write_reg(self.regFifoTxBaseAddr, 0)
        self.write_reg(self.regFifoAddrPtr, 0)
        self.write_reg(self.regPayloadLength, len(buffer))
        self.write_fifo(buffer)
        print("sending ", buffer)
        self.set_mode(self.MODE_TX)
        while self.read_reg(self.regIrqFlags) == 0:  # self.read_reg(self.regOpMode)[1] == self.MODE_TX:
            sleep(0.5)
            pass
        self.write_reg(self.regIrqFlags, 0x08)
        
    def rx_cont(self):
        self.write_reg(self.regFifoAddrPtr, 0)
        self.write_reg(self.regFifoRxBaseAddr, 0)
        self.set_mode(self.MODE_RXCONT)  # go to RX_CONTINUOUS mode
        while not self.dio0.value():  # wait 4 IRQ
            pass
        self.write_reg(self.regIrqFlags, 0x40)  # reset irq flag
        rx_len = self.read_reg(self.regRxNbBytes)
        self.write_reg(self.regFifoAddrPtr, self.read_reg(self.regFifoRxCurrentAddr))
        return self.read_fifo(rx_len)

    def rx_single(self):
        self.set_mode(self.MODE_SLEEP)
        self.write_reg(self.regFifoAddrPtr, 0)
        self.write_reg(self.regFifoRxBaseAddr, 0)
        self.set_mode(self.MODE_RXSINGLE)
        irqs = 0
        while 1:
            irqs = self.read_reg(self.regIrqFlags)
            if irqs & 0x40 or irqs & 0x80: break
        irqs &= 0xC0
        if irqs & 0x80:
            self.write_reg(self.regIrqFlags, 0xC0)
            print("rx timeout irq")
            return None
        elif irqs & 0x40:
            self.write_reg(self.regIrqFlags, 0xC0)  # reset irq flag
            rx_len = self.read_reg(self.regRxNbBytes)
            self.write_reg(self.regFifoAddrPtr, self.read_reg(self.regFifoRxCurrentAddr))
            return self.read_fifo(rx_len)
        print("no irqs fired")
        return None





