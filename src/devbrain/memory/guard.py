"""Content checks for anything an agent asks devbrain to remember.

Memories are shown to every connected agent at the start of its work, so one
poisoned entry written by one agent can steer all of them. Writes that look
like instructions to an agent, carry credentials, or hide text are refused.
"""

import re
from typing import List, Tuple
import unicodedata

from devbrain.harvester.sanitizer import sanitize_text

# Text addressed to an agent rather than a fact about the world.
_INSTRUCTION_PATTERNS = [
    r"\b(ignore|disregard|forget|override)\b[^.\n]{0,40}\b(previous|prior|above|earlier|all|any|system)\b[^.\n]{0,20}\b(instruction|prompt|rule|directive|message)s?\b",
    r"\b(abaikan|lupakan)\b[^.\n]{0,40}\b(instruksi|perintah|aturan)\b",
    r"\byou are now\b",
    r"\bnew (system )?instructions?\s*:",
    r"\bsystem prompt\b",
    r"\b(do not|don't|never) (tell|inform|mention (this )?to|reveal (this )?to) the user\b",
    r"\bjangan (beri ?tahu|kasih tahu|bilang)\b[^.\n]{0,20}\b(user|pengguna)\b",
    r"</?\s*(system|assistant|instructions?)\s*>",
    r"\[/?INST\]",
    r"<\|im_(start|end)\|>",
]

# Commands that download a script and run it.
_DOWNLOAD_AND_RUN_PATTERNS = [
    r"\b(curl|wget)\b[^\n|]{0,200}\|\s*(ba|z)?sh\b",
    r"\b(iwr|irm|invoke-webrequest|invoke-restmethod)\b[^\n]{0,200}\b(iex|invoke-expression)\b",
]

# Keys and payloads that grant access or move data off the machine.
_EXFILTRATION_PATTERNS = [
    r"\bauthorized_keys\b",
    r"\bssh-(rsa|ed25519|dss) AAAA",
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    r"\b(send|post|upload|forward|exfiltrate|kirim)\b[^.\n]{0,60}\b(api[ _-]?key|token|password|credential|secret|kata sandi)s?\b",
    r"https?://[^\s]*[?&](key|token|secret|password|apikey)=",
]

_INSTRUCTION_RE = [re.compile(p, re.IGNORECASE) for p in _INSTRUCTION_PATTERNS]
_EXFILTRATION_RE = [re.compile(p, re.IGNORECASE) for p in _EXFILTRATION_PATTERNS]
_DOWNLOAD_AND_RUN_RE = [re.compile(p, re.IGNORECASE) for p in _DOWNLOAD_AND_RUN_PATTERNS]


class MemoryRejected(ValueError):
    """A memory write refused by the content guard."""

    def __init__(self, reasons: List[str]):
        self.reasons = reasons
        super().__init__("Refused: " + "; ".join(reasons))


def _hidden_characters(text: str) -> List[str]:
    """Invisible, bidirectional-override, and tag characters that can hide instructions."""
    found = []
    for ch in text:
        code = ord(ch)
        if unicodedata.category(ch) == "Cf" or 0xE0000 <= code <= 0xE007F:
            found.append(f"U+{code:04X}")
    return sorted(set(found))


def check_memory_content(text: str) -> List[str]:
    """Reasons to refuse this text as a memory; empty when it is acceptable."""
    reasons = []

    hidden = _hidden_characters(text)
    if hidden:
        reasons.append(f"contains hidden Unicode characters ({', '.join(hidden[:5])})")

    if any(p.search(text) for p in _INSTRUCTION_RE):
        reasons.append("reads as an instruction to an agent, not a fact")

    if any(p.search(text) for p in [*_DOWNLOAD_AND_RUN_RE, *_EXFILTRATION_RE]):
        reasons.append("contains a command or key that runs code or sends data elsewhere")

    _, redactions = sanitize_text(text)
    if redactions:
        reasons.append("contains a credential or API key")

    return reasons


def check_skill_content(text: str) -> Tuple[List[str], List[str]]:
    """(refusals, warnings) for a skill's text.

    Skills are procedures, so imperative wording is expected. Refused: the same
    as for memories, except download-and-run commands, which can be a genuine
    install step and are reported to the reviewer as a warning instead.
    """
    refusals = []
    hidden = _hidden_characters(text)
    if hidden:
        refusals.append(f"contains hidden Unicode characters ({', '.join(hidden[:5])})")
    if any(p.search(text) for p in _INSTRUCTION_RE):
        refusals.append("tries to override the agent's instructions")
    if any(p.search(text) for p in _EXFILTRATION_RE):
        refusals.append("contains a key or sends data elsewhere")
    _, redactions = sanitize_text(text)
    if redactions:
        refusals.append("contains a credential or API key")

    warnings = []
    if any(p.search(text) for p in _DOWNLOAD_AND_RUN_RE):
        warnings.append("downloads and runs a script from the internet")
    return refusals, warnings


def guard_memory_content(text: str) -> None:
    """Raise MemoryRejected when the text must not be stored."""
    reasons = check_memory_content(text)
    if reasons:
        raise MemoryRejected(reasons)
