"""Tests for FastEmbed, Rank-BM25, storage, and HybridEngine integration."""

from pathlib import Path
from devbrain.core.scaffolder import scaffold_vault
from devbrain.engine.hybrid_search import HybridEngine


def test_hybrid_engine_indexing_and_search(tmp_path: Path):
    vault = tmp_path / "TestSearchVault"
    scaffold_vault(vault, is_new=True)

    engine = HybridEngine(vault_path=vault)

    # 1. Test Indexing
    stats = engine.index_vault(force_reindex=True)
    assert stats["processed"] > 0
    assert stats["total_chunks"] > 0
    assert len(engine.chunks) == stats["total_chunks"]
    assert engine.vectors.shape[0] == stats["total_chunks"]

    # 2. Test Exact Keyword Match (BM25)
    bm25_results = engine.search(query="ADR-001", mode="bm25", limit=3)
    assert len(bm25_results) > 0
    assert any("ADR-001" in r.title or "ADR-001" in r.snippet for r in bm25_results)

    # 3. Test Semantic Hybrid Match
    hybrid_results = engine.search(query="software architecture and modular system design", mode="hybrid", limit=3)
    assert len(hybrid_results) > 0
    assert hybrid_results[0].score > 0.0

    # 4. Test Persistence and Reload
    new_engine = HybridEngine(vault_path=vault)
    new_engine.initialize()
    assert len(new_engine.chunks) == len(engine.chunks)
    assert new_engine.vectors.shape == engine.vectors.shape
