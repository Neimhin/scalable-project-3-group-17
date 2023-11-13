'''
G17 ICN Node Implemenation
'''

from __future__ import annotations
import emulator
import httpx
import logging
import aiohttp
from aiohttp import web
import asyncio
from datetime import datetime
from typing import Optional

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
    def __init__(self, task_id, emulation: Optional[emulator.ICNEmulator]):
        self.task_id = task_id
        self.logger = logging.getLogger()
        self.emulation = emulation
        self.HOSTNAME = 'http://localhost:'
        self.CACHE = CACHEStore()
        async def handler_async(request):
            return await self.handler(request)
        self.server = HTTPServer(handler_async)
        self.desire_queue_task = None
        self.desire_queue = None
        self.jwt = JWT.JWT()
        self.jwt.init_jwt(key_size=32) 
        self.PIT = self.CACHE.get_PIT()
        self.FIB = self.CACHE.get_FIB()
        self.CIS = self.CACHE.get_CIS()
        self.neigbour_ports = []
        # self.TRUSTED_IDS = self.emulation.generate_trusted_keys_table_all_nodes()

    #--------------------------------------------------COMMENTS BY NAARORA----------------------------------------------------#


    #-------------------TODO: Shift this following send/forward logic to storing_and_routing script :TODO---------------------#
    #NA TASK


    '''
    Data packet has been received, now we store it in our CIS
    '''
    async def handle_satisfy_packet(self, packet, jwt, hop=None):
        assert type(hop) == int
        data_name = packet.get(PACKET_FIELD_DATA_NAME)
        # TODO verify packet came from a trusted sender
        self.CIS[data_name] = packet.get(PACKET_FIELD_DATA_PLAIN)


    '''
    Send Interest packets further to neighbours as there is no matching entry in CIS
    '''
    async def propagate_interest(self,jwt,hop=None):
        assert type(hop) == int
        current_neighbours = await self.emulation.discover_neighbours(self.task_id)
        # TODO: propagate more conservatively
        def port2task(port):
            return asyncio.create_task(self.send_payload_to(port,payload=jwt,hop=hop+1))
        tasks = [port2task(port) for port in current_neighbours]
        together = asyncio.gather(*tasks)
        await together

    '''
    When we recieve an interest packet, 
    if we have the data in CIS we return it to the device requesting for it
    If we don't have it we make an netry in the PIT and 
    then propagate the interest further as just above
    '''
    async def handle_interest_packet(self, packet, jwt, hop=None):
        assert type(hop) == int
        self.logger.debug(packet)
        data_name=packet[PACKET_FIELD_DATA_NAME]
        requestor = packet[PACKET_FIELD_REQUESTOR_PUBLIC_KEY]
        if requestor == self.jwt.public_key:
            return

        data = self.CIS.get(data_name)
        self.logger.debug("GOT DATA: ", data, self.server.port)
        if data:
            return await self.send_to_network(data_name, data)
        
        if self.PIT.get(data_name) is None:
            self.PIT[data_name] = set()
        # PIT_ENTRY = {
        #     "what they want": data_name,
        #     "who wants it": <port>, # TODO: hash of public key, not full public key
        #     "packet jwt": jwt, # <jwt-headers>.{ "data_name": ..., "requestor_public_key": ..., }.<signature>
        #     "when did they want it": packet[PACKET_FIELD_CREATED_AT],
        # }
        self.PIT[data_name].add(requestor)

        # self.FIB[data_name] = {
        #     "created_at": <timestamp>, # when was the interest packet generated?
        #     "who has it": [<port>, <port>, <port>], #TODO don't use ports, use hash of public key
        # }

        await self.propagate_interest(jwt,hop=hop)


    '''
    Receive list of neighbours from Emulator
    '''
    async def discover_neighbours(self):
        self.neighbour = await self.emulation.discover_neighbours(self.task_id)
        self.logger.debug(f"got neighbours {str(self.neighbour)}")
        return self.neighbour
    

    '''
    Check to see the pakcet type - interest or data
    Handle accordingly
    '''
    async def handler(self, request):
        hop_count=None
        try:
            self.logger.debug(request.headers)
            hop_count = int(request.headers.get(HOP_HEADER))
        except Exception as e:
            self.logger.debug(e)
            self.logger.debug(request.headers())
            return web.Response(text="failed",status=400)
        jwt = await request.text()
        packet = self.jwt.decode(jwt)
        # TODO: validate packet format
        # TODO: check if id exists in TRUSTED_IDS
        packet_type = packet.get(PACKET_FIELD_REQUEST_TYPE)
        self.logger.debug(packet_type)
        if packet_type == "interest":
                asyncio.create_task(self.handle_interest_packet(packet,jwt,hop=hop_count))
        elif packet_type == "satisfy":
                asyncio.create_task(self.handle_satisfy_packet(packet,jwt,hop=hop_count))
        else:
                raise Exception("unrecognised packet type: " + packet_type)
        return web.Response(text="ok")


    '''
    Sendind packet to device with HOSTNAME at port
    '''
    async def send_payload_to(self,port,payload=None,hop=0):
        assert type(port) == int
        assert payload is not None
        async with httpx.AsyncClient() as client:
            headers = {HOP_HEADER: str(hop)}
            await client.post(self.HOSTNAME + str(port), content=payload, headers=headers)
    

    '''
    Create packet encoding it via jwt
    send named data to the network
    Publishing ACTUAL DATA PACKET to another device
    WHAT IS HOP ????
    '''
    async def send_to_network(self, data_name, data):
        current_neighbours = await self.emulation.discover_neighbours(self.task_id)
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


    '''
    Set the desire or requests for data for current simulation
    Send interest packet to neighbours to get the desired data
    '''
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
                if self.CIS.get(item):
                    continue
                self.logger.debug(f"got item '{item}' from desire queue: node {self.task_id}: port: {self.server.port}")
                current_neighbour_ports = await self.emulation.discover_neighbours(self.task_id)
                
                # TODO: Use packet class {NARORA task}
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


    '''
    Start the async server for the device
    '''
    async def start(self):
        self.logger.debug(f"starting node {self.task_id}")
        await self.server.start()
