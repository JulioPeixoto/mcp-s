from pydantic_settings import BaseSettings


class Settings(BaseSettings, env_file=".env", env_file_encoding="utf-8"):
    openai_api_key: str
    database_url: str = "sqlite:///./test.db"


settings = Settings()