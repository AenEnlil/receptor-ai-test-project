from pydantic import BaseModel
from typing import Tuple, Dict, List


class RequestLoggingSchema(BaseModel):
    scheme: str
    method: str
    client: Tuple
    server: Tuple
    path: str
    path_params: Dict | None = None
    query_string: str | None = None
    headers: List[Dict]
    body: Dict | None = None


class ResponseLoggingSchema(BaseModel):
    status_code: int
    headers: List[Dict] | None = None
    body: Dict | List | None = None
