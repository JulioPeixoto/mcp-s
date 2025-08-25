from mcp.server.fastmcp import FastMCP
from src.queries.user_queries import get_user, get_users
from src.models.user_model import User
from typing import List

mcp = FastMCP()


@mcp.tool
def get_user_by_id(user_id: str) -> User:
    user = get_user(user_id)
    return user


@mcp.tool
def get_all_users() -> List[User]:
    users = get_users()
    return users


@mcp.tool
def get_length_of_users() -> int:
    length = get_length_of_users()
    return length
