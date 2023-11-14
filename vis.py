import asyncio
from aiohttp import web

async def run_vis(emulator):
    async def index(request):
        return web.FileResponse('./web/adjacency.html')  # Replace with the actual path

    async def adjacency_matrix(request):
        return web.json_response(emulator.adjacency_matrix)

    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/adjacency-matrix", adjacency_matrix)

    web_runner = web.AppRunner(app)
    await web_runner.setup()

    # Use 0.0.0.0 to allow external access
    site = web.TCPSite(web_runner, '0.0.0.0', 8080)
    await site.start()

    print("vis server listening")
    
    try:
        while True:
            await asyncio.sleep(10)
    finally:
        print("finished vis")

if __name__ == '__main__':
    class emulator:
        def __init__(self):
            self.adjacency_matrix = [[0,1,0],[1,0,1],[0,1,0]]
    asyncio.run(run_vis(emulator()))

# async def run_vis(emulator):
#         async def index(request):
#             return web.Response(text="Hello, World!")
#         from aiohttp import web
#         app = web.Application()
#         app.router.add_get("/", index)
#         web_runner = web.AppRunner(app)
#         await web_runner.setup()
#         site = web.TCPSite(web_runner,'localhost', 8080)
#         await site.start()
#         print("vis server listening")
#         while True:
#                 await asyncio.sleep(10)
#         print("finished vis")
