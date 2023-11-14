import master_http
import asyncio
import master_http
import httpx
import signal
import socket
import asyncio
import is_port_open

class MasterEmulator:
    def __init__(self):
        self.registered_slaves = []
        self.dead_interfaces = []

    async def run(self):
        server_task = master_http.master_emulator(self,port=33000)
        heartbeat_task = self.heartbeat()

        await asyncio.gather(server_task, heartbeat_task, return_exceptions=True)

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
                    # Usage in your heartbeat loop
                    if not await is_port_open.is_port_open(host, port):
                        print(f"Server {host}:{port} is not reachable")
                        dead_interfaces.append(s)
                        # TODO: safely remove interface from list
                        # watch out for spooky asynchronous goblin data races
                    else:
                        print(f"Server {host} {port} heartbeat ok")
                self.dead_interfaces = dead_interfaces

        return asyncio.create_task(loop())
    
    # def heartbeat(self) -> asyncio.Task:
    #     # periodically send a heartbeat request to each slave
    #     async def loop():
    #         while True:
    #             await asyncio.sleep(1)
    #             print("running heartbeat")
    #             for i,s in enumerate(self.registered_slaves):
    #                 ei = s["emulator_interface"]
    #                 host = ei["host"]
    #                 port = ei["port"]
    #                 print("heartbeat", host, port)
    #                 timeout = httpx.Timeout(0.5, connect=0.5)
    #                 async with httpx.AsyncClient(timeout=timeout) as client:
    #                     try:
    #                         res = await client.get(f"http://{host}:{port}/heartbeat")
    #                         print(res)
    #                     except httpx.RequestTimeout:
    #                         print(f"Timeout occurred for {host}:{port}")
    #                         # Handle timeout here (e.g., remove slave, retry, etc.)
    #                         # TODO: safely remove slave from list
    #     return asyncio.create_task(loop())

    def register_slave(self, registration_form):
        for i,s in enumerate(self.registered_slaves):
            f = registration_form
            fei = f["emulator_interface"]
            sei = s["emulator_interface"]
            if fei["host"] == sei["host"] and fei["port"] == sei["port"]:
                self.registered_slaves[i] = registration_form
                return
        self.registered_slaves.append(registration_form)

    # randomly update topology every 10 seconds

    async def shutdown(self):
        print("Shutting down...")
        # Cancel all running tasks
        for task in asyncio.all_tasks():
            task.cancel()
        print("Shutdown complete.")

def signal_handler(master_emulator):
    asyncio.create_task(master_emulator.shutdown())
# This script instantiates master emulator
# optionally starts vis server
# start master_http
if __name__ == "__main__":
    async def main():
        me = MasterEmulator()
        signal.signal(signal.SIGINT, lambda s, f: signal_handler(me))
        await me.run()

    asyncio.run(main())
