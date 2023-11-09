from aiohttp import web
import logging
import asyncio

logger = logging.getLogger()

class HTTPServer:
    def __init__(self,handler):
        self.logger = logging.getLogger()
        self.port = None
        self.handler = handler

    async def start(self):
        app = web.Application()
        app.router.add_post("/", lambda r: self.handler(r))
        web_runner = web.AppRunner(app)

        try:
            await web_runner.setup()
            # use TCP for server at hostname
            # set port 0 to ask OS to assign one
            default_port = 0
            HOSTNAME = 'localhost'
            site = web.TCPSite(web_runner, HOSTNAME, default_port)
            
            await site.start()
        
            addr = site._server.sockets[0].getsockname()
            self.host = addr[0]
            self.port = int(addr[1])
            
            self.logger.debug(f"started server on port {self.port}")

            # await asyncio.sleep(10)
        
        except Exception as e:
            print(e)
            raise e

        
# async def handler(self, request):
#     '''
#     When nodeA gets a request from another nodeB, nodeA will first check the location. 
#     If the location point to nodeA then nodeA will check cache to see whether it has the data. 
#     If nodeA does not satisfy the requirement of location, 
#     it will save this request to its interested table and 
#     send this request to next hop follow the entry of Forwarding Infromation Base(FIB)
#     If there is another same request coming to nodeA, 
#     nodeA will discard this request and put this request sender in waiting list.

#     Parameters:
#         request`s format: disctionary which include:
#         "data_name": request_type/(location),
#         "public_key": public key value,
#         "time_stamp": timevalue,
#         "sender_address": sender_address
#     '''
#     body = await request.text()
#     logger.debug(body)
#     return web.Response(text="ok")


# server = HTTPServer(handler)
# asyncio.run(server.start())
