"""Tests for Sprint 16: Claude Code hooks, Hermes config, and the Hermes harvester."""

import json
from pathlib import Path
import sqlite3

import pytest
from typer.testing import CliRunner
import yaml

from devbrain.cli.main import app
from devbrain.core.config import BrainConfig, save_config
from devbrain.core.constants import DIR_AGENT_SKILLS, DIR_INBOX, DIR_PROJECTS, DIR_SYSTEM
from devbrain.core.scaffolder import scaffold_vault
from devbrain.harvester.discovery import discover_sessions
from devbrain.harvester.hermes import read_core_memory
from devbrain.harvester.service import IngestionService
from devbrain.integrations import claude_hooks, hermes
from devbrain.memory.manager import MemoryManager

runner = CliRunner()

HERMES_CONFIG = """# Hermes config written by the owner
model:
  default: hermes-9router-omen-v1   # keep this comment

skills:
  external_dirs: []
  template_vars: true

memory:
  memory_enabled: true

mcp_servers:
  antigravity:
    command: C:/hermes/venv/python.exe
    args:
      - C:/hermes/mcp-servers/antigravity/server.py
    enabled: true

# ── Fallback Model ──
fallback_providers: []
"""


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    path = tmp_path / "vault"
    scaffold_vault(path, is_new=True)
    save_config(BrainConfig(vault_path=str(path)), path)
    card = path / DIR_PROJECTS / "toko" / "README.md"
    card.parent.mkdir(parents=True, exist_ok=True)
    card.write_text(
        '---\ntype: "project"\ntitle: "toko"\ncreated: "2026-11-01"\ntags: ["project"]\n'
        'local_path: "E:/work/toko"\nstatus: "active"\n---\n\n# toko\n\n## 📋 Overview\nToko online kerajinan.\n',
        encoding="utf-8",
    )
    return path


@pytest.fixture
def hermes_home(tmp_path: Path) -> Path:
    home = tmp_path / "hermes"
    (home / "memories").mkdir(parents=True)
    (home / "config.yaml").write_text(HERMES_CONFIG, encoding="utf-8")
    (home / "memories" / "MEMORY.md").write_text("Jarvis server ada di 100.x\n§\nPakai 9router combo omen", encoding="utf-8")
    (home / "memories" / "USER.md").write_text("User berbahasa Indonesia", encoding="utf-8")

    db = sqlite3.connect(home / "state.db")
    db.executescript(
        """
        CREATE TABLE sessions (id TEXT PRIMARY KEY, source TEXT, display_name TEXT, title TEXT, cwd TEXT,
            git_branch TEXT, started_at REAL, ended_at REAL, last_activity_at REAL, message_count INTEGER,
            input_tokens INTEGER, output_tokens INTEGER, cache_read_tokens INTEGER, cache_write_tokens INTEGER);
        CREATE TABLE messages (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, role TEXT, content TEXT,
            tool_name TEXT, timestamp REAL);
        """
    )
    db.execute(
        "INSERT INTO sessions VALUES ('s1', 'telegram', 'Homelab', 'Cek status server', NULL, NULL, 100, 200, 300, 4, 10, 20, 30, 0)"
    )
    db.execute("INSERT INTO sessions VALUES ('empty', 'cli', NULL, NULL, NULL, NULL, 1, 1, 1, 0, 0, 0, 0, 0)")
    db.executemany(
        "INSERT INTO messages (session_id, role, content, tool_name, timestamp) VALUES (?, ?, ?, ?, ?)",
        [
            ("s1", "user", "[Zul] cek status server jarvis", None, 1),
            ("s1", "tool", "ok", "terminal", 2),
            ("s1", "assistant", "Server jarvis aktif, uptime 3 hari.", None, 3),
            ("s1", "session_meta", None, None, 4),
        ],
    )
    db.commit()
    db.close()
    return home


# --- Claude Code hooks -----------------------------------------------------


def test_hooks_install_merge_and_uninstall(tmp_path: Path, vault: Path):
    project = tmp_path / "proj"
    settings = project / ".claude" / "settings.local.json"
    settings.parent.mkdir(parents=True)
    settings.write_text(json.dumps({
        "permissions": {"allow": ["Bash(ls)"]},
        "hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "echo mine"}]}]},
    }), encoding="utf-8")

    claude_hooks.install(project, vault)
    claude_hooks.install(project, vault)  # idempotent
    data = json.loads(settings.read_text(encoding="utf-8"))

    start_commands = [h["command"] for g in data["hooks"]["SessionStart"] for h in g["hooks"]]
    assert start_commands.count("echo mine") == 1
    assert sum(claude_hooks.HOOK_MARKER in c for c in start_commands) == 1
    assert claude_hooks.installed_events(project) == ["SessionStart", "SessionEnd"]
    assert data["permissions"] == {"allow": ["Bash(ls)"]}

    assert claude_hooks.uninstall(project)
    data = json.loads(settings.read_text(encoding="utf-8"))
    assert data["hooks"] == {"SessionStart": [{"hooks": [{"type": "command", "command": "echo mine"}]}]}
    assert not claude_hooks.uninstall(project)


def test_session_start_briefs_matching_project_only(vault: Path):
    memory = MemoryManager(vault)
    memory.remember("Deploy toko lewat GitHub Actions", scope="PROJECT", project="toko", pinned=True)
    memory.remember("Warna merek toko hijau tua", scope="PROJECT", project="toko")
    memory.remember("Fakta projek lain", scope="PROJECT", project="other")

    assert claude_hooks.find_project_for_path(vault, "E:\\work\\toko\\src") == "toko"
    assert claude_hooks.find_project_for_path(vault, "E:/work/tokoku") is None

    out = json.loads(claude_hooks.run_session_start({"cwd": "E:\\work\\toko"}, vault))
    context = out["hookSpecificOutput"]["additionalContext"]
    assert out["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "Core Memory" in context and "GitHub Actions" in context
    assert "hijau tua" in context and "Fakta projek lain" not in context
    assert 'project="toko"' in context
    assert len(context) <= claude_hooks.BRIEFING_MAX_CHARS + 400

    assert claude_hooks.run_session_start({"cwd": "C:/somewhere/else"}, vault) == ""


def test_session_end_starts_background_harvest(vault: Path):
    started = []
    args = claude_hooks.run_session_end({"transcript_path": "x.jsonl"}, vault, spawn=started.append)
    assert started == [args]
    assert args[-5:] == ["ingest", "--from", "claude-code", "--vault", str(vault.resolve())]


def test_hook_runner_never_fails(vault: Path):
    result = runner.invoke(app, ["hooks", "run", "session-start", "--vault", str(vault)], input="not json")
    assert result.exit_code == 0 and result.stdout == ""


# --- Hermes config ---------------------------------------------------------


def test_hermes_home_resolution(tmp_path: Path, hermes_home: Path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(hermes_home))
    assert hermes.hermes_home() == hermes_home
    monkeypatch.delenv("HERMES_HOME")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))  # holds the "hermes" fixture folder
    assert hermes.hermes_home() == hermes_home


def test_hermes_connect_keeps_comments_and_backs_up(vault: Path, hermes_home: Path):
    result = hermes.connect(vault, hermes_home)
    text = (hermes_home / "config.yaml").read_text(encoding="utf-8")
    data = yaml.safe_load(text)

    assert "# keep this comment" in text and "# ── Fallback Model ──" in text
    assert data["mcp_servers"]["antigravity"]["enabled"] is True
    server = data["mcp_servers"]["central-brain"]
    assert server["args"][-1] == str(vault.resolve()) and "FASTEMBED_CACHE_PATH" in server["env"]
    assert result["skills_dir"] in data["skills"]["external_dirs"]
    assert data["skills"]["template_vars"] is True
    assert result["backup"].read_text(encoding="utf-8") == HERMES_CONFIG

    # Connecting again replaces rather than duplicates
    hermes.connect(vault, hermes_home)
    again = yaml.safe_load((hermes_home / "config.yaml").read_text(encoding="utf-8"))
    assert list(again["mcp_servers"]) == ["antigravity", "central-brain"]
    assert again["skills"]["external_dirs"].count(result["skills_dir"]) == 1

    hermes.disconnect(hermes_home, vault)
    final = yaml.safe_load((hermes_home / "config.yaml").read_text(encoding="utf-8"))
    assert "central-brain" not in final["mcp_servers"] and final["skills"]["external_dirs"] == []
    assert final["fallback_providers"] == []


def test_hermes_cli_status(vault: Path, hermes_home: Path):
    runner.invoke(app, ["hermes", "connect", "--vault", str(vault), "--home", str(hermes_home)])
    out = runner.invoke(app, ["hermes", "status", "--home", str(hermes_home)]).output
    assert "configured" in out and DIR_AGENT_SKILLS.split("/")[-1] in out


# --- Hermes harvester ------------------------------------------------------


def test_hermes_sessions_and_core_memory_are_harvested(vault: Path, hermes_home: Path):
    sessions = discover_sessions(sources=["hermes"], custom_paths={"hermes": hermes_home})
    assert [s.session_id for s in sessions] == ["s1"]  # sessions without messages are skipped

    assert read_core_memory(hermes_home) == {
        "memory": ["Jarvis server ada di 100.x", "Pakai 9router combo omen"],
        "user": ["User berbahasa Indonesia"],
    }

    service = IngestionService(vault, BrainConfig(vault_path=str(vault)))
    result = service.run_ingestion(sources=["hermes"], custom_paths={"hermes": hermes_home})
    assert result.ingested == 1

    note = next((vault / DIR_INBOX / "hermes").glob("*.md")).read_text(encoding="utf-8")
    assert 'title: "Cek status server"' in note
    assert "cek status server jarvis" in note and "uptime 3 hari" in note
    assert "telegram: Homelab" in note and "terminal ×1" in note

    mirror = vault / DIR_SYSTEM / "Hermes_Memory.md"
    assert "Pakai 9router combo omen" in mirror.read_text(encoding="utf-8")

    # Unchanged memory is not rewritten
    before = mirror.stat().st_mtime_ns
    IngestionService(vault, BrainConfig(vault_path=str(vault))).run_ingestion(
        sources=["hermes"], custom_paths={"hermes": hermes_home}
    )
    assert mirror.stat().st_mtime_ns == before


def test_sessions_in_a_parent_folder_link_to_no_project(tmp_path: Path, vault: Path):
    from devbrain.harvester.entity_linker import match_session_to_project

    home_like = tmp_path / "home"
    project = home_like / "Downloads" / "case" / "1_api"
    project.mkdir(parents=True)
    (project / "package.json").write_text(json.dumps({"name": "case-api"}), encoding="utf-8")
    card = vault / DIR_PROJECTS / "case-api" / "README.md"
    card.parent.mkdir(parents=True)
    card.write_text(f'---\ntitle: "case-api"\nlocal_path: "{project.as_posix()}"\n---\n', encoding="utf-8")

    assert match_session_to_project(str(project / "src"), vault) == ("case-api", "10_Projects/case-api/README")
    assert match_session_to_project(str(home_like), vault) is None
    # A bare folder name that happens to occur in the path is not a match
    assert match_session_to_project(str(tmp_path / "case-api-old"), vault) is None


def test_auto_provision_skips_folders_that_are_not_projects(tmp_path: Path, vault: Path):
    from datetime import datetime, timezone
    from unittest.mock import patch

    from devbrain.harvester.discovery import HarvestableSession
    from devbrain.harvester.extractor import ExtractedSessionPayload

    home_like = tmp_path / "home"
    nested = home_like / "Downloads" / "notes"
    nested.mkdir(parents=True)
    (nested / "a.md").write_text("# a\n", encoding="utf-8")
    _node_project = home_like / "Downloads" / "proj"
    _node_project.mkdir()
    (_node_project / "package.json").write_text("{}", encoding="utf-8")

    session = HarvestableSession("s", "hermes", tmp_path, [], 1.0)
    payload = ExtractedSessionPayload(
        session_id="s", source_name="hermes", title="t", summary="s", body_markdown="b", tags=[],
        created_time=datetime.now(timezone.utc), num_redactions=0, workspace_hint=str(home_like),
    )
    service = IngestionService(vault, BrainConfig(vault_path=str(vault)))
    with patch("devbrain.harvester.service.discover_sessions", return_value=[session]), patch(
        "devbrain.harvester.service.extract_session_payload", return_value=payload
    ):
        result = service.run_ingestion(sources=["hermes"])

    assert result.ingested == 1 and result.linked_projects == 0
    cards = {p.name for p in (vault / DIR_PROJECTS).iterdir() if p.is_dir()}
    assert "proj" not in cards and not (vault / "20_Knowledge" / "References" / "notes").exists()
