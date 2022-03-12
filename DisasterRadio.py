from sx1278 import SX1278
from utime import sleep
from ubinascii import hexlify
import uctypes
import machine
import ujson as json

DUTY_DELAY = 1

class DR:
    def __init__(self):
        self.lora = lora = SX1278(5, 2, 14)
        self.lora.setup()
        self.PACKET_HEADER = {
            "ttl": 0 | uctypes.UINT8,
            "total_length": 1 | uctypes.UINT8,
            "sender": 2 | uctypes.UINT32,
            "receiver": 6 | uctypes.UINT32,
            "sequence": 10 | uctypes.UINT8,
            "source": 11 | uctypes.UINT32,
            "hop_count": 15 | uctypes.UINT8,
            "metric": 16 | uctypes.UINT8,
            "datagram": (17 | uctypes.ARRAY, 238 | uctypes.UINT8)
        }
        self.rt = []
        try:
            self.file_rt = open('rt.json', 'r')
            try:
                self.rt = json.loads(self.file_rt.readlines())
            except:
                self.rt = []
                self.file_rt = open('rt.json', 'w+')
                self.file_rt.close()
        except:
            self.file_rt = open('rt.json', 'w+')
            self.file_rt.close()
            self.rt = []
        else:
            self.file_rt.close()
            pass
        i = bytearray(17)
        self.p_tx = uctypes.struct(uctypes.addressof(i), self.PACKET_HEADER, uctypes.BIG_ENDIAN)
        self.p_rx = uctypes.struct(uctypes.addressof(i), self.PACKET_HEADER, uctypes.BIG_ENDIAN)
        self.id = machine.unique_id()[2:]

    def send_heartbeat(self):
        print("sending heartbeat ", hexlify(self.id).decode('ascii'))
        self.p_tx.ttl = 1
        self.p_tx.total_length = 17
        self.p_tx.sender = int.from_bytes(self.id, 'big')
        self.p_tx.receiver = int.from_bytes(b'\xAF\xFF\xFF\xFF', 'big')
        self.p_tx.sequence = 0
        self.p_tx.source = int.from_bytes(self.id, 'big')
        self.p_tx.hop_count = 0
        self.p_tx.metric = 235
        self.lora.transmit(bytearray(self.p_tx))

    def parse_packet(self, packet: bytes):
        self.p_rx = uctypes.struct(uctypes.addressof(packet), self.PACKET_HEADER, uctypes.BIG_ENDIAN)
        payload_len = self.p_rx.total_length - 17
        print("rx source: ", hex(self.p_rx.source))
        print(self.rt)
        if self.p_rx.source not in (o["dest"] for o in self.rt):
            new_route = {"dest": self.p_rx.source, "via": self.p_rx.sender, "hops": self.p_rx.hop_count}
            self.rt.append(new_route)
            print("New route: ", new_route)
            print("Routes: ", len(self.rt))
        else:
            print("RT packet received, route exists")

    def heartbeat_cycle(self):
        print("Listening...")
        rx_result = self.lora.rx_single()
        if rx_result is not None:
            self.parse_packet(rx_result)
        self.send_heartbeat()
        pass





