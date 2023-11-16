from __future__ import annotations
from quart import Quart
import quart
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
import schema
import jsonschema
import JWT
import argparse

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
        self.current_topology = {
            "devices": [],
            "connections": [],
        }

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
                print("REGISTER RES:", res)
            except Exception as e:
                print(str(e))
                print("failed to register")

    def devices_report(self):
        return {
            "total_nodes": len(self.devices),
            "num_nodes": self.num_nodes,
            "living_nodes": "NYI", # TODO implement count of living nodes (healthy servers)
            "task_ids": list(range(self.num_nodes)) # TODO make this more robust
        }

    # contributors: [agrawasa-8.11.23, nrobinso-9.11.23]
    def discover_neighbours(self, device_key_name) -> List(DeviceInterface):
        neighbour_key_names = []
        for connection in self.current_topology['connections']:
            if connection['source'] == connection['target']:
                raise Exception("source and target of connection cannot be the same")
            if connection['source'] == device_key_name:
                neighbour_key_names.append(connection['target'])
            elif connection['target'] == device_key_name:
                neighbour_key_names.append(connection['source'])
        raw = map( self.key_name_to_device_interface,    neighbour_key_names)
        dis = map( DeviceInterface.from_dict, raw)
        return list(dis)
    
    def key_name_to_device_interface(self,key_name):
        for device in self.current_topology['devices']:
            if device['key_name'] == key_name:
                return device
    
    def set_topology(self, topology):
        jsonschema.validate(topology, schema=schema.device_topology)
        self.current_topology=topology
    
    def start(self) -> List(asyncio.Task):
        import asyncio
        self.tasks = [asyncio.create_task(node.start()) for node in self.devices]
        register_task = asyncio.create_task(self.register_with_master())
        return [*self.tasks, register_task]

    async def generate_trusted_keys_table_all_nodes(self):
        d = {}
        for device in self.devices:
            hash = device.jwt.hash_of_public_key()
            pub_key = device.jwt.public_key_pem
            d[hash] = pub_key
        return d
    
    async def get_updated_topology(self, master_host='127.0.0.1', master_port=33000):
        print("Receiving Updated Device Topology from Master")
        host = get_ip_address.get_ip_address()
    
        body = {
            "emulator_interface": {
                "host": host,
                "port": self.port # TODO
            }
        }
        async with httpx.AsyncClient() as client:
            headers = {"content-type": "application/json"}
            print(body)
            res = await client.post(f"http://{master_host}:{master_port}/new_device_topology", json=body, headers=headers)
            print("DEVICE TOPOLOGY UPDATED? ", res)        


def parse_arguments():
    parser = argparse.ArgumentParser(description="Argument parser for emulator configuration")
    
    parser.add_argument(
        '--port', 
        type=int, 
        default=None, 
        help='Port number for the slave emulator (default: 34000)'
    )
    
    parser.add_argument(
        '--master-port', 
        type=int, 
        default=33000, 
        help='Port number for the master emulator (default: 33000)'
    )
    
    parser.add_argument(
        '--master-host', 
        type=str, 
        default='localhost', 
        help='Host address for the master emulator (default: None)'
    )

    parser.add_argument(
        '--num-nodes', 
        type=int, 
        default=5, 
        help='Host address for the master emulator (default: None)'
    )

    parser.add_argument(
        '--random-desires', 
        type=str, 
        default=None, 
        help='Host address for the master emulator (default: None)'
    )

    args = parser.parse_args()
    return args

async def main():
    import get_ip_address
    args = parse_arguments()
    if args.master_host is None:
        args.master_host = get_ip_address.get_ip_address()
    port = args.port
    print("PORT IS:", port)
    if port is None:
        port = gateway_port.find_free_gateway_port_reverse()
    emulator = SlaveEmulator(port=port,master_host=args.master_host,master_port=args.master_port,num_nodes=args.num_nodes)
    emulator_tasks = emulator.start()

    # instantiate app
    app = Quart(__name__)


    @app.route('/update_topology' ,methods=['POST'])
    async def update_topology():
        body = await quart.request.get_json()
        try:
            emulator.set_topology(body)
        except jsonschema.ValidationError as e:
            return quart.jsonify({"message": "bad topology", "error": str(e)}), 400
        return quart.jsonify({"message": "topology updated"}), 200
    
    @app.route('/set_desire_for_all' ,methods=['GET'])
    async def set_desire_for_all():
        # give each device a new desire
        data_name = quart.request.args.get('data_name', default=None, type=str)
        if data_name is None:
            return 'please provide data_name', 400
        for device in emulator.devices:
            await device.desire_queue.put(data_name)
        return f'set desire {data_name} for {len(emulator.devices)} devices', 200
    
    @app.route('/give_data_to_random_device', methods=['GET'])
    async def give_data_to_random_device():
        return "nyi", 500

    @app.route('/debug/topology' ,methods=['GET'])
    async def debug_topology():
        return quart.jsonify(emulator.current_topology), 200
    
    @app.route('/debug/neighbours' ,methods=['GET'])
    async def debug_neighbours():
        neighbours = []
        for device in emulator.devices:
            print(device)
            neighbours.append(emulator.discover_neighbours(device.jwt.key_name))
        print(neighbours)
        return quart.jsonify(neighbours), 200
    
    @app.route('/debug/interest' ,methods=['GET'])
    async def debug_interest():
        PITTable = []
        for device in emulator.devices:
            print(device)
            PITTable.append(list(map(lambda x: [x[0],str(x[1])], device.PIT.items())))
        print(PITTable)
        return quart.jsonify(PITTable), 200
    
    def signal_handler():
        print("interruption signal received")
        for t in emulator_tasks:
            t.cancel()
    
    import signal
    asyncio.get_event_loop().add_signal_handler(signal.SIGINT,signal_handler)
    try:
        import get_ip_address
        await asyncio.gather(*([app.run_task(host=get_ip_address.get_ip_address(), port=port,debug=True)] + emulator_tasks))
    except asyncio.exceptions.CancelledError:
        pass
    except OSError as e:
        print(str(e))
        raise e


if __name__ == "__main__":
    asyncio.run(main())
