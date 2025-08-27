import sys

from langgraph.prebuilt import MultiServerMCPClient


class MCPClient:
    def __init__(self):
        self.client = None

    async def init_mcp_client(self):
        self.client = MultiServerMCPClient({
            "users": {
                "command": sys.executable,
                "args": ["src/agents/mcp/server.py"],
                "transport": "stdio",
            }
        })