from sqlalchemy.orm import Session
from . import models

from typing import Optional

def create_response(db: Session, llm_name: str, question: str, response: str, similarity_score: Optional[float]):
    db_response = models.Response(
        llm_name=llm_name, 
        question=question, 
        response=response,
        similarity_score=similarity_score
    )
    db.add(db_response)
    db.commit()
    db.refresh(db_response)
    return db_response

def get_responses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Response).offset(skip).limit(limit).all()
