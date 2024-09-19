from fastapi import FastAPI, HTTPException
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
coinbase_symbols = set()  # Use a set to store unique symbols
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
    await coinbase_exchange.connect(list(coinbase_symbols), coinbase_channels)
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

@app.get("/coinbase-orderbook/{symbol}")
async def get_coinbase_orderbook(symbol: str):
    data = await coinbase_exchange.get_order_book(symbol)
    return data

@app.get("/coinbase-ticker/{symbol}")
async def get_coinbase_ticker(symbol: str):
    symbol = symbol.upper()  # Ensure the symbol is in uppercase
    if symbol not in coinbase_symbols:
        coinbase_symbols.add(symbol)
        try:
            await coinbase_exchange.subscribe([symbol], coinbase_channels)
        except Exception as e:
            coinbase_symbols.remove(symbol)
            raise HTTPException(status_code=400, detail=f"Failed to subscribe to {symbol}: {str(e)}")
    
    # Wait for a short time to allow the subscription to take effect
    await asyncio.sleep(1)
    
    data = await coinbase_exchange.get_ticker(symbol)
    if data is None:
        raise HTTPException(status_code=404, detail=f"No data available for {symbol}")
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
