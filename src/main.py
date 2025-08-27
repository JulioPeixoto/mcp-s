from fastapi import FastAPI

from src.core.database import create_db_and_tables
from src.http import router
from src.http.exceptions import setup_exceptions

app = FastAPI(title="mcp-agent", version="0.1.0")

setup_exceptions(app)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(router)
