import asyncio

async def demo(i):
    await asyncio.sleep(1)
    print(i)


async def main(): 
    tasks = [
        demo(i) for i in range(100)
    ]
    await asyncio.gather(*tasks)
 
asyncio.run(main())