"""Unit and integration tests for Session Ingestion and Secret Sanitizer."""

import json
from pathlib import Path
from typer.testing import CliRunner

from devbrain.cli.main import app
from devbrain.core.config import BrainConfig, save_config
from devbrain.core.constants import DIR_INBOX
from devbrain.core.scaffolder import scaffold_vault
from devbrain.harvester.discovery import discover_sessions
from devbrain.harvester.extractor import extract_session_payload
from devbrain.harvester.formatter import format_session_note
from devbrain.harvester.sanitizer import sanitize_text
from devbrain.harvester.service import IngestionService

runner = CliRunner()


def test_secret_sanitizer():
    raw_sample = """
    openai_key = "sk-proj-abc1234567890123456789012345"
    anthropic_key = "sk-ant-api03-abcdefghijklmnopqrstuvwxyz"
    google_key = "AIzaSyD12345678901234567890123456789012"
    github_pat = "ghp_123456789012345678901234567890123456"
    headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkw"}
    db_password = "password = 'SuperSecretDbPassword123!'"
    """
    sanitized, redactions = sanitize_text(raw_sample)

    assert redactions >= 5
    assert "sk-proj-" not in sanitized
    assert "sk-ant-" not in sanitized
    assert "AIzaSy" not in sanitized
    assert "ghp_" not in sanitized
    assert "SuperSecretDbPassword123!" not in sanitized
    assert "[REDACTED" in sanitized


def test_discovery_and_extraction(tmp_path: Path):
    mock_brain_dir = tmp_path / "mock_antigravity_brain"
    session_dir = mock_brain_dir / "session-uuid-1234"
    session_dir.mkdir(parents=True)

    wt_file = session_dir / "walkthrough.md"
    with open(wt_file, "w", encoding="utf-8") as f:
        f.write("# Building Auth Service\n\nCompleted JWT authentication.\nUsed api_key = 'sk-proj-testkey1234567890123456'.")

    discovered = discover_sessions(sources=["antigravity-ide"], custom_paths={"antigravity-ide": mock_brain_dir})
    assert len(discovered) == 1
    assert discovered[0].session_id == "session-uuid-1234"

    payload = extract_session_payload(discovered[0])
    assert payload is not None
    assert payload.title == "Building Auth Service"
    assert "sk-proj-" not in payload.body_markdown
    assert payload.num_redactions >= 1


def test_transcript_xml_and_newline_cleaning(tmp_path: Path):
    mock_brain_dir = tmp_path / "mock_antigravity_brain"
    session_dir = mock_brain_dir / "session-transcript-only"
    logs_dir = session_dir / ".system_generated" / "logs"
    logs_dir.mkdir(parents=True)

    raw_user_prompt = "<USER_REQUEST>\nanalisis dan pelajari projek ini\ndan buatkan arsitekturnya\n</USER_REQUEST>\n<ADDITIONAL_METADATA>\ntime: 2026-08-29\n</ADDITIONAL_METADATA>"
    with open(logs_dir / "transcript.jsonl", "w", encoding="utf-8") as f:
        f.write(json.dumps({"type": "USER_INPUT", "content": raw_user_prompt}) + "\n")

    discovered = discover_sessions(sources=["antigravity-ide"], custom_paths={"antigravity-ide": mock_brain_dir})
    payload = extract_session_payload(discovered[0])
    assert payload is not None
    assert "<USER_REQUEST>" not in payload.title
    assert "\n" not in payload.title
    assert "analisis dan pelajari projek ini" in payload.title

    filename, content = format_session_note(payload, device_name="test-omen")
    assert '<USER_REQUEST>' not in content.split("---")[1]  # Frontmatter has no XML tags
    assert "\nanalisis" not in content.split("---")[1]     # Frontmatter has no broken newlines in title


def test_ingestion_service_lifecycle_and_deduplication(tmp_path: Path):
    vault_dir = tmp_path / "IngestVault"
    scaffold_vault(vault_dir, is_new=True)
    config = BrainConfig(vault_path=str(vault_dir), device_name="test-laptop")
    save_config(config, vault_dir)

    mock_ag_root = tmp_path / "mock_ag"
    session_1 = mock_ag_root / "uuid-session-001"
    session_1.mkdir(parents=True)
    with open(session_1 / "walkthrough.md", "w", encoding="utf-8") as f:
        f.write("# Feature A Walkthrough\n\nImplemented high-speed indexing.")

    service = IngestionService(vault_path=vault_dir, config=config)

    # 1. Run Ingestion First Time
    res1 = service.run_ingestion(sources=["antigravity-ide"], custom_paths={"antigravity-ide": mock_ag_root})
    assert res1.ingested == 1
    assert res1.skipped == 0
    assert len(list((vault_dir / DIR_INBOX / "antigravity-ide").glob("*.md"))) == 1

    # 2. Run Ingestion Second Time (Should deduplicate and skip)
    res2 = service.run_ingestion(sources=["antigravity-ide"], custom_paths={"antigravity-ide": mock_ag_root})
    assert res2.ingested == 0
    assert res2.skipped == 1


def test_cli_ingest_command(tmp_path: Path, monkeypatch):
    mock_home = tmp_path / "empty_home"
    mock_home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: mock_home)

    vault_dir = tmp_path / "CliIngestVault"
    scaffold_vault(vault_dir, is_new=True)
    config = BrainConfig(vault_path=str(vault_dir))
    save_config(config, vault_dir)

    # Dry run
    res_dry = runner.invoke(app, ["ingest", "--dry-run", "--vault", str(vault_dir)])
    assert res_dry.exit_code == 0
    assert "AI Session Ingestion Report" in res_dry.output

    # Normal run
    res = runner.invoke(app, ["ingest", "--vault", str(vault_dir)])
    assert res.exit_code == 0
    assert "AI Session Ingestion Report" in res.output
