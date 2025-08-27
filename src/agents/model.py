from langchain_openai import ChatOpenAI

from src.core.settings import settings


class Model:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.5,
            max_retries=2,
            openai_api_key=settings.openai_api_key,
            streaming=True,
        )

    @staticmethod
    def get_client():
        return Model().llm


model = Model()
