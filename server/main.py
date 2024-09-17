from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from classes.data_sources.y_finance import YFinanceDataSource
from classes.streams.base import Stream, ConnectionManager
from classes.data_storage.base import LocalStorage, CloudStorage
from classes.data_sources.base import RESTDataSource, WebSocketDataSource
import asyncio

app = FastAPI()
manager = ConnectionManager()

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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(1)  # Keep the connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.on_event("startup")
async def startup_event():
    # Choose the appropriate data source
    data_source = RESTDataSource(name="example_rest", endpoint="https://api.example.com/data")
    # data_source = WebSocketDataSource(name="example_ws", uri="wss://api.example.com/stream")

    # Initialize the Stream
    stream = Stream(
        data_source=data_source,
        connection_manager=manager,
        data_storage=None,  # Or provide a DataStorage instance
        interval=5  # Interval in seconds for RESTDataSource
    )

    # Start the Stream
    asyncio.create_task(stream.start())
    app.state.stream = stream

@app.on_event("shutdown")
async def shutdown_event():
    # Stop the Stream
    await app.state.stream.stop()