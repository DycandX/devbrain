"""Comprehensive test suite for Project Harvester, Manifest Parser, Auto-Inspector & Entity Linker."""

from pathlib import Path
import pytest
from typer.testing import CliRunner

from devbrain.cli.main import app
from devbrain.core.config import BrainConfig, save_config
from devbrain.harvester.entity_linker import (
    catalog_known_projects,
    generate_graph_links_block,
    inject_backlink_to_project,
    match_session_to_project,
)
from devbrain.harvester.inspector import RepoType, inspect_repository_type
from devbrain.harvester.manifest_parser import (
    parse_node_manifest,
    parse_python_manifest,
    parse_repository_manifest,
)
from devbrain.harvester.project_harvester import (
    scan_project_metadata,
    seed_project_to_vault,
)
from devbrain.harvester.service import IngestionService

runner = CliRunner()


def test_manifest_parser_python(tmp_path: Path):
    """Verify python manifest parsing from pyproject.toml."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("""
[project]
name = "demo-python-app"
version = "1.0.0"
description = "A demo FastAPI application"
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn",
    "pydantic",
]
""", encoding="utf-8")

    manifest = parse_python_manifest(tmp_path)
    assert manifest.name == "demo-python-app"
    assert manifest.version == "1.0.0"
    assert "FastAPI" in manifest.stack_tags
    assert "Pydantic" in manifest.stack_tags
    assert "fastapi" in manifest.dependencies


def test_manifest_parser_node(tmp_path: Path):
    """Verify Node manifest parsing from package.json."""
    pkg_json = tmp_path / "package.json"
    pkg_json.write_text("""
{
  "name": "nextjs-dashboard",
  "version": "2.0.0",
  "description": "Next.js Admin Dashboard",
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "tailwindcss": "^3.0.0"
  }
}
""", encoding="utf-8")

    manifest = parse_node_manifest(tmp_path)
    assert manifest.name == "nextjs-dashboard"
    assert "React" in manifest.stack_tags
    assert "Next.js" in manifest.stack_tags
    assert "TailwindCSS" in manifest.stack_tags


def test_inspector_classification(tmp_path: Path):
    """Verify classification across various repository structures."""
    # 1. Skill repo
    skill_dir = tmp_path / "my_custom_skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("# Custom Skill\nInstructions here.", encoding="utf-8")
    t_skill, reason = inspect_repository_type(skill_dir)
    assert t_skill == RepoType.SKILL

    # 2. Knowledge / Docs repo
    docs_dir = tmp_path / "system_design_notes"
    docs_dir.mkdir()
    (docs_dir / "README.md").write_text("# System Design\nNotes", encoding="utf-8")
    (docs_dir / "chapter1.md").write_text("# Ch1", encoding="utf-8")
    (docs_dir / "chapter2.md").write_text("# Ch2", encoding="utf-8")
    t_docs, reason = inspect_repository_type(docs_dir)
    assert t_docs == RepoType.KNOWLEDGE

    # 3. Project repo
    proj_dir = tmp_path / "billing_service"
    proj_dir.mkdir()
    (proj_dir / "Cargo.toml").write_text('[package]\nname = "billing_service"\nversion = "0.1.0"', encoding="utf-8")
    t_proj, reason = inspect_repository_type(proj_dir)
    assert t_proj == RepoType.PROJECT


def test_project_seeding_and_backlinking(tmp_path: Path):
    """Verify seeding of project card and bidirectional backlink injection."""
    vault_dir = tmp_path / "TestVault"
    vault_dir.mkdir()
    save_config(BrainConfig(vault_path=str(vault_dir)), vault_dir)

    proj_dir = tmp_path / "my_ecommerce_app"
    proj_dir.mkdir()
    (proj_dir / "pyproject.toml").write_text('[project]\nname = "ecommerce-app"\ndescription = "Storefront"', encoding="utf-8")

    # 1. Scan and seed project
    meta = scan_project_metadata(proj_dir)
    seeded_file = seed_project_to_vault(meta, vault_path=vault_dir)

    assert seeded_file.is_file()
    content = seeded_file.read_text(encoding="utf-8")
    assert "PROJ-ECOMMERCE-APP" in content
    assert "Riwayat Sesi AI Terkini" in content

    # 2. Match project
    matched = match_session_to_project(str(proj_dir), vault_path=vault_dir)
    assert matched is not None
    proj_title, rel_link = matched
    assert "ecommerce" in proj_title.lower() or "ecommerce" in rel_link.lower()

    # 3. Inject backlink
    injected = inject_backlink_to_project(
        project_readme=seeded_file,
        session_title="Implemented Stripe Checkout",
        session_rel_path="90_Agent_Inbox/antigravity/session_01.md",
        created_date="2026-08-29",
    )
    assert injected is True

    updated_content = seeded_file.read_text(encoding="utf-8")
    assert "Implemented Stripe Checkout" in updated_content
    assert "90_Agent_Inbox/antigravity/session_01.md" in updated_content


def test_cli_ingest_project_and_projects(tmp_path: Path):
    """Verify CLI targeted project ingestion and batch scanning."""
    vault_dir = tmp_path / "CliTestVault"
    vault_dir.mkdir()
    save_config(BrainConfig(vault_path=str(vault_dir)), vault_dir)

    app_dir = tmp_path / "sample_rust_cli"
    app_dir.mkdir()
    (app_dir / "Cargo.toml").write_text('[package]\nname = "sample_rust_cli"\nversion = "0.1.0"', encoding="utf-8")

    # Test single project CLI
    res_single = runner.invoke(
        app,
        ["ingest", "project", str(app_dir), "--vault", str(vault_dir)],
    )
    assert res_single.exit_code == 0
    assert "sample_rust_cli" in res_single.stdout
    assert "Successfully seeded note" in res_single.stdout

    # Test batch projects CLI
    res_batch = runner.invoke(
        app,
        ["ingest", "projects", "--dir", str(tmp_path), "--vault", str(vault_dir)],
    )
    assert res_batch.exit_code == 0
    assert "Workspace Repositories Batch Scan" in res_batch.stdout
