import master_http
import asyncio

class MasterEmulator:

    # randomly update topology every 10 seconds


# This script instantiates master emulator
# optionally starts vis server
# start master_http
if __name__ == "__main__":
    me = MasterEmulator()
    asyncio.run(me.run())