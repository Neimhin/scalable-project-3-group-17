import sys
sys.path.append(".")
import JWT
import emulator
import unittest
import tempfile

import tempfile
import unittest
import numpy as np

# contributors: [nrobinso-7.11.23]
class TestJWTManager(unittest.TestCase):
    def test_jwt_operations(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            jwts = JWT.JWT()
            jwts.init_jwt()
            payload = {"user_id": 123, "username": "john_doe"}
            encoded_token = jwts.encode(payload)
            decoded_payload = jwts.decode(encoded_token)
            self.assertEqual(decoded_payload, payload)

# contributors: [nrobinso-9.11.23]
class TestLineAdjacency(unittest.TestCase):
    def test_line_adjacency(self):
        adj = np.array([[0,1,0],[1,0,1],[0,1,0]])
        a = emulator.line_adjacency_matrix(3)
        print(a)
        self.assertTrue(np.array_equal(adj,a))

# contributors: [nrobinso-9.11.23]
import graphviz
def adjacency_matrix_to_graph(adjacency_matrix, node_names=None, directed=True):
    graph = graphviz.Digraph() if directed else graphviz.Graph()
    if node_names is None:
        node_names = [str(i) for i in range(len(adjacency_matrix))]
    # add nodes and names
    for i, name in enumerate(node_names):
        graph.node(str(i), name)
    # add edges
    for i in range(len(adjacency_matrix)):
        for j in range(len(adjacency_matrix[i])):
            if adjacency_matrix[i][j] != 0:
                graph.edge(str(i), str(j), label=str(adjacency_matrix[i][j]))

    return graph

# create a vis of the line_adjacency_matrix with 8 nodes
adj_matrix = emulator.line_adjacency_matrix(8)
graph = adjacency_matrix_to_graph(adj_matrix, directed=True)
graph.render(filename='test/line_adjacency_graph', format='pdf', cleanup=True)


if __name__ == "__main__":
    unittest.main()