"""Tests for what a task briefing contains: project summary, linked sessions, selected notes."""

from pathlib import Path

from devbrain.context.builder import ContextAssemblyEngine
from devbrain.core.constants import DIR_INBOX, DIR_PROJECTS
from devbrain.core.textutil import first_prose_paragraph
from devbrain.engine.hybrid_search import HybridEngine
from devbrain.harvester.project_harvester import scan_project_metadata

PROJECT_CARD = """---
id: "PROJ-TOKO"
title: "toko-online"
type: "project"
status: "active"
language: ["TypeScript"]
stack: ["Next.js", "Supabase"]
local_path: "E:/work/toko-online"
tags: ["project", "codebase"]
---

# 🚀 toko-online

> **Local Path:** `E:\\work\\toko-online`

## 📋 Overview
Aplikasi e-commerce untuk penjualan produk kerajinan dengan pembayaran lokal.

---

## ⚡ Runnable Scripts:
- `dev` → `next dev`
- `build` → `next build`

---

## 🌳 Project Structure:
```text
toko-online/
└── src/
```
"""


def _session(vault: Path, name: str, title: str, created: str, project: str, body: str) -> str:
    rel = f"{DIR_INBOX}/antigravity-ide/{name}.md"
    path = vault / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    hub = f"- **Project Hub:** [[10_Projects/{project}/README|{project}]]\n" if project else ""
    path.write_text(
        f'---\ntitle: "{title}"\ntype: "agent-session-log"\ncreated: "{created}"\n---\n\n'
        f"# 📝 {title}\n\n## 🔗 Graph Connections & Context:\n{hub}\n---\n\n{body}\n",
        encoding="utf-8",
    )
    return rel


def _vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"
    card = vault / DIR_PROJECTS / "toko-online" / "README.md"
    card.parent.mkdir(parents=True)
    card.write_text(PROJECT_CARD, encoding="utf-8")
    return vault


def test_project_summary_drops_frontmatter_and_keeps_essentials(tmp_path: Path):
    vault = _vault(tmp_path)
    builder = ContextAssemblyEngine(vault)

    summary, stack = builder.get_project_summary("toko-online")

    assert stack == ["TypeScript", "Next.js", "Supabase"]
    assert "PROJ-TOKO" not in summary and "tags:" not in summary and "---" not in summary
    assert "**Path:** `E:/work/toko-online`" in summary and "**Status:** active" in summary
    assert "Aplikasi e-commerce untuk penjualan produk kerajinan" in summary
    assert "**Run:** `dev` → `next dev`; `build` → `next build`" in summary
    assert "Project Structure" not in summary

    # Name lookup tolerates case and separators
    assert builder.get_project_summary("Toko Online")[1] == stack
    assert "registered in DevBrain" in builder.get_project_summary("unknown")[0]


def test_project_summary_without_metadata_falls_back(tmp_path: Path):
    vault = tmp_path / "vault"
    card = vault / DIR_PROJECTS / "legacy.md"
    card.parent.mkdir(parents=True)
    card.write_text("# Legacy App\n\nBackend lama memakai Laravel dan Docker.\n", encoding="utf-8")

    summary, stack = ContextAssemblyEngine(vault).get_project_summary("legacy")

    assert "Backend lama memakai Laravel dan Docker." in summary
    assert stack == ["Laravel/PHP", "Docker"]


def test_recent_sessions_follow_project_hub_link(tmp_path: Path):
    vault = _vault(tmp_path)
    _session(vault, "s-old", "Setup keranjang belanja", "2026-08-01T10:00:00+00:00", "toko-online", "isi")
    newest = _session(vault, "s-new", "Integrasi pembayaran Midtrans", "2026-09-15T10:00:00+00:00", "toko-online", "isi")
    _session(vault, "s-other", "Perbaikan bot Discord", "2026-10-01T10:00:00+00:00", "discord-bot", "isi")
    # Mentions the project in prose but is not linked to it
    _session(vault, "s-mention", "Catatan umum", "2026-10-02T10:00:00+00:00", "", "Sekilas membahas toko-online.")

    recent = ContextAssemblyEngine(vault).get_recent_inbox_work("toko-online", limit=3)

    assert len(recent) == 2
    assert recent[0] == f"2026-09-15: Integrasi pembayaran Midtrans (`{newest}`)"
    assert "Setup keranjang belanja" in recent[1]


def test_briefing_selects_project_notes_and_rejects_weak_outsiders(tmp_path: Path):
    vault = _vault(tmp_path)
    own = _session(
        vault, "s-webhook", "Webhook pembayaran Midtrans", "2026-09-10T10:00:00+00:00", "toko-online",
        "## Hasil\nWebhook pembayaran Midtrans diverifikasi tanda tangannya lalu status pesanan diperbarui.",
    )
    for i in range(4):
        _session(
            vault, f"s-filler-{i}", f"Sesi pengisi {i}", f"2026-10-0{i + 1}T10:00:00+00:00", "toko-online",
            "## Hasil\nMerapikan tampilan katalog produk dan halaman keranjang.",
        )
    _session(
        vault, "s-foreign", "Webhook pembayaran di projek lain", "2026-09-11T10:00:00+00:00", "discord-bot",
        "## Hasil\nWebhook pembayaran Midtrans untuk projek lain, tidak terkait.",
    )
    unlinked = _session(
        vault, "s-unlinked", "Catatan webhook pembayaran Midtrans", "2026-07-01T10:00:00+00:00", "",
        "## Hasil\nWebhook pembayaran Midtrans perlu diperbaiki: verifikasi tanda tangan gagal.",
    )
    knowledge = vault / "20_Knowledge" / "webhook-idempoten.md"
    knowledge.parent.mkdir(parents=True)
    knowledge.write_text(
        "# Penanganan Webhook Pembayaran Idempoten\n\n"
        "Webhook pembayaran Midtrans bisa terkirim dua kali. Simpan pengenal kejadian dengan batasan unik.\n",
        encoding="utf-8",
    )
    unrelated = vault / "20_Knowledge" / "git-rebase.md"
    unrelated.write_text("# Git Rebase\n\nRebase cabang fitur ke main sebelum membuka pull request.\n", encoding="utf-8")

    engine = HybridEngine(vault_path=vault)
    engine.index_vault()
    builder = ContextAssemblyEngine(vault, engine=engine)

    card = builder.build_task_context(task="perbaiki webhook pembayaran Midtrans", project="toko-online")
    paths = [item["path"] for item in card.relevant_knowledge]
    wide = [n["path"] for n in builder.select_relevant_notes("perbaiki webhook pembayaran Midtrans", "toko-online", limit=10)]
    assert unlinked in wide  # not tied to any project, and both rankers agree
    assert not any("s-foreign" in p for p in wide)

    assert paths[0] == own  # the project's own session comes first
    assert "20_Knowledge/webhook-idempoten.md" in paths  # both rankers agree on it
    assert not any("s-foreign" in p for p in paths)  # another project's session log
    assert "20_Knowledge/git-rebase.md" not in paths
    assert "10_Projects/toko-online/README.md" not in paths  # summarized separately

    # Sessions listed as recent work are not repeated as knowledge
    recent_paths = {line.split("`")[1] for line in card.recent_session_work}
    assert not recent_paths & set(paths)

    markdown = card.to_markdown()
    assert f"(`{own}`)" in markdown and "PROJ-TOKO" not in markdown

    # A task nothing matches yields no pushed notes at all
    empty = builder.build_task_context(task="resep rendang daging sapi", project="toko-online")
    assert empty.relevant_knowledge == []


def test_briefing_without_engine_has_no_knowledge(tmp_path: Path):
    vault = _vault(tmp_path)
    card = ContextAssemblyEngine(vault).build_task_context(task="apa saja", project="toko-online")
    assert card.relevant_knowledge == []


def test_first_prose_paragraph_skips_decoration():
    readme = (
        "# My App\n\n"
        "[![Build](https://img.shields.io/badge/build-passing-green)](https://example.com)\n"
        "![logo](logo.png)\n\n"
        "> A tagline in a quote\n\n"
        "- a list item\n\n"
        "```bash\nnpm install\n```\n\n"
        "Platform pre-order untuk usaha wonton\nrumahan di Semarang.\n\n"
        "Paragraf kedua.\n"
    )

    assert first_prose_paragraph(readme) == "Platform pre-order untuk usaha wonton rumahan di Semarang."
    assert first_prose_paragraph("# Title\n\n- only\n- a list\n") == ""


def test_project_summary_omits_overview_made_of_badges(tmp_path: Path):
    vault = tmp_path / "vault"
    card = vault / DIR_PROJECTS / "zvdev" / "README.md"
    card.parent.mkdir(parents=True)
    card.write_text(
        "# zvdev\n\n## 📋 Overview\n[![Next.js](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org/)\n\n"
        "---\n\n## ⚡ Runnable Scripts:\n- `dev` → `next dev`\n\n---\n",
        encoding="utf-8",
    )

    summary, _ = ContextAssemblyEngine(vault).get_project_summary("zvdev")

    assert "img.shields.io" not in summary
    assert summary.endswith("**Run:** `dev` → `next dev`")


def test_scanned_project_description_uses_readme_prose(tmp_path: Path):
    repo = tmp_path / "wonton"
    repo.mkdir()
    (repo / "README.md").write_text(
        "# Wonton\n\n[![Next.js](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org/)\n\n"
        "Platform pre-order untuk usaha wonton rumahan.\n",
        encoding="utf-8",
    )

    meta = scan_project_metadata(repo)

    assert meta.description == "Platform pre-order untuk usaha wonton rumahan."
