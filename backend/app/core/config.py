from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./deposit_db.sqlite"  # Default to SQLite
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "change-me-in-production-min-32-chars-please"  # Default for development
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    TRONSCAN_API_KEY: Optional[str] = None
    ETHERSCAN_API_KEY: Optional[str] = None
    BSCSCAN_API_KEY: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # Allow case-insensitive env vars
        extra="ignore"  # Ignore extra fields from env file
    )

settings = Settings()

