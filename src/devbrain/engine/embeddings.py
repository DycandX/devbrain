"""Embedding service wrapping FastEmbed CPU ONNX models."""

from typing import List, Optional
import numpy as np


class EmbeddingEngine:
    """CPU-optimized local embedding generator using FastEmbed ONNX."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5", threads: int = 1):
        self.model_name = model_name
        self.threads = threads
        self._model = None

    def _get_model(self):
        """Lazy load FastEmbed model on first use to maintain instant CLI startup."""
        if self._model is None:
            try:
                from fastembed import TextEmbedding
                self._model = TextEmbedding(model_name=self.model_name, threads=self.threads)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to initialize FastEmbed model '{self.model_name}': {e}\n"
                    "Ensure 'fastembed' is installed in your Python environment."
                )
        return self._model

    def embed_documents(self, texts: List[str], batch_size: int = 8) -> List[List[float]]:
        """Compute dense vector embeddings for a list of document strings."""
        if not texts:
            return []
        model = self._get_model()
        # FastEmbed returns an iterator of numpy ndarrays
        embeddings_iter = model.embed(texts, batch_size=batch_size)
        return [list(vec.tolist()) for vec in embeddings_iter]

    def embed_query(self, query: str) -> List[float]:
        """Compute dense vector embedding for a single query string."""
        model = self._get_model()
        embeddings_iter = model.query_embed(query)
        first_vec = next(embeddings_iter)
        return list(first_vec.tolist())

    @staticmethod
    def cosine_similarity_matrix(query_vec: List[float], matrix: np.ndarray) -> np.ndarray:
        """Compute cosine similarity between 1 query vector and an N-dimensional matrix."""
        if matrix.shape[0] == 0:
            return np.array([], dtype=np.float32)

        q = np.array(query_vec, dtype=np.float32)
        q_norm = np.linalg.norm(q)
        if q_norm == 0:
            return np.zeros(matrix.shape[0], dtype=np.float32)

        m_norms = np.linalg.norm(matrix, axis=1)
        m_norms[m_norms == 0] = 1e-10

        dots = np.dot(matrix, q)
        similarities = dots / (m_norms * q_norm)
        # Normalize from [-1, 1] to [0, 1]
        return np.clip((similarities + 1.0) / 2.0, 0.0, 1.0)
