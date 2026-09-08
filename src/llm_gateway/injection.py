"""Pattern-based prompt-injection check. Flags likely attempts; does not prove immunity."""
import re

PATTERNS = [
    r"ignore (all |any )?(previous|prior|above) (instructions|prompts?)",
    r"disregard (the )?(system|previous|above)",
    r"you are now (a|an|in) ",
    r"(reveal|print|show|repeat) (your |the )?(system prompt|instructions)",
    r"\bdan mode\b|\bjailbreak\b|developer mode",
    r"</?(system|assistant|instruction)>",
    r"begin (new )?(system|instructions)",
]
_COMPILED = [re.compile(p, re.IGNORECASE) for p in PATTERNS]


def check(text: str) -> tuple[bool, list[str]]:
    """Returns (flagged, matched_patterns)."""
    hits = [p.pattern for p in _COMPILED if p.search(text)]
    return bool(hits), hits
