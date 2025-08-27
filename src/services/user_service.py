from uuid import UUID

from src.exceptions.user_exceptions import CreateUserError
from src.models.user_model import UserCreate
from src.queries import user_queries


class UserService:
    def __init__(self):
        self.user_crud = user_queries

    def create_user(self, user: UserCreate):
        try:
            return self.user_crud.create_user(user=user)
        except Exception as error:
            raise CreateUserError(error.args[0])

    def get_user(self, user_id: UUID):
        return self.user_crud.get_user(user_id=user_id)

    def get_users(self, skip: int = 0, limit: int = 100):
        return self.user_crud.get_users(skip=skip, limit=limit)


UserService = UserService()