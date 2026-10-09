
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Dynamic Prompt Structuring API"

    # Application authentication key, separate from the provider key.
    app_api_key: str = Field(
        default="",
        validation_alias="APP_API_KEY",
    )

    # An empty provider key enables the existing demo mode.
    api_key: str = Field(
        default="",
        validation_alias="OPENAI_API_KEY",
    )

    base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        validation_alias="OPENAI_BASE_URL",
    )

    model: str = Field(
        default="openrouter/free",
        validation_alias="OPENAI_MODEL",
    )

    @field_validator(
        "app_api_key",
        "api_key",
        "base_url",
        "model",
    )
    @classmethod
    def strip_configuration_values(cls, value: str) -> str:
        return value.strip()

    @field_validator("model")
    @classmethod
    def model_must_not_be_empty(cls, value: str) -> str:
        if not value:
            raise ValueError("OPENAI_MODEL must not be empty.")
        return value


settings = Settings()