from langchain_openai import ChatOpenAI
from src.core.settings import settings


class Model:
    def __init__(self):
        self.client = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.5,
            max_retries=2,
            openai_api_key=settings.openai_api_key,
        )

    def get_client(self):
        return self.client