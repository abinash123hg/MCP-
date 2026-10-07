from functools import lru_cache
import os
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    host: str = Field(default_factory=lambda: os.getenv("APP_HOST", "0.0.0.0"))
    port: int = Field(default_factory=lambda: int(os.getenv("APP_PORT", "8000")))
    headless: bool = Field(default_factory=lambda: os.getenv("BROWSER_HEADLESS", "true").lower() == "true")
    browser_timeout_ms: int = Field(default_factory=lambda: int(os.getenv("BROWSER_TIMEOUT_MS", "15000")))
    ollama_base_url: str = Field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"))
    ollama_model: str = Field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "llama3.2:3b"))
    max_actions_per_request: int = Field(default_factory=lambda: int(os.getenv("MAX_ACTIONS_PER_REQUEST", "8")))

@lru_cache
def get_settings() -> Settings:
    return Settings()
