"""Model Context Protocol (MCP) Server for Central AI Brain Hub (PAIOS Layer)."""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional
import uuid

from devbrain.adr.manager import ADRManager
from devbrain.context.builder import ContextAssemblyEngine
from devbrain.core.config import BrainConfig, load_config
from devbrain.core.constants import (
    DIR_AGENT_SKILLS,
    DIR_INBOX,
    DIR_PROJECTS,
    DIR_SYSTEM,
)
from devbrain.core.sqlite_db import BrainSQLiteStorage
from devbrain.engine.hybrid_search import HybridEngine


def create_mcp_server(vault_path: Path, config: Optional[BrainConfig] = None):
    """Factory creating and configuring the MCP Server with comprehensive PAIOS memory tools."""
    try:
        from mcp.server.mcpserver import MCPServer
    except ImportError:
        raise RuntimeError("The 'mcp' package is required to run the MCP server. Install via 'pip install mcp'.")

    vault_path = vault_path.resolve()
    if config is None:
        config = load_config(vault_path)

    linked_vault_paths = config.resolve_linked_vaults()
    sqlite_storage = BrainSQLiteStorage(vault_path)
    adr_manager = ADRManager(vault_path, sqlite_storage)
    context_engine = ContextAssemblyEngine(vault_path, sqlite_storage)

    # Initialize Engine & Watcher
    engine = HybridEngine(
        vault_path=vault_path,
        embedding_model=config.embedding_model,
        ignored_patterns=config.ignored_paths,
        linked_vaults=linked_vault_paths,
    )
    engine.initialize()

    # Initial scan if needed
    if not engine.chunks:
        engine.index_vault()

    server = MCPServer(
        name="central-brain",
        description="Central AI Second Brain Hub — Single Source of Truth for Multi-Agent Coding & Obsidian",
    )

    # =========================================================================
    # TOOL 1: search_brain
    # =========================================================================
    @server.tool(
        name="search_brain",
        description="Search knowledge, projects, architecture rules, and logs in Central Brain using semantic hybrid search.",
    )
    def search_brain(
        query: str,
        limit: int = 5,
        mode: Literal["hybrid", "dense", "bm25"] = "hybrid",
        scope: str = "all",
    ) -> str:
        """Search notes in the Obsidian vault."""
        results = engine.search(query=query, limit=limit, mode=mode, scope=scope)
        if not results:
            return f"No relevant notes found for query: '{query}'"

        formatted = []
        for idx, r in enumerate(results, 1):
            pct = int(r.score * 100)
            breadcrumb = f" > {r.header_path}" if r.header_path else ""
            tags_str = f" [Tags: {', '.join(r.tags)}]" if r.tags else ""
            entry = (
                f"### Result {idx}: {r.title}{breadcrumb} ({pct}% Match)\n"
                f"- **File:** `{r.file_path}`{tags_str}\n"
                f"- **Snippet:**\n{r.snippet}\n"
            )
            formatted.append(entry)

        return "\n---\n".join(formatted)

    # =========================================================================
    # TOOL 2: get_project_context
    # =========================================================================
    @server.tool(
        name="get_project_context",
        description="Retrieve comprehensive overview, architecture, active tasks, and context for a specific project.",
    )
    def get_project_context(project_name: str) -> str:
        """Fetch project documentation from 10_Projects/."""
        projects_dir = vault_path / DIR_PROJECTS
        if not projects_dir.is_dir():
            return f"Projects directory '{DIR_PROJECTS}' does not exist in vault."

        clean_name = project_name.strip().replace(" ", "_").lower()
        candidates = [
            projects_dir / f"{project_name}.md",
            projects_dir / f"{clean_name}.md",
            projects_dir / project_name / "README.md",
            projects_dir / clean_name / "README.md",
        ]

        found_file = None
        for cand in candidates:
            if cand.is_file():
                found_file = cand
                break

        if not found_file:
            matched = list(projects_dir.rglob(f"*{clean_name}*.md"))
            if matched:
                found_file = matched[0]

        if not found_file:
            fallback_results = engine.search(query=f"project {project_name}", limit=2, scope="all")
            if fallback_results:
                return (
                    f"Project file for '{project_name}' not found directly. Closest matches:\n\n"
                    + "\n\n".join(f"**{r.title}** (`{r.file_path}`):\n{r.snippet}" for r in fallback_results)
                )
            return f"No documentation found for project '{project_name}' in '{DIR_PROJECTS}/'."

        with open(found_file, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        rel_path = found_file.relative_to(vault_path).as_posix()
        return f"# Project Context: `{rel_path}`\n\n{content}"

    # =========================================================================
    # TOOL 3: build_task_context (Context Assembly Engine)
    # =========================================================================
    @server.tool(
        name="build_task_context",
        description="Assemble instant situational awareness card combining User Preferences, Project State, ADRs, and Knowledge.",
    )
    def build_task_context(task: str, project: str) -> str:
        """Assemble complete task briefing card."""
        relevant_chunks = []
        search_hits = engine.search(query=f"{project} {task}", limit=3, scope="all")
        for hit in search_hits:
            relevant_chunks.append({
                "title": hit.title,
                "path": hit.file_path,
                "snippet": hit.snippet,
            })

        card = context_engine.build_task_context(task=task, project=project, relevant_chunks=relevant_chunks)
        return card.to_markdown()

    # =========================================================================
    # TOOL 4: get_user_context
    # =========================================================================
    @server.tool(
        name="get_user_context",
        description="Retrieve global user preferences, coding persona, styling rules, and constraints.",
    )
    def get_user_context() -> str:
        """Retrieve user coding persona."""
        return context_engine.get_user_preferences()

    # =========================================================================
    # TOOL 5: get_decisions
    # =========================================================================
    @server.tool(
        name="get_decisions",
        description="Retrieve active Architecture Decision Records (ADRs) for a project or globally.",
    )
    def get_decisions(project: Optional[str] = None, status: str = "accepted") -> str:
        """Fetch architecture decisions."""
        decisions = adr_manager.list_decisions(project=project, status=status)
        if not decisions:
            proj_str = f" for project '{project}'" if project else ""
            return f"No {status} architecture decisions found{proj_str}."

        lines = [f"# Architecture Decision Records ({status.upper()})\n"]
        for d in decisions:
            proj = d.get("project") or "Global"
            lines.append(f"### [{d.get('id', 'ADR')}] {d.get('title', '')}")
            lines.append(f"- **Project:** `{proj}` | **Date:** `{d.get('date', '')}`")
            if d.get("summary"):
                lines.append(f"- **Summary:** {d.get('summary')}")
            lines.append("")
        return "\n".join(lines)

    # =========================================================================
    # TOOL 6: record_decision
    # =========================================================================
    @server.tool(
        name="record_decision",
        description="Create a new Architecture Decision Record (ADR) in 30_Decisions/.",
    )
    def record_decision(
        title: str,
        context: str,
        decision: str,
        project: Optional[str] = None,
        consequences: str = "",
        alternatives: str = "",
    ) -> str:
        """Create a new ADR note."""
        result = adr_manager.create_decision(
            title=title,
            project=project,
            context=context,
            decision=decision,
            consequences=consequences,
            alternatives=alternatives,
        )
        engine.index_vault(force_reindex=False)
        return f"Successfully created Architecture Decision Record `{result['id']}`: '{title}' at `{result['file_path']}`."

    # =========================================================================
    # TOOL 7: write_agent_log
    # =========================================================================
    @server.tool(
        name="write_agent_log",
        description="Record session summary, architecture decision, or progress log into 90_Agent_Inbox/ using append-only UUID partitioning.",
    )
    def write_agent_log(
        summary: str,
        details: str,
        tags: Optional[List[str]] = None,
        author: str = "ai-agent",
    ) -> str:
        """Write an append-only log note into 90_Agent_Inbox/."""
        inbox_dir = vault_path / DIR_INBOX
        inbox_dir.mkdir(parents=True, exist_ok=True)

        now = datetime.now(timezone.utc)
        timestamp_str = now.strftime("%Y%m%d_%H%M%S")
        log_id = str(uuid.uuid4())[:8]
        device_tag = config.device_name.replace(" ", "-").lower()

        filename = f"{timestamp_str}_{device_tag}_{log_id}.md"
        file_path = inbox_dir / filename

        all_tags = ["agent-log", author]
        if tags:
            for t in tags:
                clean_tag = t.strip().lstrip("#")
                if clean_tag not in all_tags:
                    all_tags.append(clean_tag)

        tags_yaml = json.dumps(all_tags)

        note_content = f"""---
id: "LOG-{timestamp_str}-{log_id}"
title: "{summary}"
type: agent-log
author: "{author}"
device: "{config.device_name}"
created: "{now.isoformat()}"
tags: {tags_yaml}
---

# 📝 {summary}

## Overview:
{details.strip()}

---
*Logged automatically by Central Brain Agent Protocol at {now.strftime('%Y-%m-%d %H:%M:%S UTC')}*
"""

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(note_content)

        engine.index_vault(force_reindex=False)
        rel_path = file_path.relative_to(vault_path).as_posix()
        return f"Successfully recorded agent log into `{rel_path}` and indexed into Central Brain memory."

    # =========================================================================
    # TOOL 8: load_skill
    # =========================================================================
    @server.tool(
        name="load_skill",
        description="Load instructions and workflow procedures for an Agent Skill stored in 00_System/Agent_Skills/ or custom skill roots.",
    )
    def load_skill(skill_name: str) -> str:
        """Read SKILL.md for a requested skill name from vault or external roots."""
        skills_dir = vault_path / DIR_AGENT_SKILLS
        clean_name = skill_name.strip().replace(" ", "-").lower()

        search_locations = [skills_dir / clean_name / "SKILL.md"]
        for ext_root in config.custom_skill_roots:
            p = Path(ext_root).resolve()
            search_locations.append(p / clean_name / "SKILL.md")
            search_locations.append(p / "skills" / clean_name / "SKILL.md")

        for skill_file in search_locations:
            if skill_file.is_file():
                with open(skill_file, "r", encoding="utf-8", errors="replace") as f:
                    skill_content = f.read()
                return f"# Active Skill Instructions: `{clean_name}` (from `{skill_file}`)\n\n{skill_content}"

        all_skills: list[str] = [
            d.name for d in skills_dir.glob("*")
            if d.is_dir() and (d / "SKILL.md").is_file()
        ]
        for ext_root in config.custom_skill_roots:
            p = Path(ext_root).resolve()
            if p.is_dir():
                all_skills.extend([
                    d.name for d in p.glob("*")
                    if d.is_dir() and (d / "SKILL.md").is_file()
                ])

        if all_skills:
            return (
                f"Skill '{skill_name}' not found.\n"
                f"Available active skills in vault & external roots: {', '.join(sorted(set(all_skills)))}"
            )
        return f"Skill '{skill_name}' not found and no skills are currently available."

    return server
