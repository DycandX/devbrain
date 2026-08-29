"""Tests for Unified DWIM Ingestion CLI, Tolerant Flags, IDE Deep Links, and Self-Ingestion Guard."""

from pathlib import Path
from typer.testing import CliRunner

from devbrain.cli.main import app
from devbrain.core.config import BrainConfig, save_config
from devbrain.core.scaffolder import scaffold_vault
from devbrain.harvester.service import IngestionService

runner = CliRunner()


def test_unified_ingest_positional_single_project(tmp_path: Path):
    """Test `devbrain ingest <path>` on a single repository."""
    vault = tmp_path / "UnifiedVault1"
    scaffold_vault(vault, is_new=True)
    save_config(BrainConfig(vault_path=str(vault)), vault)

    repo = tmp_path / "my_py_service"
    repo.mkdir()
    (repo / "pyproject.toml").write_text('[project]\nname = "my_py_service"\ndescription = "Test Python Service"', encoding="utf-8")
    (repo / "main.py").write_text("print('hello')", encoding="utf-8")

    res = runner.invoke(app, ["ingest", str(repo), "--vault", str(vault)])
    assert res.exit_code == 0
    assert "Repository Inspection: my_py_service" in res.stdout

    card = vault / "10_Projects" / "my_py_service" / "README.md"
    assert card.is_file()
    content = card.read_text(encoding="utf-8")
    assert "vscode://file/" in content
    assert "file:///" in content
    assert "Quick Actions:" in content


def test_unified_ingest_flag_dir_tolerance(tmp_path: Path):
    """Test `devbrain ingest --dir <path>` works seamlessly without throwing 'No such option' error."""
    vault = tmp_path / "UnifiedVault2"
    scaffold_vault(vault, is_new=True)
    save_config(BrainConfig(vault_path=str(vault)), vault)

    repo = tmp_path / "my_node_tool"
    repo.mkdir()
    (repo / "package.json").write_text('{"name": "my_node_tool", "version": "1.0.0"}', encoding="utf-8")

    # Pass via --dir
    res_dir = runner.invoke(app, ["ingest", "--dir", str(repo), "--vault", str(vault)])
    assert res_dir.exit_code == 0
    assert "Repository Inspection: my_node_tool" in res_dir.stdout
    assert (vault / "10_Projects" / "my_node_tool" / "README.md").is_file()

    # Pass via --path
    res_path = runner.invoke(app, ["ingest", "--path", str(repo), "--vault", str(vault)])
    assert res_path.exit_code == 0


def test_unified_ingest_container_workspace(tmp_path: Path):
    """Test `devbrain ingest <container_path>` auto-detects and scans sub-projects."""
    vault = tmp_path / "UnifiedVault3"
    scaffold_vault(vault, is_new=True)
    save_config(BrainConfig(vault_path=str(vault)), vault)

    container = tmp_path / "my_workspace"
    container.mkdir()
    (container / "sub1").mkdir()
    (container / "sub1" / "package.json").write_text('{"name": "sub1"}', encoding="utf-8")
    (container / "sub2").mkdir()
    (container / "sub2" / "pyproject.toml").write_text('[project]\nname = "sub2"', encoding="utf-8")

    res = runner.invoke(app, ["ingest", str(container), "--vault", str(vault)])
    assert res.exit_code == 0
    assert "Multi-Project Workspace Scan" in res.stdout
    assert (vault / "10_Projects" / "sub1" / "README.md").is_file()
    assert (vault / "10_Projects" / "sub2" / "README.md").is_file()


def test_self_ingestion_guard(tmp_path: Path):
    """Verify scanning workspace does not process the vault itself."""
    workspace = tmp_path / "all_projects"
    workspace.mkdir()

    # Vault inside workspace
    vault = workspace / "CentralVault"
    scaffold_vault(vault, is_new=True)
    config = BrainConfig(vault_path=str(vault), workspace_roots=[str(workspace)])
    save_config(config, vault)

    # Subproject alongside vault
    other = workspace / "other_app"
    other.mkdir()
    (other / "package.json").write_text('{"name": "other_app"}', encoding="utf-8")

    service = IngestionService(vault_path=vault, config=config)
    results = service.ingest_workspace_projects(root_dirs=[workspace])

    # Should only ingest other_app, not CentralVault itself
    names = [meta.name for meta, _ in results]
    assert "other_app" in names
    assert "CentralVault" not in names
