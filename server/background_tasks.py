import asyncio
import logging
from classes.data_sources.binance import BinanceAPI
from classes.data_storage.wasabi import test_wasabi_connection_and_list_buckets, save_json_to_wasabi
from datetime import datetime, timezone

binance_exchange = BinanceAPI()
logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

async def save_order_book_to_wasabi(symbol, data):
    timestamp = datetime.now(timezone.utc).isoformat()
    object_key = f"binance/orderbook/{symbol}/{timestamp}.json"
    
    # Initialize Wasabi connection
    wasabi_buckets = test_wasabi_connection_and_list_buckets(print_success=False)
    if not wasabi_buckets:
        raise Exception("Failed to connect to Wasabi or no buckets available")
    WASABI_BUCKET = wasabi_buckets[0]  # Use the first available bucket
    await asyncio.to_thread(save_json_to_wasabi, data, WASABI_BUCKET, object_key, print_success=False)

async def listen_order_book_with_retry(symbol):
    retries = 0
    while retries < MAX_RETRIES:
        try:
            await binance_exchange.listen_order_book(symbol, save_order_book_to_wasabi)
        except Exception as e:
            retries += 1
            logger.error(f"Error in Binance order book stream for {symbol}. Retry {retries}/{MAX_RETRIES}. Error: {str(e)}")
            if retries < MAX_RETRIES:
                await asyncio.sleep(RETRY_DELAY)
            else:
                logger.critical(f"Binance order book stream for {symbol} failed after {MAX_RETRIES} attempts. Stopping this stream.")
                return
        else:
            retries = 0  # Reset retries if successful

async def start_binance_order_book_stream(symbols=['BTCUSDT', 'ETHUSDT']):
    tasks = [listen_order_book_with_retry(symbol) for symbol in symbols]
    await asyncio.gather(*tasks)

def run_background_tasks():
    loop = asyncio.get_event_loop()
    loop.create_task(start_binance_order_book_stream())