import os
from functools import lru_cache

from langchain_openai import ChatOpenAI
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = ""
    tavily_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_fallback_model: str = "gpt-4o"

    langsmith_tracing: bool = False
    langsmith_endpoint: str = "https://api.smith.langchain.com"
    langsmith_api_key: str = ""
    langsmith_project: str = "ai research agent"

    @field_validator("langsmith_tracing", mode="before")
    @classmethod
    def parse_langsmith_tracing(cls, value: object) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on"}
        return False


@lru_cache
def get_settings() -> Settings:
    return Settings()


def configure_langsmith() -> None:
    settings = get_settings()
    if not settings.langsmith_tracing:
        return

    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_ENDPOINT"] = settings.langsmith_endpoint
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project

    if settings.langsmith_api_key:
        os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key


def get_llm() -> ChatOpenAI:
    settings = get_settings()
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not configured")
    return ChatOpenAI(
        model=settings.openai_model,
        temperature=0.2,
        api_key=settings.openai_api_key,
    )


def get_fallback_llm() -> ChatOpenAI:
    settings = get_settings()
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not configured")
    return ChatOpenAI(
        model=settings.openai_fallback_model,
        temperature=0.2,
        api_key=settings.openai_api_key,
    )
