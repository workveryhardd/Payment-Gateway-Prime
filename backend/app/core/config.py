from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "change-me-in-production-min-32-chars-please"  # Default for development
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    TRONSCAN_API_KEY: Optional[str] = None
    ETHERSCAN_API_KEY: Optional[str] = None
    BSCSCAN_API_KEY: Optional[str] = None
    DATA_FILE_PATH: str = "backend/data/data_store.json"
    # PayPal credentials (baked in for seamless integration)
    PAYPAL_CLIENT_ID: str = "AUBLhI7FwQ8nAYAJKSxvC0Wtz-Tt3HqmEzn8W01eUKTKccUqudyy9gNi2LHNjUWxtJMPxZX86poGWvrC"
    PAYPAL_SECRET: str = "EFpS4Ns_81GrQFt8zXWooOZbbHB_h55bg-pzCMkHldQzisq6fyPlEsm8G98aCCIPe7K28DQXYx7K9wV0"
    PAYPAL_MODE: str = "live"  # Use "sandbox" for testing
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # Allow case-insensitive env vars
        extra="ignore"  # Ignore extra fields from env file
    )

settings = Settings()

