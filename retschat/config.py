"""Configuration loaded from environment / .env file."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Azure OpenAI
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_deployment: str = "gpt-5.2-chat"
    azure_openai_api_version: str = "2024-12-01-preview"

    # LLM parameters
    temperature: float = 0.3
    max_tokens: int = 4096
    max_tool_rounds: int = 6

    # Retsinformation API
    retsinformation_base_url: str = "https://retsinformation-api.dk/v1"

    # Tool response truncation (chars)
    max_tool_response_chars: int = 12000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
