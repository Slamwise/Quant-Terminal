import websockets
from classes.base import DataSource
import aiohttp
import asyncio

### Data Sources ###

class RESTDataSource(DataSource):
    def __init__(self, name, endpoint):
        super().__init__(name)
        self.endpoint = endpoint

    async def fetch_data(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.endpoint) as response:
                return await response.json()

    async def check_health(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.endpoint) as response:
                    return response.status == 200
        except aiohttp.ClientError:
            return False

    async def data_stream(self, interval):
        while True:
            data = await self.fetch_data()
            yield data
            await asyncio.sleep(interval)
        
class WebSocketDataSource(DataSource):
    def __init__(self, name, uri):
        super().__init__(name)
        self.uri = uri
        self.ws = None

    async def connect(self):
        self.ws = await websockets.connect(self.uri)

    async def fetch_data(self):
        if self.ws is None:
            await self.connect()
        data = await self.ws.recv()
        return data

    async def check_health(self):
        return self.ws.open if self.ws else False

    async def data_stream(self):
        if self.ws is None:
            await self.connect()
        async for message in self.ws:
            yield message
