# script to emulate one network with several nodes
import sys
from pathlib import Path
root_directory = Path(__file__).resolve().parents[2]
sys.path.append(str(root_directory))
# 获取当前文件的路径，然后找到根目录的路径

import argparse
import asyncio
import random
import logging
import interest_emulation
import time
from slave_emulator import SlaveEmulator
import JWT

# TODO: refactor to another file
logging.basicConfig(level=logging.DEBUG, format='%(filename)s:%(lineno)d %(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
    parser.add_argument("--num-nodes",          help="How many nodes to emulate in this network.",                   default=5)
    parser.add_argument("--jwt-algorithm",      help="Which cryptographic algorithm to use.", type=str, default='none')
    args = parser.parse_args()

    start_time = time.perf_counter()
    
    print("JWT ALG", args.jwt_algorithm)
    emulator = SlaveEmulator(num_nodes=int(args.num_nodes),jwt_algorithm=args.jwt_algorithm)
    emulator_tasks = emulator.start()

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

    print("time taken:", end_time - start_time)

if __name__ == "__main__":
    asyncio.run(main())
