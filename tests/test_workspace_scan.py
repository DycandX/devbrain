"""Tests for scanning a workspace with nested, grouped, and sandbox project folders."""

import json
from pathlib import Path

import pytest

from devbrain.context.builder import ContextAssemblyEngine
from devbrain.core.config import BrainConfig, ProjectGroup, save_config
from devbrain.core.constants import DIR_KNOWLEDGE, DIR_PROJECTS
from devbrain.core.scaffolder import scaffold_vault
from devbrain.engine.hybrid_search import HybridEngine
from devbrain.engine.parser import parse_frontmatter
from devbrain.harvester.inspector import RepoType, inspect_repository_type
from devbrain.harvester.manifest_parser import parse_repository_manifest
from devbrain.harvester.markers import find_subprojects, is_obsidian_vault, looks_like_sandbox
from devbrain.harvester.service import IngestionService


def _node(path: Path, name: str, description: str = "") -> Path:
    path.mkdir(parents=True, exist_ok=True)
    (path / "package.json").write_text(
        json.dumps({"name": name, "description": description, "dependencies": {"next": "16"}}), encoding="utf-8"
    )
    return path


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """E:/_PROJECT in miniature."""
    root = tmp_path / "workspace"
    _node(root / "personal-web", "personal-web")
    _node(root / "_fxmedia" / "jam-dev-be", "jam-dev-be", "Backend untuk aplikasi jam kerja.")
    _node(root / "_fxmedia" / "nested" / "deep-api", "deep-api")
    docs = root / "_fxmedia" / "DOCS"
    docs.mkdir(parents=True)
    (docs / "onboarding.md").write_text("# Onboarding\n\nPanduan magang.\n", encoding="utf-8")
    _node(root / "_TEST" / "jarvis-fe-prototype", "jarvis-fe-prototype", "Prototipe antarmuka Jarvis.")
    (root / "_TEST" / "scratch-notes").mkdir()
    (root / "_TEST" / "scratch-notes" / "x.txt").write_text("coba", encoding="utf-8")
    test_vault = root / "_TEST" / "Some_Vault"
    (test_vault / ".obsidian").mkdir(parents=True)
    (test_vault / "note.md").write_text("# n\n", encoding="utf-8")
    flutter = root / "Belajar_Flutter" / "app_satu"
    flutter.mkdir(parents=True)
    (flutter / "pubspec.yaml").write_text(
        "name: app_satu\ndescription: Aplikasi latihan.\ndependencies:\n  flutter:\n    sdk: flutter\n  http: ^1.0.0\n",
        encoding="utf-8",
    )
    (root / "empty-folder").mkdir()
    return root


@pytest.fixture
def service(tmp_path: Path, workspace: Path) -> IngestionService:
    vault = tmp_path / "vault"
    scaffold_vault(vault, is_new=True)
    config = BrainConfig(
        vault_path=str(vault),
        workspace_roots=[str(workspace)],
        project_groups={"_fxmedia": ProjectGroup(label="Magang FXMedia")},
    )
    save_config(config, vault)
    return IngestionService(vault, config)


def _card(service: IngestionService, name: str) -> dict:
    text = (service.vault_path / DIR_PROJECTS / name / "README.md").read_text(encoding="utf-8")
    return parse_frontmatter(text)[0]


def test_markers_tell_projects_vaults_and_containers_apart(workspace: Path):
    assert is_obsidian_vault(workspace / "_TEST" / "Some_Vault")
    assert not is_obsidian_vault(workspace / "personal-web")

    # A codebase that keeps notes in Obsidian is still a project
    hybrid = _node(workspace / "hybrid", "hybrid")
    (hybrid / ".obsidian").mkdir()
    assert not is_obsidian_vault(hybrid)

    names = {p.name for p in find_subprojects(workspace / "_fxmedia")}
    assert names == {"jam-dev-be", "deep-api"}
    assert inspect_repository_type(workspace / "_fxmedia")[0] == RepoType.CONTAINER
    assert inspect_repository_type(workspace / "_TEST" / "Some_Vault")[0] == RepoType.UNKNOWN

    # The first word of a group folder's name decides
    assert looks_like_sandbox("_TEST") and looks_like_sandbox("sandbox") and looks_like_sandbox("test readme")
    assert not looks_like_sandbox("_fxmedia") and not looks_like_sandbox("flowkit-test-suite")


def test_manifest_parser_recognizes_flutter_and_laravel(tmp_path: Path, workspace: Path):
    flutter = parse_repository_manifest(workspace / "Belajar_Flutter" / "app_satu")
    assert flutter.name == "app_satu" and flutter.languages == ["Dart"]
    assert "Flutter" in flutter.stack_tags and flutter.dependencies == ["http"]

    laravel = tmp_path / "toko"
    laravel.mkdir()
    (laravel / "composer.json").write_text(
        json.dumps({"name": "acme/toko", "require": {"php": "^8.2", "laravel/framework": "^11.0"}}), encoding="utf-8"
    )
    php = parse_repository_manifest(laravel)
    assert php.name == "toko" and php.languages == ["PHP"] and php.stack_tags == ["Laravel"]

    java = tmp_path / "svc"
    java.mkdir()
    (java / "pom.xml").write_text("<project/>", encoding="utf-8")
    assert parse_repository_manifest(java).languages == ["Java"]


def test_workspace_scan_descends_and_groups(service: IngestionService):
    results = service.ingest_workspace_projects()
    found = {meta.name: meta for meta, _ in results}

    assert set(found) == {
        "personal-web", "jam-dev-be", "deep-api", "DOCS", "jarvis-fe-prototype", "app_satu",
    }

    # Ungrouped top-level project
    assert found["personal-web"].group is None
    assert "group" not in _card(service, "personal-web")

    # Configured group: label from config, nested projects keep the outermost group
    jam = _card(service, "jam-dev-be")
    assert jam["group"] == "Magang FXMedia" and "group/fxmedia" in jam["tags"]
    assert "sandbox" not in jam
    assert found["deep-api"].group == "_fxmedia"

    # Sandbox is inferred from the folder name
    proto = _card(service, "jarvis-fe-prototype")
    assert proto["group"] == "TEST" and proto["sandbox"] is True and "sandbox" in proto["tags"]

    # A folder wrapping a single project is not a group
    assert "group" not in _card(service, "app_satu")

    # A documents folder inside a group is recorded as knowledge
    docs = service.vault_path / DIR_KNOWLEDGE / "References" / "DOCS" / "README.md"
    assert parse_frontmatter(docs.read_text(encoding="utf-8"))[0]["group"] == "Magang FXMedia"

    # Vaults and folders without code are not turned into cards
    cards = {p.name for p in (service.vault_path / DIR_PROJECTS).iterdir() if p.is_dir()}
    assert "Some_Vault" not in cards and "scratch-notes" not in cards and "empty-folder" not in cards


def test_dry_run_reports_without_writing(service: IngestionService):
    results = service.ingest_workspace_projects(dry_run=True)

    assert len(results) == 6 and all(path is None for _, path in results)
    assert not (service.vault_path / DIR_PROJECTS / "jam-dev-be").exists()


def test_single_project_infers_group_and_container_names_it(service: IngestionService, workspace: Path):
    meta, path = service.ingest_single_project(workspace / "_fxmedia" / "jam-dev-be")
    assert meta.group == "_fxmedia" and meta.group_label == "Magang FXMedia" and path.is_file()

    meta, _ = service.ingest_single_project(workspace / "personal-web")
    assert meta.group is None

    container, subs = service.ingest_single_project(workspace / "_TEST")
    assert container.repo_type == RepoType.CONTAINER
    assert [m.name for m, _ in subs] == ["jarvis-fe-prototype"] and subs[0][0].sandbox


def test_same_name_in_two_groups_gets_separate_cards(service: IngestionService, workspace: Path):
    _node(workspace / "api", "api")
    _node(workspace / "_fxmedia" / "api", "api")

    service.ingest_workspace_projects()

    assert _card(service, "api")["local_path"].endswith("/workspace/api")
    assert _card(service, "fxmedia-api")["local_path"].endswith("/_fxmedia/api")

    # Rescanning keeps each project on its own card
    service.ingest_workspace_projects()
    cards = sorted(p.name for p in (service.vault_path / DIR_PROJECTS).iterdir() if "api" in p.name and p.is_dir())
    assert cards == ["api", "deep-api", "fxmedia-api"]


def test_rescan_keeps_session_links_on_the_card(service: IngestionService, workspace: Path):
    _, card = service.ingest_single_project(workspace / "personal-web")
    card.write_text(
        card.read_text(encoding="utf-8") + "\n\n## 📜 Riwayat Sesi AI Terkini\n- [[90_Agent_Inbox/x|2026-01-01 — Sesi]]\n",
        encoding="utf-8",
    )

    service.ingest_single_project(workspace / "personal-web")

    text = card.read_text(encoding="utf-8")
    assert text.count("90_Agent_Inbox/x") == 1


def test_sandbox_cards_stay_out_of_other_projects_briefings(service: IngestionService):
    service.ingest_workspace_projects()
    vault = service.vault_path
    engine = HybridEngine.from_config(vault)
    engine.index_vault()
    builder = ContextAssemblyEngine(vault, engine=engine)
    task = "Prototipe antarmuka Jarvis"

    # The sandbox card matches the task, and plain search still finds it
    assert any("jarvis-fe-prototype" in h.doc_id for h in engine.search(task, one_per_note=True))

    other = builder.select_relevant_notes(task, "personal-web", limit=10)
    assert not any("jarvis-fe-prototype" in n["path"] for n in other)


def test_project_with_skills_folder_stays_a_project(tmp_path: Path):
    repo = _node(tmp_path / "portfolio", "portfolio")
    (repo / "skills" / "deploy").mkdir(parents=True)
    assert inspect_repository_type(repo)[0] == RepoType.PROJECT

    library = tmp_path / "skill-library"
    (library / "skills" / "deploy").mkdir(parents=True)
    assert inspect_repository_type(library)[0] == RepoType.SKILL
