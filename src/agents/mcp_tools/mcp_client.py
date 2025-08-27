import os
import sys

from langchain_mcp_adapters.client import MultiServerMCPClient


class MCPClient:
    def __init__(self):
        self.client = None

    async def init_client(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        server_path = os.path.join(current_dir, "server.py")
        self.client = MultiServerMCPClient(
            {
                "default": {
                    "command": sys.executable,
                    "args": [server_path],
                    "transport": "stdio",
                }
            }
        )
        return self.client
