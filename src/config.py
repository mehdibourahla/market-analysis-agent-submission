from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    google_api_key: Optional[str] = Field(default=os.getenv("GOOGLE_API_KEY"), env="GOOGLE_API_KEY")

    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")

    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    max_retries: int = 3
    timeout: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()