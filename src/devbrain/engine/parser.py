"""Markdown file parser for extracting YAML frontmatter, wikilinks, tags, and document title."""

import re
from pathlib import Path
from typing import Any, Dict, List, Tuple
import yaml

from devbrain.engine.models import Document

# Regex patterns for Frontmatter, Wikilinks, and Tags
FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
WIKILINK_PATTERN = re.compile(r"\[\[([^\|\]]+)(?:\|([^\]]+))?\]\]")
INLINE_TAG_PATTERN = re.compile(r"(?<!\w)#([a-zA-Z0-9_\-/]+)")
CODE_BLOCK_PATTERN = re.compile(r"```[\s\S]*?```|`[^`]+`")


def parse_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    """Extract YAML frontmatter and remaining body from markdown text."""
    match = FRONTMATTER_PATTERN.match(text)
    if not match:
        return {}, text

    raw_yaml = match.group(1)
    body = text[match.end():]
    try:
        data = yaml.safe_load(raw_yaml)
        if isinstance(data, dict):
            return data, body
        return {}, body
    except Exception:
        return {}, body


def extract_wikilinks(text: str) -> List[str]:
    """Extract all [[Wikilinks]] target file paths/names from markdown text."""
    matches = WIKILINK_PATTERN.findall(text)
    targets: List[str] = []
    for match in matches:
        target = match[0].strip()
        if target and target not in targets:
            targets.append(target)
    return targets


def extract_tags(frontmatter: Dict[str, Any], body: str) -> List[str]:
    """Extract combined tags from frontmatter and inline #hashtags (excluding code blocks)."""
    tags: set[str] = set()

    # 1. Frontmatter tags
    fm_tags = frontmatter.get("tags") or frontmatter.get("tag")
    if isinstance(fm_tags, list):
        for t in fm_tags:
            if isinstance(t, str):
                tags.add(t.strip().lstrip("#"))
    elif isinstance(fm_tags, str):
        for t in fm_tags.split(","):
            if t.strip():
                tags.add(t.strip().lstrip("#"))

    # 2. Inline hashtags in body (strip code blocks first to prevent false matches)
    cleaned_body = CODE_BLOCK_PATTERN.sub("", body)
    for line in cleaned_body.splitlines():
        # Skip markdown headings (e.g. # Heading)
        if line.strip().startswith("#") and not line.strip().startswith("##"):
            # Check if this is a heading or tag
            rest = line.strip()[1:]
            if rest.startswith(" "):
                continue
        inline_matches = INLINE_TAG_PATTERN.findall(line)
        for t in inline_matches:
            tags.add(t.strip())

    return sorted(list(tags))


def extract_title(frontmatter: Dict[str, Any], body: str, file_path: Path) -> str:
    """Extract document title from frontmatter, first # Heading, or filename."""
    if "title" in frontmatter and isinstance(frontmatter["title"], str) and frontmatter["title"].strip():
        return frontmatter["title"].strip()

    for line in body.splitlines():
        trimmed = line.strip()
        if trimmed.startswith("# ") and not trimmed.startswith("## "):
            heading_title = trimmed[2:].strip()
            if heading_title:
                return heading_title

    return file_path.stem.replace("_", " ").replace("-", " ").title()


def parse_markdown_file(file_path: Path, vault_root: Path) -> Document:
    """Parse a Markdown file from disk into a structured Document model."""
    rel_path = file_path.resolve().relative_to(vault_root.resolve()).as_posix()
    mtime = file_path.stat().st_mtime if file_path.exists() else 0.0

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    frontmatter, body = parse_frontmatter(content)
    tags = extract_tags(frontmatter, body)
    wikilinks = extract_wikilinks(content)
    title = extract_title(frontmatter, body, file_path)

    return Document(
        doc_id=rel_path,
        file_path=rel_path,
        title=title,
        frontmatter=frontmatter,
        tags=tags,
        wikilinks=wikilinks,
        raw_content=body,
        updated_at=mtime,
    )
