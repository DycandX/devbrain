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
    DIR_PROJECTS,
    DIR_SYSTEM,
    DIR_SYSTEM_PERSONAS,
    DIR_SYSTEM_RULES,
    DIR_DAILY,
    STANDARD_DIRS,
)

# Starter Templates in English Matching 07-taksonomi-vault-dan-standar-metadata.md

GLOBAL_CONTEXT_TEMPLATE = """---
title: Global User & System Context
type: system-context
updated: 2026-08-29
tags: [system, context, global]
---

# 🌐 Global User & System Context

This document outlines global user preferences, primary technology stacks, and universal protocol guidelines for AI Agents connected to this Central Brain Hub.

## 👤 Profile & Preferences:
- **Default Languages:** Python / TypeScript
- **Environment:** Windows (PowerShell) / Linux / WSL
- **Visual PKM Application:** Obsidian Desktop

## 📌 Core Memory Principles:
1. **Single Source of Truth (SSOT):** Always read project context from `10_Projects/` before starting a new task.
2. **Append-Only Logging:** Record important session summaries and architectural decisions into `90_Agent_Inbox/`.
3. **Skill Discovery:** Leverage modular skills from `00_System/Agent_Skills/` for standardized multi-step workflows.
"""

RULES_TEMPLATE = """---
title: General System Rules
type: system-rule
tags: [system, rules, guidelines]
---

# 📌 General System & Coding Rules

1. **Clean Code & Type Annotations:** Always use explicit type annotations (`typing`) and standard docstrings.
2. **No Secret Leaks:** Never write raw API keys, secrets, or sensitive credentials into Markdown notes.
3. **Wikilinks Convention:** Use `[[Wikilinks]]` whenever referencing related concepts, architecture patterns, or project notes.
"""

PERSONA_ARCHITECT_TEMPLATE = """---
title: Backend Architect Persona
type: system-persona
role: architect
tags: [persona, backend, architecture]
---

# 🏗️ Persona: Senior Backend & System Architect

When this persona is activated:
- Emphasize resource efficiency, modularity, system scalability, and security.
- Document critical design decisions into Architecture Decision Record (ADR) format inside `30_Decisions/`.
"""

EXAMPLE_SKILL_TEMPLATE = """---
name: example-workflow
description: Standard example skill template for AI Agents in Central Brain
---

# Example Workflow Skill

Use this skill as a standard template for authoring new Agent Skills in Central Brain.

## Instructions:
1. Always verify prerequisites before executing the task.
2. Document code changes and progress in the relevant project note inside `10_Projects/`.
"""

PROJECTS_INDEX_TEMPLATE = """---
title: Active Projects Index
type: index-hub
tags: [index, projects]
---

# 📂 Active Projects Index

Index hub of all active projects:

- [[example_project/README|Example Project]] — Initial Project Setup & Testing
"""

EXAMPLE_PROJECT_README = """---
project: Example Project
status: active
priority: high
tags: [project, example]
---

# 🚀 Example Project

## 📋 Overview
Initial project workspace to test AI Agent connectivity and Obsidian Central Brain features.

## 🎯 Milestones & Tasks:
- [x] Initialize Obsidian vault structure
- [ ] Test FastEmbed & BM25 hybrid search
- [ ] Connect with Antigravity IDE & Claude Code
"""

KNOWLEDGE_INDEX_TEMPLATE = """---
title: Knowledge Base Index
type: index-hub
tags: [index, knowledge]
---

# 📚 Knowledge Base Index

Collection of technical documentation, architecture patterns, and bug solutions:

- [[Architecture_Patterns/clean_architecture|Clean Architecture]] — Modular design principles
"""

CLEAN_ARCH_TEMPLATE = """---
id: "KNOW-ARCH-001"
title: "Clean & Modular Architecture Principles"
type: knowledge-pattern
category: architecture
tags: [architecture, design-pattern, best-practice]
---

# 🏛️ Clean & Modular Architecture Principles

## Summary:
Isolate core business logic from external interfaces (CLI, Web, UI, MCP) to ensure high testability, maintainability, and rapid evolution.
"""

DECISIONS_INDEX_TEMPLATE = """---
title: Architecture Decision Records Index
type: index-hub
tags: [index, adr, decisions]
---

# 📋 Architecture Decision Records (ADR) Index

- [[ADR-001-use-fastmcp-and-fastembed|ADR-001]]: Selection of FastMCP Stdio & Local CPU FastEmbed
"""

ADR_001_TEMPLATE = """---
id: "ADR-001"
title: "Selection of FastMCP & FastEmbed Local CPU"
status: accepted
date: 2026-08-29
tags: [adr, architecture, mcp, fastembed]
---

# ADR-001: Selection of FastMCP & FastEmbed Local CPU

## Context:
Required a lightweight, 100% offline, zero-GPU second brain hub compatible out-of-the-box with Antigravity IDE and Claude Code.

## Decision:
Adopted FastMCP Python Stdio server and FastEmbed CPU ONNX (`BAAI/bge-small-en-v1.5`) for Level 1 Standalone deployment.
"""

INBOX_INDEX_TEMPLATE = """---
title: Agent Inbox Index
type: index-hub
tags: [index, inbox, agent-logs]
---

# 📥 Agent Inbox & Daily Logs

Drop zone for automated session notes and logs authored by AI Agents:
- `antigravity-ide/`: Sessions extracted from Google Antigravity IDE
- `antigravity-cli/`: Sessions extracted from Antigravity CLI (`agy`)
- `claude-code/`: Transcripts and solutions from Claude Code
- `cline/`: Tasks and logs from Cline / Roo Code
- `manual_review/`: Notes requiring human validation

## ⚡ Live Recent Ingestions:
```dataview
TABLE source, device, created, tags
FROM "90_Agent_Inbox"
WHERE file.name != "_Inbox_Index"
SORT created DESC
LIMIT 20
```
"""

DAILY_INDEX_TEMPLATE = """---
title: Daily Notes Index
type: index-hub
tags: [index, daily]
---

# 📅 Daily Notes Index

Daily logs, reflections, and session journal entries.
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
