"""Tests for IDE client auto-configuration and teardown."""

import json
from pathlib import Path
from devbrain.core.client_config import (
    configure_antigravity,
    configure_claude,
    remove_all_mcp_configs,
)


def test_ide_configuration_and_removal(tmp_path: Path, monkeypatch):
    mock_home = tmp_path / "user_home"
    mock_home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: mock_home)

    vault_dir = tmp_path / "TestVault"
    vault_dir.mkdir()

    # 1. Test Antigravity config
    ag_configs = configure_antigravity(vault_dir)
    assert len(ag_configs) > 0
    for cfg in ag_configs:
        assert cfg.is_file()
        with open(cfg, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "central-brain" in data["mcpServers"]
        assert "serve" in data["mcpServers"]["central-brain"]["args"]

    # 2. Test Claude config
    claude_cfg = configure_claude(vault_dir)
    assert claude_cfg.is_file()
    with open(claude_cfg, "r", encoding="utf-8") as f:
        c_data = json.load(f)
    assert "central-brain" in c_data["mcpServers"]

    # 3. Test Clean Teardown / Removal
    cleaned = remove_all_mcp_configs()
    assert len(cleaned) > 0

    for cfg in cleaned:
        with open(cfg, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "central-brain" not in data.get("mcpServers", {})


def test_unparseable_config_is_left_untouched(tmp_path: Path, isolated_home: Path):
    vault_dir = tmp_path / "TestVault"
    vault_dir.mkdir()

    claude_cfg = isolated_home / ".claude.json"
    claude_cfg.write_text("{ not valid json", encoding="utf-8")

    assert configure_claude(vault_dir) is None
    assert claude_cfg.read_text(encoding="utf-8") == "{ not valid json"


def test_antigravity_only_touches_existing_locations(tmp_path: Path, isolated_home: Path):
    vault_dir = tmp_path / "TestVault"
    vault_dir.mkdir()
    existing = isolated_home / ".gemini" / "antigravity-ide"
    existing.mkdir(parents=True)

    updated = configure_antigravity(vault_dir)

    assert updated == [existing / "mcp_config.json"]
    assert not (isolated_home / ".gemini" / "config").exists()
