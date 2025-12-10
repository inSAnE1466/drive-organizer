"""Application configuration."""

import os
from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings."""
    
    # API config
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Drive Organizer"
    DEBUG: bool = False
    
    # CORS settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",
        "http://localhost:8000"
    ]
    
    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    
    @property
    def REDIS_URI(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # Google API settings
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/callback"
    
    # Gemini API settings
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    
    # Firebase settings
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_SERVICE_ACCOUNT: str = "{}"
    
    # File storage
    TEMP_DIR: str = "/tmp/drive-organizer"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache
def get_settings() -> Settings:
    return Settings()
