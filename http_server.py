from aiohttp import web
import logging
import asyncio

class HTTPServer:
    def __init__(self,handler):
        self.logger = logging.getLogger()
        self.port = None
        self.handler = handler
        # an async event that is set after the server has started
        self.started = asyncio.Event()

    async def start(self):
        app = web.Application()
        app.router.add_post("/", self.handler)
        web_runner = web.AppRunner(app)
        await web_runner.setup()
        site = web.TCPSite(web_runner,'127.0.0.1', 0)
        await site.start()

        # let outside listener know the server has started:
        # usage: await server.started.wait()
        self.started.set()
        addr = site._server.sockets[0].getsockname()
        self.host = addr[0]
        self.port = int(addr[1])
        self.logger.debug(f"started server on port {self.port}")
        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    async def handler(request):
        return web.Response(text="ok")
    server = HTTPServer(handler)
    asyncio.run(server.start())