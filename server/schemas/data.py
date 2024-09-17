from pydantic import BaseModel
from typing import Any, Dict

class DataResponse(BaseModel):
    timestamp: str
    data: Dict[str, Any]
