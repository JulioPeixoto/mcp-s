from typing import List

from mcp.server.fastmcp import FastMCP

from src.models.user_model import User
from src.queries.user_queries import get_user, get_users


def users_tools(mcp_instance: FastMCP):
    @mcp_instance.tool()
    def get_user_by_id(user_id: str) -> User:
        try:
            user = get_user(user_id)
            return user
        except Exception as e:
            return {"error": str(e)}

    @mcp_instance.tool()
    def get_all_users() -> List[User]:
        try:
            users = get_users()
            return users
        except Exception as e:
            return {"error": str(e)}

    @mcp_instance.tool()
    def count_users() -> int:
        try:
            users = get_users()
            return len(users)
        except Exception as e:
            return {"error": str(e)}
