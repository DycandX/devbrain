"""Tests for Sprint 01 CLI commands."""

from pathlib import Path
from typer.testing import CliRunner
from devbrain.cli.main import app
from devbrain.core.constants import CONFIG_FILENAME

runner = CliRunner()


def test_cli_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "devbrain version" in result.stdout


def test_cli_status_no_config(tmp_path: Path):
    result = runner.invoke(app, ["status", "--vault", str(tmp_path)])
    assert result.exit_code != 0
    assert "tidak ditemukan" in result.output or "Error" in result.output


def test_cli_init_and_status(tmp_path: Path):
    vault_dir = tmp_path / "MyCliVault"
    
    # Run init with inputs: choice 1 (FastEmbed), device name "test-device"
    init_input = "1\ntest-device\n"
    result = runner.invoke(app, ["init", str(vault_dir)], input=init_input)
    assert result.exit_code == 0
    assert (vault_dir / CONFIG_FILENAME).is_file()
    
    # Run status
    status_result = runner.invoke(app, ["status", "--vault", str(vault_dir)])
    assert status_result.exit_code == 0
    assert "Status Central AI Brain Hub" in status_result.output
    assert "test-device" in status_result.output
