"""Local embedded storage for persistent vectors and document chunks in .brain_data/."""

import json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

from devbrain.core.constants import BRAIN_DATA_DIR
from devbrain.engine.models import DocumentChunk


class BrainStorage:
    """Local file-based storage managing vector matrices and chunk metadata."""

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path.resolve()
        self.data_dir = self.vault_path / BRAIN_DATA_DIR
        self.metadata_file = self.data_dir / "index_metadata.json"
        self.vectors_file = self.data_dir / "vectors.npy"

    def _ensure_dir(self):
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> Tuple[List[DocumentChunk], np.ndarray, Dict[str, float]]:
        """Load stored chunks, vector matrix, and file modification timestamps."""
        if not self.metadata_file.is_file():
            return [], np.array([], dtype=np.float32).reshape(0, 0), {}

        try:
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            raw_chunks = data.get("chunks", [])
            chunks = [DocumentChunk(**c) for c in raw_chunks]
            doc_mtimes = data.get("doc_mtimes", {})

            if self.vectors_file.is_file() and len(chunks) > 0:
                vectors = np.load(self.vectors_file)
                if vectors.shape[0] != len(chunks):
                    # Inconsistency: reset vectors
                    vectors = np.array([], dtype=np.float32).reshape(0, 0)
            else:
                vectors = np.array([], dtype=np.float32).reshape(0, 0)

            return chunks, vectors, doc_mtimes
        except Exception:
            return [], np.array([], dtype=np.float32).reshape(0, 0), {}

    def save(
        self,
        chunks: List[DocumentChunk],
        vectors: np.ndarray,
        doc_mtimes: Dict[str, float],
    ):
        """Atomically persist chunks, embeddings matrix, and mtimes to disk."""
        self._ensure_dir()

        payload = {
            "version": "1.0",
            "total_chunks": len(chunks),
            "doc_mtimes": doc_mtimes,
            "chunks": [c.model_dump() for c in chunks],
        }

        # Save metadata JSON
        temp_meta = self.metadata_file.with_suffix(".tmp")
        with open(temp_meta, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        temp_meta.replace(self.metadata_file)

        # Save vectors .npy
        if vectors.size > 0:
            temp_vec = self.vectors_file.with_suffix(".tmp.npy")
            np.save(temp_vec, vectors)
            temp_vec.replace(self.vectors_file)
        elif self.vectors_file.exists():
            self.vectors_file.unlink()

    def clear(self):
        """Remove all persistent index files."""
        if self.metadata_file.exists():
            self.metadata_file.unlink()
        if self.vectors_file.exists():
            self.vectors_file.unlink()
