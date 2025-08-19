from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    LLM_PROVIDER: str = "groq"
    GROQ_API_KEY: str = Field(default="", env="GROQ_API_KEY")
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()