import aiohttp
import json
from classes.base import ExchangeAPI

class BinanceAPI(ExchangeAPI):
    BASE_URL = 'https://api.binance.com'
    WS_URL = 'wss://fstream.binance.com/stream'

    # Websocket orderboo
    async def listen_order_book(self, symbol='BTCUSDT', callback=None):
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(f"{self.WS_URL}/{symbol.lower()}@depth") as ws:
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        if callback:
                            await callback(symbol, data)
                    elif msg.type == aiohttp.WSMsgType.CLOSED:
                        break
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        break

    async def get_trades(self, symbol='BTCUSDT', limit=500):
        endpoint = '/api/v3/trades'
        params = {'symbol': symbol, 'limit': limit}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}{endpoint}", params=params) as resp:
                data = await resp.json()
                return data

    async def check_health(self):
        endpoint = '/api/v3/ping'
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}{endpoint}") as resp:
                return resp.status == 200

    async def fetch_order_book(self, symbol='BTCUSDT', limit=100):
        endpoint = '/api/v3/depth'
        params = {'symbol': symbol, 'limit': limit}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}{endpoint}", params=params) as resp:
                return await resp.json()

    async def fetch_ohlcv(self, symbol='BTCUSDT', interval='1m', limit=1):
        endpoint = '/api/v3/klines'
        params = {'symbol': symbol, 'interval': interval, 'limit': limit}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}{endpoint}", params=params) as resp:
                return await resp.json()

    # Optionally, keep the check_health method if you still need it
    async def check_health(self):
        endpoint = '/api/v3/ping'
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}{endpoint}") as resp:
                return resp.status == 200
