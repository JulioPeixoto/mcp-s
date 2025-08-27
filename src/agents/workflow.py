import asyncio
import sys

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import HumanMessage, MessagesState, SystemMessage, ToolNode

from src.agents.mcp.mcp_client import MCPClient
from src.agents.prompts import SYSTEM_INSTRUCTIONS
from src.agents.user_agent.agent import Model


class WorkflowManager:
    def __init__(self):
        self.graph = None
        self.client = None
        self.tools = None
        self.llm = Model.get_client()
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        mcp = MCPClient()
        self.client = mcp.init_mcp_client()
        
    async def build_graph(self):
        client = await self.init_mcp_client()
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
    graph = await WorkflowManager.build_graph()
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
