import asyncio
import aiohttp
import logging
from datetime import datetime
from classes.base import ExchangeAPI
import json
import websockets

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
            
class CoinbaseAPI(ExchangeAPI):
    BASE_URL = 'https://api.exchange.coinbase.com'

    async def get_order_book(self, symbol='BTC-USD', level=2):
        endpoint = f'/products/{symbol}/book'
        params = {'level': level}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}{endpoint}", params=params) as resp:
                data = await resp.json()
                return data

    async def get_trades(self, symbol='BTC-USD', limit=100):
        endpoint = f'/products/{symbol}/trades'
        params = {'limit': limit}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}{endpoint}", params=params) as resp:
                data = await resp.json()
                return data

    async def check_health(self):
        endpoint = '/products'
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}{endpoint}") as resp:
                return resp.status == 200

class CoinbaseWebSocketAPI(ExchangeAPI):
    WS_URL = 'wss://ws-feed.exchange.coinbase.com'

    def __init__(self):
        self.websocket = None
        self.latest_order_books = {}
        self.latest_tickers = {}
        self.lock = asyncio.Lock()
        self.subscribed_channels = set()
        self.subscribed_symbols = set()

    async def connect(self, symbols=None, channels=None):
        self.websocket = await websockets.connect(self.WS_URL)
        if channels is None:
            channels = ["level2", "ticker_batch"]
        self.subscribed_channels = set(channels)
        if symbols:
            self.subscribed_symbols = set(symbols)
        await self._send_subscribe_message()

    async def _send_subscribe_message(self):
        subscribe_message = {
            "type": "subscribe",
            "product_ids": list(self.subscribed_symbols),
            "channels": list(self.subscribed_channels)
        }
        await self.websocket.send(json.dumps(subscribe_message))

    async def subscribe(self, symbols, channels=None):
        new_symbols = set(symbols) - self.subscribed_symbols
        if new_symbols:
            self.subscribed_symbols.update(new_symbols)
            if channels:
                self.subscribed_channels.update(channels)
            await self._send_subscribe_message()

    async def disconnect(self):
        if self.websocket:
            await self.websocket.close()

    async def listen(self):
        while True:
            try:
                message = await self.websocket.recv()
                data = json.loads(message)
                logging.debug(f"Received message: {data}")
                if data['type'] == 'snapshot' and 'level2' in self.subscribed_channels:
                    await self.handle_snapshot(data)
                elif data['type'] == 'l2update' and 'level2' in self.subscribed_channels:
                    await self.update_order_book(data)
                elif data['type'] == 'ticker' and 'ticker_batch' in self.subscribed_channels:
                    await self.update_ticker(data)
            except websockets.exceptions.ConnectionClosed:
                logging.error("WebSocket connection closed. Attempting to reconnect...")
                await asyncio.sleep(5)
                await self.connect()
            except Exception as e:
                logging.error(f"WebSocket error: {e}")
                await asyncio.sleep(5)
                await self.connect()

    async def handle_snapshot(self, data):
        async with self.lock:
            self.latest_order_books[data['product_id']] = {
                'bids': data['bids'],
                'asks': data['asks']
            }
        logging.debug(f"Received snapshot for {data['product_id']}")

    async def update_ticker(self, data):
        async with self.lock:
            self.latest_tickers[data['product_id']] = {
                'price': data['price'],
                'open_24h': data['open_24h'],
                'volume_24h': data['volume_24h'],
                'low_24h': data['low_24h'],
                'high_24h': data['high_24h'],
                'volume_30d': data['volume_30d'],
                'best_bid': data['best_bid'],
                'best_ask': data['best_ask'],
                'timestamp': data['time']
            }
        logging.debug(f"Updated ticker for {data['product_id']}")

    async def get_ticker(self, symbol='BTC-USD'):
        async with self.lock:
            ticker = self.latest_tickers.get(symbol)
            if ticker is None:
                logging.warning(f"No ticker data available for {symbol}")
                return {"error": f"No ticker data available for {symbol}"}
            logging.info(f"Returning ticker for {symbol}")
            return ticker

    async def get_order_book(self, symbol='BTC-USD'):
        async with self.lock:
            return self.latest_order_books.get(symbol, {"message": f"No data available for {symbol}"})

    async def check_health(self):
        return self.websocket and self.websocket.open

    async def get_trades(self, symbol='BTC-USD', limit=100):
        # Coinbase Pro doesn't provide a WebSocket feed for recent trades
        # We'll need to implement a REST API call for this
        # This is a placeholder implementation
        logging.warning("get_trades method not fully implemented for CoinbaseWebSocketAPI")
        return {"message": "Trades data not available via WebSocket, use REST API instead"}
