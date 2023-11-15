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
        import get_ip_address
        import gateway_port
        await web_runner.setup()
        self.port = gateway_port.find_free_gateway_port()
        site = web.TCPSite(web_runner,get_ip_address.get_ip_address(), self.port)
        await site.start()

        # let outside listener know the server has started:
        # usage: await server.started.wait()
        self.started.set()
        addr = site._server.sockets[0].getsockname()
        self.host = addr[0]
        self.port = int(addr[1])
        self.logger.debug(f"started server on port {self.port}")