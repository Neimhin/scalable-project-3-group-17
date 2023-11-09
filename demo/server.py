from aiohttp import web
import logging
import asyncio
class HTTPServer:
    def __init__(self,handler):
        self.logger = logging.getLogger()
        self.port = None
        self.handler = handler

    async def start(self):
        app = web.Application()
        app.router.add_post("/", lambda r: self.handler(r))
        web_runner = web.AppRunner(app)
        # TODO handle errors
        await web_runner.setup()
        site = web.TCPSite(web_runner,'localhost', 0)
        await site.start()
        print(site._server.sockets)
        addr = site._server.sockets[0].getsockname()
        self.host = addr[0]
        self.port = int(addr[1])
        print(type(self.port))
        self.logger.debug(f"started server on port {self.port}")

    def set_desires(self, desires):
        self.desires = desires

if __name__ == "__main__":
    async def handler(self, request):
        return web.Response(text="ok")
    httpd = HTTPServer()
    asyncio.run(httpd.start())

