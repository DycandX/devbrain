"""Hybrid search engine combining FastEmbed dense vectors and Rank-BM25 sparse search."""

from pathlib import Path
from typing import Callable, Dict, List, Literal, Optional
import numpy as np

from devbrain.core.constants import DEFAULT_IGNORED_PATTERNS
from devbrain.engine.bm25 import BM25Engine
from devbrain.engine.chunker import chunk_document
from devbrain.engine.embeddings import EmbeddingEngine
from devbrain.engine.models import DocumentChunk, SearchResult
from devbrain.engine.parser import parse_markdown_file
from devbrain.engine.storage import BrainStorage


class HybridEngine:
    """Core orchestrator for document indexing, embeddings, BM25, and hybrid search."""

    def __init__(
        self,
        vault_path: Path,
        embedding_model: str = "BAAI/bge-small-en-v1.5",
        ignored_patterns: Optional[List[str]] = None,
    ):
        self.vault_path = vault_path.resolve()
        self.ignored_patterns = ignored_patterns or list(DEFAULT_IGNORED_PATTERNS)
        self.storage = BrainStorage(self.vault_path)
        self.embedder = EmbeddingEngine(model_name=embedding_model)
        self.bm25 = BM25Engine()

        self.chunks: List[DocumentChunk] = []
        self.vectors: np.ndarray = np.array([], dtype=np.float32).reshape(0, 0)
        self.doc_mtimes: Dict[str, float] = {}
        self._is_initialized = False

    def initialize(self):
        """Load stored index from disk and build BM25 in-memory structure."""
        if self._is_initialized:
            return

        self.chunks, self.vectors, self.doc_mtimes = self.storage.load()
        if self.chunks:
            self.bm25.build_index([c.content for c in self.chunks])
        self._is_initialized = True

    def _is_ignored(self, path: Path) -> bool:
        """Check if a file or directory matches ignore rules."""
        rel = path.relative_to(self.vault_path).as_posix()
        for part in path.parts:
            if part.startswith(".brain_data") or part == ".obsidian" or part == ".git":
                return True
        for pattern in self.ignored_patterns:
            if pattern.startswith("*.") and path.name.endswith(pattern[1:]):
                return True
            if pattern in rel or pattern in path.name:
                return True
        return False

    def get_vault_markdown_files(self) -> List[Path]:
        """Discover all non-ignored Markdown files in the vault."""
        md_files: List[Path] = []
        for file_path in self.vault_path.rglob("*.md"):
            if not self._is_ignored(file_path):
                md_files.append(file_path)
        return md_files

    def index_vault(
        self,
        force_reindex: bool = False,
        on_progress: Optional[Callable[[str, int, int], None]] = None,
    ) -> Dict[str, int]:
        """Index all vault files incrementally or from scratch."""
        self.initialize()

        if force_reindex:
            self.storage.clear()
            self.chunks = []
            self.vectors = np.array([], dtype=np.float32).reshape(0, 0)
            self.doc_mtimes = {}

        current_files = self.get_vault_markdown_files()
        current_rel_paths = {
            f.relative_to(self.vault_path).as_posix(): f for f in current_files
        }

        # 1. Identify deleted documents
        existing_doc_ids = set(self.doc_mtimes.keys())
        deleted_doc_ids = existing_doc_ids - set(current_rel_paths.keys())

        # 2. Identify new or modified files
        files_to_process: List[Path] = []
        for rel_path, full_path in current_rel_paths.items():
            curr_mtime = full_path.stat().st_mtime
            prev_mtime = self.doc_mtimes.get(rel_path)
            if prev_mtime is None or curr_mtime > prev_mtime:
                files_to_process.append(full_path)

        total_to_process = len(files_to_process)
        if not files_to_process and not deleted_doc_ids:
            return {"processed": 0, "deleted": 0, "total_chunks": len(self.chunks)}

        # Filter out deleted/modified chunks from existing lists
        doc_ids_to_remove = deleted_doc_ids.union(
            {f.relative_to(self.vault_path).as_posix() for f in files_to_process}
        )

        if doc_ids_to_remove:
            keep_indices = [
                i for i, c in enumerate(self.chunks) if c.doc_id not in doc_ids_to_remove
            ]
            self.chunks = [self.chunks[i] for i in keep_indices]
            if self.vectors.size > 0 and len(keep_indices) > 0:
                self.vectors = self.vectors[keep_indices]
            else:
                self.vectors = np.array([], dtype=np.float32).reshape(0, 0)

            for doc_id in doc_ids_to_remove:
                self.doc_mtimes.pop(doc_id, None)

        # Process new/modified files
        new_chunks: List[DocumentChunk] = []
        for idx, file_path in enumerate(files_to_process):
            if on_progress:
                on_progress(file_path.name, idx + 1, total_to_process)

            doc = parse_markdown_file(file_path, self.vault_path)
            doc_chunks = chunk_document(doc)
            new_chunks.extend(doc_chunks)
            self.doc_mtimes[doc.doc_id] = doc.updated_at

        # Embed new chunks
        if new_chunks:
            chunk_texts = [c.content for c in new_chunks]
            new_embeddings_list = self.embedder.embed_documents(chunk_texts)
            new_vecs = np.array(new_embeddings_list, dtype=np.float32)

            self.chunks.extend(new_chunks)
            if self.vectors.size > 0:
                self.vectors = np.vstack([self.vectors, new_vecs])
            else:
                self.vectors = new_vecs

        # Rebuild BM25 & persist
        self.bm25.build_index([c.content for c in self.chunks])
        self.storage.save(self.chunks, self.vectors, self.doc_mtimes)

        return {
            "processed": len(files_to_process),
            "deleted": len(deleted_doc_ids),
            "total_chunks": len(self.chunks),
        }

    def search(
        self,
        query: str,
        limit: int = 5,
        mode: Literal["hybrid", "dense", "bm25"] = "hybrid",
        scope: str = "all",
    ) -> List[SearchResult]:
        """Perform semantic, keyword, or hybrid search across indexed chunks."""
        self.initialize()

        if not self.chunks or not query.strip():
            return []

        num_chunks = len(self.chunks)

        # 1. Compute Dense Scores
        dense_scores = np.zeros(num_chunks, dtype=np.float32)
        if mode in ("hybrid", "dense") and self.vectors.size > 0:
            query_vec = self.embedder.embed_query(query)
            dense_scores = self.embedder.cosine_similarity_matrix(query_vec, self.vectors)

        # 2. Compute BM25 Scores
        bm25_scores = np.zeros(num_chunks, dtype=np.float32)
        if mode in ("hybrid", "bm25"):
            bm25_scores = self.bm25.search(query)

        # 3. Fuse Scores
        if mode == "dense":
            final_scores = dense_scores
        elif mode == "bm25":
            final_scores = bm25_scores
        else:  # hybrid
            final_scores = (0.6 * dense_scores) + (0.4 * bm25_scores)

        # 4. Scope Filtering & Ranking
        scored_indices = np.argsort(-final_scores)
        results: List[SearchResult] = []

        for idx in scored_indices:
            score = float(final_scores[idx])
            if score <= 0.001:
                continue

            chunk = self.chunks[idx]

            # Scope filtering
            if scope != "all":
                # Match scope in tags or path
                in_tags = scope.lower() in [t.lower() for t in chunk.tags]
                in_path = scope.lower() in chunk.file_path.lower()
                if not (in_tags or in_path):
                    continue

            # Extract clean snippet without breadcrumb line
            lines = chunk.content.splitlines()
            snippet_body = "\n".join(lines[1:]).strip() if len(lines) > 1 else chunk.content
            snippet = snippet_body[:300] + ("..." if len(snippet_body) > 300 else "")

            results.append(
                SearchResult(
                    chunk_id=chunk.chunk_id,
                    doc_id=chunk.doc_id,
                    file_path=chunk.file_path,
                    title=chunk.title,
                    header_path=chunk.header_path,
                    snippet=snippet,
                    score=round(score, 4),
                    dense_score=round(float(dense_scores[idx]), 4) if mode != "bm25" else None,
                    bm25_score=round(float(bm25_scores[idx]), 4) if mode != "dense" else None,
                    match_type=mode,
                    tags=chunk.tags,
                )
            )

            if len(results) >= limit:
                break

        return results
