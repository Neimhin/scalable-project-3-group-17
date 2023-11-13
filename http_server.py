from aiohttp import web
import logging
import asyncio


class HTTPServer:
    def __init__(self,handler):
        self.logger = logging.getLogger()
        self.port = None
        self.handler = handler
        # an async event that is set after the server has started
        # TODO: create a more sophisticated _state Queue to query the state of the server
        self.started = asyncio.Event()

    # TODO: an async function to get the port that waits until startup
    # async def get_port():
    #  ...

    # TODO: a method to pause the device, i.e. stop it from listening on the TCP socket
    # def pause():
    #  ...

    async def start(self,port):
        app = web.Application()
        app.router.add_post("/", self.handler)
        web_runner = web.AppRunner(app)
        await web_runner.setup()
        site = web.TCPSite(web_runner,'127.0.0.1',port)
        await site.start()

        # let outside listener know the server has started:
        # usage: await server.started.wait()
        self.started.set()
        addr = site._server.sockets[0].getsockname()
        # TODO make sure this is correct
        self.host = addr[0]
        self.port = int(addr[1])
        self.logger.debug(f"started server on port {self.port}")