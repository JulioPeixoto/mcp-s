from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.prompts import SYSTEM_INSTRUCTIONS
from src.agents.workflow import WorkflowManager


class AgentsService:
    def __init__(self):
        self.workflow = WorkflowManager()

    async def invoke(self, messages: str):
        workflow = WorkflowManager()
        graph = await workflow.build_graph()
        out = await graph.ainvoke(
            {
                "messages": [
                    SystemMessage(content=SYSTEM_INSTRUCTIONS),
                    HumanMessage(content=messages),
                ]
            }
        )
        return out["messages"][-1]


agents_service = AgentsService()
