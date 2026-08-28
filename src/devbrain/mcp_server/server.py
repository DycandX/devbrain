"""Model Context Protocol (MCP) Server for Central AI Brain Hub."""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional
import uuid

from devbrain.core.config import BrainConfig, load_config
from devbrain.core.constants import (
    DIR_AGENT_SKILLS,
    DIR_INBOX,
    DIR_PROJECTS,
    DIR_SYSTEM,
)
from devbrain.engine.hybrid_search import HybridEngine
from devbrain.watcher.vault_watcher import VaultWatcher


def create_mcp_server(vault_path: Path, config: Optional[BrainConfig] = None):
    """Factory creating and configuring the MCP Server with 4 core memory tools."""
    try:
        from mcp.server.mcpserver import MCPServer
    except ImportError:
        raise RuntimeError("The 'mcp' package is required to run the MCP server. Install via 'pip install mcp'.")

    vault_path = vault_path.resolve()
    if config is None:
        config = load_config(vault_path)

    # Initialize Engine & Watcher
    engine = HybridEngine(
        vault_path=vault_path,
        embedding_model=config.embedding_model,
        ignored_patterns=config.ignored_paths,
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
            # Search by glob
            matched = list(projects_dir.rglob(f"*{clean_name}*.md"))
            if matched:
                found_file = matched[0]

        if not found_file:
            # Fallback to hybrid search
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
    # TOOL 3: write_agent_log
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

        # Trigger incremental re-index
        engine.index_vault(force_reindex=False)

        rel_path = file_path.relative_to(vault_path).as_posix()
        return f"Successfully recorded agent log into `{rel_path}` and indexed into Central Brain memory."

    # =========================================================================
    # TOOL 4: load_skill
    # =========================================================================
    @server.tool(
        name="load_skill",
        description="Load instructions and workflow procedures for an Agent Skill stored in 00_System/Agent_Skills/.",
    )
    def load_skill(skill_name: str) -> str:
        """Read SKILL.md for a requested skill name."""
        skills_dir = vault_path / DIR_AGENT_SKILLS
        clean_name = skill_name.strip().replace(" ", "-").lower()

        skill_file = skills_dir / clean_name / "SKILL.md"
        if not skill_file.is_file():
            # Try fuzzy search in skills folder
            all_skills = [
                d.name for d in skills_dir.glob("*")
                if d.is_dir() and (d / "SKILL.md").is_file()
            ]
            if all_skills:
                return (
                    f"Skill '{skill_name}' not found at `{skill_file}`.\n"
                    f"Available active skills in vault: {', '.join(all_skills)}"
                )
            return f"Skill '{skill_name}' not found and no skills are currently created in `{DIR_AGENT_SKILLS}/`."

        with open(skill_file, "r", encoding="utf-8", errors="replace") as f:
            skill_content = f.read()

        return f"# Active Skill Instructions: `{clean_name}`\n\n{skill_content}"

    return server
