"""Sparse lexical search indexer using Rank-BM25."""

import re
from typing import List
import numpy as np


def tokenize_text(text: str) -> List[str]:
    """Tokenize markdown/code text into normalized lowercase tokens."""
    # Split on whitespace and non-alphanumeric punctuation, preserving identifiers
    tokens = re.findall(r"[a-zA-Z0-9_\-\.]+", text.lower())
    return [t for t in tokens if len(t) > 1]


class BM25Engine:
    """In-memory BM25 index for sparse keyword search."""

    def __init__(self):
        self.corpus_tokens: List[List[str]] = []
        self._bm25 = None

    def build_index(self, corpus_texts: List[str]):
        """Build BM25Okapi index from a list of chunk texts."""
        if not corpus_texts:
            self.corpus_tokens = []
            self._bm25 = None
            return

        from rank_bm25 import BM25Okapi

        self.corpus_tokens = [tokenize_text(text) for text in corpus_texts]
        self._bm25 = BM25Okapi(self.corpus_tokens)

    def search(self, query: str) -> np.ndarray:
        """Compute normalized BM25 relevance scores for all documents in index."""
        if self._bm25 is None or not self.corpus_tokens:
            return np.array([], dtype=np.float32)

        query_tokens = tokenize_text(query)
        if not query_tokens:
            return np.zeros(len(self.corpus_tokens), dtype=np.float32)

        raw_scores = np.array(self._bm25.get_scores(query_tokens), dtype=np.float32)
        max_score = np.max(raw_scores)

        if max_score > 0:
            # Normalize to [0.0, 1.0] range
            return raw_scores / max_score
        return np.zeros(len(self.corpus_tokens), dtype=np.float32)
