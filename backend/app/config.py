"""
config.py
----------
Centralized application configuration.
Loads values from environment variables (.env file) using pydantic-settings.
This keeps secrets and environment-specific values out of source code.
"""

import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application info
    APP_NAME: str = "AI Smart Waste Management System"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS - stored as a raw string, parsed into a list below
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # Database
    DATABASE_URL: str = "sqlite:///./waste_management.db"

    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: str = "jpg,jpeg,png,webp"

    # AI Model
    MODEL_PATH: str = "ai_model/saved_model/waste_classifier.h5"
    MODEL_INPUT_SIZE: int = 224
    CONFIDENCE_THRESHOLD: float = 0.5

    # Alerts
    FULL_BIN_ALERT_ENABLED: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def cors_origins(self) -> List[str]:
        """Convert the comma-separated ALLOWED_ORIGINS string into a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def allowed_extensions_list(self) -> List[str]:
        """Convert the comma-separated ALLOWED_EXTENSIONS string into a list."""
        return [ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(",")]


# Singleton settings instance used across the app
settings = Settings()

# Ensure the upload directory always exists at startup
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
