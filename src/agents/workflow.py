from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from src.agents.mcp_tools.mcp_client import MCPClient
from src.agents.user_agent.agent import Model


class WorkflowManager:
    def __init__(self):
        self.graph = None
        self.client = None
        self.tools = None
        self.mcp = MCPClient()
        self.llm = Model.get_client()
        self.llm_with_tools = None

    async def build_graph(self):
        self.client = await self.mcp.init_mcp_client()
        self.tools = await self.client.get_tools()
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        tool_node = ToolNode(self.tools)

        g = StateGraph(MessagesState)
        g.add_node("call_model", self.call_model)
        g.add_node("tools", tool_node)
        g.add_edge(START, "call_model")
        g.add_conditional_edges("call_model", self.should_continue)
        g.add_edge("tools", "call_model")
        return g.compile()

    async def call_model(self, state: MessagesState):
        ai_msg = await self.llm_with_tools.ainvoke(state["messages"])
        return {"messages": [ai_msg]}

    def should_continue(self, state: MessagesState):
        last = state["messages"][-1]
        tool_calls = getattr(last, "tool_calls", None) or getattr(
            getattr(last, "additional_kwargs", {}), "get", lambda *_: None
        )("tool_calls")
        return "tools" if tool_calls else END
