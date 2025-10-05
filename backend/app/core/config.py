"""
Application Configuration
Loads settings from environment variables
"""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment"""
    
    # Application
    APP_NAME: str = "PlayCricket API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://cricket_user:cricket_pass_dev@localhost:5432/playcricket_dev"
    )
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 300  # 5 minutes default
    
    # Security
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production-min-32-chars-long")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:4200", "http://localhost:3000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # API
    API_V1_PREFIX: str = "/api"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS_PER_MATCH: int = 1000
    
    # Performance
    RESPONSE_CACHE_ENABLED: bool = True
    QUERY_CACHE_ENABLED: bool = True
    MAX_REQUEST_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()