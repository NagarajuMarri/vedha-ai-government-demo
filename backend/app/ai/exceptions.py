"""Internal AI infrastructure exceptions."""


class AIInfrastructureError(Exception):
    """Base class for provider-independent AI infrastructure errors."""

    category = "provider_unavailable"


class AIConfigurationError(AIInfrastructureError):
    """Raised when the AI subsystem is misconfigured."""

    category = "missing_configuration"


class AIAuthenticationError(AIInfrastructureError):
    """Raised when provider credentials are invalid or rejected."""

    category = "authentication_error"


class AIRateLimitError(AIInfrastructureError):
    """Raised when the provider throttles or rate limits the request."""

    category = "rate_limit"


class AIInsufficientQuotaError(AIInfrastructureError):
    """Raised when the configured provider account has insufficient quota."""

    category = "insufficient_quota"


class AIModelNotFoundError(AIInfrastructureError):
    """Raised when the configured model is unavailable to the account."""

    category = "model_not_found"


class AITimeoutError(AIInfrastructureError):
    """Raised when a provider request times out."""

    category = "timeout"


class AIProviderUnavailableError(AIInfrastructureError):
    """Raised when the provider service is unavailable or unreachable."""

    category = "provider_unavailable"


class AIInvalidResponseError(AIInfrastructureError):
    """Raised when provider output does not match the required schema."""

    category = "malformed_response"


class AIReviewerRejectionError(AIInvalidResponseError):
    """Raised when deterministic lesson review rejects provider output."""

    category = "reviewer_rejection"

    def __init__(self, validation_rule: str) -> None:
        super().__init__("Lesson failed deterministic review")
        self.validation_rule = validation_rule


class AIRefusalError(AIInfrastructureError):
    """Raised when the provider safely refuses to generate lesson content."""

    category = "malformed_response"
