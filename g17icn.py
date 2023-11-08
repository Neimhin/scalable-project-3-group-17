# script to emulate one network with several nodes

import argparse
import asyncio
import random
import logging
import g17jwt
import numpy as np

# TODO: refactor to another file
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("default.log")
file_handler.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.debug("hello world")

import aiohttp
class HTTPServer:
    def __init__(self):
        pass

    async def handler(self, request):
        return aiohttp.web.Response(text="ok")

    async def start(self):
        app = aiohttp.web.Application()
        app.router.add_get("/", lambda r: self.handler(r))
        web_runner = aiohttp.web.AppRunner(app)
        # TODO handle errors
        await web_runner.setup()
        site = aiohttp.web.TCPSite(web_runner,'localhost', 0)
        await site.start()
        self.port = site._server.sockets[0].getsocketname()[1]
        self.logger.debug("started server on port", self.port)

# interested party and producer
# interested party sends interest to network
# producer sends data to satisfy interest if interest is received

class G17ICNNODE:

    def __init__(self, task_id, scenario):
        self.task_id = task_id
        self.logger = logging.getLogger()
        self.jwt = g17jwt.JWT()
        self.jwt.init_jwt(key_size=32)

        self.PIT = {}
        self.FIB = {}
        self.emulation = emulation

        self.port = 0 # placeholder

        self.server = HttpServer()

    async def discover_neighbours(self):
        current_neighbours = await self.emulation.discover_neighbours(self.task_id)

    # start a http server to listen for connections and handle publish/subscribe messages
    async def start(self): 
        pass


    '''
    Handle a request for a interested. 
    When it get a request from other nodes, it will at first check the self.PIT to find if there is a same request, if exist, do not pass this request, and save this request to waiting list.
    When a request interested come back to this node, it should check the time validity, if not valid, discard it. if valid, return this interested message to the requestor and nodes in the waiting list.
    It will check its` cache, if there is an entry suitable to this interested, return it. If not, it will use the self.FIB to pass this request to the next hop and save this request to its pit.
    '''
    def HandleInterested():
        pass

    # send interest to data to the network to satisfy interest
    async def get(self):
        pass

    # send named data to the network
    async def set(self):
        pass

    async def start(self):
        self.logger.debug(f"starting node {self.task_id}")
        while True:
            await asyncio.sleep(random.randint(1,3))
            self.logger.debug(f"task {self.task_id} awakes")


class ICNEmulator:
    async def discover_neighbours(task_id):
            pass
    
    def initialize_adjacency_matrix():
        pass
    
    def __init__(self,num_nodes=3):
        self.num_nodes = 3
        self.adjacency_matrix = np.array(
            [[0,1,0],
             [1,0,1],
             [0,1,0]])

        self.node_ids = np.array(list(range(3)))

        self.nodes = [G17ICNNODE(idx,self) for idx in self.node_ids]
        self.tasks = [asyncio.create_task(node.start()) for node in self.nodes]
    
    async def start(self):
        await asyncio.gather(self.tasks)


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
