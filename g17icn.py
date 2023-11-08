# script to emulate one network with several nodes

import requests
import argparse
import asyncio
import random
import logging
import g17jwt
import httpx
import numpy as np
from datetime import datetime

# TODO: refactor to another file
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.debug("hello world")

from aiohttp import web
class HTTPServer:
    def __init__(self,handler):
        self.logger = logging.getLogger()
        self.port = None
        self.handler = handler

    async def start(self):
        app = web.Application()
        app.router.add_post("/", lambda r: self.handler(r))
        web_runner = web.AppRunner(app)
        # TODO handle errors
        await web_runner.setup()
        site = web.TCPSite(web_runner,'localhost', 0)
        await site.start()
        print(site._server.sockets)
        addr = site._server.sockets[0].getsockname()
        self.host = addr[0]
        self.port = int(addr[1])
        print(type(self.port))
        self.logger.debug(f"started server on port {self.port}")

    def set_desires(self, desires):
        self.desires = desires

# interested party and producer
# interested party sends interest to network
# producer sends data to satisfy interest if interest is received

class G17ICNNODE:
    def __init__(self, task_id, emulation):
        self.task_id = task_id
        self.logger = logging.getLogger()
        self.emulation = emulation
        self.location="124.0.0" # represented the node location
        self.server = HTTPServer()
        self.neighbour=[]
        self.PIT={}
        self.FIB={}

    def discover_neighbours(self):
        self.neighbour = self.emulation.discover_neighbours(self.task_id)
        self.logger.debug(f"got neighbours {str(self.neighbour)}")
        return self.neighbour

    
    
    async def handler(self, request,flag):
        '''
        Author:[zhfu-8th-11-2023]

        When nodeA gets a request from another nodeB, nodeA will first check the location. If the location point to nodeA then nodeA will check cache to see whether it has the data. 
        If nodeA does not satisfy the requirement of location, it will save this request to its interested table and send this request to next hop follow the entry of Forwarding Infromation Base(FIB)
        If there is another same request coming to nodeA, nodeA will discard this request and put this request sender in waiting list.
        Parameters:
        request`s format: disctionary which include:
            "data_name": request_type/(location),
            "public_key": public key value,
            "time_stamp": timevalue,
            "sender_address": sender_address,
        flag represented this request come from where, 0 shows that this request comes from itself, 1 represented other nodes.
        '''
        t = await request.text()
        print(t)
        packet = self.jwt.decode(t)
        print(packet)
        web.Response(text="ok")
        
        request_interesting=packet['data_name']
        if packet['location']==self.location:
            request_type=request_interesting.split("/")[0]  # request_type value should be "tempture", "light_intensive" and anything else like this.
            packet["data"]=self.CACHE[request_type]
            return self.jwt.encode( packet)
        else:
            if self.PIT[request_interesting]==None:
                #self.PIT[request_interesting]={}
                sub_dict={}
                sub_dict['flag']=flag
                sub_dict['waiting_list']=[packet['public_key']]
                self.PIT[request_interesting]=sub_dict
            else:
                self.PIT[request_interesting]['waiting_list'].append(packet['public_key'])
            
            message=self.jwt.encode({
                        'data_name':request_interesting,
                        "public_key":self.jwt.public_key,
                        "time_stamp":time,
                        "hop_number":packet['hop_number']+1,
                        "data":packet["data"]
                    })

            if self.FIB[request_interesting]==None:
                min_hop=100000,
                min_port=-1
                time=datetime.now().timestamp()

                for neighbor in self.neighbour:
                    
                    print(f"send intereseting message to {neighbor}")
                    response = send_interest_to(neighbor,message)
                    res=self.jwt.decode(response)
                    if min_hop>res['hop_number']:
                        min_port=neighbor
                port_info={}
                port_info['time_stamp']=datetime.now().timestamp()
                port_info['min_hop']=min_port
                self.FIB[request_interesting]=port_info
                
            else:
                port = self.FIB[request_interesting]
                respond=send_interes_to(port,message)
            
            return response
                

    # send interest to data to the network to satisfy interest
    async def get(self,data_name):
        cached_data = self.CACHE.get(data_name)
        if cached_data:
            return
        for port in self.neigbour_ports:
            await self.send_interest_to(port, data_name)
        pass

    async def send_interest_to(self,port,data_name):
        if not port:
            return
        async with httpx.AsyncClient() as client:
            payload = self.jwt.encode({
                "type": "interest",
                "name": data_name,
                "public_key": str(self.jwt.public_key)
                })
            response = await client.post("http://localhost:" + str(port), content=payload)
            print("RESPONSE", response.text)
            # TODO handle 200 ok response and error responses
    # send named data to the network
    async def set(self):
        pass

    async def start(self):
        self.jwt = g17jwt.JWT()
        print(self.jwt)
        self.jwt.init_jwt(key_size=32)
        self.PIT = {} # 
        self.FIB = {}
        self.CACHE = {}
        async def handler_async(request):
            return await self.handler(request)
        self.server = HTTPServer(handler_async)
        self.desires = ["/port/0", "/port/1", "/port/2"]
        self.neigbour_ports = []
        self.logger.debug(f"starting node {self.task_id}")
        await self.server.start()
        data_name = f"/port/{self.task_id}"
        print(self.jwt)
        data = self.jwt.encode({data_name: self.server.port})
        self.CACHE[data_name] = data
        while True:
            self.neigbour_ports = self.discover_neighbours()
            await asyncio.gather(*[asyncio.create_task(self.get(desire)) for desire in self.desires])
                
            self.logger.debug(f"still running on port {self.server.port}: task_id: {self.task_id}")
            await asyncio.sleep(3)



class ICNEmulator:
    def initialize_adjacency_matrix(self, n):
        # Initialize an n x n matrix filled with zeros
        adj_matrix = [[0] * n for _ in range(n)]

        # Fill the adjacency matrix to represent linear connections
        for i in range(n):
            if i > 0:
                adj_matrix[i][i - 1] = 1  # Connect to the previous node
            if i < n - 1:
                adj_matrix[i][i + 1] = 1  # Connect to the next node

        return adj_matrix

    def discover_neighbours(self, node_number):
        if node_number < 0 or node_number >= len(self.adjacency_matrix):
            return []  # Invalid node number

        neighbors = []
        for task_id, connected in enumerate(self.adjacency_matrix[node_number]):
            if connected:
                neighbors.append(task_id)

        print(neighbors)
        return [self.nodes[i].server.port for i in neighbors]
    
    def __init__(self,num_nodes=3):
        self.num_nodes = num_nodes
        self.adjacency_matrix = self.initialize_adjacency_matrix(self.num_nodes)
        self.node_ids = np.array(list(range(self.num_nodes)))
        self.nodes = [G17ICNNODE(idx,self) for idx in self.node_ids]
        self.tasks = [asyncio.create_task(node.start()) for node in self.nodes]

    def emulation_loop(self):
        async def loop():
            while True:
                await asyncio.sleep(1)
                self.logger.debug("running emulation loop")
        return asyncio.create_task(loop())
    
    async def start(self):
        await asyncio.gather(*self.tasks)


async def main():
    parser = argparse.ArgumentParser(description="Simulate an Information Centric Network")
    parser.add_argument("--num-nodes",          help="How many nodes to emulate in this network.",                  default=5)
    parser.add_argument("--dynamic-topology",   help="Whether the topology of the network should change of time.",  action="store_true")
    parser.add_argument("--nodes-can-die",      help="Whether or not nodes can die at random",                      action="store_true")
    args = parser.parse_args()
    
    emulator = ICNEmulator()
    await emulator.start()

if __name__ == "__main__":
    asyncio.run(main())
