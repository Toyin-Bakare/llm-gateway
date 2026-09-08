from ..errors import ProviderError
from .base import RawResult


class GoogleProvider:
    def __init__(self, api_key: str | None = None):
        try:
            from google import genai
        except ImportError as e:
            raise ProviderError("pip install 'llm-gateway[google]'") from e
        self._genai = genai
        self._client = genai.Client(api_key=api_key)

    def complete(self, system: str, user: str, model: str, max_tokens: int) -> RawResult:
        try:
            r = self._client.models.generate_content(
                model=model,
                contents=user,
                config=self._genai.types.GenerateContentConfig(
                    system_instruction=system, max_output_tokens=max_tokens
                ),
            )
        except Exception as e:
            raise ProviderError(str(e)) from e
        usage = r.usage_metadata
        return RawResult(
            r.text or "",
            usage.prompt_token_count or 0,
            usage.candidates_token_count or 0,
            model,
        )
