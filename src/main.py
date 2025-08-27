from fastapi import FastAPI

from src.core.database import create_db_and_tables
from src.http.exceptions import setup_exceptions
from src.http import router

app = FastAPI(title="Veritas", version="0.1.0")

setup_exceptions(app)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(router)
