"""Vault scaffolder for initializing standard Obsidian directory hierarchy."""

from pathlib import Path
from typing import List

from devbrain.core.constants import (
    BRAIN_IGNORE_FILENAME,
    DEFAULT_IGNORED_PATTERNS,
    DIR_AGENT_SKILLS,
    DIR_INBOX,
    DIR_KNOWLEDGE,
    DIR_PROJECTS,
    DIR_SYSTEM,
    STANDARD_DIRS,
)

# Starter Templates
RULES_TEMPLATE = """# 🧠 Central AI Brain - System Rules & Memory Protocol

Dokumen ini mendefinisikan aturan global dan protokol perilaku untuk semua AI Agent yang terhubung ke Central Brain ini.

## 📌 Protokol Memori AI:
1. **Single Source of Truth:** Selalu prioritaskan konteks proyek yang tersimpan di `10_Projects/`.
2. **Append-Only Logging:** Simpan ringkasan sesi penting atau keputusan arsitektur baru ke `90_Agent_Inbox/`.
3. **Skill Discovery:** Sebelum mengeksekusi instruksi khusus, periksa skill yang relevan di `00_System/Agent_Skills/`.
"""

EXAMPLE_SKILL_TEMPLATE = """---
name: example-workflow
description: Contoh template skill standar untuk AI Agent di Central Brain
---

# Example Workflow Skill

Gunakan skill ini sebagai acuan format penulisan Agent Skill baru di Central Brain.

## Instruksi:
1. Selalu lakukan verifikasi prasyarat sebelum memulai task.
2. Catat perubahan kode pada catatan proyek terkait di `10_Projects/`.
"""

PROJECTS_INDEX_TEMPLATE = """# 📂 Active Projects Index

Daftar seluruh proyek aktif yang sedang dikerjakan:

- [[example_project]] - Inisialisasi Proyek Perdana
"""

KNOWLEDGE_INDEX_TEMPLATE = """# 📚 Knowledge Base Index

Kumpulan dokumentasi teknis, arsitektur, dan referensi stack:

- [[tech_stack_overview]] - Gambaran umum arsitektur sistem
"""

INBOX_INDEX_TEMPLATE = """# 📥 Agent Inbox & Daily Logs

Folder ini menampung log harian dan ringkasan sesi kerja otomatis yang dicatat oleh AI Agent.
"""


def scaffold_vault(vault_path: Path, is_new: bool = True) -> List[Path]:
    """Scaffold standard directory structure and starter markdown files.

    Non-destructive: Does not overwrite files if they already exist.
    """
    created_items: List[Path] = []
    vault_path = vault_path.resolve()
    vault_path.mkdir(parents=True, exist_ok=True)

    # 1. Create Standard Directories
    for rel_dir in STANDARD_DIRS:
        target_dir = vault_path / rel_dir
        if not target_dir.exists():
            target_dir.mkdir(parents=True, exist_ok=True)
            created_items.append(target_dir)

    # Also create example skill folder
    example_skill_dir = vault_path / DIR_AGENT_SKILLS / "example_skill"
    if not example_skill_dir.exists():
        example_skill_dir.mkdir(parents=True, exist_ok=True)
        created_items.append(example_skill_dir)

    # 2. Create Starter Markdown Files (Non-destructive)
    files_to_create = [
        (vault_path / DIR_SYSTEM / "rules.md", RULES_TEMPLATE),
        (example_skill_dir / "SKILL.md", EXAMPLE_SKILL_TEMPLATE),
        (vault_path / DIR_PROJECTS / "_index.md", PROJECTS_INDEX_TEMPLATE),
        (vault_path / DIR_KNOWLEDGE / "_index.md", KNOWLEDGE_INDEX_TEMPLATE),
        (vault_path / DIR_INBOX / "_index.md", INBOX_INDEX_TEMPLATE),
        (
            vault_path / BRAIN_IGNORE_FILENAME,
            "\n".join(DEFAULT_IGNORED_PATTERNS) + "\n",
        ),
    ]

    for file_path, content in files_to_create:
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content.strip() + "\n")
            created_items.append(file_path)

    return created_items
