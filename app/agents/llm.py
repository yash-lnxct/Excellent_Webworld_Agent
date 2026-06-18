import logging
from typing import TypeVar

from openai import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError
from pydantic import BaseModel

from app.config import get_fallback_llm, get_llm
from app.exceptions import LLMError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

MAIN_OPENAI_ERRORS = (
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
    APIStatusError,
)


def _is_fallback_eligible(exc: Exception) -> bool:
    if isinstance(exc, (APIConnectionError, APITimeoutError, RateLimitError)):
        return True
    if isinstance(exc, APIStatusError):
        return exc.status_code in {404, 408, 429, 500, 502, 503, 529}
    return False


def invoke_structured(prompt: str, schema: type[T]) -> T:
    primary_error = ""
    try:
        return get_llm().with_structured_output(schema).invoke(prompt)
    except MAIN_OPENAI_ERRORS as exc:
        if not _is_fallback_eligible(exc):
            raise
        primary_error = str(exc)
        logger.warning(
            "Primary OpenAI model failed: %s — falling back to %s",
            primary_error,
            get_fallback_llm().model_name,
        )

    fallback_error = ""
    try:
        return get_fallback_llm().with_structured_output(schema).invoke(prompt)
    except MAIN_OPENAI_ERRORS as exc:
        fallback_error = str(exc)
        logger.error("Fallback OpenAI model also failed: %s", fallback_error)

    raise LLMError(
        f"OpenAI request failed on primary and fallback models. "
        f"Primary: {primary_error}. Fallback: {fallback_error}.",
        primary_error=primary_error,
        fallback_error=fallback_error,
    )
