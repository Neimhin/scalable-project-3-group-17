from __future__ import annotations
import asyncio
import httpx
import signal
import asyncio
import is_port_open
import quart
import asyncio
import schema
import jsonschema

class MasterEmulator:
    def __init__(self,heartbeat=1):
        self.heartbeat_interval = heartbeat
        self.registered_slaves = []
        self.dead_interfaces = []
        self.adjacency_matrix = []
        self.current_topology = {
            "devices": [],
            "connections": [],
        }
        self.should_propagate = asyncio.Event()

    def run(self):
        heartbeat_task = self.heartbeat()
        topology_propagation_task = self.propagate_topology()
        return [heartbeat_task, topology_propagation_task]

    def heartbeat(self) -> asyncio.Task:
        # periodically send a heartbeat request to each slave
        async def loop():
            while True:
                await asyncio.sleep(self.heartbeat_interval)
                print("running heartbeat")
                dead_interfaces = []
                for i, s in enumerate(self.registered_slaves):
                    ei = s["emulator_interface"]
                    host = ei["host"]
                    port = ei["port"]
                    print("heartbeat", host, port)
                    if not await is_port_open.is_port_open(host, port):
                        print(f"Server {host}:{port} is not reachable")
                        dead_interfaces.append(s['emulator_interface'])
                        # TODO: safely remove interface from list
                        # watch out for spooky asynchronous goblin data races
                    else:
                        print(f"Server {host} {port} heartbeat ok")

                self.registered_slaves = [
                    s for s in self.registered_slaves if not any(d["host"] == s["emulator_interface"]["host"] and d["port"] == s["emulator_interface"]["port"] for d in dead_interfaces)
                ]
                if dead_interfaces:
                    print(f"Removed {len(dead_interfaces)} dead interfaces.")

                if len(dead_interfaces) > 0:
                    self.create_ring_topology()
                    self.should_propagate.set()


        return asyncio.create_task(loop())
    
    ##### contributor: naarora #####

    async def send_topology_to_slave(self, slave):

        slave_emulator_interface = slave["emulator_interface"]
        host = slave_emulator_interface['host']
        port = int(slave_emulator_interface['port'])
        headers = ["Content-Type: application/json"]

        try:
            import encapsulate_http
            import json
            response_raw = encapsulate_http.http_request("/update_topology", host, port, method="POST", headers=headers, body=json.dumps(self.current_topology))
            response = encapsulate_http.extract_body_from_response(response_raw)
            print(response)
        # timeout = httpx.Timeout(0.5)
        # async with httpx.AsyncClient(timeout=timeout) as client:
        #         headers = {"content-type": "application/json"}
        #         await client.post(f"http://{slave_emulator_interface['host']}:{slave_emulator_interface['port']}/update_topology", json=self.current_topology, headers=headers)
        #         return True
        except Exception as e:
            print(f"failed to send topology to {host}:{port}", str(e))
            raise e
            return False
    
    def propagate_topology(self) -> asyncio.Task:
        async def task():
            while True:
                await self.should_propagate.wait()
                try:
                    self.should_propagate.clear()
                    tasks = [asyncio.create_task(self.send_topology_to_slave(s)) for s in self.registered_slaves]
                    together = asyncio.gather(*tasks,return_exceptions=True)
                    results = await together
                    print("finished propagating topology")
                    print(self.current_topology)
                    print(results)
                except Exception as e:
                    print("exception while propagating topology", str(e))
        return asyncio.create_task(task())

    def create_ring_topology(self):
        devices = []
        for form in self.registered_slaves:
            devices = devices + form["devices"]
        self.current_topology = schema.create_ring_topology(devices)

    def create_ocean_demo_topology(self):
        emulator_rings = []
        ring_connections = []
        devices = []
        for emulator_form in self.registered_slaves:
            emulator_ring = schema.create_ring_topology(emulator_form['devices'])
            emulator_rings.append(emulator_ring)
            ring_connections += emulator_ring['connections']
            devices += emulator_form['devices']
        print(emulator_ring)

        if len(emulator_rings) > 1:
            for i in range(len(emulator_rings)):
                orig_ring = emulator_rings[i]
                next_ring = emulator_rings[(i+1) % len(emulator_rings)]
                import random
                random_source_interface = orig_ring['devices'][random.randint(0,len(orig_ring['devices']) - 1)]
                random_target_interface = next_ring['devices'][random.randint(0,len(next_ring['devices']) - 1)]
                ring_connections.append({
                    "source": random_source_interface['key_name'],
                    "target": random_target_interface['key_name'],
                })
        self.current_topology = {
            "devices": devices,
            "connections": ring_connections,
        }
        self.should_propagate.set()
        
    def disconnect_device(self, key_name):
        connections = []
        print(key_name, len(self.current_topology['connections']))
        for connection in self.current_topology['connections']:
            if connection['source'] != key_name and connection['target'] != key_name:
                connections.append(connection)
                print("not keeping connection", connection)
        self.current_topology['connections'] = connections
        print(key_name, len(self.current_topology['connections']))


    def register_slave(self, registration_form):
        for i, slave in enumerate(self.registered_slaves):
            if (registration_form["emulator_interface"]["host"] == slave["emulator_interface"]["host"] and
                    registration_form["emulator_interface"]["port"] == slave["emulator_interface"]["port"]):
                self.registered_slaves[i] = registration_form
                return "Slave Updated"
        self.registered_slaves.append(registration_form)
        self.create_ocean_demo_topology()
        print("setting should_propagate")
        try:
            self.should_propagate.set()
        except Exception as e:
            print(str(e))
            raise e
        return "New Slave Registered"

def parse_arguments():
    import argparse
    parser = argparse.ArgumentParser(description="Argument parser for emulator configuration")
    
    parser.add_argument(
        '--port', 
        type=int, 
        default=33000, 
        help='Port number for the master emulator (default: 33000)'
    )

    parser.add_argument(
        '--heartbeat', 
        type=int, 
        default=1, 
        help='Interval in seconds between heartbeats.'
    )

    parser.add_argument(
        '--host',
        type=str, 
        default='localhost', 
        help='Port number for the master emulator (default: 33000)'
    )
        

import argparse
def parse_arguments():
    parser = argparse.ArgumentParser(description="Argument parser for emulator configuration")
    
    parser.add_argument(
        '--host', 
        type=str, 
        default='localhost', 
        help='Which host to listen on'
    )

    parser.add_argument(
        '--port', 
        type=int, 
        default=33000, 
        help='Which host to listen on'
    )

    parser.add_argument(
        '--heartbeat', 
        type=int, 
        default=1, 
        help='Interval between heartbeats.'
    )
    args = parser.parse_args()
    return args

async def main():
    args = parse_arguments()
    emulator = MasterEmulator()
    emulator = MasterEmulator(heartbeat=args.heartbeat)
    emulator_tasks = emulator.run()
    app = quart.Quart(__name__)
    @app.route('/register' ,methods=['POST'])
    async def register():
        print("run register")
        bytes = await quart.request.get_data()
        json_str = bytes.decode("utf-8")
        import json
        request_data = json.loads(json_str)
        print(request_data)
        request_data = await quart.request.get_json()
        print(request_data)
        try:
            jsonschema.validate(instance=request_data, schema=schema.register_slave)
            emulator.register_slave(request_data)
            return quart.jsonify({"message": "registration successful"}), 200
        except jsonschema.ValidationError as e:
            print(str(e))
            return quart.jsonify({"error": str(e)}), 400
        
    @app.route('/' ,methods=['GET'])
    async def index():
        print("rendering index.html")
        return await quart.render_template('index.html')
    
    @app.route('/new_device_topology', methods=['GET'])
    async def new_adjacency_matrix():
        if not emulator:
            return quart.jsonify("no emulator"), 500
        return quart.jsonify(emulator.adjacency_matrix)
    
    @app.route('/slaves', methods=['GET'])
    async def slave():
        return quart.jsonify(emulator.registered_slaves)
    
    @app.route('/disconnect_device', methods=['GET'])
    async def disconnect_device():
        device_key_name = quart.request.args.get('key_name',default=None, type=str)
        if device_key_name is None:
            import random
            device_key_name = random.choice(emulator.current_topology['devices'])['key_name']
        emulator.disconnect_device(device_key_name)
        emulator.should_propagate.set()
        return "ok baby", 200
    
    @app.route('/devices', methods=['GET'])
    async def devices_index():
        import render
        html = ''
        for slave in emulator.registered_slaves:
            html += render.emulator(slave)
        html +=     '<script src="{{ url_for(\'static\', filename=\'js/util.js\') }}"></script>'
        rendered_html = await quart.render_template_string(html)
        print(rendered_html)
        return rendered_html, 200
        
    # for vis
    @app.route('/current_topology', methods=['GET'])
    async def current_topology():
        if not emulator:
            return quart.jsonify("no emulator"), 500
        return quart.jsonify(emulator.current_topology)
    
    @app.after_serving
    async def shutdown():
        print("shuttting down...")
        for task in emulator_tasks:
            task.cancel()
        
    def signal_handler():
        print("interruption signal received")
        for t in emulator_tasks:
            t.cancel()
        
    asyncio.get_event_loop().add_signal_handler(signal.SIGINT,signal_handler)

    if args.host == 'auto':
        import get_ip_address
        args.host = get_ip_address.get_ip_address()

    try:
        await asyncio.gather(*([app.run_task(host=args.host, port=args.port,debug=True)] + emulator_tasks))
    except asyncio.exceptions.CancelledError:
        pass

# This script instantiates master emulator
# optionally starts vis server
# start master_http
if __name__ == "__main__":
   
    asyncio.run(main())
