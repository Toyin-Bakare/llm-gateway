from dataclasses import dataclass
from typing import Protocol


@dataclass
class RawResult:
    text: str
    input_tokens: int
    output_tokens: int
    model: str


class Provider(Protocol):
    def complete(self, system: str, user: str, model: str, max_tokens: int) -> RawResult: ...
