"""Internal AI infrastructure exceptions."""


class AIInfrastructureError(Exception):
    """Base class for provider-independent AI infrastructure errors."""


class AIConfigurationError(AIInfrastructureError):
    """Raised when the AI subsystem is misconfigured."""


class AIAuthenticationError(AIInfrastructureError):
    """Raised when provider credentials are invalid or rejected."""


class AIRateLimitError(AIInfrastructureError):
    """Raised when the provider throttles or rate limits the request."""


class AITimeoutError(AIInfrastructureError):
    """Raised when a provider request times out."""


class AIProviderUnavailableError(AIInfrastructureError):
    """Raised when the provider service is unavailable or unreachable."""


class AIInvalidResponseError(AIInfrastructureError):
    """Raised when provider output does not match the required schema."""
