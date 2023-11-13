'''
G17 ICN Node
'''

from __future__ import annotations
from typing import Optional
import emulator
import httpx
import logging
import aiohttp
from aiohttp import web
import asyncio
from datetime import datetime
import JWT
from http_server import HTTPServer
from cache import CACHEStore
from typing import Tuple

PACKET_FIELD_DATA_NAME =                "data_name"
PACKET_FIELD_REQUESTOR_PUBLIC_KEY =     "requestor_public_key"
PACKET_FIELD_SENDER_PUBLIC_KEY =        "sender_public_key"
PACKET_FIELD_REQUEST_TYPE =             "type"
PACKET_FIELD_CREATED_AT =               "created_at"
PACKET_FIELD_DATA_PLAIN =               "data"
PACKET_FIELD_PORT_NUMBER=               "port"
HOP_HEADER =                            "x-tcdicn-hop"

class Device:
    # TODO: remove circular depedency Device has ICNEmulator and ICNEmulator has list of Device's
    def __init__(self, task_id, emulation: Optional[emulator.ICNEmulator]):
        self.task_id = task_id
        self.logger = logging.getLogger()
        self.emulation = emulation
        self.CACHE = {} # TODO: use  CACHEStore()
        async def handler_async(request):
            return await self.handler(request)
        self.server = HTTPServer(handler_async)
        self.desire_queue_task = None
        self.desire_queue = None
        self.jwt = JWT.JWT()
        self.jwt.init_jwt(key_size=32)
        self.debug_flag=False
        # TODO: define these from seperate class cache       
        self.PIT = {} 
        self.FIB = {}
        self.CACHE = {}
        self.neigbour_ports = []

        self.payloads_sent = 0
        self.interest_packets_handled = 0
        self.satisfy_packets_handled = 0
        # self.TRUSTED_IDS = self.emulation.generate_trusted_keys_table_all_nodes()

    def create_FIB_entry(self,data_name, hop,port):
        entry = {}
        entry['hop']=hop
        entry['port']=port
        entry['created_at']=datetime.now().timestamp()
        self.FIB[data_name]=entry

    async def handle_satisfy_packet(self, packet, jwt, hop=None):
        self.satisfy_packets_handled = self.satisfy_packets_handled + 1
        assert type(hop) == int
        data_name = packet.get(PACKET_FIELD_DATA_NAME)
        #_list = self.PIT[data_name]['waiting_list']
        data_entry = self.PIT.get(data_name)
        if data_entry:
            _list = data_entry.get('waiting_list')
            if _list==None:
                _list=[packet[PACKET_FIELD_SENDER_PUBLIC_KEY]]
        else:
            _list=[packet[PACKET_FIELD_SENDER_PUBLIC_KEY]]

        #print(f"now the {self.task_id} node has a waiting list {_list} for {data_name}")

        data = packet.get(PACKET_FIELD_DATA_PLAIN)
        await self.send_to_network(data_name,data,hop,_list)
        self.PIT.pop(data_name,None)

        entry_fib = self.FIB.get(data_name)
        if entry_fib==None:
            self.create_FIB_entry(data_name,hop,packet[PACKET_FIELD_PORT_NUMBER])
        else:
            if entry_fib['hop']>hop:
                entry_fib['port']=packet[PACKET_FIELD_PORT_NUMBER]

        # TODO verify packet came from a trusted sender
        # TODO delete entry that time is invalid
        self.CACHE[data_name] = packet.get(PACKET_FIELD_DATA_PLAIN)

       # print(f"{self.task_id} get a message {data_name}, cache number is {len(self.CACHE)}")

    async def propagate_interest(self,packet,hop=None):
        assert type(hop) == int
        current_neighbours = self.emulation.discover_neighbours(self.task_id)
        packet[PACKET_FIELD_PORT_NUMBER]=self.server.port
        # TODO: propagate more conservatively
        def device_descriptor2task(device_descriptor):
            return asyncio.create_task(self.send_payload_to(device_descriptor,payload=self.jwt.encode(packet),hop=hop+1))
        
        next_port = self.FIB.get(packet[PACKET_FIELD_DATA_NAME],None)
        if False and next_port:
            tasks=[device_descriptor2task(next_port)]
        else:
            tasks = [device_descriptor2task(device_descriptor) for device_descriptor in current_neighbours]
        together = asyncio.gather(*tasks)
        await together

    async def handle_interest_packet(self, packet, jwt, hop=None,):
        self.interest_packets_handled = self.interest_packets_handled + 1
        assert type(hop) == int
        self.logger.debug(packet)
        data_name=packet[PACKET_FIELD_DATA_NAME]
        requestor = packet[PACKET_FIELD_REQUESTOR_PUBLIC_KEY]
        if requestor == self.jwt.public_key:
            return

        data = self.CACHE.get(data_name)
        self.logger.debug(f"GOT DATA: {data} {self.jwt.key_name[:10]}")
        if data:
            #print(f"get data {self.task_id}")
            return await self.send_to_network(data_name, data,hop, [packet[PACKET_FIELD_PORT_NUMBER]] )
        
        is_the_first=True  # true represented this request is the first request for some interst

        if self.PIT.get(data_name) is None:
            #self.PIT[data_name] = set()
            self.PIT[data_name]={} # PIT should be a dictionary of dictionary, instead of a set.
            sub_dict={}
            sub_dict['waiting_list']=[]
            sub_dict['waiting_list'].append(packet[PACKET_FIELD_PORT_NUMBER])
            sub_dict['time_stamp']= datetime.now().timestamp()  # mark the time intersted entry created
            self.PIT[data_name]=sub_dict
            await self.propagate_interest(packet,hop=hop+1)       
        else:
            
            self.PIT[data_name]['waiting_list'].append(packet[PACKET_FIELD_PORT_NUMBER])
            #print(f"node {self.task_id} in {data_name} get another request from {packet[PACKET_FIELD_PORT_NUMBER]} waiting list is {self.PIT[data_name]['waiting_list']}")
            

            
        # PIT_ENTRY = {
        #     "what they want": data_name,
        #     "who wants it": [port,], # TODO: hash of public key, not full public key
        #     "packet jwt": jwt, # <jwt-headers>.{ "data_name": ..., "requestor_public_key": ..., }.<signature>
        #     "when did they want it": packet[PACKET_FIELD_CREATED_AT],
        # }

        #self.PIT[data_name].add(requestor)
        

        # self.FIB[data_name] = {
        #     "created_at": <timestamp>, # when was the interest packet generated?
        #     "port": [<port>], #TODO don't use port, use hash of public key,
        #      "hop": hop value   #represented the min value to go to node
        # }
        # if is_the_first:
             

    def discover_neighbours(self):
        self.neighbour = self.emulation.discover_neighbours(self.task_id)
        self.logger.debug(f"got neighbours {str(self.neighbour)}")
        return self.neighbour
    
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

        #print(f"data type is {packet_type}, now node task_id is {self.task_id}, reveive request data_name is {packet[PACKET_FIELD_DATA_NAME]}, the requestor node port number is {packet[PACKET_FIELD_PORT_NUMBER]}")

        if packet_type == "interest":
                asyncio.create_task(self.handle_interest_packet(packet,jwt,hop=hop_count+1))
        elif packet_type == "satisfy":
                asyncio.create_task(self.handle_satisfy_packet(packet,jwt,hop=hop_count))
        else:
                raise Exception("unrecognised packet type: " + packet_type)
        return web.Response(text="ok")

    async def send_payload_to(self,device_descriptor: Tuple(str,str,int),payload: str=None,hop=0):
        print(device_descriptor)
        key_name, host, port = (None,None,None)
        try:
            key_name, host, port = device_descriptor
        except Exception as e:
            print(device_descriptor, payload)
            print(f"bad format device descriptor: {e}")
            exit()
        self.logger.debug(f"sending payload {key_name}, {host}, {port}, {payload[:20]}")
        assert type(port) == int
        assert payload is not None
        async with httpx.AsyncClient() as client:
            headers = {HOP_HEADER: str(hop)}
            await client.post(f"http://{host}:{port}", content=payload, headers=headers)
            self.payloads_sent = self.payloads_sent + 1
            print(f"PAYLOADS SENT: from {self.server.port} {self.payloads_sent}")
    
    # send named data to the network
    async def send_to_network(self, data_name, data,hop,forward_to_key_names):
        current_neighbours = self.emulation.discover_neighbours(self.task_id)
        neighbour_dict = {d[0]: d for d in current_neighbours}
        forward_to = []
        for name in forward_to_key_names:
            device = neighbour_dict.get(name)
            if device:
                forward_to.append(device)


        payload = self.jwt.encode({
            PACKET_FIELD_REQUEST_TYPE: "satisfy",
            PACKET_FIELD_DATA_NAME: data_name,
            PACKET_FIELD_DATA_PLAIN: data,
            PACKET_FIELD_SENDER_PUBLIC_KEY: self.jwt.key_name,
            PACKET_FIELD_CREATED_AT: datetime.now().timestamp(),
            PACKET_FIELD_PORT_NUMBER:self.server.port
        })

        def device_descriptor2task(device_descriptor):
            coroutine = self.send_payload_to(device_descriptor, hop=hop,payload=payload, )
            return asyncio.create_task(coroutine)
        
        #[port2task(port) for port in current_neighbours]
        together = asyncio.gather(*[device_descriptor2task(dd) for dd in forward_to]) # directly pass the data to the requestor, the reason that do not need to use neighbour is we just want to pass the data to the node who needs it.
        await together

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
                #print(f"want got item '{item}' from desire queue: node {self.task_id}: port: {self.server.port}")

                self.logger.debug(f"got item '{item}' from desire queue: node {self.task_id}: port: {self.server.port}")

                current_neighbours = self.emulation.discover_neighbours(self.task_id)
                self.logger.debug(str(current_neighbours))
                payload = self.jwt.encode({
                    PACKET_FIELD_REQUEST_TYPE: "interest",
                    PACKET_FIELD_DATA_NAME: item,
                    PACKET_FIELD_REQUESTOR_PUBLIC_KEY: self.jwt.key_name,
                    PACKET_FIELD_CREATED_AT: datetime.now().timestamp(),
                    PACKET_FIELD_PORT_NUMBER:self.server.port
                })
                tasks = [asyncio.create_task(self.send_payload_to(device_descriptor, payload)) for device_descriptor in current_neighbours]
                await asyncio.gather(*tasks)
                

        self.desire_queue = queue
        self.desire_queue_task = asyncio.create_task(handle())

    async def start(self):
        print("STARTING DEVICE")
        self.logger.debug(f"starting node {self.task_id}")
        await self.server.start()
