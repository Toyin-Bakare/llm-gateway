from llm_gateway.limits import MemoryLimits


def test_rate_limit():
    lim = MemoryLimits(rate_limit_per_session=1, daily_budget_usd=10)
    assert lim.session_allowed("s")
    lim.record("s", 0.0)
    assert not lim.session_allowed("s")
    assert lim.session_allowed("other")


def test_budget():
    lim = MemoryLimits(rate_limit_per_session=99, daily_budget_usd=0.01)
    assert lim.budget_allowed()
    lim.record("s", 0.01)
    assert not lim.budget_allowed()
