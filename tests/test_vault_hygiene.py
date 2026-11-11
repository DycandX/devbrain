"""Tests for Sprint 14: note writers produce clean notes, and lint repairs old ones."""

from datetime import datetime, timezone
import json
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from devbrain.adr.manager import ADRManager
from devbrain.cli.main import app
from devbrain.context.builder import ContextAssemblyEngine
from devbrain.core.constants import DIR_DAILY, DIR_PROJECTS, DIR_SYSTEM
from devbrain.engine.parser import parse_frontmatter, parse_markdown_file
from devbrain.harvester.entity_linker import generate_graph_links_block, inject_backlink_to_project
from devbrain.harvester.extractor import ExtractedSessionPayload, clean_user_prompt, sanitize_frontmatter_string
from devbrain.harvester.formatter import format_session_note
from devbrain.harvester.project_harvester import scan_project_metadata, seed_project_to_vault
from devbrain.maintenance.lint import lint_vault

runner = CliRunner()


def _fm(path: Path) -> dict:
    return parse_frontmatter(path.read_text(encoding="utf-8"))[0]


# --- Writers ---------------------------------------------------------------


def test_harness_blocks_are_removed_from_prompts():
    raw = (
        "<USER_REQUEST>cek versi opencode</USER_REQUEST>\n"
        "<ADDITIONAL_METADATA>cwd: E:/x</ADDITIONAL_METADATA>\n"
        "<USER_SETTINGS_CHANGE>\nThe user changed setting `Model Selection` from None to Gemini. "
        "No need to comment.\n</USER_SETTINGS_CHANGE>"
    )
    assert clean_user_prompt(raw) == "cek versi opencode"
    # A notice whose tags were stripped earlier and that was cut off mid-word
    assert sanitize_frontmatter_string("Task: cek agy The user changed setting `Mod...") == "Task: cek agy"


def test_session_note_frontmatter_survives_backslashes_and_quotes():
    payload = ExtractedSessionPayload(
        session_id="abc", source_name="claude-code",
        title="@'E:\\_PROJECT\\_fxmedia\\docs\\plan.md' baca \"ini\"", summary="s", body_markdown="b",
        tags=["x"], created_time=datetime(2026, 11, 1, tzinfo=timezone.utc), num_redactions=0,
    )
    _, content = format_session_note(payload, device_name="omen-15")
    meta = yaml.safe_load(content.split("---")[1])
    assert meta["title"].startswith("@'E:\\_PROJECT")


def test_graph_block_has_no_daily_link():
    block = generate_graph_links_block(datetime(2026, 11, 1), ("toko", "10_Projects/toko/README"), "omen")
    assert "99_Daily" not in block and "[[10_Projects/toko/README|toko]]" in block


def test_project_card_aliases_created_and_clean_history(tmp_path: Path):
    repo = tmp_path / "toko-online"
    repo.mkdir()
    (repo / "package.json").write_text(json.dumps({"name": "toko-online"}), encoding="utf-8")
    vault = tmp_path / "vault"

    card = seed_project_to_vault(scan_project_metadata(repo), vault)
    meta = _fm(card)
    assert meta["aliases"] == ["toko-online"] and meta["created"]
    assert "(Live Dataview):" not in card.read_text(encoding="utf-8")

    # A session link lands on its own line under the heading
    assert inject_backlink_to_project(card, "Sesi A", "90_Agent_Inbox/a.md", "2026-11-01")
    text = card.read_text(encoding="utf-8")
    assert "- [[90_Agent_Inbox/a.md|2026-11-01 — Sesi A]]\n" in text

    # Rescanning keeps the creation time and the link, without duplicating either
    seed_project_to_vault(scan_project_metadata(repo), vault)
    rescanned = card.read_text(encoding="utf-8")
    assert _fm(card)["created"] == meta["created"]
    assert rescanned.count("90_Agent_Inbox/a.md") == 1


def test_view_blocks_are_not_indexed(tmp_path: Path):
    note = tmp_path / "n.md"
    note.write_text(
        "# Catatan\n\nIsi penting.\n\n```dataview\nTABLE created FROM \"x\"\n```\n\n```python\nprint(1)\n```\n",
        encoding="utf-8",
    )
    body = parse_markdown_file(note, tmp_path).raw_content
    assert "TABLE created" not in body and "print(1)" in body and "Isi penting." in body


# --- Lint ------------------------------------------------------------------


@pytest.fixture
def messy_vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"

    def note(rel: str, text: str) -> None:
        path = vault / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    note(f"{DIR_SYSTEM}/User_Preferences.md", "# User Preferences\n\n- Bahasa Indonesia\n")
    note("90_Agent_Inbox/claude-code/broken.md",
         # "\h" is not a valid escape in a double-quoted YAML scalar
         '---\ntitle: "@\'E:\\_PROJECT\\hvac\'"\ntype: "agent-session-log"\ncreated: "2026-11-01"\ntags: []\n---\n\n# Sesi\n')
    note("90_Agent_Inbox/antigravity-ide/noisy.md",
         '---\ntitle: "Task: cek agy The user changed se..."\ntype: "agent-session-log"\ncreated: "2026-08-26"\ntags: []\n---\n\n'
         "# 📝 Task: cek agy The user changed se...\n\n## 🔗 Graph Connections & Context:\n"
         "- **Project Hub:** [[10_Projects/devbrain/README|devbrain]]\n- **Timeline:** [[99_Daily/2026-08-26|2026-08-26]]\n\n"
         "## 🎯 Initial User Goal\ncek agy The user changed setting `Model Selection` from None to Gemini.\n")
    note(f"{DIR_PROJECTS}/devbrain/README.md",
         '---\nid: "PROJ-DEVBRAIN"\ntitle: "devbrain"\ntype: "project"\nlast_scanned: "2026-08-30T02:33:31+00:00"\ntags: ["project"]\n---\n\n'
         "# devbrain\n\n## 📜 Riwayat Sesi AI Terkini\n- [[90_Agent_Inbox/x.md|Sesi]] (Live Dataview): (Live Dataview):\n"
         "- [[90_Agent_Inbox/y.md|2026-08-26 — Task: cek agy The user changed se...]]\n```dataview\nTABLE x\n```\n")
    note("30_Decisions/ADR-001-old.md", "---\nid: \"ADR-001\"\ntitle: \"Old\"\nstatus: accepted\ndate: 2026-08-29\ntags: [adr]\n---\n\n# ADR-001: Old\n")
    note("00_System/Agent_Skills/demo/SKILL.md", "---\nname: demo\ndescription: \"Demo skill\"\n---\n\n# Demo\n")
    note(f"{DIR_DAILY}/2026-08-27.md", "---\ntype: daily\ntitle: \"2026-08-27\"\ncreated: \"2026-08-27\"\ntags: []\n---\n")
    note("20_Knowledge/link.md",
         '---\ntype: "knowledge-doc"\ntitle: "L"\ncreated: "2026-08-27"\ntags: []\n---\n\nLihat [[99_Daily/2026-08-27|kemarin]] dan [[99_Daily/2026-01-01|lama]].\n')
    return vault


def test_lint_reports_without_changing_files(messy_vault: Path):
    before = {p: p.read_bytes() for p in messy_vault.rglob("*.md")}
    reports = {r.rel_path: {i.rule for i in r.issues} for r in lint_vault(messy_vault)}

    assert reports["90_Agent_Inbox/claude-code/broken.md"] == {"invalid-yaml"}
    assert reports[f"{DIR_SYSTEM}/User_Preferences.md"] == {"missing-frontmatter"}
    assert reports["90_Agent_Inbox/antigravity-ide/noisy.md"] == {"broken-daily-link", "noisy-title"}
    assert reports[f"{DIR_PROJECTS}/devbrain/README.md"] == {
        "missing-keys", "project-aliases", "noisy-link-label", "legacy-suffix",
    }
    assert reports["30_Decisions/ADR-001-old.md"] == {"missing-keys"}
    assert reports["20_Knowledge/link.md"] == {"broken-daily-link"}
    assert "00_System/Agent_Skills/demo/SKILL.md" not in reports  # skills follow their own format
    assert before == {p: p.read_bytes() for p in messy_vault.rglob("*.md")}


def test_lint_fix_repairs_everything(messy_vault: Path):
    lint_vault(messy_vault, fix=True)
    assert lint_vault(messy_vault) == []

    assert _fm(messy_vault / "90_Agent_Inbox/claude-code/broken.md")["title"] == "@'E:\\_PROJECT\\hvac'"

    noisy = messy_vault / "90_Agent_Inbox/antigravity-ide/noisy.md"
    text = noisy.read_text(encoding="utf-8")
    assert _fm(noisy)["title"] == "Task: cek agy"
    assert "# 📝 Task: cek agy\n\n## 🔗" in text
    assert "99_Daily" not in text and "The user changed" not in text

    card = messy_vault / f"{DIR_PROJECTS}/devbrain/README.md"
    meta = _fm(card)
    assert meta["aliases"] == ["devbrain"] and meta["created"] == "2026-08-30T02:33:31+00:00"
    card_text = card.read_text(encoding="utf-8")
    assert "- [[90_Agent_Inbox/x.md|Sesi]]\n" in card_text
    assert "- [[90_Agent_Inbox/y.md|2026-08-26 — Task: cek agy]]\n\n```dataview" in card_text

    adr = _fm(messy_vault / "30_Decisions/ADR-001-old.md")
    assert adr["type"] == "adr" and str(adr["created"]) == "2026-08-29"

    link = (messy_vault / "20_Knowledge/link.md").read_text(encoding="utf-8")
    assert "[[99_Daily/2026-08-27|kemarin]]" in link and "dan lama." in link

    # Frontmatter added to the preferences file never reaches a briefing
    prefs = ContextAssemblyEngine(messy_vault).get_user_preferences()
    assert prefs.startswith("# User Preferences") and "type:" not in prefs


def test_lint_cli(messy_vault: Path):
    dry = runner.invoke(app, ["lint", "--vault", str(messy_vault)])
    assert dry.exit_code == 0 and "Run with --fix" in dry.output

    fixed = runner.invoke(app, ["lint", "--fix", "--vault", str(messy_vault)])
    assert fixed.exit_code == 0 and "Repaired" in fixed.output
    assert "No issues found" in runner.invoke(app, ["lint", "--vault", str(messy_vault)]).output


# --- ADR supersede ---------------------------------------------------------


def test_adr_supersede(tmp_path: Path):
    manager = ADRManager(tmp_path)
    old = manager.create_decision(title="Use bge-small", context="c", decision="d")
    new = manager.create_decision(title="Use multilingual model", context="c", decision="d")

    result = manager.supersede_decision("adr-001", new["id"])
    assert result["old"] == "ADR-001" and result["new"] == "ADR-002"

    accepted = [d["id"] for d in manager.list_decisions(status="accepted")]
    assert accepted == ["ADR-002"]

    old_file = Path(old["file_path"])
    old_meta = _fm(old_file)
    assert old_meta["status"] == "superseded" and old_meta["superseded_by"] == "ADR-002"
    assert "**Superseded by** [[" in old_file.read_text(encoding="utf-8")
    assert _fm(Path(new["file_path"]))["supersedes"] == "ADR-001"

    # Running it twice does not duplicate the notice
    manager.supersede_decision("ADR-001", "ADR-002")
    assert old_file.read_text(encoding="utf-8").count("Superseded by") == 1

    with pytest.raises(FileNotFoundError):
        manager.supersede_decision("ADR-001", "ADR-009")
    with pytest.raises(ValueError):
        manager.supersede_decision("ADR-002", "ADR-002")

    out = runner.invoke(app, ["adr", "supersede", "ADR-001", "ADR-002", "--vault", str(tmp_path)])
    assert out.exit_code == 0 and "superseded by ADR-002" in out.output
