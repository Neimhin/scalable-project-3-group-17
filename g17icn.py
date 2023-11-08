# script to emulate one network with several nodes

import requests
import argparse
import asyncio
import random
import logging
import g17jwt
import httpx
import numpy as np

import http_server
from node import G17ICNNODE
from emulator import ICNEmulator

# TODO: refactor to another file
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
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
    
    emulator = ICNEmulator()
    await emulator.start()


if __name__ == "__main__":
    asyncio.run(main())
