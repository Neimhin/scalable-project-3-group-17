import numpy as np
from device import Device
import logging
import asyncio
import get_ip_address
import httpx
import slave_http
import logging
import device
from DeviceInterface import DeviceInterface
from typing import List

# contributors: [agrawasa-8.11.23, nrobinso-9.11.23]
def line_adjacency_matrix(n):
    adj_matrix = [[0] * n for _ in range(n)]
    for i in range(n-1):
        adj_matrix[i+1][i] = 1 
        adj_matrix[i][i+1] = 1
    return adj_matrix

class SlaveEmulator:
    def __init__(self,num_nodes=3,jwt_algorithm=None):
        import asyncio
        self.num_nodes = num_nodes
        self.adjacency_matrix = line_adjacency_matrix(self.num_nodes)
        self.node_ids = np.array(list(range(self.num_nodes)))
        self.devices = [Device(idx,self,jwt_algorithm=jwt_algorithm) for idx in self.node_ids]
        self.tasks = [asyncio.create_task(node.start()) for node in self.devices]
        self.start_event = asyncio.Event()
        self.logger = logging.getLogger()

        # TODO: start slave http server

    async def register_with_master(self, master_host='127.0.0.1', master_port=33000):
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
        print("REGISTERING NOW")
        async with httpx.AsyncClient() as client:
            headers = {"content-type": "application/json"}
            print(body)
            res = await client.post(f"http://{master_host}:{master_port}/register", json=body, headers=headers)
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
    
    async def start(self):
        import asyncio
        self.logger.debug("starting emulator")
        together = asyncio.gather(*self.tasks, return_exceptions=True)
        self.logger.debug("registering")
        self.server_task, self.port = slave_http.slave_server(self)
        await self.register_with_master()
        # MERGE await asyncio.gather(*self.tasks)

    def generate_trusted_keys_table_all_nodes(self):
        d = {}
        for device in self.devices:
            hash = device.jwt.hash_of_public_key()
            pub_key = device.jwt.public_key_pem
            d[hash] = pub_key
        return d
    

async def main():
    se = SlaveEmulator()
    t1 = se.start()
    await asyncio.create_task(t1)


if __name__ == "__main__":
    asyncio.run(main())
