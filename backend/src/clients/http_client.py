from aiohttp import ClientSession


async def get_http_client():
    async with ClientSession() as session:
        yield session
