from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import field_serializer
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True, index=True)


class UserCreate(SQLModel):
    name: str
    email: str


class UserRead(SQLModel):
    id: UUID
    name: str
    email: str

    @field_serializer("id")
    def serialize_id(self, id: UUID) -> str:
        return str(id)


class UserResponse(SQLModel):
    data: UserRead
    message: str
    status: str


class UsersListResponse(SQLModel):
    length: int
    data: List[UserRead]
