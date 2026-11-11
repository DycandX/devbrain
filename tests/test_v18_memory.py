"""Tests for v1.8: long-term memory, sized tool output, and usage reporting."""

import asyncio
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from devbrain.cli.main import app
from devbrain.core.config import BrainConfig, save_config
from devbrain.core.constants import DIR_MEMORIES, DIR_PROJECTS
from devbrain.core.scaffolder import scaffold_vault
from devbrain.core.textutil import extract_section, one_line, truncate_to_budget
from devbrain.harvester.usage_stats import collect_claude_usage
from devbrain.mcp_server.server import create_mcp_server
from devbrain.memory.manager import MemoryManager

runner = CliRunner()


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    path = tmp_path / "vault"
    scaffold_vault(path, is_new=True)
    save_config(BrainConfig(vault_path=str(path), device_name="test-machine"), path)
    return path


def _call(server, tool: str, args: dict) -> str:
    result = asyncio.run(server.call_tool(tool, args))
    content = result if isinstance(result, list) else result.content
    return content[0].text


# --- Text budget helpers ---------------------------------------------------


def test_truncate_to_budget_cuts_at_line_and_reports_omission():
    text = "\n".join(f"line {i}" for i in range(200))
    out = truncate_to_budget(text, 100, "Use read_note.")

    assert len(out) < 200
    assert "more characters omitted. Use read_note.]" in out
    assert truncate_to_budget("short", 100) == "short"


def test_extract_section_stops_at_same_level_heading():
    doc = "# Title\n\n## Setup\nstep one\n\n### Detail\nmore\n\n## Usage\nrun it\n"

    assert extract_section(doc, "setup") == "## Setup\nstep one\n\n### Detail\nmore"
    assert extract_section(doc, "Usage") == "## Usage\nrun it"
    assert extract_section(doc, "missing") is None
    assert one_line("a\n  b   c", 10) == "a b c"


# --- Memory lifecycle ------------------------------------------------------


def test_memory_remember_recall_supersede_forget(vault: Path):
    memory = MemoryManager(vault)

    first = memory.remember("Pengguna lebih suka TypeScript mode strict untuk semua projek frontend")
    assert first["created"]
    assert (vault / DIR_MEMORIES / f"{first['id']}.md").is_file()

    # Same text again is not stored twice
    assert memory.remember("Pengguna lebih suka TypeScript  mode strict untuk semua projek frontend") == {
        "id": first["id"], "created": False, "status": "active", "superseded": None,
    }

    scoped = memory.remember(
        "Gerbang pembayaran toko memakai Midtrans Snap", scope="PROJECT", project="toko-online"
    )

    hits = memory.recall("bahasa pemrograman frontend yang disukai")
    assert hits and hits[0]["id"] == first["id"]

    # Project memories stay out of other projects; global ones are shared
    other = memory.recall("gerbang pembayaran midtrans", project="synapse-cs")
    assert scoped["id"] not in [m["id"] for m in other]
    own = memory.recall("gerbang pembayaran midtrans", project="toko-online")
    assert own and own[0]["id"] == scoped["id"]

    # Superseding retires the old memory and removes its note
    newer = memory.remember(
        "Pengguna sekarang memakai Python dengan type hints ketat untuk backend", supersedes=first["id"]
    )
    assert newer["superseded"] == first["id"]
    assert not (vault / DIR_MEMORIES / f"{first['id']}.md").exists()
    assert memory.sqlite.get_memory(first["id"])["status"] == "superseded"
    assert first["id"] not in [m["id"] for m in memory.recall("TypeScript mode strict frontend")]

    assert memory.forget(scoped["id"])
    assert memory.sqlite.get_memory(scoped["id"])["status"] == "forgotten"
    assert memory.recall("gerbang pembayaran midtrans", project="toko-online") == []
    assert not memory.forget("mem_does_not_exist")


def test_memory_rejects_invalid_input(vault: Path):
    memory = MemoryManager(vault)

    with pytest.raises(ValueError):
        memory.remember("   ")
    with pytest.raises(ValueError):
        memory.remember("x" * 1001)
    with pytest.raises(ValueError):
        memory.remember("fact", scope="PROJECT")
    with pytest.raises(ValueError):
        memory.remember("fact", scope="EVERYWHERE")


# --- MCP tools -------------------------------------------------------------


def test_mcp_memory_tools_and_briefing(vault: Path):
    server = create_mcp_server(vault)
    tool_names = {t.name for t in asyncio.run(server.list_tools())}
    assert {"remember", "recall", "forget", "read_note"} <= tool_names

    saved = _call(server, "remember", {
        "content": "Deploy example_project selalu lewat GitHub Actions, jangan manual",
        "scope": "PROJECT", "project": "example_project",
    })
    memory_id = saved.split("`")[1]
    assert memory_id.startswith("mem_")

    assert memory_id in _call(server, "recall", {"query": "cara deploy", "project": "example_project"})
    assert "Not saved" in _call(server, "remember", {"content": "x", "scope": "PROJECT"})

    briefing = _call(server, "build_task_context", {"task": "deploy ke produksi", "project": "example_project"})
    assert "Remembered Facts" in briefing and "GitHub Actions" in briefing

    # A project's own memories reach its briefing even when the task wording does not
    # match them; another project's memories never do. Global memories stand in for
    # the preferences file, and join the remembered facts only on a match.
    _call(server, "remember", {"content": "Warna merek toko adalah hijau tua", "scope": "PROJECT", "project": "toko"})
    _call(server, "remember", {"content": "Pengguna tinggal di Semarang"})
    unrelated = _call(server, "build_task_context", {"task": "tulis ulang parser tanggal", "project": "example_project"})
    remembered = unrelated.split("## 🧠 Remembered Facts")[1].split("---")[0]
    assert "GitHub Actions" in remembered
    assert "hijau tua" not in unrelated
    assert "Semarang" not in remembered
    assert "Semarang" in unrelated.split("## 👤")[1].split("---")[0]

    assert "Forgot" in _call(server, "forget", {"memory_id": memory_id})
    assert _call(server, "recall", {"query": "cara deploy", "project": "example_project"}) == "No matching memories."


def test_search_index_then_read_note(vault: Path):
    note = vault / "20_Knowledge" / "long-note.md"
    sections = "\n\n".join(f"## Bagian {i}\n" + ("Isi tentang pipeline deployment kontainer. " * 40) for i in range(8))
    note.write_text(f"# Panduan Deployment Kontainer\n\n{sections}\n", encoding="utf-8")

    server = create_mcp_server(vault)

    index = _call(server, "search_brain", {"query": "pipeline deployment kontainer", "limit": 5})
    # One line per note even though many chunks of the same note match
    assert index.count("20_Knowledge/long-note.md") == 1
    assert len(index) < 1500

    whole = _call(server, "read_note", {"path": "20_Knowledge/long-note.md", "max_chars": 800})
    assert len(whole) < 1100 and "more characters omitted" in whole

    section = _call(server, "read_note", {"path": "20_Knowledge/long-note.md", "heading": "Bagian 3", "max_chars": 4000})
    assert section.startswith("## Bagian 3") and "## Bagian 4" not in section

    assert "Headings:" in _call(server, "read_note", {"path": "20_Knowledge/long-note.md", "heading": "tidak ada"})


def test_read_note_and_load_skill_stay_inside_vault(vault: Path, tmp_path: Path):
    secret = tmp_path / "outside.md"
    secret.write_text("# Outside\nprivate", encoding="utf-8")
    (tmp_path / "evil").mkdir()
    (tmp_path / "evil" / "SKILL.md").write_text("stolen", encoding="utf-8")

    server = create_mcp_server(vault)

    assert "not found" in _call(server, "read_note", {"path": "../outside.md"})
    assert "not found" in _call(server, "read_note", {"path": str(secret)})
    assert "stolen" not in _call(server, "load_skill", {"skill_name": "../../../evil"})


def test_project_context_is_capped(vault: Path):
    card = vault / DIR_PROJECTS / "big_project.md"
    card.write_text("# Big Project\n\n" + ("Deskripsi panjang projek. " * 2000), encoding="utf-8")

    server = create_mcp_server(vault)
    out = _call(server, "get_project_context", {"project_name": "big_project"})

    assert len(out) < 7000 and "more characters omitted" in out


# --- Usage report ----------------------------------------------------------


def _session(cwd: str, brain_calls: int) -> list[dict]:
    usage = {"input_tokens": 100, "output_tokens": 50, "cache_read_input_tokens": 900,
             "cache_creation_input_tokens": 0}
    records = [{"type": "user", "cwd": cwd, "message": {"role": "user", "content": "do the thing"}}]
    for i in range(brain_calls):
        records.append({"type": "assistant", "message": {"id": f"b{i}", "usage": usage, "content": [
            {"type": "tool_use", "name": "mcp__central-brain__search_brain", "input": {"query": "x"}}]}})
    records.append({"type": "assistant", "message": {"id": "final", "usage": usage, "content": [
        {"type": "text", "text": "done"}]}})
    return records


def test_usage_is_aggregated_per_project(tmp_path: Path, isolated_home: Path):
    root = isolated_home / ".claude" / "projects"
    for folder, name, cwd, calls in [
        ("E--work-app", "s1.jsonl", "E:\\work\\app", 2),
        ("E--work-app", "s2.jsonl", "E:\\work\\app", 0),
        ("E--work-api", "s3.jsonl", "E:/work/api", 0),
    ]:
        path = root / folder / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(json.dumps(r) for r in _session(cwd, calls)), encoding="utf-8")

    rows = {r.name: r for r in collect_claude_usage()}

    assert set(rows) == {"app", "api"}
    assert rows["app"].sessions == 2 and rows["app"].brain_calls == 2
    assert rows["app"].context_tokens == 4 * 1000  # 3 + 1 assistant messages
    assert rows["app"].cache_hit_ratio == 0.9

    result = runner.invoke(app, ["usage", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["total"]["sessions"] == 3
    assert payload["total"]["central_brain_calls"] == 2
