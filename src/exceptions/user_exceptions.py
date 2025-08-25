from fastapi import HTTPException
from typing import Optional, Dict, Any


class BaseAPIException(HTTPException):
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.error_code = error_code
        self.details = details
        self.metadata = metadata or {}

        # Converter UUIDs para string no metadata
        serialized_metadata = {}
        for key, value in self.metadata.items():
            if hasattr(value, "__str__"):
                serialized_metadata[key] = str(value)
            else:
                serialized_metadata[key] = value

        super().__init__(
            status_code=status_code,
            detail={
                "error": {
                    "code": error_code,
                    "message": message,
                    "details": details,
                    "metadata": serialized_metadata,
                }
            },
        )


class UserNotFoundError(BaseAPIException):
    def __init__(self, user_id):
        super().__init__(
            status_code=404,
            error_code="USER_NOT_FOUND",
            message="Usuário não encontrado",
            details=f"O usuário com ID {user_id} não foi encontrado no sistema",
            metadata={"user_id": user_id},
        )


class UserAlreadyExistsError(BaseAPIException):
    def __init__(self, email: str):
        super().__init__(
            status_code=409,
            error_code="USER_ALREADY_EXISTS",
            message="Usuário já existe",
            details=f"Já existe um usuário cadastrado com o email {email}",
            metadata={"email": email},
        )


class InvalidUserDataError(BaseAPIException):
    def __init__(self, field: str, reason: str):
        super().__init__(
            status_code=422,
            error_code="INVALID_USER_DATA",
            message="Dados do usuário inválidos",
            details=f"Campo '{field}': {reason}",
            metadata={"field": field, "reason": reason},
        )


class DatabaseConnectionError(BaseAPIException):
    def __init__(self, operation: str):
        super().__init__(
            status_code=503,
            error_code="DATABASE_CONNECTION_ERROR",
            message="Erro de conexão com banco de dados",
            details=f"Não foi possível realizar a operação: {operation}",
            metadata={"operation": operation},
        )


class CreateUserError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=500, detail=f"Error creating user: {message}")
