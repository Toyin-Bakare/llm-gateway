"""In-memory rate limit and daily budget. Swap the class for SQLite/Redis later."""
import threading
from collections import defaultdict
from datetime import UTC, datetime


class MemoryLimits:
    def __init__(self, rate_limit_per_session: int, daily_budget_usd: float):
        self.rate_limit = rate_limit_per_session
        self.budget = daily_budget_usd
        self._calls: dict[str, int] = defaultdict(int)
        self._spend: dict[str, float] = defaultdict(float)
        self._lock = threading.Lock()

    @staticmethod
    def _today() -> str:
        return datetime.now(UTC).strftime("%Y-%m-%d")

    def session_allowed(self, session_id: str) -> bool:
        with self._lock:
            return self._calls[session_id] < self.rate_limit

    def budget_allowed(self) -> bool:
        with self._lock:
            return self._spend[self._today()] < self.budget

    def record(self, session_id: str, cost_usd: float) -> None:
        with self._lock:
            self._calls[session_id] += 1
            self._spend[self._today()] += cost_usd

    def spend_today(self) -> float:
        with self._lock:
            return self._spend[self._today()]
