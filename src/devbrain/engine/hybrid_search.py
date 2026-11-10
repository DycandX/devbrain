"""Hybrid search engine combining FastEmbed dense vectors and Rank-BM25 sparse search."""

from pathlib import Path
import threading
from typing import Callable, Dict, List, Literal, Optional, Tuple
import numpy as np

from devbrain.core.config import BrainConfig, load_config
from devbrain.core.constants import (
    CONFIG_FILENAME,
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_IGNORED_PATTERNS,
    EMBEDDING_MODEL_MIN_SIMILARITY,
)
from devbrain.engine.bm25 import BM25Engine
from devbrain.engine.chunker import chunk_document
from devbrain.engine.embeddings import EmbeddingEngine
from devbrain.engine.models import DocumentChunk, SearchResult
from devbrain.engine.parser import parse_markdown_file
from devbrain.engine.storage import BrainStorage


# Reciprocal Rank Fusion constant from Cormack et al. (2009); 60 is the usual default.
RRF_K = 60
# Share of distinct query terms a chunk must contain to count as a keyword candidate.
DEFAULT_MIN_KEYWORD_COVERAGE = 0.5


def _reciprocal_rank_fusion(rankers: List[Tuple[np.ndarray, np.ndarray]]) -> np.ndarray:
    """Fuse several (scores, eligible_mask) rankings into one score per chunk in [0, 1].

    Each ranker contributes 1 / (RRF_K + rank) for the chunks it considers eligible.
    Only rank positions are used, so rankers with different score scales combine
    fairly. A chunk ranked first by every ranker scores 1.0; a chunk no ranker
    considers eligible scores 0.0.
    """
    num_chunks = len(rankers[0][0])
    fused = np.zeros(num_chunks, dtype=np.float64)
    for scores, eligible in rankers:
        candidates = np.flatnonzero(eligible)
        if candidates.size == 0:
            continue
        order = candidates[np.argsort(-scores[candidates], kind="stable")]
        fused[order] += 1.0 / (RRF_K + np.arange(1, order.size + 1))
    return (fused * (RRF_K + 1) / len(rankers)).astype(np.float32)


class HybridEngine:
    """Core orchestrator for document indexing, embeddings, BM25, and federated hybrid search."""

    def __init__(
        self,
        vault_path: Path,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
        ignored_patterns: Optional[List[str]] = None,
        linked_vaults: Optional[Dict[str, Path]] = None,
        min_dense_similarity: Optional[float] = None,
        min_keyword_coverage: float = DEFAULT_MIN_KEYWORD_COVERAGE,
    ):
        self.vault_path = vault_path.resolve()
        self.embedding_model = embedding_model
        # Cosine floor for a chunk to count as a semantic candidate; model dependent.
        self.min_dense_similarity = (
            min_dense_similarity
            if min_dense_similarity is not None
            else EMBEDDING_MODEL_MIN_SIMILARITY.get(embedding_model, 0.0)
        )
        self.min_keyword_coverage = min_keyword_coverage
        self.ignored_patterns = ignored_patterns or list(DEFAULT_IGNORED_PATTERNS)
        self.linked_vaults: Dict[str, Path] = linked_vaults or {}
        self.storage = BrainStorage(self.vault_path)
        self.embedder = EmbeddingEngine(model_name=embedding_model)
        self.bm25 = BM25Engine()

        self.chunks: List[DocumentChunk] = []
        self.vectors: np.ndarray = np.array([], dtype=np.float32).reshape(0, 0)
        self.doc_mtimes: Dict[str, float] = {}
        self._is_initialized = False
        # The MCP server and the vault watcher share one engine across threads.
        self._lock = threading.RLock()

    @classmethod
    def from_config(cls, vault_path: Path, config: Optional[BrainConfig] = None) -> "HybridEngine":
        """Build an engine from the vault's .brainrc.json (or the given config).

        Falls back to defaults when the vault has no configuration file.
        """
        vault_path = Path(vault_path).resolve()
        if config is None and (vault_path / CONFIG_FILENAME).is_file():
            config = load_config(vault_path)
        if config is None:
            return cls(vault_path=vault_path)
        return cls(
            vault_path=vault_path,
            embedding_model=config.embedding_model,
            ignored_patterns=config.ignored_paths,
            linked_vaults=config.resolve_linked_vaults(),
        )

    def initialize(self):
        """Load stored index from disk and build BM25 in-memory structure."""
        if self._is_initialized:
            return

        self.chunks, self.vectors, self.doc_mtimes = self.storage.load(self.embedding_model)
        if self.chunks:
            self.bm25.build_index([c.content for c in self.chunks])
        self._is_initialized = True

    def is_ignored(self, path: Path, base_dir: Path) -> bool:
        """Check if a file or directory matches ignore rules."""
        try:
            rel = path.relative_to(base_dir).as_posix()
        except ValueError:
            rel = path.name

        for part in path.parts:
            if part.startswith(".brain_data") or part == ".obsidian" or part == ".git" or part == "Linked_Vaults":
                return True
        for pattern in self.ignored_patterns:
            if pattern.startswith("*.") and path.name.endswith(pattern[1:]):
                return True
            if pattern in rel or pattern in path.name:
                return True
        return False

    def get_vault_markdown_files(self) -> Dict[str, Path]:
        """Discover all non-ignored Markdown files across Central Vault and Linked Vaults.

        Returns mapping of unique doc_id -> absolute file Path.
        """
        doc_map: Dict[str, Path] = {}

        # 1. Central Vault files
        for file_path in self.vault_path.rglob("*.md"):
            if not self.is_ignored(file_path, self.vault_path):
                rel_id = file_path.relative_to(self.vault_path).as_posix()
                doc_map[rel_id] = file_path

        # 2. Linked External Vaults
        for alias, linked_path in self.linked_vaults.items():
            if not linked_path.is_dir():
                continue
            for file_path in linked_path.rglob("*.md"):
                if not self.is_ignored(file_path, linked_path):
                    rel_id = f"linked:{alias}:{file_path.relative_to(linked_path).as_posix()}"
                    doc_map[rel_id] = file_path

        return doc_map

    def index_vault(
        self,
        force_reindex: bool = False,
        on_progress: Optional[Callable[[str, int, int], None]] = None,
    ) -> Dict[str, int]:
        """Index all Central Vault and Linked Vault files incrementally or from scratch."""
        with self._lock:
            return self._index_vault(force_reindex, on_progress)

    def _index_vault(
        self,
        force_reindex: bool,
        on_progress: Optional[Callable[[str, int, int], None]],
    ) -> Dict[str, int]:
        self.initialize()

        if force_reindex:
            self.storage.clear()
            self.chunks = []
            self.vectors = np.array([], dtype=np.float32).reshape(0, 0)
            self.doc_mtimes = {}

        current_docs = self.get_vault_markdown_files()

        # 1. Identify deleted documents
        existing_doc_ids = set(self.doc_mtimes.keys())
        deleted_doc_ids = existing_doc_ids - set(current_docs.keys())

        # 2. Identify new or modified files
        files_to_process: List[tuple[str, Path]] = []
        for doc_id, full_path in current_docs.items():
            curr_mtime = full_path.stat().st_mtime
            prev_mtime = self.doc_mtimes.get(doc_id)
            if prev_mtime is None or curr_mtime > prev_mtime:
                files_to_process.append((doc_id, full_path))

        total_to_process = len(files_to_process)
        if not files_to_process and not deleted_doc_ids:
            return {"processed": 0, "deleted": 0, "total_chunks": len(self.chunks)}

        # Filter out deleted/modified chunks from existing lists
        doc_ids_to_remove = deleted_doc_ids.union({doc_id for doc_id, _ in files_to_process})

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
        for idx, (doc_id, file_path) in enumerate(files_to_process):
            if on_progress:
                on_progress(file_path.name, idx + 1, total_to_process)

            if doc_id.startswith("linked:"):
                # Linked external doc
                parts = doc_id.split(":", 2)
                alias = parts[1]
                base_dir = self.linked_vaults[alias]
                doc = parse_markdown_file(file_path, base_dir)
                doc.doc_id = doc_id
                doc.tags.append(f"vault:{alias}")
            else:
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
        self.storage.save(self.chunks, self.vectors, self.doc_mtimes, self.embedding_model)

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
        one_per_note: bool = False,
    ) -> List[SearchResult]:
        """Perform semantic, keyword, or federated hybrid search across indexed chunks.

        With one_per_note, only the best-ranked chunk of each note is returned, so
        a long note cannot fill every result slot.
        """
        with self._lock:
            return self._search(query, limit, mode, scope, one_per_note)

    def _search(
        self,
        query: str,
        limit: int,
        mode: Literal["hybrid", "dense", "bm25"],
        scope: str,
        one_per_note: bool,
    ) -> List[SearchResult]:
        self.initialize()

        if not self.chunks or not query.strip():
            return []

        num_chunks = len(self.chunks)

        # 1. Dense: raw cosine similarity. Chunks below the floor are not candidates.
        dense_scores = np.zeros(num_chunks, dtype=np.float32)
        dense_ok = np.zeros(num_chunks, dtype=bool)
        if mode in ("hybrid", "dense") and self.vectors.size > 0:
            query_vec = self.embedder.embed_query(query)
            dense_scores = self.embedder.cosine_similarity_matrix(query_vec, self.vectors)
            dense_ok = dense_scores >= self.min_dense_similarity

        # 2. Keyword: BM25 normalized to the best match. In hybrid mode a chunk must
        #    also contain a minimum share of the query terms, so one common word
        #    is not enough to surface it.
        bm25_scores = np.zeros(num_chunks, dtype=np.float32)
        bm25_ok = np.zeros(num_chunks, dtype=bool)
        if mode in ("hybrid", "bm25"):
            bm25_scores = self.bm25.search(query)
            bm25_ok = bm25_scores > 0
            if mode == "hybrid":
                bm25_ok &= self.bm25.coverage(query) >= self.min_keyword_coverage

        # 3. Fuse
        if mode == "dense":
            final_scores = np.where(dense_ok, np.clip(dense_scores, 0.0, 1.0), 0.0)
        elif mode == "bm25":
            final_scores = bm25_scores
        else:
            final_scores = _reciprocal_rank_fusion([(dense_scores, dense_ok), (bm25_scores, bm25_ok)])

        # 4. Scope Filtering & Ranking
        scored_indices = np.argsort(-final_scores)
        results: List[SearchResult] = []
        seen_docs: set = set()
        scope_clean = scope.strip().lower()

        for idx in scored_indices:
            score = float(final_scores[idx])
            if score <= 0.0:
                break

            chunk = self.chunks[idx]

            # Scope filtering
            if scope_clean != "all":
                if scope_clean in ("central", "local"):
                    if chunk.doc_id.startswith("linked:"):
                        continue
                elif scope_clean in self.linked_vaults:
                    linked_prefix = f"linked:{scope_clean}:"
                    if not chunk.doc_id.startswith(linked_prefix):
                        continue
                else:
                    # General tag or keyword scope filter
                    in_tags = scope_clean in [t.lower() for t in chunk.tags]
                    in_path = scope_clean in chunk.file_path.lower()
                    if not (in_tags or in_path):
                        continue

            if one_per_note:
                if chunk.doc_id in seen_docs:
                    continue
                seen_docs.add(chunk.doc_id)

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
