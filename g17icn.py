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
logger.debug("hello world")

from aiohttp import web
class HTTPServer:
    def __init__(self):
        self.logger = logging.getLogger()
        self.desires = ["/meaning-of-life"]
        pass

    async def handler(self, request):
        return web.Response(text="ok")

    async def start(self):
        app = web.Application()
        app.router.add_get("/", lambda r: self.handler(r))
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
        self.jwt = g17jwt.JWT().init_jwt(key_size=32)
        self.PIT = {} # 
        self.FIB = {}
        self.emulation = emulation
        self.server = HTTPServer()

    async def discover_neighbours(self):
        current_neighbours = await self.emulation.discover_neighbours(self.task_id)

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
        await self.server.start()
        while True:
            await asyncio.sleep(3)
            self.logger.debug(f"still running on port {self.server.port}: task_id: {self.task_id}")


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
