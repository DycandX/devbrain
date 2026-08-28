"""Tests for Sprint 02 CLI commands (search & index)."""

from pathlib import Path
from typer.testing import CliRunner
from devbrain.cli.main import app
from devbrain.core.config import BrainConfig, save_config
from devbrain.core.scaffolder import scaffold_vault

runner = CliRunner()


def test_cli_index_and_search_commands(tmp_path: Path):
    vault_dir = tmp_path / "CliSearchVault"
    scaffold_vault(vault_dir, is_new=True)

    config = BrainConfig(vault_path=str(vault_dir))
    save_config(config, vault_dir)

    # 1. Run index command
    index_result = runner.invoke(app, ["index", "--vault", str(vault_dir)])
    assert index_result.exit_code == 0
    assert "Indexing completed successfully" in index_result.output

    # 2. Run search command
    search_result = runner.invoke(app, ["search", "architecture", "--vault", str(vault_dir)])
    assert search_result.exit_code == 0
    assert "Search Results for:" in search_result.output
