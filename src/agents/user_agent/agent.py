import asyncio
import sys
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from src.core.settings import settings


SYSTEM_INSTRUCTIONS = """\
Você é um agente de dados de usuários.
- Para perguntas sobre usuários, SEMPRE chame ferramentas MCP (get_user_by_id, get_all_users, count_users).
- Não invente dados. Se a ferramenta retornar vazio, explique isso.
- Oculte PII por padrão; só inclua se o pedido for explícito e autorizado.
"""

class Model:
    def __init__(self):
        self.client = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.5,
            max_retries=2,
            openai_api_key=settings.openai_api_key,
        )

    @staticmethod
    def get_client():
        return Model().client


async def build_graph():
    client = MultiServerMCPClient({
        "users": {
            "command": sys.executable,
            "args": ["src/agents/mcp/server.py"],
            "transport": "stdio",
        }
    })

    tools = await client.get_tools()
    tool_node = ToolNode(tools)

    llm = Model.get_client()
    llm_with_tools = llm.bind_tools(tools)

    async def call_model(state: MessagesState):
        ai_msg = await llm_with_tools.ainvoke(state["messages"])
        return {"messages": [ai_msg]}

    def should_continue(state: MessagesState):
        last = state["messages"][-1]
        tool_calls = getattr(last, "tool_calls", None) or getattr(getattr(last, "additional_kwargs", {}), "get", lambda *_: None)("tool_calls")
        return "tools" if tool_calls else END

    g = StateGraph(MessagesState)
    g.add_node("call_model", call_model)
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
                SystemMessage(content=SYSTEM_INSTRUCTIONS),
                HumanMessage(content="Quantos usuários ativos temos?"),
            ]
        }
    )
    print(out["messages"][-1].content)
    

if __name__ == "__main__":
    asyncio.run(demo())
