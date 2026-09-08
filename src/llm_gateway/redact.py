"""Regex-based PII redaction. Catches common shapes only; it is not a full PII detector."""
import re

PATTERNS = {
    "EMAIL": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "PHONE": re.compile(r"(?<!\d)(?:\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}(?!\d)"),
    "SSN": re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)"),
    "CARD": re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)"),
    "API_KEY": re.compile(r"\b(?:sk|pk|ghp|xox[abp]|AKIA|AIza)[-_A-Za-z0-9]{16,}\b"),
}


def redact(text: str) -> tuple[str, int]:
    """Replace PII-shaped spans with [TYPE]. Returns (redacted_text, count)."""
    count = 0
    for label, pattern in PATTERNS.items():
        text, n = pattern.subn(f"[{label}]", text)
        count += n
    return text, count
