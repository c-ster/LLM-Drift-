from pydantic import BaseModel
import datetime
from typing import Optional

class ResponseBase(BaseModel):
    llm_name: str
    question: str
    response: str

class ResponseCreate(ResponseBase):
    pass

class Response(ResponseBase):
    id: int
    timestamp: datetime.datetime
    similarity_score: Optional[float]

    class Config:
        from_attributes = True
