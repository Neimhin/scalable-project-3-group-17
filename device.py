'''
G17 ICN Node
'''

import httpx
import logging
import aiohttp
from aiohttp import web
import asyncio
from datetime import datetime

import JWT
from http_server import HTTPServer
from cache import CACHEStore

PACKET_FIELD_DATA_NAME =                "data_name"
PACKET_FIELD_REQUESTOR_PUBLIC_KEY =     "requestor_public_key"
PACKET_FIELD_SENDER_PUBLIC_KEY =        "sender_public_key"
PACKET_FIELD_REQUEST_TYPE =             "type"
PACKET_FIELD_CREATED_AT =               "created_at"
PACKET_FIELD_DATA_PLAIN =               "data"
HOP_HEADER =                            "x-tcdicn-hop"

class Device:
    # TODO: remove circular depedency Device has ICNEmulator and ICNEmulator has list of Device's
    def __init__(self, task_id, emulation):
        self.task_id = task_id
        self.logger = logging.getLogger()
        self.emulation = emulation
        self.HOSTNAME = 'http://localhost:'
        self.CACHE = {} # TODO: use  CACHEStore()
        async def handler_async(request):
            return await self.handler(request)
        self.server = HTTPServer(handler_async)
        self.desire_queue_task = None
        self.desire_queue = None
        self.jwt = JWT.JWT()
        self.jwt.init_jwt(key_size=32) 
        # TODO: define these from seperate class cache       
        self.PIT = {} 
        self.FIB = {}
        self.CACHE = {}
        self.neigbour_ports = []
        # self.TRUSTED_IDS = self.emulation.generate_trusted_keys_table_all_nodes()

    async def handle_satisfy_packet(self, packet, jwt, hop=None):
        assert type(hop) == int
        data_name = packet.get(PACKET_FIELD_DATA_NAME)
        # TODO verify packet came from a trusted sender
        self.CACHE[data_name] = packet.get(PACKET_FIELD_DATA_PLAIN)

    async def propagate_interest(self,jwt,hop=None):
        assert type(hop) == int
        current_neighbours = self.emulation.discover_neighbours(self.task_id)
        # TODO: propagate more conservatively
        def port2task(port):
            return asyncio.create_task(self.send_payload_to(port,payload=jwt,hop=hop+1))
        tasks = [port2task(port) for port in current_neighbours]
        together = asyncio.gather(*tasks)
        await together

    async def handle_interest_packet(self, packet, jwt, hop=None):
        assert type(hop) == int
        print(packet)
        data_name=packet[PACKET_FIELD_DATA_NAME]
        requestor = packet[PACKET_FIELD_REQUESTOR_PUBLIC_KEY]
        if requestor == self.jwt.public_key:
            return

        data = self.CACHE.get(data_name)
        print("GOT DATA: ", data, self.server.port)
        if data:
            return await self.send_to_network(data_name, data)
        
        if self.PIT.get(data_name) is None:
            #self.PIT[data_name] = set()
            self.PIT[data_name]={} # PIT should be a dictionary of dictionary, instead of a set.
        # PIT_ENTRY = {
        #     "what they want": data_name,
        #     "who wants it": <port>, # TODO: hash of public key, not full public key
        #     "packet jwt": jwt, # <jwt-headers>.{ "data_name": ..., "requestor_public_key": ..., }.<signature>
        #     "when did they want it": packet[PACKET_FIELD_CREATED_AT],
        # }

        #self.PIT[data_name].add(requestor)
        

        # self.FIB[data_name] = {
        #     "created_at": <timestamp>, # when was the interest packet generated?
        #     "who has it": [<port>, <port>, <port>], #TODO don't use ports, use hash of public key
        # }

        await self.propagate_interest(jwt,hop=hop)

    def discover_neighbours(self):
        self.neighbour = self.emulation.discover_neighbours(self.task_id)
        self.logger.debug(f"got neighbours {str(self.neighbour)}")
        return self.neighbour
    
    async def handler(self, request):
        hop_count=None
        try:
            print(request.headers)
            hop_count = int(request.headers.get(HOP_HEADER))
        except Exception as e:
            print(e)
            print(request.headers())
            return web.Response(text="failed",status=400)
        jwt = await request.text()
        packet = self.jwt.decode(jwt)
        # TODO: validate packet format
        # TODO: check if id exists in TRUSTED_IDS
        packet_type = packet.get(PACKET_FIELD_REQUEST_TYPE)
        print(packet_type)
        match packet_type:
            case "interest":
                asyncio.create_task(self.handle_interest_packet(packet,jwt,hop=hop_count))
            case "satisfy":
                asyncio.create_task(self.handle_satisfy_packet(packet,jwt,hop=hop_count))
            case _:
                raise Exception("unrecognised packet type: " + packet_type)
        return web.Response(text="ok")

    async def send_payload_to(self,port,payload=None,hop=0):
        assert type(port) == int
        assert payload is not None
        async with httpx.AsyncClient() as client:
            headers = {HOP_HEADER: str(hop)}
            await client.post(self.HOSTNAME + str(port), content=payload, headers=headers)
    
    # send named data to the network
    async def send_to_network(self, data_name, data):
        current_neighbours = self.emulation.discover_neighbours(self.task_id)
        payload = self.jwt.encode({
            PACKET_FIELD_REQUEST_TYPE: "satisfy",
            PACKET_FIELD_DATA_NAME: data_name,
            PACKET_FIELD_DATA_PLAIN: data,
            PACKET_FIELD_SENDER_PUBLIC_KEY: self.jwt.public_key.decode("utf-8"),
            PACKET_FIELD_CREATED_AT: datetime.now().timestamp()
        })

        def port2task(port):
            coroutine = self.send_payload_to(port, payload=payload, hop=0)
            return asyncio.create_task(coroutine)
        [port2task(port) for port in current_neighbours]

    def set_desire_queue(self, queue):
        if self.desire_queue_task:
            self.desire_queue_task.cancel()
            # TODO: 
            # try:
            #   await self.desire_queue_task
            # except Exception as e:
            #   pass # handle exceptions
        async def handle():
            while True:
                item = await queue.get()
                if self.CACHE.get(item):
                    continue
                print(f"got item '{item}' from desire queue: node {self.task_id}: port: {self.server.port}")
                current_neighbour_ports = self.emulation.discover_neighbours(self.task_id)
                payload = self.jwt.encode({
                    PACKET_FIELD_REQUEST_TYPE: "interest",
                    PACKET_FIELD_DATA_NAME: item,
                    PACKET_FIELD_REQUESTOR_PUBLIC_KEY: self.jwt.public_key.decode('utf-8'),
                    PACKET_FIELD_CREATED_AT: datetime.now().timestamp()
                })
                tasks = [asyncio.create_task(self.send_payload_to(port, payload)) for port in current_neighbour_ports]
                together = asyncio.gather(*tasks)
                await together

        self.desire_queue = queue
        self.desire_queue_task = asyncio.create_task(handle())

    async def start(self):
        self.logger.debug(f"starting node {self.task_id}")
        await self.server.start()
