import numpy as np
from device import Device

# contributors: [agrawal-8.11.23, nrobinso-9.11.23]
def line_adjacency_matrix(n):
    adj_matrix = [[0] * n for _ in range(n)]
    for i in range(n-1):
        adj_matrix[i+1][i] = 1 
        adj_matrix[i][i+1] = 1
    return adj_matrix

class ICNEmulator:
    def __init__(self,num_nodes=3):
        import asyncio
        self.num_nodes = num_nodes
        self.adjacency_matrix = line_adjacency_matrix(self.num_nodes)
        self.node_ids = np.array(list(range(self.num_nodes)))
        self.devices = [Device(idx,self) for idx in self.node_ids]
        self.tasks = [asyncio.create_task(node.start()) for node in self.devices]
        self.start_event = asyncio.Event()

    def devices_report(self):
        return {
            "total_nodes": len(self.devices),
            "num_nodes": self.num_nodes,
            "living_nodes": "NYI", # TODO implement count of living nodes (healthy servers)
            "task_ids": list(range(self.num_nodes)) # TODO make this more robust
        }

    # contributors: [agrawal-8.11.23, nrobinso-9.11.23]
    def discover_neighbours(self, node_number):
        print("DISCOVER NEIGHBOURS:", node_number)
        neighbors = []
        if node_number < 0 or node_number >= len(self.adjacency_matrix):
            return neighbors
        for task_id, connected in enumerate(self.adjacency_matrix[node_number]):
            if connected:
                neighbors.append(task_id)
        print("FOUND NEIGHBOURS:", str(neighbors))
        
        neighbor_device_info = []
        for i in neighbors:
            device = self.devices[i]
            server = device.server
            print("SERVER PORT:", server.port)
            if server.port is not None:
                neighbor_device_info.append((device.jwt.key_name, server.host, server.port))
        print("FOUND NEIGHBOUR DEVICE INFO:", neighbor_device_info)
        return neighbor_device_info
        
    async def start(self):
        print("STARTING Emulator")
        import asyncio
        try:


            for device in self.devices:
                await device.server.started.wait()
            await asyncio.gather(*self.tasks)
        except AssertionError as e:
            print(f"assertion failed: {e}")

    def generate_trusted_keys_table_all_nodes(self):
        d = {}
        for device in self.devices:
            hash = device.jwt.hash_of_public_key()
            pub_key = device.jwt.public_key_pem
            d[hash] = pub_key
        return d