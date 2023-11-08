import numpy as np
from node import G17ICNNODE

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
        import asyncio
        self.num_nodes = num_nodes
        self.adjacency_matrix = self.initialize_adjacency_matrix(self.num_nodes)
        self.node_ids = np.array(list(range(self.num_nodes)))
        self.nodes = [G17ICNNODE(idx,self) for idx in self.node_ids]
        self.tasks = [asyncio.create_task(node.start()) for node in self.nodes]

    def emulation_loop(self):
        import asyncio
        async def loop():
            while True:
                await asyncio.sleep(1)
                self.logger.debug("running emulation loop")
        return asyncio.create_task(loop())
    
    async def start(self):
        import asyncio
        await asyncio.gather(*self.tasks)