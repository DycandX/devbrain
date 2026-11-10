"""Tests for the v1.7 foundation work: rank fusion, model-aware index, Claude Code harvesting."""

import asyncio
import json
import os
from pathlib import Path

import numpy as np
import yaml

from devbrain.core.config import BrainConfig, save_config
from devbrain.core.constants import DIR_INBOX
from devbrain.core.scaffolder import scaffold_vault
from devbrain.engine.hybrid_search import HybridEngine, _reciprocal_rank_fusion
from devbrain.engine.models import DocumentChunk
from devbrain.engine.storage import BrainStorage
from devbrain.harvester.claude_code import parse_claude_transcript, render_claude_session
from devbrain.harvester.service import IngestionService
from devbrain.mcp_server.server import create_mcp_server
from devbrain.watcher.debounce import DebounceManager
from devbrain.watcher.vault_watcher import VaultEventHandler


def _write_note(vault: Path, rel: str, title: str, body: str) -> Path:
    path = vault / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {title}\n\n{body}\n", encoding="utf-8")
    return path


# --- Rank fusion -----------------------------------------------------------


def test_rrf_ranks_agreement_first_and_ignores_ineligible():
    dense = np.array([0.9, 0.8, 0.1, 0.7], dtype=np.float32)
    bm25 = np.array([1.0, 0.0, 0.0, 0.5], dtype=np.float32)
    dense_ok = np.array([True, True, False, True])
    bm25_ok = bm25 > 0

    fused = _reciprocal_rank_fusion([(dense, dense_ok), (bm25, bm25_ok)])

    assert fused[0] == 1.0  # first in both rankers
    assert fused[2] == 0.0  # eligible in neither
    assert fused[0] > fused[3] > fused[1] > fused[2]


def test_hybrid_search_abstains_on_unrelated_query(tmp_path: Path):
    vault = tmp_path / "vault"
    _write_note(vault, "20_Knowledge/docker.md", "Docker Multi-Stage Builds",
                "Copy only built artifacts into a slim runtime image to shrink the container.")
    _write_note(vault, "20_Knowledge/postgres.md", "Optimasi Query PostgreSQL",
                "Tambahkan indeks gabungan dan periksa rencana eksekusi dengan EXPLAIN ANALYZE.")

    engine = HybridEngine(vault_path=vault)
    engine.index_vault()

    assert engine.search("resep rendang daging sapi") == []

    hits = engine.search("cara mempercepat kueri basis data")
    assert hits and hits[0].doc_id == "20_Knowledge/postgres.md"
    assert 0.0 < hits[0].score <= 1.0


# --- Model-aware index -----------------------------------------------------


def test_index_is_discarded_when_embedding_model_changes(tmp_path: Path):
    storage = BrainStorage(tmp_path)
    chunk = DocumentChunk(
        chunk_id="a#0", doc_id="a.md", file_path="a.md", title="A", content="A\nbody"
    )
    storage.save([chunk], np.ones((1, 4), dtype=np.float32), {"a.md": 1.0}, "model-a")

    chunks, vectors, mtimes = storage.load("model-a")
    assert len(chunks) == 1 and vectors.shape == (1, 4) and mtimes == {"a.md": 1.0}

    chunks, vectors, mtimes = storage.load("model-b")
    assert chunks == [] and vectors.size == 0 and mtimes == {}


def test_engine_from_config_uses_vault_settings(tmp_path: Path):
    vault = tmp_path / "vault"
    vault.mkdir()
    save_config(BrainConfig(vault_path=str(vault), embedding_model="custom/model"), vault)

    engine = HybridEngine.from_config(vault)

    assert engine.embedding_model == "custom/model"
    assert engine.min_dense_similarity == 0.0  # unknown model: no calibrated floor


# --- Claude Code harvesting ------------------------------------------------


def _claude_records(cwd: str) -> list[dict]:
    usage = {"input_tokens": 10, "output_tokens": 20, "cache_read_input_tokens": 300,
             "cache_creation_input_tokens": 40}
    return [
        {"type": "user", "cwd": cwd, "gitBranch": "main",
         "message": {"role": "user", "content": "Fix the login bug in auth.py"}},
        {"type": "user", "isMeta": True, "message": {"role": "user", "content": "meta noise"}},
        {"type": "user", "message": {"role": "user", "content": "<local-command-stdout>x</local-command-stdout>"}},
        # One streamed message split across two records with the same id and usage
        {"type": "assistant", "message": {"id": "m1", "usage": usage, "content": [
            {"type": "tool_use", "name": "Edit", "input": {"file_path": "src/auth.py"}}]}},
        {"type": "assistant", "message": {"id": "m1", "usage": usage, "content": [
            {"type": "tool_use", "name": "Bash", "input": {"command": "pytest"}}]}},
        {"type": "user", "message": {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "t1", "content": "ok"}]}},
        {"type": "assistant", "isSidechain": True, "message": {"id": "side", "usage": usage, "content": [
            {"type": "text", "text": "subagent chatter"}]}},
        {"type": "assistant", "message": {"id": "m2", "usage": usage, "content": [
            {"type": "text", "text": "Fixed the token expiry check. api_key = 'sk-ant-abcdefghijklmnopqrstuvwxyz123456'"}]}},
    ]


def _write_transcript(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r) for r in records) + "\nnot json\n", encoding="utf-8")


def test_claude_transcript_is_summarized(tmp_path: Path):
    transcript = tmp_path / "proj" / "11111111-aaaa.jsonl"
    _write_transcript(transcript, _claude_records("E:/work/app"))

    summary = parse_claude_transcript(transcript)

    assert summary.user_prompts == ["Fix the login bug in auth.py"]
    assert summary.cwd == "E:/work/app" and summary.git_branch == "main"
    assert summary.files_changed == ["src/auth.py"]
    assert summary.tool_calls == {"Edit": 1, "Bash": 1}
    assert summary.assistant_messages == 2  # m1 counted once, sidechain skipped
    assert summary.usage["cache_read_input_tokens"] == 600
    assert summary.final_answer.startswith("Fixed the token expiry check")

    body = render_claude_session(summary)
    assert "## 🎯 Goal" in body and "`src/auth.py`" in body and "subagent chatter" not in body


def test_claude_transcript_without_prompt_is_skipped(tmp_path: Path):
    transcript = tmp_path / "proj" / "empty.jsonl"
    _write_transcript(transcript, [{"type": "system", "content": "boot"}])
    assert parse_claude_transcript(transcript) is None


def test_claude_sessions_ingest_one_note_each_and_refresh_on_change(tmp_path: Path):
    vault = tmp_path / "vault"
    scaffold_vault(vault, is_new=True)
    config = BrainConfig(vault_path=str(vault), device_name="test-device")
    save_config(config, vault)

    projects_root = tmp_path / "claude_projects"
    first = projects_root / "E--work-app" / "11111111-aaaa.jsonl"
    second = projects_root / "E--work-app" / "22222222-bbbb.jsonl"
    _write_transcript(first, _claude_records("E:/missing/app"))
    _write_transcript(second, _claude_records("E:/missing/app"))

    service = IngestionService(vault, config)
    paths = {"claude-code": projects_root}

    result = service.run_ingestion(sources=["claude-code"], custom_paths=paths)
    assert result.ingested == 2
    notes = sorted((vault / DIR_INBOX / "claude-code").glob("*.md"))
    assert len(notes) == 2
    text = notes[0].read_text(encoding="utf-8")
    assert "Fix the login bug in auth.py" in text
    assert "sk-ant-" not in text  # secrets are redacted

    # Unchanged sessions are skipped
    again = IngestionService(vault, config).run_ingestion(sources=["claude-code"], custom_paths=paths)
    assert again.ingested == 0 and again.skipped == 2

    # A session that grew is re-ingested into the same note
    records = _claude_records("E:/missing/app")
    records.append({"type": "user", "message": {"role": "user", "content": "Now add a regression test"}})
    _write_transcript(first, records)
    later = first.stat().st_mtime + 60
    os.utime(first, (later, later))

    refreshed = IngestionService(vault, config).run_ingestion(sources=["claude-code"], custom_paths=paths)
    assert refreshed.ingested == 1
    notes_after = sorted((vault / DIR_INBOX / "claude-code").glob("*.md"))
    assert [n.name for n in notes_after] == [n.name for n in notes]
    assert any("Now add a regression test" in n.read_text(encoding="utf-8") for n in notes_after)


# --- Watcher and MCP log ---------------------------------------------------


def test_watcher_handler_follows_engine_ignore_rules(tmp_path: Path):
    vault = tmp_path / "vault"
    vault.mkdir()
    handler = VaultEventHandler(HybridEngine(vault_path=vault), DebounceManager(delay=0.01))

    assert handler._should_process(str(vault / "20_Knowledge" / "note.md"))
    assert not handler._should_process(str(vault / "20_Knowledge" / "image.png"))
    assert not handler._should_process(str(vault / ".obsidian" / "workspace.md"))
    assert not handler._should_process(str(vault / ".brain_data" / "cache.md"))


def test_agent_log_frontmatter_survives_quotes(tmp_path: Path):
    vault = tmp_path / "vault"
    scaffold_vault(vault, is_new=True)
    config = BrainConfig(vault_path=str(vault), device_name="test-machine")
    save_config(config, vault)
    server = create_mcp_server(vault, config=config)

    summary = 'Fixed "quoted" title: with colon'
    asyncio.run(server.call_tool("write_agent_log", {"summary": summary, "details": "body"}))

    log_file = next(f for f in (vault / DIR_INBOX).glob("*.md") if not f.name.startswith("_"))
    frontmatter = log_file.read_text(encoding="utf-8").split("---")[1]
    assert yaml.safe_load(frontmatter)["title"] == summary
