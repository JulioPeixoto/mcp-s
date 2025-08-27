from langchain_openai import ChatOpenAI

from src.core.settings import settings


class MathAgentModel:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2,
            max_retries=2,
            openai_api_key=settings.openai_api_key,
        )

    @staticmethod
    def get_client():
        return MathAgentModel().llm

math_agent_model = MathAgentModel()