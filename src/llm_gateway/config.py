from dataclasses import dataclass


@dataclass
class GatewayConfig:
    provider: str = "anthropic"          # "anthropic" | "openai" | "google"
    model: str = "claude-sonnet-4-5"
    fallback_model: str | None = None    # tried once if the primary call fails
    max_tokens: int = 1024
    rate_limit_per_session: int = 20     # calls per session_id
    daily_budget_usd: float = 5.00       # total estimated spend per UTC day
    redact_pii: bool = True
    injection_check: bool = True
    block_on_injection: bool = False     # False = flag only; True = raise InjectionBlocked
    api_key: str | None = None           # falls back to the provider's env var
