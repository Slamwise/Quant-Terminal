from fastapi import FastAPI
import asyncio
from classes.data_sources.stocks import YFinanceDataSource
from classes.data_sources.crypto import BinanceAPI

import asyncio

app = FastAPI()

# Initialize Binance API
exchange = BinanceAPI()
latest_order_book = None
data_lock = asyncio.Lock()

async def fetch_data_continuously():
    global latest_order_book
    while True:
        try:
            data = await exchange.get_order_book()
            async with data_lock:
                latest_order_book = data
        except Exception as e:
            print(f"Error fetching data: {e}")
        await asyncio.sleep(5)  # Adjust the interval as needed

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(fetch_data_continuously())

@app.get("/live-feed")
async def get_live_feed():
    async with data_lock:
        if latest_order_book is not None:
            return latest_order_book
        else:
            return {"message": "Data not available yet"}

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
