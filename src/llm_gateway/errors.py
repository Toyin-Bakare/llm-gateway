class GatewayError(Exception):
    """Base class for all gateway errors."""


class RateLimited(GatewayError):
    """Session exceeded its call limit."""


class BudgetExceeded(GatewayError):
    """Daily spend limit reached."""


class InjectionBlocked(GatewayError):
    """Input looked like a prompt injection and blocking is enabled."""


class ProviderError(GatewayError):
    """The model provider returned an error or is not installed."""
