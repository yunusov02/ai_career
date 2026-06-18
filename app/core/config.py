"""
Application Configuration Module

This module handles all configuration settings using Pydantic Settings.
Environment variables are loaded from .env file.
"""

from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, model_validator
import json


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings can be overridden via environment variables or .env file.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Application Settings
    app_name: str = "SkillBridge"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "production"
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database Settings
    database_url: str = "sqlite+aiosqlite:///./career_assessment.db"
    
    # JWT Settings
    secret_key: str = "your-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # OTP and SMS Settings
    sms_provider: str = "console"
    eskiz_email: str = ""
    eskiz_password: str = ""
    eskiz_from: str = "4546"
    otp_expire_minutes: int = 5
    otp_resend_seconds: int = 60
    otp_max_attempts: int = 5
    
    # OpenAI Settings
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    
    # CORS Settings
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    cors_origin_regex: str = (
        r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"
    )
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value):
        """Accept common environment labels as boolean debug values."""
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "production", "prod", "false", "0", "off", "no"}:
                return False
            if normalized in {"development", "dev", "debug", "true", "1", "on", "yes"}:
                return True
        return value

    @field_validator("openai_api_key", mode="after")
    @classmethod
    def ignore_placeholder_api_keys(cls, value: str) -> str:
        """Do not send placeholder values to the OpenAI API."""
        normalized = value.strip()
        if normalized.lower() in {
            "your-openai-api-key",
            "your_openai_api_key",
            "changeme",
        }:
            return ""
        return normalized

    @model_validator(mode="after")
    def validate_production_secrets(self):
        """Reject unsafe defaults when deployed in production mode."""
        if self.is_production and self.secret_key == "your-super-secret-key-change-in-production":
            raise ValueError("SECRET_KEY must be changed in production")
        if self.sms_provider == "eskiz" and not (self.eskiz_email and self.eskiz_password):
            raise ValueError("ESKIZ_EMAIL and ESKIZ_PASSWORD are required for SMS_PROVIDER=eskiz")
        return self
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to ensure settings are only loaded once.
    """
    return Settings()


# Global settings instance
settings = get_settings()
