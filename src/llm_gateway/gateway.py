import hashlib
import time
import uuid
from dataclasses import dataclass

from . import injection, pricing, redact
from .config import GatewayConfig
from .errors import BudgetExceeded, InjectionBlocked, ProviderError, RateLimited
from .limits import MemoryLimits
from .providers.base import Provider, RawResult


@dataclass
class GatewayResponse:
    text: str
    request_id: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: int
    input_hash: str          # sha256 of the (redacted) system + user text
    redactions: int          # PII spans replaced
    injection_flagged: bool
    injection_hits: list[str]
    prompt_ref: str
    caller: str
    session_id: str

    def audit(self) -> dict:
        """Everything except the response text, for the audit log."""
        d = self.__dict__.copy()
        d.pop("text")
        return d


def _make_provider(cfg: GatewayConfig) -> Provider:
    if cfg.provider == "anthropic":
        from .providers.anthropic import AnthropicProvider
        return AnthropicProvider(cfg.api_key)
    if cfg.provider == "openai":
        from .providers.openai import OpenAIProvider
        return OpenAIProvider(cfg.api_key)
    if cfg.provider == "google":
        from .providers.google import GoogleProvider
        return GoogleProvider(cfg.api_key)
    raise ProviderError(f"unknown provider: {cfg.provider}")


class Gateway:
    def __init__(self, config: GatewayConfig, provider: Provider | None = None, limits=None):
        self.cfg = config
        self.provider = provider or _make_provider(config)
        self.limits = limits or MemoryLimits(config.rate_limit_per_session, config.daily_budget_usd)

    def call(
        self,
        system: str,
        user: str,
        session_id: str,
        caller: str,
        prompt_ref: str = "",
    ) -> GatewayResponse:
        # 1. limits
        if not self.limits.session_allowed(session_id):
            raise RateLimited(f"session {session_id} over {self.cfg.rate_limit_per_session} calls")
        if not self.limits.budget_allowed():
            raise BudgetExceeded(f"daily budget ${self.cfg.daily_budget_usd:.2f} reached")

        # 2. redact
        redactions = 0
        if self.cfg.redact_pii:
            user, n1 = redact.redact(user)
            system, n2 = redact.redact(system)
            redactions = n1 + n2

        # 3. injection check
        flagged, hits = (False, [])
        if self.cfg.injection_check:
            flagged, hits = injection.check(user)
            if flagged and self.cfg.block_on_injection:
                raise InjectionBlocked(f"matched: {hits}")

        # 4. model call, with one fallback
        start = time.perf_counter()
        raw = self._complete(system, user)
        latency_ms = int((time.perf_counter() - start) * 1000)

        # 5. cost + record
        cost = pricing.estimate(raw.model, raw.input_tokens, raw.output_tokens)
        self.limits.record(session_id, cost)

        return GatewayResponse(
            text=raw.text,
            request_id=uuid.uuid4().hex,
            model=raw.model,
            input_tokens=raw.input_tokens,
            output_tokens=raw.output_tokens,
            cost_usd=cost,
            latency_ms=latency_ms,
            input_hash=hashlib.sha256((system + "\n" + user).encode()).hexdigest(),
            redactions=redactions,
            injection_flagged=flagged,
            injection_hits=hits,
            prompt_ref=prompt_ref,
            caller=caller,
            session_id=session_id,
        )

    def _complete(self, system: str, user: str) -> RawResult:
        try:
            return self.provider.complete(system, user, self.cfg.model, self.cfg.max_tokens)
        except ProviderError:
            if not self.cfg.fallback_model:
                raise
            return self.provider.complete(system, user, self.cfg.fallback_model, self.cfg.max_tokens)
