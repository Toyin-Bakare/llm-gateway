import pytest

from llm_gateway import Gateway, GatewayConfig
from llm_gateway.errors import ProviderError
from llm_gateway.providers.base import RawResult


class FakeProvider:
    def __init__(self, fail_models=()):
        self.calls = []
        self.fail_models = set(fail_models)

    def complete(self, system, user, model, max_tokens):
        self.calls.append((system, user, model))
        if model in self.fail_models:
            raise ProviderError("boom")
        return RawResult(text=f"echo: {user}", input_tokens=10, output_tokens=5, model=model)


@pytest.fixture
def fake():
    return FakeProvider()


@pytest.fixture
def gw(fake):
    cfg = GatewayConfig(model="gpt-4o", rate_limit_per_session=2, daily_budget_usd=1.0)
    return Gateway(cfg, provider=fake)
