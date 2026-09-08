"""Hand-maintained $ per 1M tokens. Costs are estimates. Verify against provider price pages.

LAST_VERIFIED: 2026-09-08
"""

LAST_VERIFIED = "2026-09-08"

# model -> (input $/1M, output $/1M)
PRICES: dict[str, tuple[float, float]] = {
    "claude-sonnet-4-5": (3.00, 15.00),
    "claude-haiku-4-5": (1.00, 5.00),
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "gemini-2.5-pro": (1.25, 10.00),
    "gemini-2.5-flash": (0.30, 2.50),
}


def estimate(model: str, input_tokens: int, output_tokens: int) -> float:
    """Returns estimated USD. Unknown models cost 0.0 (and should be added to PRICES)."""
    inp, out = PRICES.get(model, (0.0, 0.0))
    return round((input_tokens * inp + output_tokens * out) / 1_000_000, 6)
