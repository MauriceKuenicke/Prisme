import json
from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime application settings loaded from environment variables."""

    # Runtime
    ENVIRONMENT: Literal["development", "test", "production"] = "development"

    # Database
    DATABASE_URL: str = "sqlite:///./prisme.db"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:5173", "http://localhost:3000"])

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 5
    ALLOWED_IMAGE_EXTENSIONS: list[str] = Field(default_factory=lambda: ["jpg", "jpeg", "png", "webp"])

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key_strength(cls, value: str) -> str:
        """Require sufficiently long signing secrets for JWT integrity."""
        if len(value) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters.")
        return value

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str] | None) -> list[str]:
        """Accept CORS origins as JSON array, comma-separated string, or list."""
        if value is None:
            return ["http://localhost:5173", "http://localhost:3000"]

        if isinstance(value, str):
            text = value.strip()
            if not text:
                return []

            if text.startswith("["):
                try:
                    parsed = json.loads(text)
                except json.JSONDecodeError as exc:
                    raise ValueError("CORS_ORIGINS JSON format is invalid.") from exc
                if not isinstance(parsed, list):
                    raise ValueError("CORS_ORIGINS JSON value must be a list.")
                return [str(item).strip() for item in parsed if str(item).strip()]

            return [item.strip() for item in text.split(",") if item.strip()]

        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]

        raise ValueError("CORS_ORIGINS must be a list or comma-separated string.")

    @model_validator(mode="after")
    def validate_environment_security(self) -> "Settings":
        """Prevent unsafe defaults from being used in production deployments."""
        insecure_default = "dev-secret-key-change-in-production-min-32-chars"
        if self.ENVIRONMENT == "production" and self.SECRET_KEY == insecure_default:
            raise ValueError("Set a unique SECRET_KEY in production.")
        return self


@lru_cache()
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()


settings = get_settings()
