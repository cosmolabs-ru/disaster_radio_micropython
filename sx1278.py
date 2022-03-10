from machine import Pin, SPI


class SX1278:
    class Regmap:
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
        regMaxpayloadLength = 0x23
        regDioMapping1 = 0x40
        regDioMapping2 = 0x41
        
    def __init__(self, nss, dio0, reset):
        self.spi = SPI(2, baudrate=8000000, polarity=0, phase=0, bits=8, firstbit=0, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
        self.nss = Pin(nss, Pin.OUT)
        self.dio0 = Pin(dio0, Pin.IN)
        self.reset = Pin(reset, Pin.OUT)

        