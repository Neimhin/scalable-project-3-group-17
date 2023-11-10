import asyncio

async def waiter(queue):
    print('waiting for it ...')
    item = await queue.get()
    print('... got it!',item)

async def main():
    queue = asyncio.Queue()
    waiter_task = asyncio.create_task(waiter(queue))
    await asyncio.sleep(1)
    await queue.put("hello world")
    await waiter_task

asyncio.run(main())