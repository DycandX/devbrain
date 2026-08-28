"""End-to-End lifecycle integration test for devbrain Level 1 Core."""

import asyncio
from pathlib import Path
from typer.testing import CliRunner

from devbrain.cli.main import app
from devbrain.core.client_config import configure_antigravity, configure_claude, remove_all_mcp_configs
from devbrain.core.config import BrainConfig, load_config, save_config
from devbrain.core.scaffolder import scaffold_vault
from devbrain.engine.hybrid_search import HybridEngine
from devbrain.mcp_server.server import create_mcp_server

runner = CliRunner()


def test_full_level1_lifecycle_flow(tmp_path: Path, monkeypatch):
    # 1. Setup Mock User Home & Vault Directory
    mock_home = tmp_path / "user_home"
    mock_home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: mock_home)

    vault_dir = tmp_path / "E2EVault"
    
    # 2. Test Scaffolding
    created_items = scaffold_vault(vault_dir, is_new=True)
    assert len(created_items) > 0
    assert (vault_dir / "00_System" / "global_context.md").is_file()
    assert (vault_dir / "10_Projects" / "_Project_Index.md").is_file()

    # 3. Save Config
    config = BrainConfig(vault_path=str(vault_dir), device_name="e2e-tester")
    save_config(config, vault_dir)
    loaded_config = load_config(vault_dir / ".brainrc.json")
    assert loaded_config.device_name == "e2e-tester"

    # 4. Test Engine Indexing
    engine = HybridEngine(vault_path=vault_dir)
    engine.initialize()
    stats = engine.index_vault(force_reindex=True)
    assert stats["total_chunks"] > 0

    # 5. Test Hybrid Search
    results = engine.search("Modular Architecture", limit=3)
    assert len(results) > 0
    assert any("Architecture" in r.title or "Knowledge" in r.file_path for r in results)

    # 6. Test FastMCP Server Tools
    server = create_mcp_server(vault_dir, config=loaded_config)
    
    # Tool: get_project_context
    proj_res = asyncio.run(server.call_tool("get_project_context", {"project_name": "example_project"}))
    proj_text = proj_res[0].text if isinstance(proj_res, list) else str(proj_res)
    assert "Example Project" in proj_text

    # Tool: write_agent_log
    log_res = asyncio.run(server.call_tool("write_agent_log", {
        "summary": "E2E Test Session Verified",
        "details": "All core modules in Level 1 passed end-to-end integration.",
        "tags": ["e2e", "verified"],
        "author": "e2e-agent",
    }))
    log_text = log_res[0].text if isinstance(log_res, list) else str(log_res)
    assert "Successfully recorded agent log" in log_text

    # Verify search finds the newly written log
    search_new_log = engine.search("E2E Test Session Verified", limit=2)
    assert len(search_new_log) > 0

    # 7. Test IDE Config Registration
    ag_cfgs = configure_antigravity(vault_dir)
    claude_cfg = configure_claude(vault_dir)
    assert len(ag_cfgs) > 0
    assert claude_cfg.is_file()

    # 8. Test Clean Teardown
    cleaned = remove_all_mcp_configs()
    assert len(cleaned) > 0
