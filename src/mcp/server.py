import asyncio
import json
from typing import Any, Dict
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    Tool,
    TextContent,
    TextContent,
    TextContentType,
)

from src.services.user_service import UserService
from src.models.user_model import UserRead, UsersListResponse

def create_mcp_server() -> Server:
    server = Server("user-database-mcp")

    @server.list_tools()
    async def handle_list_tools() -> ListToolsResult:
        return ListToolsResult(
            tools=[
                Tool(
                    name="get_all_users",
                    description="Busca todos os usuários do banco de dados com paginação opcional",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "skip": {
                                "type": "integer",
                                "description": "Número de registros para pular (padrão: 0)",
                                "default": 0
                            },
                            "limit": {
                                "type": "integer", 
                                "description": "Número máximo de registros para retornar (padrão: 100)",
                                "default": 100
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="get_user_by_id",
                    description="Busca um usuário específico pelo ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "ID do usuário (UUID)",
                                "format": "uuid"
                            }
                        },
                        "required": ["user_id"]
                    }
                ),
                Tool(
                    name="get_user_by_email",
                    description="Busca um usuário específico pelo email",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "email": {
                                "type": "string",
                                "description": "Email do usuário",
                                "format": "email"
                            }
                        },
                        "required": ["email"]
                    }
                )
            ]
        )

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
        try:
            if name == "get_all_users":
                skip = arguments.get("skip", 0)
                limit = arguments.get("limit", 100)
                
                users = UserService.get_users(skip=skip, limit=limit)
                
                users_data = [UserRead.from_orm(user) for user in users]
                response = UsersListResponse(
                    length=len(users_data),
                    data=users_data
                )
                
                return CallToolResult(
                    content=[
                        TextContent(
                            type=TextContentType.TEXT,
                            text=json.dumps(response.model_dump(), indent=2, ensure_ascii=False)
                        )
                    ]
                )
                
            elif name == "get_user_by_id":
                user_id = arguments["user_id"]
                from uuid import UUID
                
                user = UserService.get_user(UUID(user_id))
                if user:
                    user_data = UserRead.from_orm(user)
                    return CallToolResult(
                        content=[
                            TextContent(
                                type=TextContentType.TEXT,
                                text=json.dumps(user_data.model_dump(), indent=2, ensure_ascii=False)
                            )
                        ]
                    )
                else:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type=TextContentType.TEXT,
                                text=json.dumps({"error": "Usuário não encontrado"}, indent=2, ensure_ascii=False)
                            )
                        ]
                    )
                    
            elif name == "get_user_by_email":
                email = arguments["email"]
                
                user = UserService.user_crud.get_user_by_email(email)
                if user:
                    user_data = UserRead.from_orm(user)
                    return CallToolResult(
                        content=[
                            TextContent(
                                type=TextContentType.TEXT,
                                text=json.dumps(user_data.model_dump(), indent=2, ensure_ascii=False)
                            )
                        ]
                    )
                else:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type=TextContentType.TEXT,
                                text=json.dumps({"error": "Usuário não encontrado"}, indent=2, ensure_ascii=False)
                            )
                        ]
                    )
            else:
                return CallToolResult(
                    content=[
                        TextContent(
                            type=TextContentType.TEXT,
                            text=json.dumps({"error": f"Ferramenta '{name}' não encontrada"}, indent=2, ensure_ascii=False)
                        )
                    ]
                )
                
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type=TextContentType.TEXT,
                        text=json.dumps({"error": str(e)}, indent=2, ensure_ascii=False)
                    )
                ]
            )

    return server

async def main():
    server = create_mcp_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="user-database-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
