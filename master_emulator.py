import master_http
import asyncio
import master_http

class MasterEmulator:
    async def run(self):
        await master_http.master_emulator(self,port=34000)

    # randomly update topology every 10 seconds


# This script instantiates master emulator
# optionally starts vis server
# start master_http
if __name__ == "__main__":
    me = MasterEmulator()
    asyncio.run(me.run())