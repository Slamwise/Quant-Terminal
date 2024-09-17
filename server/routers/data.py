from fastapi import APIRouter
from server.classes.data_sources.base import RESTDataSource
from schemas.data import DataResponse

router = APIRouter()

@router.get('/fetch-data', response_model=DataResponse)
async def fetch_data():
    data_source = RESTDataSource('Example API', 'https://api.example.com/data')
    data = await data_source.fetch_data()
    return DataResponse(timestamp='2024-09-15T00:00:00Z', data=data)
