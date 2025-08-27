from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from src.agents.model import Model

class MathAgent:
    def __init__(self):
        self.llm = Model.get_client()
        self.graph = None
        self.tools = None

    async def initialize(self, tools):
        self.tools = tools
        math_llm = self.llm.bind_tools(self.tools)
        
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
        g.add_node("tools", ToolNode(self.tools))
        g.add_edge(START, "call_model")
        g.add_conditional_edges("call_model", should_continue)
        g.add_edge("tools", "call_model")
        
        self.graph = g.compile()
        return self.graph

    async def process(self, user_text: str):
        if not self.graph:
            raise ValueError("Agent não foi inicializado. Chame initialize() primeiro.")
        
        system_message = SystemMessage(
            content="Você é um agente de matemática. Use apenas as ferramentas de matemática disponíveis."
        )
        
        result = await self.graph.ainvoke({
            "messages": [system_message, {"role": "user", "content": user_text}]
        })
        
        return result["messages"][-1]
