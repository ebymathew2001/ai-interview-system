from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str = ""
    sarvam_api_key: str = "" 
    database_url: str = "sqlite:///./interview.db"
    total_questions: int = 2
    llm_model: str = "llama-3.3-70b-versatile"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()