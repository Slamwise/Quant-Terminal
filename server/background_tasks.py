# background_tasks.py

import asyncio
import logging
from classes.data_sources.binance import BinanceAPI
from classes.data_storage.wasabi import test_wasabi_connection_and_list_buckets, save_json_to_wasabi
from datetime import datetime, timezone

binance_api = BinanceAPI()
logger = logging.getLogger(__name__)

# Initialize Wasabi connection and select the bucket once
wasabi_buckets = test_wasabi_connection_and_list_buckets(print_success=False)
if not wasabi_buckets:
    raise Exception("Failed to connect to Wasabi or no buckets available")
WASABI_BUCKET = wasabi_buckets[0]  # Use the first available bucket

async def save_data_to_wasabi(exchange, symbol, order_book, ohlcv):
    timestamp = datetime.now(timezone.utc).isoformat()
    data = {
        'timestamp': timestamp,
        'symbol': symbol,
        'order_book': order_book,
        'ohlcv': ohlcv
    }
    object_key = f"{exchange}/{symbol}/{timestamp}.json"
    # Save to Wasabi (assuming save_json_to_wasabi is your utility function)
    await asyncio.to_thread(save_json_to_wasabi, data, WASABI_BUCKET, object_key)

async def fetch_and_save_data(symbol):
    try:
        order_book = await binance_api.fetch_order_book(symbol)
        ohlcv = await binance_api.fetch_ohlcv(symbol)
        await save_data_to_wasabi('binance', symbol, order_book, ohlcv)
        logger.info(f"Data for {symbol} saved successfully.")
    except Exception as e:
        logger.error(f"Error fetching or saving data for {symbol}: {str(e)}")

async def scheduled_data_collection(symbols):
    while True:
        tasks = [fetch_and_save_data(symbol) for symbol in symbols]
        await asyncio.gather(*tasks)
        await asyncio.sleep(60)  # Sleep for 1 minute

def run_background_tasks():
    symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'SEIUSDT', 'SUIUSDT', 'PEPEUSDT']
    task = asyncio.create_task(scheduled_data_collection(symbols))
    return task