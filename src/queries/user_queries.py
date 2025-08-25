from sqlmodel import Session, select, func
from typing import Optional, List
from uuid import UUID
from src.core.database import engine
from src.models.user_model import User, UserCreate
from src.exceptions.user_exceptions import (
    UserAlreadyExistsError,
    DatabaseConnectionError,
)
from sqlalchemy.exc import IntegrityError

session = Session(bind=engine)


def create_user(user: UserCreate) -> User:
    try:
        db_user = User(name=user.name, email=user.email)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    except IntegrityError as e:
        session.rollback()
        if "UNIQUE constraint failed" in str(e) and "email" in str(e):
            raise UserAlreadyExistsError(user.email)
        raise DatabaseConnectionError("create_user")
    except Exception:
        session.rollback()
        raise DatabaseConnectionError("create_user")


def get_user(user_id: UUID) -> Optional[User]:
    try:
        statement = select(User).where(User.id == user_id)
        return session.exec(statement).first()
    except Exception:
        raise DatabaseConnectionError("get_user")


def get_users(skip: int = 0, limit: int = 100) -> List[User]:
    try:
        statement = select(User).offset(skip).limit(limit)
        return session.exec(statement).all()
    except Exception:
        raise DatabaseConnectionError("get_users")


def get_user_by_email(email: str) -> Optional[User]:
    try:
        statement = select(User).where(User.email == email)
        return session.exec(statement).first()
    except Exception:
        raise DatabaseConnectionError("get_user_by_email")


def check_email_exists(email: str) -> bool:
    user = get_user_by_email(email)
    return user is not None
