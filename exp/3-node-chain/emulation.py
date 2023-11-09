# script to emulate one network with several nodes
import sys
sys.path.append(".")

import requests
import argparse
import asyncio
import random
import logging
import g17jwt
import interest_emulation

from emulator import ICNEmulator

# TODO: refactor to another file
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.debug("hello world")

'''
Interested party and producer
Interested party sends interest to network
Producer sends data to satisfy interest if interest is received
'''

async def main():
    parser = argparse.ArgumentParser(description="Simulate an Information Centric Network")
    parser.add_argument("--num-nodes",          help="How many nodes to emulate in this network.",                  default=5)
    parser.add_argument("--dynamic-topology",   help="Whether the topology of the network should change of time.",  action="store_true")
    parser.add_argument("--nodes-can-die",      help="Whether or not nodes can die at random",                      action="store_true")
    args = parser.parse_args()
    
    emulator = ICNEmulator(num_nodes=10)
    emulator_task = asyncio.create_task(emulator.start())

    def data_name(i):
        return "/foo/bar/" + str(i)

    for i,device in enumerate(emulator.devices):
        await device.server.started.wait()
        device.CACHE[data_name(i)] = device.server.port

    desires = [data_name(i) for i in range(emulator.num_nodes)]
    desire_queues = [interest_emulation.desire_queue_deterministic(desires,interval=(i+1)*0.1) for i in range(emulator.num_nodes)]
    for desire_queue,device in zip(desire_queues, emulator.devices):
        device.set_desire_queue(desire_queue)

    while True:
        await asyncio.sleep(0.2)
        for i,device in enumerate(emulator.devices):
            print("cache ", i, device.CACHE)

    emulator_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())