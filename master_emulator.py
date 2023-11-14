import master_http
import asyncio
import master_http
import httpx
import signal
import asyncio
import is_port_open


class MasterEmulator:
    def __init__(self):
        self.registered_slaves = []
        self.dead_interfaces = []
        self.adjacency_matrix = []

    async def run(self):
        server_task = master_http.master_emulator(self,port=33000)
        heartbeat_task = self.heartbeat()
        results = await asyncio.gather(server_task, heartbeat_task, return_exceptions=True)
        for r in results:
            print(r)

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


    async def send_topology_to_slave(self):
        # TODO: By Naman Arora
        # have to send to slave
        # need the address of slave requesting updated topology
        # or send updated topology from control center
        return self.adjacency_matrix


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
        me = MasterEmulator()
        await me.run()

    asyncio.run(main())
