import asyncio

# contributors: [nrobinso-9.11.23]
def desire_queue_deterministic(list_of_desires: list,interval=1):
    queue = asyncio.Queue()
    for item in list_of_desires:
        assert type(item) is str

    async def put_to_queue():
        for item in list_of_desires:
            await asyncio.sleep(interval)
            await queue.put(item)
    
    asyncio.create_task(put_to_queue())
    return queue

if __name__ == "__main__":

    # TODO move this to unit test in ./test
    # demo a simple queue
    async def main():
        queue = desire_queue_deterministic(["a","b","c"],0.3)
        for i in range(3):
            item = await queue.get()
            print(i,item)
    asyncio.run(main())
