"""Vault scaffolder for initializing standard Obsidian directory hierarchy matching docs/brainstorming/07."""

from pathlib import Path
from typing import List

from devbrain.core.constants import (
    BRAIN_IGNORE_FILENAME,
    DEFAULT_IGNORED_PATTERNS,
    DIR_AGENT_SKILLS,
    DIR_DECISIONS,
    DIR_INBOX,
    DIR_KNOWLEDGE,
    DIR_KNOWLEDGE_ARCH,
    DIR_KNOWLEDGE_BUGS,
    DIR_PROJECTS,
    DIR_SYSTEM,
    DIR_SYSTEM_PERSONAS,
    DIR_SYSTEM_RULES,
    DIR_DAILY,
    STANDARD_DIRS,
)

# Starter Templates Matching 07-taksonomi-vault-dan-standar-metadata.md

GLOBAL_CONTEXT_TEMPLATE = """---
title: Global User & System Context
type: system-context
updated: 2026-08-29
tags: [system, context, global]
---

# 🌐 Global User & System Context

Dokumen ini memuat profil preferensi global, stack teknologi utama, dan aturan umum untuk AI Agent yang terhubung ke Central Brain ini.

## 👤 Profil & Preferensi:
- **Default Language:** Python / TypeScript
- **Environment:** Windows (PowerShell) / Linux / WSL
- **UI PKM App:** Obsidian Desktop

## 📌 Prinsip Utama AI:
1. **Single Source of Truth (SSOT):** Selalu baca context proyek dari `10_Projects/` sebelum memulai task baru.
2. **Append-Only Logging:** Catat ringkasan sesi kerja penting dan keputusan arsitektur baru ke `90_Agent_Inbox/`.
3. **Skill Discovery:** Gunakan skill dari `00_System/Agent_Skills/` untuk alur kerja yang sudah terstandarisasi.
"""

RULES_TEMPLATE = """---
title: General System Rules
type: system-rule
tags: [system, rules, guidelines]
---

# 📌 General System & Coding Rules

1. **Clean Code & Type Hints:** Selalu gunakan type hints (`typing`) dan docstring standar.
2. **No Secret Leaks:** Jangan pernah menyimpan API Key, token rahasia, atau kredensial mentah ke dalam catatan Markdown.
3. **Wikilinks Convention:** Gunakan `[[Wikilinks]]` saat mereferensikan konsep, modul, atau catatan proyek lain.
"""

PERSONA_ARCHITECT_TEMPLATE = """---
title: Backend Architect Persona
type: system-persona
role: architect
tags: [persona, backend, architecture]
---

# 🏗️ Persona: Senior Backend & System Architect

Ketika mengaktifkan persona ini:
- Fokus pada efisiensi resource, modularitas, skalabilitas, dan keamanan sistem.
- Dokumentasikan setiap keputusan desain kritis ke dalam format Architecture Decision Record (ADR) di `30_Decisions/`.
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

PROJECTS_INDEX_TEMPLATE = """---
title: Active Projects Index
type: index-hub
tags: [index, projects]
---

# 📂 Active Projects Index

Hub indeks seluruh proyek aktif:

- [[example_project/README|Example Project]] — Inisialisasi Proyek Perdana
"""

EXAMPLE_PROJECT_README = """---
project: Example Project
status: active
priority: high
tags: [project, example]
---

# 🚀 Example Project

## 📋 Overview
Proyek inisialisasi awal untuk menguji konektivitas AI Agent dan Obsidian Central Brain.

## 🎯 Milestones & Tasks:
- [x] Inisialisasi struktur vault Obsidian
- [ ] Uji coba pencarian hybrid FastEmbed & BM25
- [ ] Hubungkan ke Antigravity IDE & Claude Code
"""

KNOWLEDGE_INDEX_TEMPLATE = """---
title: Knowledge Base Index
type: index-hub
tags: [index, knowledge]
---

# 📚 Knowledge Base Index

Kumpulan dokumentasi teknis, pola arsitektur, dan solusi bug:

- [[Architecture_Patterns/clean_architecture|Clean Architecture]] — Prinsip desain modular
"""

CLEAN_ARCH_TEMPLATE = """---
id: "KNOW-ARCH-001"
title: "Prinsip Clean & Modular Architecture"
type: knowledge-pattern
category: architecture
tags: [architecture, design-pattern, best-practice]
---

# 🏛️ Prinsip Clean & Modular Architecture

## Ringkasan:
Memisahkan logika bisnis inti dari antarmuka luar (CLI, Web, UI, MCP) agar sistem mudah diuji dan dikembangkan.
"""

DECISIONS_INDEX_TEMPLATE = """---
title: Architecture Decision Records Index
type: index-hub
tags: [index, adr, decisions]
---

# 📋 Architecture Decision Records (ADR) Index

- [[ADR-001-use-fastmcp-and-fastembed|ADR-001]]: Pemilihan FastMCP Stdio & FastEmbed CPU ONNX
"""

ADR_001_TEMPLATE = """---
id: "ADR-001"
title: "Pemilihan FastMCP & FastEmbed Local CPU"
status: accepted
date: 2026-08-29
tags: [adr, architecture, mcp, fastembed]
---

# ADR-001: Pemilihan FastMCP & FastEmbed Local CPU

## Konteks:
Dibutuhkan sistem Central Brain yang ringan, 100% offline, bebas GPU, dan kompatibel langsung dengan Antigravity IDE & Claude Code.

## Keputusan:
Menggunakan FastMCP Python Stdio server dan FastEmbed CPU ONNX (`bge-small-en-v1.5`) untuk Level 1 Standalone.
"""

INBOX_INDEX_TEMPLATE = """---
title: Agent Inbox Index
type: index-hub
tags: [index, inbox, agent-logs]
---

# 📥 Agent Inbox & Daily Logs

Zona drop catatan otomatis yang ditulis oleh AI Agent:
- `antigravity/`: Log dan solusi dari sesi Antigravity IDE
- `claude-code/`: Log dari Claude Code
- `hermes/`: Log dari Hermes Agent
- `manual_review/`: Catatan yang butuh review manusia
"""

DAILY_INDEX_TEMPLATE = """---
title: Daily Notes Index
type: index-hub
tags: [index, daily]
---

# 📅 Daily Notes Index

Catatan harian dan refleksi progres coding harian.
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

    # Subdirectories for example project & skill
    example_project_dir = vault_path / DIR_PROJECTS / "example_project"
    if not example_project_dir.exists():
        example_project_dir.mkdir(parents=True, exist_ok=True)
        created_items.append(example_project_dir)

    example_skill_dir = vault_path / DIR_AGENT_SKILLS / "example_skill"
    if not example_skill_dir.exists():
        example_skill_dir.mkdir(parents=True, exist_ok=True)
        created_items.append(example_skill_dir)

    # 2. Create Starter Markdown Files (Non-destructive)
    files_to_create = [
        (vault_path / DIR_SYSTEM / "global_context.md", GLOBAL_CONTEXT_TEMPLATE),
        (vault_path / DIR_SYSTEM_RULES / "general_rules.md", RULES_TEMPLATE),
        (vault_path / DIR_SYSTEM_PERSONAS / "backend_architect.md", PERSONA_ARCHITECT_TEMPLATE),
        (example_skill_dir / "SKILL.md", EXAMPLE_SKILL_TEMPLATE),
        (vault_path / DIR_PROJECTS / "_Project_Index.md", PROJECTS_INDEX_TEMPLATE),
        (example_project_dir / "README.md", EXAMPLE_PROJECT_README),
        (vault_path / DIR_KNOWLEDGE / "_Knowledge_Index.md", KNOWLEDGE_INDEX_TEMPLATE),
        (vault_path / DIR_KNOWLEDGE_ARCH / "clean_architecture.md", CLEAN_ARCH_TEMPLATE),
        (vault_path / DIR_DECISIONS / "_Decisions_Index.md", DECISIONS_INDEX_TEMPLATE),
        (vault_path / DIR_DECISIONS / "ADR-001-use-fastmcp-and-fastembed.md", ADR_001_TEMPLATE),
        (vault_path / DIR_INBOX / "_Inbox_Index.md", INBOX_INDEX_TEMPLATE),
        (vault_path / DIR_DAILY / "_Daily_Index.md", DAILY_INDEX_TEMPLATE),
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
