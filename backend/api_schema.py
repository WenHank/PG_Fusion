from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    max_price: float = 100000.0
