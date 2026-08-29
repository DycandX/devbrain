"""Tests for Auto-Entity Linker Engine and Graph Connections."""

from datetime import datetime, timezone
from pathlib import Path

from devbrain.core.config import BrainConfig, save_config
from devbrain.core.scaffolder import scaffold_vault
from devbrain.harvester.discovery import HarvestableSession
from devbrain.harvester.entity_linker import (
    catalog_known_projects,
    generate_graph_links_block,
    inject_backlink_to_project,
    match_session_to_project,
)
from devbrain.harvester.formatter import format_session_note
from devbrain.harvester.project_harvester import scan_project_metadata, seed_project_to_vault
from devbrain.harvester.service import IngestionService


def test_entity_linker_matching_and_formatting(tmp_path: Path):
    """Verify end-to-end matching of session to project and markdown formatting."""
    vault_dir = tmp_path / "LinkerVault"
    scaffold_vault(vault_dir, is_new=True)

    # 1. Create a mock project
    proj_dir = tmp_path / "workspaces" / "crm_backend"
    proj_dir.mkdir(parents=True)
    (proj_dir / "pyproject.toml").write_text('[project]\nname = "crm-backend"\ndescription = "CRM Core API"', encoding="utf-8")

    meta = scan_project_metadata(proj_dir)
    seeded_proj = seed_project_to_vault(meta, vault_path=vault_dir)
    assert seeded_proj.is_file()

    # 2. Match session with workspace hint
    matched = match_session_to_project(str(proj_dir), vault_path=vault_dir)
    assert matched is not None
    title, rel_link = matched
    assert "crm" in title.lower() or "crm" in rel_link.lower()

    # 3. Generate graph connections block
    dt = datetime(2026, 8, 29, 14, 30, 0, tzinfo=timezone.utc)
    block = generate_graph_links_block(created_time=dt, matched_project=matched, device_name="DevLaptop")
    assert "[[10_Projects/" in block
    assert "[[99_Daily/2026-08-29|2026-08-29]]" in block
    assert "`DevLaptop`" in block


def test_service_auto_provisioning_and_linking(tmp_path: Path, monkeypatch):
    """Verify IngestionService automatically creates project card and injects backlinks."""
    mock_home = tmp_path / "mock_home"
    mock_home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: mock_home)

    vault_dir = tmp_path / "ServiceVault"
    scaffold_vault(vault_dir, is_new=True)
    config = BrainConfig(vault_path=str(vault_dir), device_name="Workstation")
    save_config(config, vault_dir)

    # Create workspace repo on disk
    workspace_dir = tmp_path / "my_microservice"
    workspace_dir.mkdir()
    (workspace_dir / "package.json").write_text('{"name": "my-microservice", "version": "1.0.0"}', encoding="utf-8")

    # Create mock Antigravity session
    antigravity_dir = mock_home / ".gemini" / "antigravity-ide" / "brain" / "mock-session-uuid"
    antigravity_dir.mkdir(parents=True)
    (antigravity_dir / "walkthrough.md").write_text("# Implemented Auth Flow\nJWT tokens added.", encoding="utf-8")
    
    logs_dir = antigravity_dir / ".system_generated" / "logs"
    logs_dir.mkdir(parents=True)
    import json
    record = {
        "step_index": 1,
        "type": "USER_INPUT",
        "content": "setup auth",
        "tool_calls": [{"args": {"Cwd": str(workspace_dir)}}],
    }
    (logs_dir / "transcript.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")

    service = IngestionService(vault_path=vault_dir, config=config)
    res = service.run_ingestion(sources=["antigravity-ide"])

    assert res.ingested == 1
    assert res.linked_projects >= 1

    # Check project card was auto-provisioned
    proj_readme = vault_dir / "10_Projects" / "my-microservice" / "README.md"
    assert proj_readme.is_file()
    proj_text = proj_readme.read_text(encoding="utf-8")
    assert "Riwayat Sesi AI Terkini" in proj_text
    assert "Implemented Auth Flow" in proj_text

    # Check session note contains wikilinks
    session_files = list((vault_dir / "90_Agent_Inbox" / "antigravity-ide").glob("*.md"))
    assert len(session_files) == 1
    session_text = session_files[0].read_text(encoding="utf-8")
    assert "[[10_Projects/my-microservice/README" in session_text
    assert "[[99_Daily/" in session_text
