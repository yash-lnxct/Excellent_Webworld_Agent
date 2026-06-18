class AgentError(Exception):
    """Base error for agent workflow failures."""


class LLMError(AgentError):
    def __init__(self, message: str, primary_error: str, fallback_error: str = "") -> None:
        self.primary_error = primary_error
        self.fallback_error = fallback_error
        super().__init__(message)
