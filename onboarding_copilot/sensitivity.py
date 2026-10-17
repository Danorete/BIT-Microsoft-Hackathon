"""Rule based detection of sensitive columns and sensitive text.

Deterministic on purpose: a manager or auditor can read these rules and see exactly
why something was flagged. No model is involved in this module.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# Column name rules: kind -> regex matched against the lowercase column name.
NAME_RULES: dict[str, str] = {
    "email": r"e[_ ]?mail",
    "phone": r"phone|mobile|\btel\b",
    "ssn": r"\bssn\b|social[_ ]?security|tax[_ ]?id",
    "salary": r"salary|wage|compensation|bonus|pay[_ ]?rate",
    "date_of_birth": r"\bdob\b|birth",
    "address": r"address|street|\bzip\b|postal",
    "person_name": r"^(first|last|full)[_ ]?name$",
    "credential": r"password|passwd|secret|api[_ ]?key|token",
    "health": r"diagnos|medical|health",
}

# Value rules: kind -> compiled regex matched against actual text or cell values.
VALUE_RULES: dict[str, re.Pattern[str]] = {
    "email": re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "phone": re.compile(r"\(?\b\d{3}\)?[\-.\s]\d{3}[\-.\s]\d{4}\b"),
    "api_key": re.compile(r"\b(?:sk-[A-Za-z0-9_\-]{16,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,})\b"),
    "credit_card": re.compile(r"\b(?:\d[ \-]?){15}\d\b"),
}

ADVICE: dict[str, str] = {
    "email": "Emails identify people. Ask for counts or domains instead of raw addresses.",
    "phone": "Phone numbers identify people. Ask for counts or area codes instead.",
    "ssn": "Government ID numbers must never be pasted into an AI tool. Ask who owns this data first.",
    "salary": "Pay data is usually restricted. Ask your manager whether you are cleared to use it.",
    "date_of_birth": "Birth dates are personal data. Use age bands instead of exact dates.",
    "address": "Addresses identify people. Aggregate by region instead.",
    "person_name": "Names identify people. Work with IDs instead.",
    "credential": "Secrets and keys must never be pasted into an AI tool or committed to a repo.",
    "health": "Health data is heavily regulated. Check with the data owner before using it.",
    "api_key": "This looks like an API key. Remove it and rotate the key if it was shared.",
    "credit_card": "This looks like a payment card number. Remove it before continuing.",
}


@dataclass(frozen=True)
class Finding:
    kind: str
    where: str
    advice: str


def classify_column(name: str, sample_values: list[str] | None = None) -> list[str]:
    """Return the sensitive kinds a column appears to hold, from its name and sample values."""
    kinds: list[str] = []
    lowered = name.lower()
    for kind, pattern in NAME_RULES.items():
        if re.search(pattern, lowered):
            kinds.append(kind)
    for value in sample_values or []:
        for kind, pattern in VALUE_RULES.items():
            if kind not in kinds and pattern.search(str(value)):
                kinds.append(kind)
    return kinds


def scan_text(text: str) -> list[Finding]:
    """Find sensitive values inside free text, such as a question a new hire is about to send."""
    findings: list[Finding] = []
    for kind, pattern in VALUE_RULES.items():
        if pattern.search(text):
            findings.append(Finding(kind=kind, where="your message", advice=ADVICE[kind]))
    return findings


def redact(text: str) -> str:
    """Replace sensitive values in text with a labeled placeholder."""
    cleaned = text
    for kind, pattern in VALUE_RULES.items():
        cleaned = pattern.sub(f"[{kind.upper()} REMOVED]", cleaned)
    return cleaned
