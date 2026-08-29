"""Tests for Multi-Vault Federation, Linking, Mounting, and Federated Search."""

from pathlib import Path
from typer.testing import CliRunner

from devbrain.cli.main import app
from devbrain.core.config import BrainConfig, load_config, save_config
from devbrain.core.scaffolder import scaffold_vault
from devbrain.core.vault_federation import VaultFederationManager
from devbrain.engine.hybrid_search import HybridEngine

runner = CliRunner()


def test_vault_federation_link_and_list(tmp_path: Path):
    """Test linking external vaults and listing federation metadata."""
    central_vault = tmp_path / "CentralVault1"
    scaffold_vault(central_vault, is_new=True)
    save_config(BrainConfig(vault_path=str(central_vault)), central_vault)

    # External Vault 1
    ext1 = tmp_path / "WorkVault"
    ext1.mkdir()
    (ext1 / "Note1.md").write_text("# Work Note 1\nDiscussing system architecture.", encoding="utf-8")
    (ext1 / "Note2.md").write_text("# Work Note 2\nMeeting notes.", encoding="utf-8")

    manager = VaultFederationManager(vault_path=central_vault)
    alias, resolved_path, is_mounted = manager.link_vault(ext1, alias="work", mount=False)

    assert alias == "work"
    assert resolved_path == ext1.resolve()
    assert is_mounted is False

    # Verify config updated
    cfg = load_config(central_vault)
    assert "work" in cfg.linked_vaults
    assert cfg.linked_vaults["work"] == str(ext1.resolve())

    # List linked vaults
    items = manager.list_linked_vaults()
    assert len(items) == 1
    assert items[0].alias == "work"
    assert items[0].exists is True
    assert items[0].note_count == 2
    assert items[0].is_mounted is False


def test_vault_federation_mount_and_unlink(tmp_path: Path):
    """Test junction mounting and safe unlinking."""
    central_vault = tmp_path / "CentralVault2"
    scaffold_vault(central_vault, is_new=True)
    save_config(BrainConfig(vault_path=str(central_vault)), central_vault)

    ext = tmp_path / "PersonalWiki"
    ext.mkdir()
    (ext / "Ideas.md").write_text("# Ideas\nSome personal thoughts.", encoding="utf-8")

    manager = VaultFederationManager(vault_path=central_vault)
    alias, _, is_mounted = manager.link_vault(ext, alias="personal", mount=True)

    assert alias == "personal"
    # Check mounted path
    mount_point = central_vault / "20_Knowledge" / "Linked_Vaults" / "personal"
    assert mount_point.exists() or mount_point.is_symlink()

    # Unlink
    success = manager.unlink_vault("personal", clean_mount=True)
    assert success is True

    # Target folder and files must still be intact
    assert ext.is_dir()
    assert (ext / "Ideas.md").is_file()

    # Mount point must be removed
    assert not mount_point.exists()


def test_federated_hybrid_search(tmp_path: Path):
    """Test that HybridEngine indexes and searches across Central Vault and Linked Vaults."""
    central_vault = tmp_path / "CentralVault3"
    scaffold_vault(central_vault, is_new=True)
    save_config(BrainConfig(vault_path=str(central_vault)), central_vault)

    # Central file
    (central_vault / "10_Projects" / "App.md").write_text(
        "# App Architecture\nWe use FastMCP and Redis for caching.", encoding="utf-8"
    )

    # External Vault
    ext = tmp_path / "KnowledgeHub"
    ext.mkdir()
    (ext / "Kubernetes.md").write_text(
        "# Kubernetes Guide\nDeployment guide for docker containers and pods.", encoding="utf-8"
    )

    engine = HybridEngine(
        vault_path=central_vault,
        linked_vaults={"knowledge": ext},
    )
    res = engine.index_vault(force_reindex=True)
    assert res["processed"] >= 2

    # 1. Search across all (finds both)
    all_results = engine.search("caching and redis", scope="all")
    assert len(all_results) > 0
    assert any("App.md" in r.file_path for r in all_results)

    k8s_results = engine.search("kubernetes docker pods", scope="all")
    assert len(k8s_results) > 0
    assert any("Kubernetes.md" in r.file_path for r in k8s_results)

    # 2. Scope filter to linked vault only
    scoped_k8s = engine.search("kubernetes", scope="knowledge")
    assert len(scoped_k8s) > 0
    assert all("linked:knowledge:" in r.doc_id for r in scoped_k8s)

    # 3. Scope filter to central only: must NOT return any linked vault chunks
    scoped_central = engine.search("kubernetes", scope="central")
    assert len(scoped_central) > 0
    assert all(not r.doc_id.startswith("linked:") for r in scoped_central)

    # 4. Keyword exact search check
    scoped_central_bm25 = engine.search("kubernetes", mode="bm25", scope="central")
    assert len(scoped_central_bm25) == 0

    scoped_linked_bm25 = engine.search("kubernetes", mode="bm25", scope="knowledge")
    assert len(scoped_linked_bm25) > 0
    assert "Kubernetes.md" in scoped_linked_bm25[0].file_path


def test_cli_vault_subapp_commands(tmp_path: Path):
    """Test CLI commands `devbrain vault link`, `list`, `sync`, and `unlink`."""
    vault = tmp_path / "CliVaultFederation"
    scaffold_vault(vault, is_new=True)
    save_config(BrainConfig(vault_path=str(vault)), vault)

    ext = tmp_path / "OfficeNotes"
    ext.mkdir()
    (ext / "Meeting.md").write_text("# Meeting Notes\nQ3 planning roadmap.", encoding="utf-8")

    # 1. CLI link
    res_link = runner.invoke(
        app,
        ["vault", "link", str(ext), "--alias", "office", "--vault", str(vault)],
    )
    assert res_link.exit_code == 0
    assert "Successfully linked vault" in res_link.stdout

    # 2. CLI list
    res_list = runner.invoke(app, ["vault", "list", "--vault", str(vault)])
    assert res_list.exit_code == 0
    assert "office" in res_list.stdout

    # 3. CLI sync
    res_sync = runner.invoke(app, ["vault", "sync", "--vault", str(vault)])
    assert res_sync.exit_code == 0
    assert "Multi-Vault Sync Complete" in res_sync.stdout

    # 4. CLI unlink
    res_unlink = runner.invoke(app, ["vault", "unlink", "office", "--vault", str(vault)])
    assert res_unlink.exit_code == 0
    assert "Successfully unlinked vault" in res_unlink.stdout
