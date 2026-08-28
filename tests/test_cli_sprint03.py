"""Tests for Sprint 03 CLI commands (skill and uninstall)."""

from pathlib import Path
from typer.testing import CliRunner
from devbrain.cli.main import app
from devbrain.core.config import BrainConfig, save_config
from devbrain.core.constants import DIR_AGENT_SKILLS
from devbrain.core.scaffolder import scaffold_vault

runner = CliRunner()


def test_cli_skill_commands(tmp_path: Path):
    vault_dir = tmp_path / "SkillCliVault"
    scaffold_vault(vault_dir, is_new=True)

    config = BrainConfig(vault_path=str(vault_dir))
    save_config(config, vault_dir)

    # 1. Run skill list
    list_res = runner.invoke(app, ["skill", "list", "--vault", str(vault_dir)])
    assert list_res.exit_code == 0
    assert "Active Central Brain Agent Skills" in list_res.output
    assert "example_skill" in list_res.output

    # 2. Run skill add
    add_res = runner.invoke(app, ["skill", "add", "docker-deploy", "--vault", str(vault_dir)])
    assert add_res.exit_code == 0
    assert "Created new skill template" in add_res.output

    # Verify skill file exists on disk
    new_skill_file = vault_dir / DIR_AGENT_SKILLS / "docker-deploy" / "SKILL.md"
    assert new_skill_file.is_file()


def test_cli_uninstall_command(tmp_path: Path, monkeypatch):
    mock_home = tmp_path / "home"
    mock_home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: mock_home)

    vault_dir = tmp_path / "UninstallVault"
    scaffold_vault(vault_dir, is_new=True)
    config = BrainConfig(vault_path=str(vault_dir))
    save_config(config, vault_dir)

    # Run uninstall with input "y\n"
    uninstall_res = runner.invoke(app, ["uninstall", "--vault", str(vault_dir)], input="y\n")
    assert uninstall_res.exit_code == 0
    assert "cleanly unregistered" in uninstall_res.output
