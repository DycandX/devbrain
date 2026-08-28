"""Tests for header-aware markdown chunking and breadcrumb hierarchy."""

from devbrain.engine.chunker import chunk_document
from devbrain.engine.models import Document

COMPLEX_MD = """# Architecture Overview

This is the top overview.

## Database Layer

Details about PostgreSQL and SQLite.

### Vector Search Engine

Details about Qdrant and FastEmbed.

## Security

Authentication via JWT.
"""


def test_chunk_document_hierarchy():
    doc = Document(
        doc_id="arch.md",
        file_path="arch.md",
        title="Architecture Overview",
        frontmatter={},
        tags=["architecture"],
        wikilinks=[],
        raw_content=COMPLEX_MD,
        updated_at=100.0,
    )

    chunks = chunk_document(doc)
    assert len(chunks) >= 4

    # Check vector search chunk breadcrumb
    vector_chunk = next(c for c in chunks if "Vector Search Engine" in c.content)
    assert "Database Layer > Vector Search Engine" in vector_chunk.header_path
    assert "[Architecture Overview] > Database Layer > Vector Search Engine" in vector_chunk.content


def test_chunk_document_long_text_subchunking():
    # Create long text exceeding max_chunk_chars
    long_para = "This is a detailed paragraph with extensive explanations. " * 40
    long_md = f"# Deep Dive\n\n## Section 1\n\n{long_para}\n\n{long_para}"

    doc = Document(
        doc_id="deep.md",
        file_path="deep.md",
        title="Deep Dive",
        frontmatter={},
        tags=[],
        wikilinks=[],
        raw_content=long_md,
        updated_at=100.0,
    )

    chunks = chunk_document(doc, max_chunk_chars=500)
    assert len(chunks) > 2
    for chunk in chunks:
        assert len(chunk.content) > 0
        assert chunk.doc_id == "deep.md"
