'''
G17 ICN Node
'''
from __future__ import annotations
import httpx
import logging
from aiohttp import web
import asyncio
from datetime import datetime
import JWT
from http_server import HTTPServer
from cache import CACHEStore
from DeviceInterface import DeviceInterface

PACKET_FIELD_DATA_NAME =                "data_name"
PACKET_FIELD_REQUESTOR_PUBLIC_KEY =     "requestor_public_key"
PACKET_FIELD_SENDER_PUBLIC_KEY =        "sender_public_key"
PACKET_FIELD_REQUEST_TYPE =             "type"
PACKET_FIELD_CREATED_AT =               "created_at"
PACKET_FIELD_DATA_PLAIN =               "data"
#PACKET_FIELD_PORT_NUMBER=               "port"
PACKET_FIELD_DEVICE_INTERFACE = "device_interface"
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
        self.jwt.init_jwt(key_size=512)
        self.debug_flag=False
        # TODO: define these from seperate class cache       
        self.PIT = {} 
        self.FIB = {}
        self.CACHE = {}
        self.neighbours = []
        # self.TRUSTED_IDS = self.emulation.generate_trusted_keys_table_all_nodes()

    def create_FIB_entry(self,data_name, hop,device_interface_dict):
        entry = {}
        entry['hop']=hop
        entry['port']=device_interface_dict
        entry['created_at']=datetime.now().timestamp()
        self.FIB[data_name]=entry

    '''
    TODO: Shift this send/forward logic to storing and routing
    '''

    async def handle_satisfy_packet(self, packet, jwt, hop=None):
        assert type(hop) == int
        data_name = packet.get(PACKET_FIELD_DATA_NAME)
        #_list = self.PIT[data_name]['waiting_list']
        pit_entry = self.PIT.get(data_name)
        _list = None
        if pit_entry:
            _list = pit_entry.get('waiting_list')
        if _list is None:
            _list=[DeviceInterface.from_dict(packet[PACKET_FIELD_DEVICE_INTERFACE])]

        #print(f"now the {self.task_id} node has a waiting list {_list} for {data_name}")

        data = packet.get(PACKET_FIELD_DATA_PLAIN)
        await self.send_to_network(data_name,data,hop,_list)
        self.PIT.pop(data_name,None)

        entry_fib = self.FIB.get(data_name)
        if entry_fib==None:
            self.create_FIB_entry(data_name,hop,packet[PACKET_FIELD_DEVICE_INTERFACE])
        else:
            if entry_fib['hop']>hop:
                # TODO: rename to "device_interface"
                entry_fib['port']=packet[PACKET_FIELD_DEVICE_INTERFACE]

        # TODO verify packet came from a trusted sender
        # TODO delete entry that time is invalid
        self.CACHE[data_name] = packet.get(PACKET_FIELD_DATA_PLAIN)

       # print(f"{self.task_id} get a message {data_name}, cache number is {len(self.CACHE)}")

    async def propagate_interest(self,packet,hop=None):
        assert type(hop) == int
        current_neighbours = self.emulation.discover_neighbours(self.task_id)
        packet[PACKET_FIELD_DEVICE_INTERFACE]=self.device_interface_dict()
        # TODO: propagate more conservatively
        def di2task(di: DeviceInterface):
            return asyncio.create_task(self.send_payload_to(di,payload=self.jwt.encode(packet),hop=hop+1))
        
        next_port = self.FIB.get(packet[PACKET_FIELD_DATA_NAME],None)
        print("NEXT PORT", next_port)
        if next_port:
            tasks=[di2task(next_port)]
        else:
            tasks = [di2task(port) for port in current_neighbours]
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
        self.logger.debug(f"GOT DATA: {data} {self.server.port}")
        if data:
            #print(f"get data {self.task_id}")
            return await self.send_to_network(data_name, data,hop, [packet[PACKET_FIELD_DEVICE_INTERFACE]] )
        
        is_the_first=True  # true represented this request is the first request for some interst

        if self.PIT.get(data_name) is None:
            #self.PIT[data_name] = set()
            self.PIT[data_name]={} # PIT should be a dictionary of dictionary, instead of a set.
            sub_dict={}
            sub_dict['waiting_list']=[]
            sub_dict['waiting_list'].append(packet[PACKET_FIELD_DEVICE_INTERFACE])
            sub_dict['time_stamp']= datetime.now().timestamp()  # mark the time intersted entry created
            self.PIT[data_name]=sub_dict
            await self.propagate_interest(packet,hop=hop+1)       
        else:
            
            self.PIT[data_name]['waiting_list'].append(packet[PACKET_FIELD_DEVICE_INTERFACE])
            

            
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
        self.neighbours = self.emulation.discover_neighbours(self.task_id)
        self.logger.debug(f"got neighbours {str(self.neighbours)}")
        return self.neighbours
    
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
                asyncio.create_task(self.handle_interest_packet(packet,jwt,hop=hop_count+1))
        elif packet_type == "satisfy":
                asyncio.create_task(self.handle_satisfy_packet(packet,jwt,hop=hop_count))
        else:
                raise Exception("unrecognised packet type: " + str(packet_type))
        return web.Response(text="ok")

    async def send_payload_to(self,di: DeviceInterface, payload=None,hop=0):
        try:
            print("device interface", di)
            assert type(di) == DeviceInterface or di["host"] and di["port"] and di["key_name"]
        except AssertionError as e:
            print("device interface is wrong type:", di)
            print(str(Exception()),str(e))
        assert payload is not None
        request = self.jwt.decode(payload)

        url = "http://" + di["host"] + ":" + str(di["port"]) if type(di) is not DeviceInterface else di.url()

        async with httpx.AsyncClient() as client:
            headers = {HOP_HEADER: str(hop)}
            await client.post(url, content=payload, headers=headers)
    
    # send named data to the network
    async def send_to_network(self, data_name, data, hop, neighbours):
        #current_neighbours = self.emulation.discover_neighbours(self.task_id)
        payload = self.jwt.encode({
            PACKET_FIELD_REQUEST_TYPE: "satisfy",
            PACKET_FIELD_DATA_NAME: data_name,
            PACKET_FIELD_DATA_PLAIN: data,
            # TODO: don't decode every time
            PACKET_FIELD_SENDER_PUBLIC_KEY: self.jwt.public_key.decode("utf-8"),
            PACKET_FIELD_CREATED_AT: datetime.now().timestamp(),
            PACKET_FIELD_DEVICE_INTERFACE: DeviceInterface.from_device(self).to_dict()
        })

        def di2task(di: DeviceInterface) -> asyncio.Task:
            coroutine = self.send_payload_to(di, hop=hop,payload=payload, )
            return asyncio.create_task(coroutine)
        [di2task(di) for di in neighbours] # directly pass the data to the requestor, the reason that do not need to use neighbour is we just want to pass the data to the node who needs it.


    def device_interface_dict(self):
        return DeviceInterface.from_device(self).to_dict()
    
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

                self.logger.debug(f"got item '{item}' from desire queue: node {self.task_id}: port: {self.server.port}")

                current_neighbours = self.discover_neighbours()
                d = {
                    PACKET_FIELD_REQUEST_TYPE: "interest",
                    PACKET_FIELD_DATA_NAME: item,
                    PACKET_FIELD_REQUESTOR_PUBLIC_KEY: self.jwt.public_key.decode('utf-8'),
                    PACKET_FIELD_CREATED_AT: datetime.now().timestamp(),
                    PACKET_FIELD_DEVICE_INTERFACE: self.device_interface_dict()
                }
                print(d)
                payload = self.jwt.encode(d)
                tasks = [asyncio.create_task(self.send_payload_to(di, payload)) for di in current_neighbours]
                await asyncio.gather(*tasks)
                

        self.desire_queue = queue
        self.desire_queue_task = asyncio.create_task(handle())
        return self.desire_queue_task

    async def start(self):
        self.logger.debug(f"starting node {self.task_id}")
        await self.server.start()


if __name__ == "__main__":
    async def main():
        class Emulation:
            def __init__(self):
                pass
            def discover_neighbours(self,task_id):
                import get_ip_address
                return [DeviceInterface.from_dict({
                    "host": get_ip_address.get_ip_address(),
                    "port": 34000,
                    "key_name": "abc",
                })]

        em = Emulation()

        device = Device(0, em)
        await device.start()
        import interest_emulation
        q = interest_emulation.desire_queue_deterministic(["a","b","c"],interval=1)
        device.set_desire_queue(q)
        await device.send_payload_to(device.device_interface_dict(), payload=device.jwt.encode({"hi": "ok"}), hop=0)

    asyncio.run(main())