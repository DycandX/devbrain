"""Tests for Markdown frontmatter, tags, wikilinks, and title parsing."""

from pathlib import Path
from devbrain.engine.parser import (
    extract_tags,
    extract_title,
    extract_wikilinks,
    parse_frontmatter,
    parse_markdown_file,
)

SAMPLE_MD = """---
title: "Custom Title From YAML"
tags: [backend, fastapi, auth]
category: guide
---

# Heading 1 Title

This is a paragraph discussing [[ADR-001]] and [[10_Projects/auth_system|Auth System]].
Here is an inline tag: #security/jwt and another #performance.

```python
# This is a comment in code, not a tag #should_be_ignored
def foo():
    pass
```
"""


def test_parse_frontmatter():
    fm, body = parse_frontmatter(SAMPLE_MD)
    assert fm.get("title") == "Custom Title From YAML"
    assert fm.get("tags") == ["backend", "fastapi", "auth"]
    assert "# Heading 1 Title" in body


def test_extract_wikilinks():
    wikilinks = extract_wikilinks(SAMPLE_MD)
    assert "ADR-001" in wikilinks
    assert "10_Projects/auth_system" in wikilinks


def test_extract_tags():
    fm, body = parse_frontmatter(SAMPLE_MD)
    tags = extract_tags(fm, body)
    assert "backend" in tags
    assert "fastapi" in tags
    assert "security/jwt" in tags
    assert "performance" in tags
    assert "should_be_ignored" not in tags


def test_extract_title():
    fm, body = parse_frontmatter(SAMPLE_MD)
    title = extract_title(fm, body, Path("test.md"))
    assert title == "Custom Title From YAML"

    # Test title fallback to first heading
    title_fallback = extract_title({}, body, Path("test.md"))
    assert title_fallback == "Heading 1 Title"


def test_parse_markdown_file(tmp_path: Path):
    vault = tmp_path / "Vault"
    vault.mkdir()
    note = vault / "10_Projects" / "test_note.md"
    note.parent.mkdir()
    note.write_text(SAMPLE_MD, encoding="utf-8")

    doc = parse_markdown_file(note, vault)
    assert doc.doc_id == "10_Projects/test_note.md"
    assert doc.title == "Custom Title From YAML"
    assert len(doc.tags) >= 4
    assert len(doc.wikilinks) == 2
