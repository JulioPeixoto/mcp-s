from pydantic_settings import BaseSettings
from langchain_openai import ChatOpenAI


class Settings(BaseSettings):
    openai_api_key: str

    database_url: str = "sqlite:///./test.db"
