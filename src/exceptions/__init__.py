from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import IntegrityError
from .user_exceptions import BaseAPIException
from .exception_handlers import (
    base_api_exception_handler,
    integrity_error_handler,
    http_exception_handler
)

def setup_exceptions(app: FastAPI) -> None:
    app.add_exception_handler(BaseAPIException, base_api_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)

__all__ = ["setup_exceptions"]
