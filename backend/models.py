from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.sql import func
from .database import Base

class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    llm_name = Column(String, index=True)
    question = Column(Text)
    response = Column(Text)
    similarity_score = Column(Float, nullable=True)
