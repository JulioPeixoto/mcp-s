from uuid import UUID

from fastapi import APIRouter

from src.http.exceptions.user_exceptions import UserNotFoundError
from src.models.user_model import UserCreate, UserRead, UserResponse, UsersListResponse
from src.services.user_service import UserService

router = APIRouter(tags=["users"])


@router.post("/users/", response_model=UserRead)
def create_user(user: UserCreate):
    db_user = UserService.create_user(user=user)
    return db_user


@router.get("/users/{user_id}/", response_model=UserResponse)
def read_user(user_id: UUID):
    db_user = UserService.get_user(user_id=user_id)
    if db_user is None:
        raise UserNotFoundError(user_id)
    return UserResponse(
        data=db_user, message="User retrieved successfully", status="success"
    )


@router.get("/users/", response_model=UsersListResponse)
def read_users(skip: int = 0, limit: int = 100):
    users = UserService.get_users(skip=skip, limit=limit)
    return UsersListResponse(length=len(users), data=users)
