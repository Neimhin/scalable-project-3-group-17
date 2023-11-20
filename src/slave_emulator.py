from __future__ import annotations
from quart import Quart
import quart
from typing import List
from device import Device
from DeviceInterface import DeviceInterface
import gateway_port
import asyncio
import numpy as np
import logging
import get_ip_address
import schema
import jsonschema
import JWT
import argparse
import http_client
from typing import Optional
from router import BasicRouter

class SlaveEmulator:
    def __init__(self,num_nodes:int=3,jwt_algorithm:str=JWT.ALGORITHM,port:int=34000,host:str='localhost',master_port:int=33000, master_host:Optional[str]=None):
        self.port = port
        self.host = host or get_ip_address.get_ip_address()
        self.num_nodes = num_nodes
        self.node_ids = np.array(list(range(self.num_nodes)))
        self.devices = [Device(self,BasicRouter(),jwt_algorithm=jwt_algorithm) for idx in range(self.num_nodes)]
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
        host = self.host
        devices = []
        for device in self.devices:
            await device.server.started.wait()
            devices.append({
                "key_name": device.jwt.key_name,
                "host": host,
                "port": device.server.port,
                "public_key": device.jwt.public_key.decode("utf-8"),
                "emulator_id":self.port
            })

        body = {
            "emulator_interface": {
                "host": host,
                "port": self.port, # TODO
            },
            "devices": devices
        }
        # try:
        #     import encapsulate_http
        #     import json
        #     body = json.dumps(body)
        #     headers=["Content-Type: application/json"]
        #     res_raw = encapsulate_http.http_request("/register",self.master_host,self.master_port,method="POST",body=body,headers=headers)
        #     print("RES RAW:", res_raw)
        #     res_body = encapsulate_http.extract_body_from_response(res_raw)
        #     print("RES BODY ENCAPSULATE:", res_body)
        # except Exception as e:
        #     print(str(e))
        #     exit()
        async with http_client.no_proxy() as client:
            headers = {"content-type": "application/json"}
            print(body)
            try:
                res = await client.post(f"http://{self.master_host}:{self.master_port}/register", json=body, headers=headers)
                print("REGISTER RES:", res)
            except Exception as e:
                print(str(e))
                print("failed to register")
                raise e

    def devices_report(self):
        return {
            "total_nodes": len(self.devices),
            "num_nodes": self.num_nodes,
            "living_nodes": "NYI", # TODO implement count of living nodes (healthy servers)
            "task_ids": list(range(self.num_nodes)) # TODO make this more robust
        }

    # contributors: [agrawasa-8.11.23, nrobinso-9.11.23]
    def discover_neighbours(self, device_key_name:str) -> List[DeviceInterface]:
        neighbour_key_names: List[str] = []
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
    
    def start(self) -> List[asyncio.Task]:
        self.tasks = [asyncio.create_task(node.start()) for node in self.devices]
        register_task = asyncio.create_task(self.register_with_master())
        return [*self.tasks, register_task]

    async def generate_trusted_keys_table_all_nodes(self) -> dict[str,str]:
        d: dict[str,str] = {}
        for device in self.devices:
            hash = device.jwt.hash_of_public_key()
            pub_key = device.jwt.public_key_pem
            d[hash] = pub_key
        return d
    
    async def get_updated_topology(self, master_host:str='127.0.0.1', master_port:int=33000):
        print("Receiving Updated Device Topology from Master")
        host:str = self.host
    
        body = {
            "emulator_interface": {
                "host": host,
                "port": self.port # TODO
            }
        }
        async with http_client.no_proxy() as client:
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
        '--host', 
        type=str, 
        default='localhost', 
        help='Port number for host (default: localhost)'
    )

    parser.add_argument(
        '--master-port', 
        type=int, 
        default=33000, 
        help='Port number for the master emulator (default: find free)'
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
    if args.host == 'auto':
        args.host = get_ip_address.get_ip_address()
    return args

async def main():
    args = parse_arguments()
    if args.master_host is None:
        args.master_host = get_ip_address.get_ip_address()
    port = args.port
    print("PORT IS:", port)
    if port is None:
        port = gateway_port.find_free_gateway_port_reverse()
    emulator = SlaveEmulator(
        port=port,
        master_host=args.master_host,
        master_port=args.master_port,
        num_nodes=args.num_nodes,
        host=args.host)
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
    
    @app.route('/set_desire_for_one' ,methods=['GET'])
    async def set_desire_for_one():
        # give one device a new desire
        data_name = quart.request.args.get('data_name', default=None, type=str)
        device_key_name = quart.request.args.get("key_name", default=None, type=str)
        if data_name is None or device_key_name is None:
            return 'please provide data_name and device key_name', 400
        for device in emulator.devices:
            if device.jwt.key_name == device_key_name:
                await device.desire_queue.put(data_name)
                return f'set desire {data_name} for device {device.jwt.key_name}', 200
    
    @app.route('/give_data_to_random_device', methods=['GET'])
    async def give_data_to_random_device():
        data_name = quart.request.args.get("data_name", default=None, type=str)
        data      = quart.request.args.get("data", default=None, type=str)
        if data_name is None or data is None:
            return 'please provide data_name and data', 400
        import random
        random_i = random.randint(0,len(emulator.devices)-1)
        device = emulator.devices[random_i]
        device.CACHE[data_name] = data
        return f"gave data to device {random_i} {device.host}:{device.server.port}", 200
    
    @app.route('/all_dbs', methods=['GET'])
    async def all_dbs():
        dbs = []
        for device in emulator.devices:
            db_set = {
                "key_name": device.jwt.key_name,
                "CACHE": device.CACHE,
            }
            dbs.append(db_set)
        return quart.jsonify(dbs), 200

    @app.route('/debug/topology' ,methods=['GET'])
    async def debug_topology():
        return quart.jsonify(emulator.current_topology), 200
    
    @app.route('/debug/cache' ,methods=['GET'])
    async def debug_cache():
        neighbours = []
        for device in emulator.devices:
            print(device)
            neighbours.append(device.CACHE)
        print(neighbours)
        return quart.jsonify(neighbours), 200
    
        
    @app.route('/debug/fib' ,methods=['GET'])
    async def debug_fib():
        neighbours = []
        for device in emulator.devices:
            print(device)
            neighbours.append(device.FIB)
        print(neighbours)
        return quart.jsonify(neighbours), 200
    
    @app.route('/debug/pit' ,methods=['GET'])
    async def debug_pit():
        neighbours = []
        for device in emulator.devices:
            print(device)
            neighbours.append(device.PIT)
        print(neighbours)
        return quart.jsonify(neighbours), 200
    
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
    
    if args.host == 'auto':
        args.host = get_ip_address.get_ip_address()
        print(args.host)
    try:
        import get_ip_address
        await asyncio.gather(*([app.run_task(host=args.host, port=port,debug=True)] + emulator_tasks))
    except asyncio.exceptions.CancelledError:
        pass
    except OSError as e:
        print(str(e))
        raise e


if __name__ == "__main__":
    asyncio.run(main())
