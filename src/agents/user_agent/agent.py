import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage
from src.agents.model import Model

SYSTEM_INSTRUCTIONS = """\
Você é um agente de dados de usuários.
- Para perguntas sobre usuários, SEMPRE chame ferramentas MCP (get_user_by_id, search_users, count_users).
- Não invente dados. Se a ferramenta retornar vazio, explique isso.
- Oculte PII por padrão; só inclua se o pedido for explícito e autorizado.
"""


async def build_graph():
    client = MultiServerMCPClient(
        {
            "users": {
                "command": "python",
                "args": ["src/agents/mcp/server.py"],
                "transport": "stdio",
            }
        }
    )

    mcp_tools = await client.get_tool_node("users")
    tool_node = ToolNode(mcp_tools)

    llm = Model()
    llm_with_tools = llm.bind_tools([mcp_tools])

    async def call_llm(messages: list[BaseMessage]):
        response = await llm_with_tools.ainvoke(messages)
        return response.content

    def should_continue(state: MessagesState):
        last_message = state.messages[-1]
        return "tools_node" if getattr(last_message, "tool_calls", None) else END

    g = StateGraph(MessagesState)
    g.add_node("call_model", call_llm)
    g.add_node("tools", tool_node)
    g.add_edge(START, "call_model")
    g.add_conditional_edges("call_model", should_continue)
    g.add_edge("tools", "call_model")
    return g.compile()


async def demo():
    graph = await build_graph()
    out = await graph.ainvoke(
        {
            "messages": [
                {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                {"role": "user", "content": "Quantos usuários ativos temos?"},
            ]
        }
    )
    print(out["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(demo())
