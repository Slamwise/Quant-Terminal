import asyncio
import aiohttp
import logging
from datetime import datetime
from classes.base import ExchangeAPI

logging.basicConfig(level=logging.INFO)

class BinanceAPI(ExchangeAPI):
    BASE_URL = 'https://api.binance.com'

    async def get_order_book(self, symbol='BTCUSDT', limit=100):
        endpoint = '/api/v3/depth'
        params = {'symbol': symbol, 'limit': limit}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}{endpoint}", params=params) as resp:
                data = await resp.json()
                return data

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