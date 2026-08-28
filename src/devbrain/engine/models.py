"""Data models for documents, chunks, and search results."""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class Document(BaseModel):
    """Represents a single parsed Markdown file in the Obsidian vault."""

    doc_id: str = Field(description="Unique identifier (relative file path)")
    file_path: str = Field(description="Relative path from vault root")
    title: str = Field(description="Extracted document title")
    frontmatter: Dict[str, Any] = Field(default_factory=dict, description="Parsed YAML frontmatter")
    tags: List[str] = Field(default_factory=list, description="Extracted #tags and frontmatter tags")
    wikilinks: List[str] = Field(default_factory=list, description="Extracted [[Wikilinks]] targets")
    raw_content: str = Field(description="Raw markdown body content without frontmatter")
    updated_at: float = Field(default=0.0, description="File modification timestamp (mtime)")


class DocumentChunk(BaseModel):
    """Represents a hierarchical, header-scoped text chunk for embedding & search."""

    chunk_id: str = Field(description="Unique chunk ID (doc_id#header#index)")
    doc_id: str = Field(description="Parent document ID")
    file_path: str = Field(description="Relative path from vault root")
    title: str = Field(description="Parent document title")
    header_path: str = Field(default="", description="Breadcrumb hierarchy e.g. 'Overview > Architecture'")
    content: str = Field(description="Chunk body text including contextual breadcrumb header")
    tags: List[str] = Field(default_factory=list, description="Inherited tags")
    chunk_index: int = Field(default=0, description="Sequential index within document")


class SearchResult(BaseModel):
    """Represents a ranked search match returned by the Hybrid Search Engine."""

    chunk_id: str
    doc_id: str
    file_path: str
    title: str
    header_path: str
    snippet: str
    score: float = Field(description="Normalized relevance score between 0.0 and 1.0")
    dense_score: Optional[float] = None
    bm25_score: Optional[float] = None
    match_type: Literal["dense", "bm25", "hybrid"] = "hybrid"
    tags: List[str] = Field(default_factory=list)
