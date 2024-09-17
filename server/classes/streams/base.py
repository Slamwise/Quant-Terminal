from classes.base import DataSource, DataStorage
from classes.data_sources.base import RESTDataSource, WebSocketDataSource
from classes.data_storage.base import LocalStorage, CloudStorage
import asyncio
from typing import Optional, List
from fastapi import WebSocket, WebSocketDisconnect
import json

class Stream:
    def __init__(self, data_source: DataSource, connection_manager, data_storage: Optional[DataStorage] = None, interval: Optional[float] = None):
        self.data_source = data_source
        self.connection_manager = connection_manager
        self.data_storage = data_storage
        self.interval = interval  # For RESTDataSource
        self.running = False
        self.health_check_interval = 60  # in seconds
        self.last_health_check = 0
        self.retry_delay = 5  # in seconds

    async def start(self):
        self.running = True
        asyncio.create_task(self.run())

    async def stop(self):
        self.running = False

    async def run(self):
        while self.running:
            try:
                if isinstance(self.data_source, RESTDataSource):
                    data_stream = self.data_source.data_stream(self.interval)
                elif isinstance(self.data_source, WebSocketDataSource):
                    data_stream = self.data_source.data_stream()
                else:
                    raise NotImplementedError("Unsupported DataSource type")

                async for data in data_stream:
                    await self.process_data(data)
                    await self.check_health_periodically()
            except Exception as e:
                print(f"Error in data stream: {e}")
                await self.retry()

    async def process_data(self, data):
        # Send data to clients
        await self.connection_manager.send_data(data)
        # Optionally save data
        if self.data_storage:
            await self.save_data(data)

    async def save_data(self, data):
        # Implement saving logic based on your storage type
        pass

    async def check_health_periodically(self):
        current_time = asyncio.get_event_loop().time()
        if current_time - self.last_health_check > self.health_check_interval:
            healthy = await self.data_source.check_health()
            if not healthy:
                print("Data source is unhealthy. Attempting to reconnect...")
                await self.retry()
            self.last_health_check = current_time

    async def retry(self):
        await asyncio.sleep(self.retry_delay)
        await self.data_source.connect()

    async def save_data(self, data):
        if isinstance(self.data_storage, LocalStorage):
            await self.data_storage.save_file("data.json", json.dumps(data).encode())
        elif isinstance(self.data_storage, CloudStorage):
            await self.data_storage.save_file("data.json", json.dumps(data).encode())

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_data(self, data):
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except WebSocketDisconnect:
                self.disconnect(connection)
            except Exception as e:
                print(f"Error sending data to client: {e}")
                self.disconnect(connection)
