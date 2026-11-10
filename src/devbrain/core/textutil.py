"""Text helpers for keeping tool output within a predictable size."""

import re
from typing import Optional

# Rough conversion used for budgeting tool output: 1 token is about 4 characters.
CHARS_PER_TOKEN = 4


def truncate_to_budget(text: str, max_chars: int, hint: str = "") -> str:
    """Cut text at a line boundary near max_chars and say how much was left out.

    The hint tells the reader how to get the rest, e.g. which tool to call.
    """
    if max_chars <= 0 or len(text) <= max_chars:
        return text

    cut = text.rfind("\n", 0, max_chars)
    if cut < max_chars // 2:
        cut = max_chars
    omitted = len(text) - cut
    notice = f"\n\n[... {omitted:,} more characters omitted."
    notice += f" {hint}]" if hint else "]"
    return text[:cut].rstrip() + notice


def one_line(text: str, max_chars: int) -> str:
    """Collapse whitespace into a single line and shorten it."""
    flat = re.sub(r"\s+", " ", text).strip()
    return flat if len(flat) <= max_chars else flat[:max_chars].rstrip() + "..."


def extract_section(markdown: str, heading: str) -> Optional[str]:
    """Return the section under the first heading whose text contains `heading`.

    The section runs until the next heading of the same or a higher level.
    """
    wanted = heading.strip().lstrip("#").strip().lower()
    lines = markdown.splitlines()
    start = level = None
    for i, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if not match:
            continue
        if start is None:
            if wanted in match.group(2).lower():
                start, level = i, len(match.group(1))
        elif len(match.group(1)) <= level:
            return "\n".join(lines[start:i]).strip()
    return "\n".join(lines[start:]).strip() if start is not None else None


# Line starts that are structure or decoration rather than prose.
_NON_PROSE_PREFIXES = ("#", ">", "---", "===", "|", "[![", "![", "<", "- ", "* ", "+ ")


def first_prose_paragraph(markdown: str) -> str:
    """First paragraph of running text in a Markdown document.

    Skips headings, quotes, rules, tables, lists, badges, images, HTML, and
    fenced code, so a README that opens with badges still yields a sentence.
    Returns an empty string when the document has no prose.
    """
    lines: list[str] = []
    in_fence = False
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            if lines:
                break
            continue
        if in_fence:
            continue
        if not stripped or stripped.startswith(_NON_PROSE_PREFIXES) or re.match(r"^\d+[.)]\s", stripped):
            if lines:
                break
            continue
        lines.append(stripped)
    return " ".join(lines)
