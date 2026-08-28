"""Secret Redaction and Credential Sanitizer for Central Brain Ingestion."""

import re
from typing import List, Pattern, Tuple

SECRET_PATTERNS: List[Tuple[str, Pattern]] = [
    # 1. OpenAI API Keys (legacy sk-... and project-scoped sk-proj-...)
    (
        "OpenAI API Key",
        re.compile(r"\bsk-(?:proj-)?[a-zA-Z0-9_-]{20,}\b"),
    ),
    # 2. Anthropic API Keys
    (
        "Anthropic API Key",
        re.compile(r"\bsk-ant-[a-zA-Z0-9_-]{20,}\b"),
    ),
    # 3. Google Gemini / AI Studio API Keys
    (
        "Google AI Key",
        re.compile(r"\bAIzaSy[a-zA-Z0-9_-]{33}\b"),
    ),
    # 4. GitHub Personal Access Tokens (Classic & Fine-Grained)
    (
        "GitHub PAT",
        re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36}\b"),
    ),
    (
        "GitHub Fine-Grained PAT",
        re.compile(r"\bgithub_pat_[a-zA-Z0-9_]{50,}\b"),
    ),
    # 5. Generic Bearer Authentication Headers
    (
        "Bearer Token",
        re.compile(r"\bBearer\s+[a-zA-Z0-9_\-\.]{25,}\b", re.IGNORECASE),
    ),
    # 6. Generic Password / API Key Assignments in Code/Configs
    (
        "Secret Key Assignment",
        re.compile(
            r"""(?i)\b(?:api[_\s-]?key|secret[_\s-]?key|auth[_\s-]?token|password)\s*[:=]\s*['"]([^'"]{8,})['"]"""
        ),
    ),
]


def sanitize_text(text: str) -> Tuple[str, int]:
    """Scrub sensitive credentials, API keys, and auth tokens from text.

    Returns:
        (sanitized_text, num_redactions)
    """
    if not text:
        return "", 0

    sanitized = text
    total_redactions = 0

    for name, pattern in SECRET_PATTERNS:
        if name == "Secret Key Assignment":
            # For key assignment, preserve the key name and redact the value
            def _replace_assignment(m):
                full = m.group(0)
                val = m.group(1)
                return full.replace(val, "[REDACTED_SECRET]")

            matches = list(pattern.finditer(sanitized))
            if matches:
                total_redactions += len(matches)
                sanitized = pattern.sub(_replace_assignment, sanitized)
        elif name == "Bearer Token":
            matches = list(pattern.finditer(sanitized))
            if matches:
                total_redactions += len(matches)
                sanitized = pattern.sub("Bearer [REDACTED_AUTH_TOKEN]", sanitized)
        else:
            matches = list(pattern.finditer(sanitized))
            if matches:
                total_redactions += len(matches)
                sanitized = pattern.sub("[REDACTED_API_KEY]", sanitized)

    return sanitized, total_redactions
