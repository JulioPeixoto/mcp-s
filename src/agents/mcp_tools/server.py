import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from mcp.server.fastmcp import FastMCP
from src.agents.mcp_tools.tools.users_tool import users_tools
from src.agents.mcp_tools.tools.math_tools import math_tools

mcp = FastMCP()
users_tools(mcp)
math_tools(mcp)

if __name__ == "__main__":
    mcp.run()
