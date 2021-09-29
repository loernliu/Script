import asyncio

from aiohttp import ClientSession

async def compute(x, y):
    print("Compute %s + %s ..." % (x, y))
    await asyncio.sleep(1.0)
    return x + y

async def print_sum(x, y):
    result = await compute(x, y)
    print("%s + %s = %s" % (x, y, result))

loop = asyncio.get_event_loop()
loop.run_until_complete(print_sum(1, 2))
loop.close()


async def fetch(session, url):
    async with session.get(url) as resp:
        return await resp


async def main():
    url_list = []
    tasks = []
    async with ClientSession() as session:
        for url in url_list:
            tasks.append(fetch(session, url))
        htmls = await asyncio.gather(*tasks)
