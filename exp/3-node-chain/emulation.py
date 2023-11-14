# script to emulate one network with several nodes
import sys
from pathlib import Path
root_directory = Path(__file__).resolve().parents[2]
sys.path.append(str(root_directory))
# 获取当前文件的路径，然后找到根目录的路径

import requests
import argparse
import asyncio
import random
import logging
import JWT
import interest_emulation
import vis
import time
from emulator import ICNEmulator

# TODO: refactor to another file
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.CRITICAL)
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
    parser.add_argument("--nodes-can-die",      help="Whether or not nodes can die at random.",                      action="store_true")
    parser.add_argument("--vis",                help="Whether to run a visualization web app.",                      action="store_true")
    args = parser.parse_args()

    start_time = time.perf_counter()

    emulator = ICNEmulator(num_nodes=int(args.num_nodes))
    emulator_task = asyncio.create_task(emulator.start())

    def data_name(i):
        return "/foo/bar/" + str(i)
    
    for i,device in enumerate(emulator.devices):
        await device.server.started.wait()
        # TODO: use CIS
        device.CACHE[data_name(i)] = random.randint(0,100)

    # each device gets the same desires
    desires = [data_name(i) for i in range(emulator.num_nodes)]
    print(f"desires is {desires}")
    desire_queues = [interest_emulation.desire_queue_deterministic(desires,interval=(i+1)*0.1) for i in range(emulator.num_nodes)]
    for desire_queue,device in zip(desire_queues, emulator.devices):
        device.set_desire_queue(desire_queue)

    vis_task = asyncio.create_task(vis.run_vis(emulator)) if args.vis else None
    print("enter loop")
    FINISHED = False
    while not FINISHED:
        await asyncio.sleep(0.1)

        FINISHED = True
        #print("\n")
        for i,device in enumerate(emulator.devices):
            print(f"device {i} has {len(device.CACHE.items())} ")
            if len(device.CACHE.items()) < len(emulator.devices):
                FINISHED = False
    end_time = time.perf_counter()
    print(" total time is ",end_time-start_time)



if __name__ == "__main__":
    asyncio.run(main())
