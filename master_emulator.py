from __future__ import annotations

import master_http
import asyncio
import master_http
import httpx
import signal
import asyncio
import is_port_open

import quart
import asyncio
from typing import Optional
import master_emulator
import schema
import jsonschema



class MasterEmulator:
    def __init__(self):
        self.registered_slaves = []
        self.dead_interfaces = []
        self.adjacency_matrix = []

    def run(self):
        heartbeat_task = self.heartbeat()
        return [heartbeat_task]

    def heartbeat(self) -> asyncio.Task:
        # periodically send a heartbeat request to each slave
        async def loop():
            timeout = httpx.Timeout(0.5, connect=0.5)  # Set a short timeout
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

    def register_slave(self, registration_form):
        for i,s in enumerate(self.registered_slaves):
            f = registration_form
            fei = f["emulator_interface"]
            sei = s["emulator_interface"]
            if fei["host"] == sei["host"] and fei["port"] == sei["port"]:
                self.registered_slaves[i] = registration_form
                return
        self.registered_slaves.append(registration_form)

    async def shutdown(self):
        print("Shutting down...")
        # Cancel all running tasks
        for task in asyncio.all_tasks():
            task.cancel()
        print("Shutdown complete.")

# This script instantiates master emulator
# optionally starts vis server
# start master_http
if __name__ == "__main__":
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
                return quart.jsonify({"message": "registratior successful"}), 200
            except jsonschema.ValidationError as e:
                print(str(e))
                return quart.jsonify({"error": str(e)}), 400
            
        @app.route('/' ,methods=['GET'])
        async def index():
            return await quart.render_template('index.html')
            
        @app.route('/new_adjacency_matrix', methods=['GET'])
        async def new_adjacency_matrix():
            if not emulator:
                return quart.jsonify("no emulator"), 500
            return quart.jsonify(emulator.adjacency_matrix)
        
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
            await asyncio.gather(*([app.run_task(host=get_ip_address.get_ip_address(), port=34000,debug=True)] + emulator_tasks))
        except asyncio.exceptions.CancelledError:
            pass

    asyncio.run(main())
