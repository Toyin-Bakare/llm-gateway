from ..errors import ProviderError
from .base import RawResult


class OpenAIProvider:
    def __init__(self, api_key: str | None = None):
        try:
            import openai
        except ImportError as e:
            raise ProviderError("pip install 'llm-gateway[openai]'") from e
        self._client = openai.OpenAI(api_key=api_key)

    def complete(self, system: str, user: str, model: str, max_tokens: int) -> RawResult:
        try:
            r = self._client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
        except Exception as e:
            raise ProviderError(str(e)) from e
        text = r.choices[0].message.content or ""
        return RawResult(text, r.usage.prompt_tokens, r.usage.completion_tokens, r.model)
