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
    def __init__(self):
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
        return [heartbeat_task]

    def heartbeat(self) -> asyncio.Task:
        # periodically send a heartbeat request to each slave
        async def loop():
            while True:
                await asyncio.sleep(1)
                print("running heartbeat")
                dead_interfaces = []
                for i, s in enumerate(self.registered_slaves):
                    ei = s["emulator_interface"]
                    host = ei["host"]
                    port = ei["port"]
                    print("heartbeat", host, port)
                    if not await is_port_open.is_port_open(host, port):
                        print(f"Server {host}:{port} is not reachable")
                        dead_interfaces.append(s)
                        # TODO: safely remove interface from list
                        # watch out for spooky asynchronous goblin data races
                    else:
                        print(f"Server {host} {port} heartbeat ok")
                self.dead_interfaces = dead_interfaces

        return asyncio.create_task(loop())
    
    async def send_topology_to_slave(self, slave):
        i = slave["emulator_interface"]
        timeout = httpx.Timeout(0.5)
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                headers = {"content-type": "application/json"}
                await client.post(f"http://{i['host']}:{i['port']}/update_topology", json=self.current_topology, headers=headers)
                return True
            except Exception as e:
                print("failed to send topology to {i.host}:{i.port}", str(e))
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
                    print(results)
                except Exception as e:
                    print("exception while propagating topology", str(e))
        return asyncio.create_task(task())

    def create_ring_topology(self):
        devices = []
        for form in self.registered_slaves:
            devices = devices + form["devices"]
        self.current_topology = schema.create_ring_topology(devices)

    def register_slave(self, registration_form):
        for i,s in enumerate(self.registered_slaves):
            f = registration_form
            fei = f["emulator_interface"]
            sei = s["emulator_interface"]
            if fei["host"] == sei["host"] and fei["port"] == sei["port"]:
                self.registered_slaves[i] = registration_form
                self.should_propagate.set()
                return
        self.registered_slaves.append(registration_form)
        self.create_ring_topology()
        print("setting should_propagate")
        try:
            self.should_propagate.set()
        except Exception as e:
            print(str(e))
            raise e


async def main():
    emulator = MasterEmulator()
    emulator_tasks = emulator.run()
    app = quart.Quart(__name__)
    @app.route('/register' ,methods=['POST'])
    async def register():
        print("run register")
        my_schema = schema.register_slave
        request_data = await quart.request.get_json()
        print(request_data)
        try:
            jsonschema.validate(instance=request_data, schema=my_schema)
            emulator.register_slave(request_data)
            return quart.jsonify({"message": "registration successful"}), 200
        except jsonschema.ValidationError as e:
            print(str(e))
            return quart.jsonify({"error": str(e)}), 400
        
    @app.route('/' ,methods=['GET'])
    async def index():
        return await quart.render_template('index.html')
    
    @app.route('/new_device_topology', methods=['GET'])
    async def new_adjacency_matrix():
        if not emulator:
            return quart.jsonify("no emulator"), 500
        return quart.jsonify(emulator.adjacency_matrix)
        
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
    try:
        import get_ip_address
        await asyncio.gather(*([app.run_task(host=get_ip_address.get_ip_address(), port=33000,debug=True)] + emulator_tasks))
    except asyncio.exceptions.CancelledError:
        pass

# This script instantiates master emulator
# optionally starts vis server
# start master_http
if __name__ == "__main__":
   
    asyncio.run(main())