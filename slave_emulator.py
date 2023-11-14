from __future__ import annotations
from quart import Quart
from typing import List
from device import Device
from DeviceInterface import DeviceInterface
import gateway_port
import asyncio
import get_ip_address
import numpy as np
import logging
import asyncio
import get_ip_address
import httpx
import logging
import JWT

# contributors: [agrawasa-8.11.23, nrobinso-9.11.23]
def line_adjacency_matrix(n):
    adj_matrix = [[0] * n for _ in range(n)]
    for i in range(n-1):
        adj_matrix[i+1][i] = 1 
        adj_matrix[i][i+1] = 1
    return adj_matrix

class SlaveEmulator:
    def __init__(self,num_nodes=3,jwt_algorithm=JWT.ALGORITHM,port=34000, master_port=33000, master_host=None):
        self.port = port
        self.num_nodes = num_nodes
        self.adjacency_matrix = line_adjacency_matrix(self.num_nodes)
        self.node_ids = np.array(list(range(self.num_nodes)))
        self.devices = [Device(idx,self,jwt_algorithm=jwt_algorithm) for idx in self.node_ids]
        self.start_event = asyncio.Event()
        self.logger = logging.getLogger()
        self.master_host = master_host or get_ip_address.get_ip_address()
        self.master_port = master_port or 33000

        # TODO: start slave http server

    async def register_with_master(self):
        print("in register_with_master")
        host = get_ip_address.get_ip_address()
        devices = []
        for device in self.devices:
            await device.server.started.wait()
            devices.append({
                "key_name": device.jwt.key_name,
                "host": host,
                "port": device.server.port,
                "public_key": device.jwt.public_key.decode("utf-8")
            })

        body = {
            "emulator_interface": {
                "host": host,
                "port": self.port, # TODO
            },
            "devices": devices
        }
        async with httpx.AsyncClient() as client:
            headers = {"content-type": "application/json"}
            print(body)
            try:
                res = await client.post(f"http://{self.master_host}:{self.master_port}/register", json=body, headers=headers)
            except Exception as e:
                print(str(e))
                print("failed to register")
            print("REGISTER RES:", res)

    def devices_report(self):
        return {
            "total_nodes": len(self.devices),
            "num_nodes": self.num_nodes,
            "living_nodes": "NYI", # TODO implement count of living nodes (healthy servers)
            "task_ids": list(range(self.num_nodes)) # TODO make this more robust
        }

    # contributors: [agrawasa-8.11.23, nrobinso-9.11.23]
    def discover_neighbours(self, node_number):
        neighbors = []
        if node_number < 0 or node_number >= len(self.adjacency_matrix):
            return neighbors
        for task_id, connected in enumerate(self.adjacency_matrix[node_number]):
            if connected:
                neighbors.append(task_id)
        return [DeviceInterface.from_device(self.devices[i]) for i in neighbors]
    
    def start(self) -> List(asyncio.Task):
        import asyncio
        self.tasks = [asyncio.create_task(node.start()) for node in self.devices]
        register_task = asyncio.create_task(self.register_with_master())
        return [*self.tasks, register_task]

    def generate_trusted_keys_table_all_nodes(self):
        d = {}
        for device in self.devices:
            hash = device.jwt.hash_of_public_key()
            pub_key = device.jwt.public_key_pem
            d[hash] = pub_key
        return d
    

async def main():
    port = 34000
    emulator = SlaveEmulator(port=port)
    emulator_tasks = emulator.start()

    app = Quart(__name__)
    @app.route('/update_topology' ,methods=['POST'])
    async def update_topology():
        # ------------ NA TASK ------------- #

        # get body of post request, parse as json

        # update emulator adjacency/topology
        pass

    def signal_handler():
        print("interruption signal received")
        for t in emulator_tasks:
            t.cancel()
    
    import signal
    asyncio.get_event_loop().add_signal_handler(signal.SIGINT,signal_handler)
    try:
        import get_ip_address
        await asyncio.gather(*([app.run_task(host=get_ip_address.get_ip_address(), port=34000,debug=True)] + emulator_tasks))
    except asyncio.exceptions.CancelledError:
        pass
    except OSError as e:
        print(str(e))
        raise e


if __name__ == "__main__":
    asyncio.run(main())