from ..errors import ProviderError
from .base import RawResult


class AnthropicProvider:
    def __init__(self, api_key: str | None = None):
        try:
            import anthropic
        except ImportError as e:
            raise ProviderError("pip install 'llm-gateway[anthropic]'") from e
        self._client = anthropic.Anthropic(api_key=api_key)

    def complete(self, system: str, user: str, model: str, max_tokens: int) -> RawResult:
        try:
            r = self._client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
        except Exception as e:
            raise ProviderError(str(e)) from e
        text = "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
        return RawResult(text, r.usage.input_tokens, r.usage.output_tokens, r.model)
