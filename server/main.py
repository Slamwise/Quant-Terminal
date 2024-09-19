from fastapi import FastAPI
import asyncio
from classes.data_sources.stocks import YFinanceDataSource
from classes.data_sources.crypto import BinanceAPI, CoinbaseWebSocketAPI
import logging
from contextlib import asynccontextmanager

app = FastAPI()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Binance API
binance_exchange = BinanceAPI()
binance_latest_order_books = {}
binance_data_lock = asyncio.Lock()

# Initialize Coinbase WebSocket API
coinbase_exchange = CoinbaseWebSocketAPI()
# TODO: Figure out how to dynamically set the coinbase symbols and channels from requests
coinbase_symbols = ['BTC-USD', 'ETH-USD']
coinbase_channels = ["ticker_batch"] 

async def fetch_binance_data_continuously(symbols=['BTCUSDT', 'ETHUSDT'], interval=5):
    global binance_latest_order_books
    while True:
        for symbol in symbols:
            try:
                data = await binance_exchange.get_order_book(symbol=symbol)
                async with binance_data_lock:
                    binance_latest_order_books[symbol] = data
                logger.info(f"Fetched Binance data for {symbol}")
            except Exception as e:
                logger.error(f"Error fetching Binance data for {symbol}: {e}")
        await asyncio.sleep(interval)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    await coinbase_exchange.connect(coinbase_symbols, coinbase_channels)
    asyncio.create_task(coinbase_exchange.listen())
    yield
    # Shutdown logic (if any)

app = FastAPI(lifespan=lifespan)

@app.get("/binance-live-feed/{symbol}")
async def get_binance_live_feed(symbol: str):
    async with binance_data_lock:
        data = binance_latest_order_books.get(symbol)
        if data is not None:
            return data
        else:
            return {"message": f"Binance data not available for {symbol}"}

@app.get("/coinbase-live-feed/{symbol}")
async def get_coinbase_live_feed(symbol: str):
    data = await coinbase_exchange.get_order_book(symbol)
    return data

@app.get("/coinbase-ticker/{symbol}")
async def get_coinbase_ticker(symbol: str):
    data = await coinbase_exchange.get_ticker(symbol)
    return data

# Create an instance of YFinanceDataSource
aapl_datasource = YFinanceDataSource("AAPL_DATA", "AAPL")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/stock_data")
async def get_stock_data():
    data = await aapl_datasource.fetch_data()
    return data

@app.get("/health")
async def check_health():
    is_healthy = await aapl_datasource.check_health()
    return {"status": "healthy" if is_healthy else "unhealthy"}
