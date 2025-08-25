import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from mcp.server.fastmcp import FastMCP
from src.queries.user_queries import get_user, get_users
from src.models.user_model import User
from typing import List


mcp = FastMCP()

@mcp.tool()
def get_user_by_id(user_id: str) -> User:
    try:
        user = get_user(user_id)
        return user
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_all_users() -> List[User]:
    try:
        users = get_users()
        return users
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def count_users() -> int:
    try:
        users = get_users()
        return len(users)
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run()
