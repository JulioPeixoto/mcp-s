from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from src.http.exceptions.user_exceptions import BaseAPIException, UserAlreadyExistsError


async def base_api_exception_handler(request: Request, exc: BaseAPIException):
    return JSONResponse(status_code=exc.status_code, content=exc.detail)


async def integrity_error_handler(request: Request, exc: IntegrityError):
    error_message = str(exc)

    if "UNIQUE constraint failed" in error_message and "email" in error_message:
        email = "unknown"
        raise UserAlreadyExistsError(email)

    return JSONResponse(
        status_code=409,
        content={
            "error": {
                "code": "DATABASE_CONSTRAINT_VIOLATION",
                "message": "Violação de restrição do banco de dados",
                "details": "Os dados fornecidos violam uma restrição única do banco",
                "metadata": {"constraint": "unique"},
            }
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail,
                "details": "Erro HTTP padrão",
                "metadata": {"status_code": exc.status_code},
            }
        },
    )
