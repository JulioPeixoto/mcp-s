from fastapi import Depends
from sqlmodel import Session
from src.core.database import get_session

def get_db_session() -> Session:
    return Depends(get_session)
