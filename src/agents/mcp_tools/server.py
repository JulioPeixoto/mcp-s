import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from mcp.server.fastmcp import FastMCP

from src.agents.mcp_tools.tools.users_tool import users_tools

mcp = FastMCP()

users_tools(mcp)

if __name__ == "__main__":
    mcp.run()
