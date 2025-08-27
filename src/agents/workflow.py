from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from src.agents.mcp_tools.mcp_client import MCPClient
from src.agents.user_agent.user_agent import Model as UserAgentModel
from src.agents.math_agent.math_agent import MathAgentModel
from src.agents.prompts import SYSTEM_INSTRUCTIONS


class WorkflowManager:
    def __init__(self):
        self.users_graph = None
        self.math_graph = None
        self.all_tools = None
        self.users_tools = None
        self.math_tools = None
        self.mcp = MCPClient()
        self.user_llm = UserAgentModel.get_client()
        self.math_llm = MathAgentModel.get_client()

    async def _ensure_tools(self):
        if self.all_tools is None:
            client = await self.mcp.init_client()
            self.all_tools = await client.get_tools()
            user_names = {"get_user_by_id", "get_all_users", "count_users"}
            math_names = {"add", "subtract", "multiply", "divide", "power"}
            self.users_tools = [t for t in self.all_tools if t.name in user_names]
            self.math_tools = [t for t in self.all_tools if t.name in math_names]

    async def build_users_graph(self):
        await self._ensure_tools()
        users_llm = self.user_llm.bind_tools(self.users_tools)

        async def call_model(state: MessagesState):
            ai_msg = await users_llm.ainvoke(state["messages"])
            return {"messages": [ai_msg]}

        def should_continue(state: MessagesState):
            last = state["messages"][-1]
            tool_calls = getattr(last, "tool_calls", None) or getattr(
                getattr(last, "additional_kwargs", {}), "get", lambda *_: None
            )("tool_calls")
            return "tools" if tool_calls else END

        g = StateGraph(MessagesState)
        g.add_node("call_model", call_model)
        g.add_node("tools", ToolNode(self.users_tools))
        g.add_edge(START, "call_model")
        g.add_conditional_edges("call_model", should_continue)
        g.add_edge("tools", "call_model")
        self.users_graph = g.compile()
        return self.users_graph

    async def build_math_graph(self):
        await self._ensure_tools()
        math_llm = self.math_llm.bind_tools(self.math_tools)

        async def call_model(state: MessagesState):
            ai_msg = await math_llm.ainvoke(state["messages"])
            return {"messages": [ai_msg]}

        def should_continue(state: MessagesState):
            last = state["messages"][-1]
            tool_calls = getattr(last, "tool_calls", None) or getattr(
                getattr(last, "additional_kwargs", {}), "get", lambda *_: None
            )("tool_calls")
            return "tools" if tool_calls else END

        g = StateGraph(MessagesState)
        g.add_node("call_model", call_model)
        g.add_node("tools", ToolNode(self.math_tools))
        g.add_edge(START, "call_model")
        g.add_conditional_edges("call_model", should_continue)
        g.add_edge("tools", "call_model")
        self.math_graph = g.compile()
        return self.math_graph

    @staticmethod
    def _is_math_intent(text: str) -> bool:
        if not text:
            return False
        text_l = text.lower()
        keys = [
            "somar",
            "subtrair",
            "multiplicar",
            "dividir",
            "potência",
            "quanto é",
            "+",
            "-",
            "*",
            "/",
            "^",
        ]
        return any(k in text_l for k in keys)

    @staticmethod
    def _is_user_intent(text: str) -> bool:
        if not text:
            return False
        text_l = text.lower()
        keys = ["usuário", "usuario", "users", "user", "id do usuário", "listar usuários"]
        return any(k in text_l for k in keys)

    async def route_and_invoke(self, user_text: str):
        if self._is_math_intent(user_text):
            graph = self.math_graph or await self.build_math_graph()
            out = await graph.ainvoke({
                "messages": [
                    SystemMessage(content="Você é um agente de matemática. Use apenas as ferramentas de matemática."),
                    HumanMessage(content=user_text),
                ]
            })
            return out["messages"][-1].content
        if self._is_user_intent(user_text):
            graph = self.users_graph or await self.build_users_graph()
            out = await graph.ainvoke({
                "messages": [
                    SystemMessage(content=SYSTEM_INSTRUCTIONS),
                    HumanMessage(content=user_text),
                ]
            })
            return out["messages"][-1].content
        return "não consigo responder"
