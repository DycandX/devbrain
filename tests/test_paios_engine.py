"""Unit and integration tests for DevBrain PAIOS Layer (SQLite, ADR, Context, Rules, Extended Skills)."""

from pathlib import Path
import tempfile

from typer.testing import CliRunner

from devbrain.adr.manager import ADRManager
from devbrain.cli.main import app
from devbrain.context.builder import ContextAssemblyEngine
from devbrain.core.config import BrainConfig, save_config
from devbrain.core.constants import DIR_AGENT_SKILLS, DIR_DECISIONS, DIR_PROJECTS, DIR_SYSTEM
from devbrain.core.sqlite_db import BrainSQLiteStorage
from devbrain.rules.generator import RulesGenerator

runner = CliRunner()


def test_sqlite_storage_memories(tmp_path: Path):
    """Test SQLite storage memory insertion, scope filtering, and superseding."""
    storage = BrainSQLiteStorage(tmp_path)

    # Insert global preference memory
    m1 = storage.upsert_memory(
        content="Always use TypeScript with strict mode",
        type="preference",
        scope="GLOBAL",
        source="user",
    )
    assert m1.startswith("mem_")

    # Insert project-scoped memory
    m2 = storage.upsert_memory(
        content="Database uses PostgreSQL 16 on port 5432",
        type="fact",
        scope="PROJECT",
        project="simaku",
        source="antigravity",
    )

    # Test filtering by scope
    global_mems = storage.get_memories(scope="GLOBAL")
    assert len(global_mems) == 1
    assert "TypeScript" in global_mems[0]["content"]

    proj_mems = storage.get_memories(project="simaku")
    assert len(proj_mems) == 2  # Includes global (project IS NULL) + simaku

    # Test superseding memory
    m3 = storage.upsert_memory(
        content="Migrated to PostgreSQL 17",
        type="fact",
        scope="PROJECT",
        project="simaku",
    )
    superseded = storage.supersede_memory(old_memory_id=m2, new_memory_id=m3)
    assert superseded is True

    active_proj = storage.get_memories(project="simaku", status="active")
    assert any(m["id"] == m3 for m in active_proj)
    assert not any(m["id"] == m2 for m in active_proj)


def test_sqlite_storage_decisions_and_file_cache(tmp_path: Path):
    """Test ADR indexing and file caching in SQLite."""
    storage = BrainSQLiteStorage(tmp_path)

    storage.upsert_decision(
        id="ADR-001",
        title="Use FastEmbed for Local Embeddings",
        project="CentralBrain",
        status="accepted",
        file_path=str(tmp_path / "30_Decisions/ADR-001.md"),
        date="2026-08-30",
        summary="Chosen for 0ms network latency.",
    )

    decisions = storage.get_decisions(project="CentralBrain")
    assert len(decisions) == 1
    assert decisions[0]["id"] == "ADR-001"
    assert decisions[0]["title"] == "Use FastEmbed for Local Embeddings"

    # File cache
    storage.update_file_cache(
        file_path="10_Projects/test.md",
        mtime=123456.78,
        sha256_hash="abc123hash",
        chunk_count=4,
    )
    cached = storage.get_file_cache("10_Projects/test.md")
    assert cached is not None
    assert cached["sha256_hash"] == "abc123hash"
    assert cached["chunk_count"] == 4


def test_adr_manager_lifecycle(tmp_path: Path):
    """Test creating, listing, and linking ADRs via ADRManager."""
    # Create project card first
    proj_dir = tmp_path / DIR_PROJECTS / "simaku"
    proj_dir.mkdir(parents=True, exist_ok=True)
    proj_readme = proj_dir / "README.md"
    proj_readme.write_text("# Simaku Project\n\n## Overview\nTest project.", encoding="utf-8")

    adr_mgr = ADRManager(tmp_path)

    res1 = adr_mgr.create_decision(
        title="Use Laravel 11 Backend",
        project="simaku",
        context="Need modern PHP framework with strong ecosystem.",
        decision="Adopt Laravel 11 for all REST APIs.",
        consequences="Requires PHP 8.2+ runtime.",
        status="accepted",
    )
    assert res1["id"] == "ADR-001"
    assert Path(res1["file_path"]).is_file()

    # Check auto-link to project readme
    updated_readme = proj_readme.read_text(encoding="utf-8")
    assert "[[ADR-001]]" in updated_readme

    # Create second ADR
    res2 = adr_mgr.create_decision(
        title="Use SQLite State Cache",
        project="simaku",
        context="Fast relational indexing.",
        decision="Embedded SQLite database in .brain_data/.",
    )
    assert res2["id"] == "ADR-002"

    # List decisions
    all_adrs = adr_mgr.list_decisions(project="simaku")
    assert len(all_adrs) == 2
    assert all_adrs[0]["id"] == "ADR-001"
    assert all_adrs[1]["id"] == "ADR-002"


def test_context_assembly_engine(tmp_path: Path):
    """Test ContextAssemblyEngine assembling 5 context tiers."""
    # Scaffold user preferences
    sys_dir = tmp_path / DIR_SYSTEM
    sys_dir.mkdir(parents=True, exist_ok=True)
    (sys_dir / "User_Preferences.md").write_text("- Style: Clean architecture\n- Language: TypeScript Strict", encoding="utf-8")

    # Scaffold project card
    proj_dir = tmp_path / DIR_PROJECTS / "ecommerce"
    proj_dir.mkdir(parents=True, exist_ok=True)
    (proj_dir / "README.md").write_text("# Ecommerce App\n\nStack: TypeScript, Next.js, FastAPI, Docker.", encoding="utf-8")

    # Create ADR
    adr_mgr = ADRManager(tmp_path)
    adr_mgr.create_decision(
        title="Use Stripe Elements",
        project="ecommerce",
        context="Payment processing integration.",
        decision="Use Stripe Elements instead of redirect checkout.",
    )

    engine = ContextAssemblyEngine(tmp_path)
    card = engine.build_task_context(
        task="Implement webhook handler for checkout completion",
        project="ecommerce",
    )

    assert card.project == "ecommerce"
    assert "TypeScript Strict" in card.user_preferences
    assert "TypeScript" in card.tech_stack
    assert len(card.active_decisions) >= 1
    assert card.active_decisions[0]["id"] == "ADR-001"

    # Test markdown output
    md = card.to_markdown()
    assert "# 🧠 SITUATIONAL TASK CONTEXT BRIEFING" in md
    assert "[[ecommerce]]" in md
    assert "Stripe Elements" in md

    # Test dict output
    d = card.to_dict()
    assert d["task"] == "Implement webhook handler for checkout completion"
    assert d["project"] == "ecommerce"


def test_rules_generator(tmp_path: Path):
    """Test generating AGENTS.md and CLAUDE.md rule contracts."""
    generator = RulesGenerator(vault_path=tmp_path)

    project_repo = tmp_path / "my_project"
    project_repo.mkdir(parents=True, exist_ok=True)

    written = generator.write_rules_to_project(
        project_dir=project_repo,
        project_name="SimakuPBL",
        tech_stack=["Laravel", "PHP 8.2", "PostgreSQL"],
    )

    assert "AGENTS.md" in written
    assert "CLAUDE.md" in written

    agents_content = written["AGENTS.md"].read_text(encoding="utf-8")
    assert "SimakuPBL" in agents_content
    assert "Hierarchy of Truth" in agents_content
    assert "Current Working Codebase" in agents_content
    assert "Central Brain ADRs" in agents_content


def test_cli_adr_commands(tmp_path: Path):
    """Test CLI devbrain adr new and devbrain adr list."""
    # Setup config
    cfg = BrainConfig(vault_path=str(tmp_path))
    save_config(cfg, tmp_path / ".brainrc.json")

    # Run devbrain adr new
    res_new = runner.invoke(
        app,
        ["adr", "new", "Migrate to SQLite", "--project", "DevBrain", "--context", "Need speed", "--decision", "Use brain.db", "--vault", str(tmp_path)],
    )
    assert res_new.exit_code == 0
    assert "Created Architecture Decision Record" in res_new.stdout

    # Run devbrain adr list
    res_list = runner.invoke(
        app,
        ["adr", "list", "--project", "DevBrain", "--vault", str(tmp_path)],
    )
    assert res_list.exit_code == 0
    assert "ADR-001" in res_list.stdout
    assert "SQLite" in res_list.stdout
    assert "DevBrain" in res_list.stdout


def test_cli_context_commands(tmp_path: Path):
    """Test CLI devbrain context build."""
    cfg = BrainConfig(vault_path=str(tmp_path))
    save_config(cfg, tmp_path / ".brainrc.json")

    # Create dummy project card
    proj_dir = tmp_path / DIR_PROJECTS / "auth_service"
    proj_dir.mkdir(parents=True, exist_ok=True)
    (proj_dir / "README.md").write_text("# Auth Service\n\nStack: Python, FastAPI.", encoding="utf-8")

    res = runner.invoke(
        app,
        ["context", "auth_service", "--task", "Setup JWT refresh token", "--vault", str(tmp_path)],
    )
    assert res.exit_code == 0
    assert "Task Briefing: auth_service" in res.stdout


def test_cli_rules_commands(tmp_path: Path):
    """Test CLI devbrain rules init."""
    target_repo = tmp_path / "dummy_repo"
    target_repo.mkdir(parents=True, exist_ok=True)

    res = runner.invoke(
        app,
        ["rules", "init", str(target_repo), "--name", "DummyApp", "--vault", str(tmp_path)],
    )
    assert res.exit_code == 0
    assert "Successfully generated AI Agent rules" in res.stdout
    assert (target_repo / "AGENTS.md").is_file()
    assert (target_repo / "CLAUDE.md").is_file()


def test_cli_skill_link_and_attach(tmp_path: Path):
    """Test CLI devbrain skill link and devbrain skill attach."""
    cfg = BrainConfig(vault_path=str(tmp_path))
    save_config(cfg, tmp_path / ".brainrc.json")

    # Create external skill folder
    ext_skill_dir = tmp_path / "ext_skills" / "docker-flow"
    ext_skill_dir.mkdir(parents=True, exist_ok=True)
    (ext_skill_dir / "SKILL.md").write_text("---\nname: docker-flow\ndescription: Docker automation\n---\n# Docker Flow", encoding="utf-8")

    # Run devbrain skill link
    res_link = runner.invoke(
        app,
        ["skill", "link", str(ext_skill_dir.parent), "--vault", str(tmp_path)],
    )
    assert res_link.exit_code == 0
    assert "Registered external skill root" in res_link.stdout

    # Run devbrain skill list to verify external skill shows up
    res_list = runner.invoke(
        app,
        ["skill", "list", "--vault", str(tmp_path)],
    )
    assert res_list.exit_code == 0
    assert "docker-flow" in res_list.stdout

    # Run devbrain skill attach to a project
    target_proj = tmp_path / "my_project"
    target_proj.mkdir(parents=True, exist_ok=True)

    res_attach = runner.invoke(
        app,
        ["skill", "attach", "docker-flow", "--project", str(target_proj), "--vault", str(tmp_path)],
    )
    assert res_attach.exit_code == 0
    assert (target_proj / ".agents" / "skills" / "docker-flow" / "SKILL.md").exists()
