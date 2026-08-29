"""Tests for Codebase Structure Analyzer, README-less Project Synthesis, and Container Auto-Delegation."""

from pathlib import Path
from typer.testing import CliRunner

from devbrain.cli.main import app
from devbrain.core.config import BrainConfig, save_config
from devbrain.core.scaffolder import scaffold_vault
from devbrain.harvester.inspector import RepoType, inspect_repository_type
from devbrain.harvester.project_harvester import scan_project_metadata, seed_project_to_vault
from devbrain.harvester.service import IngestionService
from devbrain.harvester.tree_analyzer import analyze_codebase_structure, generate_ascii_tree

runner = CliRunner()


def test_ascii_tree_generation_and_ignored_directories(tmp_path: Path):
    """Verify ASCII tree generation excludes node_modules, .git, and venv."""
    repo = tmp_path / "my_express_app"
    repo.mkdir()
    (repo / "src").mkdir()
    (repo / "src" / "index.js").write_text("console.log('hi')", encoding="utf-8")
    (repo / "node_modules").mkdir()
    (repo / "node_modules" / "express").mkdir(parents=True)
    (repo / "node_modules" / "express" / "index.js").write_text("module.exports = {}", encoding="utf-8")
    (repo / "server.js").write_text("const express = require('express');", encoding="utf-8")
    (repo / "docker-compose.yml").write_text("version: '3'", encoding="utf-8")

    analysis = analyze_codebase_structure(repo)
    assert "node_modules" not in analysis.ascii_tree
    assert "server.js" in analysis.ascii_tree
    assert "src/" in analysis.ascii_tree
    assert "server.js" in analysis.entrypoints
    assert "docker-compose.yml" in analysis.infra_files


def test_readme_less_project_card_synthesis(tmp_path: Path):
    """Verify intelligent card synthesis when README.md is absent."""
    vault = tmp_path / "TestVault"
    scaffold_vault(vault, is_new=True)

    repo = tmp_path / "neo4j_express_service"
    repo.mkdir()
    (repo / "server.js").write_text("// express app", encoding="utf-8")
    (repo / "docker-compose.yml").write_text("services: {}", encoding="utf-8")
    (repo / "package.json").write_text("""
{
  "name": "neo4j-express-service",
  "version": "1.0.0",
  "scripts": {
    "dev": "nodemon server.js",
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.18.0",
    "neo4j-driver": "^5.0.0"
  }
}
""", encoding="utf-8")

    meta = scan_project_metadata(repo)
    assert "Auto-synthesized" in meta.description or "Express" in meta.description
    assert "dev" in meta.scripts

    seeded_file = seed_project_to_vault(meta, vault_path=vault)
    assert seeded_file.is_file()

    content = seeded_file.read_text(encoding="utf-8")
    assert "## ⚡ Runnable Scripts:" in content
    assert "npm run dev" in content or "nodemon server.js" in content
    assert "## 🌳 Project Structure:" in content
    assert "server.js" in content
    assert "PROJ-NEO4J_EXPRESS_SERVICE" in content or "PROJ-NEO4J-EXPRESS-SERVICE" in content


def test_container_workspace_auto_delegation(tmp_path: Path):
    """Verify multi-project container folder (like _fxmedia) is auto-delegated to sub-projects."""
    vault = tmp_path / "ContainerVault"
    scaffold_vault(vault, is_new=True)
    config = BrainConfig(vault_path=str(vault))
    save_config(config, vault)

    # Create container folder with 2 subprojects and NO root manifest
    container = tmp_path / "_fxmedia"
    container.mkdir()

    sub_a = container / "neo4j-express-demo"
    sub_a.mkdir()
    (sub_a / "package.json").write_text('{"name": "neo4j-express-demo", "version": "1.0.0"}', encoding="utf-8")
    (sub_a / "server.js").write_text("// server", encoding="utf-8")

    sub_b = container / "qdrant-local-demo"
    sub_b.mkdir()
    (sub_b / "pyproject.toml").write_text('[project]\nname = "qdrant-local-demo"', encoding="utf-8")

    # 1. Inspector should detect CONTAINER
    repo_type, reason = inspect_repository_type(container)
    assert repo_type == RepoType.CONTAINER

    # 2. IngestionService should auto-delegate
    service = IngestionService(vault_path=vault, config=config)
    meta, sub_results = service.ingest_single_project(container)

    assert meta.repo_type == RepoType.CONTAINER
    assert isinstance(sub_results, list)
    assert len(sub_results) == 2

    # Verify both sub-projects were seeded in 10_Projects/
    assert (vault / "10_Projects" / "neo4j-express-demo" / "README.md").is_file()
    assert (vault / "10_Projects" / "qdrant-local-demo" / "README.md").is_file()

    # 3. CLI execution
    res = runner.invoke(app, ["ingest", "project", str(container), "--vault", str(vault)])
    assert res.exit_code == 0
    assert "Multi-Project Workspace Scan" in res.stdout
    assert "neo4j-express-demo" in res.stdout
    assert "qdrant-local-demo" in res.stdout
