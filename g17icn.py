# script to emulate one network with several nodes

import requests
import argparse
import asyncio
import random
import logging
import g17jwt
import httpx
import numpy as np

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
        self.HOSTNAME = "http://localhost:"


    def discover_neighbours(self):
        current_neighbours_ports = self.emulation.discover_neighbours(self.task_id)
        self.logger.debug(f"got neighbours {str(current_neighbours_ports)}")
        return current_neighbours_ports

    '''
    Handle an interest request (whih is a JWT).
    When we get a request from another node, we will first check the self.PIT to find if we have already received this interest request.
    If we have, do not pass this request, and sender to list of nodes waiting for that data.
    When an interest request is received, it should check the time validity, if not valid, discard it.
    If valid respond to the sender with a 200 OK response code.
    It will check its` cache, if there is an entry suitable to satisfy the interest request, respond with the data as a JWT.
    If not, it will use the self.FIB to pass this request to the next hop and save this request to its pit.
    TO BE CONTINUE lol
    '''
    async def handler(self, request):
        t = await request.text()
        print(t)
        packet = self.jwt.decode(t)
        # print(packet)
        return web.Response(text="ok")

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
                "public_key": self.jwt.public_key.decode('utf-8')
                })
            response = await client.post(self.HOSTNAME + str(port), content=payload)
            print("RESPONSE", response.text)
            # TODO handle 200 ok response and error responses
    # send named data to the network
    async def set(self):
        pass

    async def start(self):
        self.jwt = g17jwt.JWT()
        # print(self.jwt)
        self.jwt.init_jwt(key_size=32)        
        self.PIT = {} 
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
        # print(self.jwt)
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
