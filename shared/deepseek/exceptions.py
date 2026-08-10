class DeepSeekError(Exception):
    """Base provider error."""


class DeepSeekRateLimitError(DeepSeekError):
    """Raised when the provider rate limits the request."""


class DeepSeekResponseError(DeepSeekError):
    """Raised when the provider response is invalid."""


class DeepSeekTemporaryError(DeepSeekError):
    """Raised for transient provider issues."""
