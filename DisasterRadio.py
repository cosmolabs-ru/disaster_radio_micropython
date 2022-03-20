from sx1278 import SX1278
from utime import sleep
from ubinascii import hexlify
import uctypes
import machine
import ujson as json
import uasyncio as asyncio

DUTY_DELAY = 1
DROP_RT = 1


class DR:
    def __init__(self):
        self.id = machine.unique_id()[2:]
        self.lora = lora = SX1278(5, 2, 21, 14)
        self.lora.setup()
        self.lora.write_reg(self.lora.regSymbTimeoutLSB, self.id[3])
        self.fl_heartbeat_complete = asyncio.ThreadSafeFlag()
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
        except:
            print("RT file opening failed")
            self.file_rt = open('rt.json', 'w+')
            self.file_rt.close()
            self.rt = []
        else:
            pass
        try:
            self.rt = json.loads(self.file_rt.read())
        except:
            print("JSON parsing exceprion on loading RT!")
            self.rt = []
            self.file_rt = open('rt.json', 'w+')
            self.file_rt.close()
        self.file_rt.close()
        if DROP_RT:
            print("WARNING: DROP_RT flag is set. Routing table is now cleared!")
            self.rt = []
            self.file_rt = open('rt.json', 'w+')
            self.file_rt.close()
        print("Routes loaded from RT: ", len(self.rt))
        i = bytearray(17)
        self.p_tx = uctypes.struct(uctypes.addressof(i), self.PACKET_HEADER, uctypes.BIG_ENDIAN)
        self.p_rx = uctypes.struct(uctypes.addressof(i), self.PACKET_HEADER, uctypes.BIG_ENDIAN)

    async def send_heartbeat(self):
        print("sending heartbeat ", hexlify(self.id).decode('ascii'))
        self.p_tx.ttl = 1
        self.p_tx.total_length = 17
        self.p_tx.sender = int.from_bytes(self.id, 'big')
        self.p_tx.hop_count = 0
        self.p_tx.receiver = int.from_bytes(b'\xAF\xFF\xFF\xFF', 'big')
        self.p_tx.sequence = 0
        self.p_tx.source = int.from_bytes(self.id, 'big')
        self.p_tx.metric = 235
        await self.lora.async_transmit(bytearray(self.p_tx))

    def parse_packet(self, packet: bytes):
        self.p_rx = uctypes.struct(uctypes.addressof(packet), self.PACKET_HEADER, uctypes.BIG_ENDIAN)
        payload_len = self.p_rx.total_length - 17
        if self.p_rx.source not in (o["dest"] for o in self.rt):
            new_route = {"dest": self.p_rx.source, "via": self.p_rx.sender, "hops": self.p_rx.hop_count}
            self.rt.append(new_route)
            print("New route to", hex(new_route["dest"]), "accepted!")
            print("Routes: ", len(self.rt))
        else:
            for route in self.rt:
                if route["dest"] == self.p_rx.source:
                    if route["hops"] > self.p_rx.hop_count:
                        route["hops"] = self.p_rx.hop_count
                        route["via"] = self.p_rx.sender
                        print("Found shorter or newer RTE to ", hex(self.p_rx.source))
                        break
                    else:
                        print("Received existing route to", hex(self.p_rx.source))
        serialized_rt = json.dumps(self.rt)
        try:
            self.file_rt = open('rt.json', 'w+')
            self.file_rt.write(serialized_rt)
            self.file_rt.close()
        except:
            print("Failed to save RT to file")
            pass

    async def heartbeat_cycle(self):
        print("Rx Timeout(sym):", self.id[3] | 0x300)
        print("Listening...")
        rx_result = await self.lora.async_rx_single()
        if rx_result is not None:
            self.parse_packet(rx_result)
        else:
            await self.send_heartbeat()
        pass
