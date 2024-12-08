import asyncio
# import concurrent.futures.Future

def convert_future(fut) -> asyncio.Future:
    return asyncio.wrap_future(fut)