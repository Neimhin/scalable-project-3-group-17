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
PACKET_FIELD_TASK_ID=                   "task_id"
HOP_HEADER =                            "x-tcdicn-hop"


class Device:
    # TODO: remove circular depedency Device has ICNEmulator and ICNEmulator has list of Device's
    def __init__(self, task_id, emulation):
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
        # TODO: define these from seperate class cache       
        self.PIT = self.CACHE.get_PIT()
        self.FIB = self.CACHE.get_FIB()
        self.CIS = self.CACHE.get_CIS()
        self.neigbour_ports = []
        # self.TRUSTED_IDS = self.emulation.generate_trusted_keys_table_all_nodes()

    '''
    TODO: Shift this send/forward logic to storing and routing
    '''

    
        
    def create_FIB_entry(self,data_name, hop,task_id):#[zhfu 13-Nov]
        entry = {}
        entry['hop']=hop
        entry['task_id']=task_id
        entry['created_at']=datetime.now().timestamp()
        self.FIB[data_name]=entry

    async def handle_satisfy_packet(self, packet, jwt, hop=None): #[zhfu 13-Nov]
        assert type(hop) == int
        data_name = packet.get(PACKET_FIELD_DATA_NAME)
        data_entry = self.PIT.get(data_name)

        if data_entry:
            _list = data_entry.get('waiting_list')
            if _list==None:
                _list=[packet[PACKET_FIELD_TASK_ID]]
        else:
            _list=[packet[PACKET_FIELD_TASK_ID]]
        _list=self.transfer_task_id2interface(_list)
        print(f"now the {self.task_id} node has a waiting list {_list} for {data_name}")

        data = packet.get(PACKET_FIELD_DATA_PLAIN)
        await self.send_to_network(data_name,data,hop,_list)
        self.PIT.pop(data_name,None)

        entry_fib = self.FIB.get(data_name)
        if entry_fib==None:
            self.create_FIB_entry(data_name,hop,packet[PACKET_FIELD_TASK_ID])
        else:
            if entry_fib['hop']>hop:
                entry_fib['task_id']=packet[PACKET_FIELD_TASK_ID]

        # TODO verify packet came from a trusted sender
        # TODO delete entry that time is invalid
        self.CIS[data_name] = packet.get(PACKET_FIELD_DATA_PLAIN)

        print(f"{self.task_id} get a message {data_name}, cache number is {len(self.CIS.items())}")

    def transfer_task_id2interface(self,task_id_list):  # [zhfu 13-Nov-2023]
        '''
        task_id_list should be list. [task_id, task_id]
        '''
        return [self.neighbour[taskid] for taskid in task_id_list]

    async def propagate_interest(self,packet,hop=None):#[zhfu 13-Nov]
        assert type(hop) == int
        current_neighbours = self.emulation.discover_neighbours(self.task_id)
        packet[PACKET_FIELD_TASK_ID] = self.task_id
        # TODO: propagate more conservatively
        def port2task(value):
            return asyncio.create_task(self.send_payload_to(value,payload=self.jwt.encode(packet),hop=hop+1))
        
        next_port = self.FIB.get(packet[PACKET_FIELD_DATA_NAME],None)
        if next_port:
            tasks = [port2task(next_port)]
        else:
            tasks = [port2task(value) for value in current_neighbours.values()]
        together = asyncio.gather(*tasks)
        await together

    async def handle_interest_packet(self, packet, jwt, hop=None):#[zhfu 13-Nov]
        assert type(hop) == int
        self.logger.debug(packet)
        data_name=packet[PACKET_FIELD_DATA_NAME]
        requestor = packet[PACKET_FIELD_REQUESTOR_PUBLIC_KEY]
        if requestor == self.jwt.public_key:
            return

        data = self.CIS.get(data_name)
        self.logger.debug("GOT DATA: ", data, self.server.port)
        if data:
            print(f"get data {self.task_id}")
            return await self.send_to_network(data_name, data,hop, [self.neighbour(packet[PACKET_FIELD_TASK_ID])] )
        
        is_the_first=True  # true represented this request is the first request for some interst

        if self.PIT.get(data_name) is None:
            #self.PIT[data_name] = set()
            self.PIT[data_name]={} # PIT should be a dictionary of dictionary, instead of a set.
            sub_dict={}
            sub_dict['waiting_list']=[]
            sub_dict['waiting_list'].append(packet[PACKET_FIELD_TASK_ID])
            sub_dict['time_stamp']= datetime.now().timestamp()  # mark the time intersted entry created
            self.PIT[data_name]=sub_dict
            await self.propagate_interest(packet,hop=hop+1)       
        else:
            
            self.PIT[data_name]['waiting_list'].append(packet[PACKET_FIELD_TASK_ID])
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
        if packet_type == "interest":
                asyncio.create_task(self.handle_interest_packet(packet,jwt,hop=hop_count))
        elif packet_type == "satisfy":
                asyncio.create_task(self.handle_satisfy_packet(packet,jwt,hop=hop_count))
        else:
                raise Exception("unrecognised packet type: " + packet_type)
        return web.Response(text="ok")

    async def send_payload_to(self,value,payload=None,hop=0):
        assert type(value['port']) == int
        assert payload is not None
        request = self.jwt.decode(payload)
        data_name = request[PACKET_FIELD_DATA_NAME]

        #print(f"{self.task_id} node is sending request to {port} for {data_name}")

        async with httpx.AsyncClient() as client:
            headers = {HOP_HEADER: str(hop)}
            await client.post(value['ip'] + str(value['port']), content=payload, headers=headers)
    
    # send named data to the network
    async def send_to_network(self, data_name, data,hop,values):
        #current_neighbours = self.emulation.discover_neighbours(self.task_id)
        payload = self.jwt.encode({
            PACKET_FIELD_REQUEST_TYPE: "satisfy",
            PACKET_FIELD_DATA_NAME: data_name,
            PACKET_FIELD_DATA_PLAIN: data,
            PACKET_FIELD_SENDER_PUBLIC_KEY: self.jwt.public_key.decode("utf-8"),
            PACKET_FIELD_CREATED_AT: datetime.now().timestamp(),
            PACKET_FIELD_TASK_ID:self.task_id
        })

        def port2task(value):
            coroutine = self.send_payload_to(value, hop=hop,payload=payload, )
            return asyncio.create_task(coroutine)
        
        #[port2task(port) for port in current_neighbours]
        [port2task(value) for value in values] # directly pass the data to the requestor, the reason that do not need to use neighbour is we just want to pass the data to the node who needs it.


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
                current_neighbour = self.emulation.discover_neighbours(self.task_id)
                context={
                    PACKET_FIELD_REQUEST_TYPE: "interest",
                    PACKET_FIELD_DATA_NAME: item,
                    PACKET_FIELD_REQUESTOR_PUBLIC_KEY: self.jwt.public_key.decode('utf-8'),
                    PACKET_FIELD_TASK_ID: self.task_id,
                    PACKET_FIELD_CREATED_AT: datetime.now().timestamp()
                }
                payload = self.jwt.encode(context)
                tasks = [asyncio.create_task(self.send_payload_to(value, payload)) for value in current_neighbour.values()]
                together = asyncio.gather(*tasks)
                await together

        self.desire_queue = queue
        self.desire_queue_task = asyncio.create_task(handle())

    async def start(self):
        self.logger.debug(f"starting node {self.task_id}")
        await self.server.start()
