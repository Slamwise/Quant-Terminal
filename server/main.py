from fastapi import FastAPI
import logging
from contextlib import asynccontextmanager

from background_tasks import run_background_tasks

app = FastAPI()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    background_task = run_background_tasks() # Start Binance order book stream
    yield
    # Shutdown logic
    background_task.cancel()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello World"}