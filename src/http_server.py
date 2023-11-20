from aiohttp import web
import logging
import asyncio


class HTTPServer:
    def __init__(self,handler,host='localhost'):
        self.logger = logging.getLogger()
        self.port = None
        self.handler = handler
        self.host = host
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
        site = web.TCPSite(web_runner,self.host, self.port)
        await site.start()

        # let outside listener know the server has started:
        # usage: await server.started.wait()
        self.started.set()
        self.logger.debug(f"started server on port {self.port}")