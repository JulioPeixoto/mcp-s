from src.agents.workflow import WorkflowManager


class AgentsService:
    def __init__(self):
        self.workflow = WorkflowManager()

    async def invoke(self, messages: str):
        try:
            result = await self.workflow.route_and_invoke(messages)
            return result
        except Exception as e:
            return f"Erro ao processar mensagem: {str(e)}"


agents_service = AgentsService()
