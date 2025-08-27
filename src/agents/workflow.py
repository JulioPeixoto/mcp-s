from langchain_core.messages import SystemMessage

from src.agents.model import Model
from src.agents.math_agent import MathAgent
from src.agents.user_agent import UserAgent
from src.agents.mcp_tools.mcp_client import MCPClient
from src.agents.prompts import CLASSIFICATION_PROMPT


class WorkflowManager:
    def __init__(self):
        self.all_tools = None
        self.users_tools = None
        self.math_tools = None
        self.mcp = MCPClient()
        self.user_agent = UserAgent()
        self.math_agent = MathAgent()
        self.receptor_llm = Model.get_client()

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
        return await self.user_agent.initialize(self.users_tools)

    async def build_math_graph(self):
        await self._ensure_tools()
        return await self.math_agent.initialize(self.math_tools)

    async def _classify_intent(self, user_text: str) -> str:
        classification_prompt = CLASSIFICATION_PROMPT.format(user_text=user_text)
        messages = [SystemMessage(content=classification_prompt)]
        response = await self.receptor_llm.ainvoke(messages)
        classification = response.content.strip().upper()
        return classification

    async def route_and_invoke(self, user_text: str):
        intent = await self._classify_intent(user_text)

        if intent == "MATH":
            if not self.math_agent.graph:
                await self.build_math_graph()
            return await self.math_agent.process(user_text)

        elif intent == "USER":
            if not self.user_agent.graph:
                await self.build_users_graph()
            return await self.user_agent.process(user_text)

        else:
            return "Não consigo responder"
