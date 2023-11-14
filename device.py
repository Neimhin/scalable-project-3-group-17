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
PACKET_FIELD_PORT_NUMBER=               "port"
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
        self.debug_flag=False
        # TODO: define these from seperate class cache       
        self.PIT = {} 
        self.FIB = {}
        self.CACHE = {}
        self.neigbour_ports = []
        # self.TRUSTED_IDS = self.emulation.generate_trusted_keys_table_all_nodes()

    def create_FIB_entry(self,data_name, hop,port):
        entry = {}
        entry['hop']=hop
        entry['port']=port
        entry['created_at']=datetime.now().timestamp()
        self.FIB[data_name]=entry


    async def handle_satisfy_packet(self, packet, jwt, hop=None):
        assert type(hop) == int
        data_name = packet.get(PACKET_FIELD_DATA_NAME)
        #_list = self.PIT[data_name]['waiting_list']
        data_entry = self.PIT.get(data_name)
        if data_entry:
            _list = data_entry.get('waiting_list')
            if _list==None:
                _list=[packet[PACKET_FIELD_PORT_NUMBER]]
        else:
            _list=[packet[PACKET_FIELD_PORT_NUMBER]]

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
        def port2task(port):
            return asyncio.create_task(self.send_payload_to(port,payload=self.jwt.encode(packet),hop=hop+1))
        
        next_port = self.FIB.get(packet[PACKET_FIELD_DATA_NAME],None)
        if next_port:
            tasks=[port2task(next_port)]
        else:
            tasks = [port2task(port) for port in current_neighbours]
        together = asyncio.gather(*tasks)
        await together

    async def handle_interest_packet(self, packet, jwt, hop=None,):
        assert type(hop) == int
        self.logger.debug(packet)
        data_name=packet[PACKET_FIELD_DATA_NAME]
        requestor = packet[PACKET_FIELD_REQUESTOR_PUBLIC_KEY]
        if requestor == self.jwt.public_key:
            return

        data = self.CACHE.get(data_name)
        self.logger.debug("GOT DATA: ", data, self.server.port)
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

    async def send_payload_to(self,port,payload=None,hop=0):
        assert type(port) == int
        assert payload is not None
        request = self.jwt.decode(payload)
        data_name = request[PACKET_FIELD_DATA_NAME]

        #print(f"{self.task_id} node is sending request to {port} for {data_name}")

        async with httpx.AsyncClient() as client:
            headers = {HOP_HEADER: str(hop)}
            await client.post(self.HOSTNAME + str(port), content=payload, headers=headers)
    
    # send named data to the network
    async def send_to_network(self, data_name, data,hop,ports):
        #current_neighbours = self.emulation.discover_neighbours(self.task_id)
        payload = self.jwt.encode({
            PACKET_FIELD_REQUEST_TYPE: "satisfy",
            PACKET_FIELD_DATA_NAME: data_name,
            PACKET_FIELD_DATA_PLAIN: data,
            PACKET_FIELD_SENDER_PUBLIC_KEY: self.jwt.public_key.decode("utf-8"),
            PACKET_FIELD_CREATED_AT: datetime.now().timestamp(),
            PACKET_FIELD_PORT_NUMBER:self.server.port
        })

        def port2task(port):
            coroutine = self.send_payload_to(port, hop=hop,payload=payload, )
            return asyncio.create_task(coroutine)
        
        #[port2task(port) for port in current_neighbours]
        [port2task(port) for port in ports] # directly pass the data to the requestor, the reason that do not need to use neighbour is we just want to pass the data to the node who needs it.

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

                current_neighbour_ports = self.emulation.discover_neighbours(self.task_id)
                payload = self.jwt.encode({
                    PACKET_FIELD_REQUEST_TYPE: "interest",
                    PACKET_FIELD_DATA_NAME: item,
                    PACKET_FIELD_REQUESTOR_PUBLIC_KEY: self.jwt.public_key.decode('utf-8'),
                    PACKET_FIELD_CREATED_AT: datetime.now().timestamp(),
                    PACKET_FIELD_PORT_NUMBER:self.server.port
                })
                tasks = [asyncio.create_task(self.send_payload_to(port, payload)) for port in current_neighbour_ports]
                await asyncio.gather(*tasks)
                

        self.desire_queue = queue
        self.desire_queue_task = asyncio.create_task(handle())

    async def start(self):
        self.logger.debug(f"starting node {self.task_id}")
        await self.server.start()
