'''
G17 ICN Node
'''
from __future__ import annotations
import http_client
import logging
from aiohttp import web
import asyncio
from datetime import datetime
import JWT
from http_server import HTTPServer
from cache import CACHEStore
from DeviceInterface import DeviceInterface
import interest_emulation
from typing import List
from typing import Optional
import os



PACKET_FIELD_DATA_NAME =                "data_name"
PACKET_FIELD_REQUESTOR_PUBLIC_KEY =     "requestor_public_key"
PACKET_FIELD_SENDER_PUBLIC_KEY =        "sender_public_key"
PACKET_FIELD_REQUEST_TYPE =             "type"
PACKET_FIELD_CREATED_AT =               "created_at"
PACKET_FIELD_DATA_PLAIN =               "data"
PACKET_FIELD_REQUESTOR_KEY_NAME =       "requestor_key_name"
PACKET_FIELD_SENDER_KEY_NAME =          "requestor_key_name"
#PACKET_FIELD_PORT_NUMBER=               "port"

def find_device_by_key_name(key_name: str, dis: List(DeviceInterface)) -> Optional(DeviceInterface):
    for di in dis:
        if di.key_name == key_name:
            return di
    return None


# TODO: just send key_name in packet, not device_interface
PACKET_FIELD_DEVICE_INTERFACE = "device_interface"
HOP_HEADER =                            "x-tcdicn-hop"

class Device:
    # TODO: remove circular depedency Device has ICNEmulator and ICNEmulator has list of Device's
    def __init__(self, task_id, emulation,jwt_algorithm=None,host='localhost'):
        self.host = host
        self.task_id = task_id
        self.logger = logging.getLogger()
        self.emulation = emulation
        self.CACHE = {} # TODO: use  CACHEStore()
        async def handler_async(request):
            return await self.handler(request)
        self.server = HTTPServer(handler_async,host=host)
        self.desire_queue_task = None
        self.desire_queue = asyncio.Queue()
        self.jwt = JWT.JWT(algorithm=jwt_algorithm)
        self.jwt.init_jwt(key_size=512)
        self.debug_flag=False
        # TODO: define these from seperate class cache       
        self.PIT = {} 
        self.FIB = {}
        self.CACHE = {}
        self.neighbours = []
        # self.TRUSTED_IDS = self.emulation.generate_trusted_keys_table_all_nodes()

    async def init_logger(self):
        # Set up logging to a file
        await self.server.started.wait()
        log_filename = f"logs/{self.host}:{self.server.port}"
        os.makedirs(os.path.dirname(log_filename), exist_ok=True)
        
        # Create a logger
        self.logger = logging.getLogger(log_filename)
        self.logger.setLevel(logging.DEBUG)  # or any other level

        # Create file handler which logs even debug messages
        fh = logging.FileHandler(log_filename, mode='w')  # 'w' to overwrite the file each time
        fh.setLevel(logging.DEBUG)

        # Create formatter and add it to the handlers
        formatter = logging.Formatter('%(filename)s:%(lineno)s %(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)

        # Add the handlers to the logger
        self.logger.addHandler(fh)

    def create_FIB_entry(self, data_name, hop, device_interface: DeviceInterface, interested_key_name: str):
        entry = {}
        entry['hop']=hop
        # entry['device_interface']=device_interface
        entry['interested_key_name']=interested_key_name
        entry['created_at']=datetime.now().timestamp()
        self.FIB[data_name]=entry
        self.logger.debug("CREATED FIB ENTRY:", entry)

    '''
    TODO: Shift this send/forward logic to storing and routing
    '''

    async def handle_satisfy_packet(self, packet, jwt, hop=None):
        assert type(hop) == int
        data_name = packet.get(PACKET_FIELD_DATA_NAME)
        #_list = self.PIT[data_name]['waiting_list']
        pit_entry = self.PIT.get(data_name)
        # di = DeviceInterface.from_dict(packet[PACKET_FIELD_DEVICE_INTERFACE])
        interested_key_name = packet.get(PACKET_FIELD_REQUESTOR_KEY_NAME)
        _list = None
        if pit_entry:
            _list = pit_entry.get('waiting_list')
        if _list is None:
            _list=[interested_key_name]

        #self.logger.debug(f"now the {self.task_id} node has a waiting list {_list} for {data_name}")

        data = packet.get(PACKET_FIELD_DATA_PLAIN)
        await self.send_to_network(data_name,data,hop,_list)
        self.PIT.pop(data_name,None)

        entry_fib = self.FIB.get(data_name)

        if entry_fib is None:
            self.create_FIB_entry(data_name,hop,None,interested_key_name)
        elif entry_fib['hop']>hop:
            # entry_fib['device_interface']=di
            entry_fib['interested_key_name']=packet.get(PACKET_FIELD_REQUESTOR_PUBLIC_KEY)

        # TODO verify packet came from a trusted sender
        # TODO delete entry that time is invalid
        self.CACHE[data_name] = packet.get(PACKET_FIELD_DATA_PLAIN)

       # self.logger.debug(f"{self.task_id} get a message {data_name}, cache number is {len(self.CACHE)}")

    async def propagate_interest(self,packet,hop=None):
        assert type(hop) == int
        current_neighbours = self.discover_neighbours()
        packet[PACKET_FIELD_DEVICE_INTERFACE]=self.device_interface_dict()
        # TODO: propagate more conservatively
        def di2task(di: DeviceInterface):
            return asyncio.create_task(self.send_payload_to(di,payload=self.jwt.encode(packet),hop=hop+1))
        
        fib_entry = self.FIB.get(packet[PACKET_FIELD_DATA_NAME])
        next_device = None
        if fib_entry:
            next_device = find_device_by_key_name(fib_entry['interested_key_name'], current_neighbours)
        tasks = []
        if next_device:
            self.logger.debug("JUST SENDING TO ONE INTERESTED DEVICE", next_device)
            tasks=[di2task(next_device)]
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
        interested_key_name = packet[PACKET_FIELD_REQUESTOR_KEY_NAME]
        # di_dict = packet[PACKET_FIELD_DEVICE_INTERFACE]
        # di = DeviceInterface.from_dict(di_dict)
        if data:
            
            #self.logger.debug(f"get data {self.task_id}")
            return await self.send_to_network(data_name, data,hop, [interested_key_name] )
        
        if self.PIT.get(data_name) is None:
            #self.PIT[data_name] = set()
            self.PIT[data_name]={} # PIT should be a dictionary of dictionary, instead of a set.
            sub_dict={}
            # TODO: make 'waiting_list' a set not a list
            sub_dict['waiting_list']=[]
            sub_dict['waiting_list'].append(interested_key_name)
            sub_dict['time_stamp']= datetime.now().timestamp()  # mark the time intersted entry created
            self.PIT[data_name]=sub_dict
            await self.propagate_interest(packet,hop=hop+1)       
        else:
            self.PIT[data_name]['waiting_list'].append(interested_key_name)
            
            
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
        self.neighbours = self.emulation.discover_neighbours(self.jwt.key_name)
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

    '''
    Send out directly to a device
    '''
    async def send_payload_to(self,di: DeviceInterface, payload=None,hop=0):
        try:
            self.logger.debug(f"from {self.device_interface_dict()} to device interface", di)
            assert type(di) == DeviceInterface
        except AssertionError as e:
            self.logger.debug("device interface is wrong type:", di)
            self.logger.debug(str(Exception()),str(e))
        assert payload is not None
        url = di.url()
        async with http_client.no_proxy() as client:
            headers = {HOP_HEADER: str(hop)}
            await client.post(url, content=payload, headers=headers)

    
    # send named data to the network
    async def send_to_network(self, data_name, data, hop, neighbour_key_names: List(str)):
        self.logger.debug(f"sending data to network {data_name}, {data}, {hop}")
        payload = self.jwt.encode({
            PACKET_FIELD_REQUEST_TYPE: "satisfy",
            PACKET_FIELD_DATA_NAME: data_name,
            PACKET_FIELD_DATA_PLAIN: data,
            # TODO: don't decode every time
            PACKET_FIELD_SENDER_KEY_NAME: self.jwt.key_name,
            PACKET_FIELD_CREATED_AT: datetime.now().timestamp(),
            PACKET_FIELD_DEVICE_INTERFACE: DeviceInterface.from_device(self).to_dict()
        })

        neighbour_interfaces = self.discover_neighbours()

        forward_to = []
        for n in neighbour_interfaces:
            for name in neighbour_key_names:
                if n.key_name == name:
                    forward_to.append(n)

        def di2task(di: DeviceInterface) -> asyncio.Task:
            coroutine = self.send_payload_to(di, hop=hop,payload=payload, )
            return asyncio.create_task(coroutine)
        tasks = [di2task(di) for di in forward_to] # directly pass the data to the requestor, the reason that do not need to use neighbour is we just want to pass the data to the node who needs it.
        gathered_tasks = asyncio.gather(*tasks)
        await gathered_tasks

    def device_interface_dict(self):
        return DeviceInterface.from_device(self).to_dict()
    
    def start_queue_handler(self):
        async def handle():
            while True:
                data_name = await self.desire_queue.get()
                self.logger.debug("processing new desire:", data_name)
                if self.CACHE.get(data_name):
                    continue

                self.logger.debug(f"got item '{data_name}' from desire queue: node {self.task_id}: port: {self.server.port}")

                # TODO what if device has no neighbours currently?
                # should store desire until there are neighbour
                current_neighbours = []
                while len(current_neighbours) == 0:
                    current_neighbours = self.discover_neighbours()
                    await asyncio.sleep(1)
                    self.logger.debug("sending to neighbours:", current_neighbours)
                    data = {
                        PACKET_FIELD_REQUEST_TYPE: "interest",
                        PACKET_FIELD_DATA_NAME: data_name,
                        PACKET_FIELD_REQUESTOR_PUBLIC_KEY: self.jwt.public_key.decode('utf-8'), # DEPRECATED
                        PACKET_FIELD_REQUESTOR_KEY_NAME: self.jwt.key_name,
                        PACKET_FIELD_CREATED_AT: datetime.now().timestamp(),
                        PACKET_FIELD_DEVICE_INTERFACE: self.device_interface_dict()
                    }
                    self.logger.debug(data)
                    payload = self.jwt.encode(data)
                    tasks = [asyncio.create_task(self.send_payload_to(di, payload)) for di in current_neighbours]
                    await asyncio.gather(*tasks)

        self.desire_queue_task = asyncio.create_task(handle())
        return self.desire_queue_task

    async def start(self):
        self.logger.debug(f"starting node {self.task_id}")
        self.start_queue_handler()
        await self.server.start()
        await self.init_logger()


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
            

async def main():
        # instantiate emulation
        em = Emulation()
        # instantiate device and pass emulation
        device = Device(0, em)
        
        await device.start()

        # create queue for device to send out interest packets
        interest_queue = interest_emulation.desire_queue_deterministic(["a","b","c"],interval=1)
        
        device.set_desire_queue(interest_queue)
        
        await device.send_payload_to(device.device_interface_dict(), payload=device.jwt.encode({"hi": "ok"}), hop=0)


if __name__ == "__main__":
    asyncio.run(main())