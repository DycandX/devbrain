"""Model Context Protocol (MCP) Server for Central AI Brain Hub (PAIOS Layer).

Tool output is sized deliberately: every response an agent reads costs context
tokens, so tools return a compact answer first and point to `read_note` for
detail instead of returning whole files.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import List, Literal, Optional
import uuid

from devbrain.adr.manager import ADRManager
from devbrain.context.builder import ContextAssemblyEngine
from devbrain.core.config import BrainConfig, load_config
from devbrain.core.constants import DIR_AGENT_SKILLS, DIR_INBOX, DIR_PROJECTS
from devbrain.core.fsutil import atomic_write_text
from devbrain.core.sqlite_db import BrainSQLiteStorage
from devbrain.core.textutil import extract_section, one_line, truncate_to_budget
from devbrain.engine.hybrid_search import HybridEngine
from devbrain.memory.manager import MemoryManager

# Output budgets in characters (about 4 characters per token).
SEARCH_PREVIEW_CHARS = 140
NOTE_MAX_CHARS = 6000
PROJECT_MAX_CHARS = 6000
READ_NOTE_HINT = "Call read_note with a `heading` to fetch one section, or raise `max_chars`."

_SKILL_NAME = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def create_mcp_server(
    vault_path: Path,
    config: Optional[BrainConfig] = None,
    engine: Optional[HybridEngine] = None,
):
    """Factory creating and configuring the MCP Server with comprehensive PAIOS memory tools.

    Pass a prebuilt engine to share it with other components such as the vault watcher.
    """
    try:
        from mcp.server.mcpserver import MCPServer
    except ImportError:
        raise RuntimeError("The 'mcp' package is required to run the MCP server. Install via 'pip install mcp'.")

    vault_path = vault_path.resolve()
    if config is None:
        config = load_config(vault_path)

    sqlite_storage = BrainSQLiteStorage(vault_path)
    adr_manager = ADRManager(vault_path, sqlite_storage)
    if engine is None:
        engine = HybridEngine.from_config(vault_path, config)
    engine.initialize()
    context_engine = ContextAssemblyEngine(vault_path, sqlite_storage, engine)

    # Initial scan if needed
    if not engine.chunks:
        engine.index_vault()

    memory = MemoryManager(vault_path, sqlite_storage, engine, config)
    linked_vaults = config.resolve_linked_vaults()

    server = MCPServer(
        name="central-brain",
        description="Central AI Second Brain Hub — Single Source of Truth for Multi-Agent Coding & Obsidian",
    )

    def resolve_note(ref: str) -> Optional[Path]:
        """Map a note reference from search results to a file inside a known vault."""
        ref = ref.strip().strip("`")
        base, rel = vault_path, ref
        if ref.startswith("linked:"):
            parts = ref.split(":", 2)
            if len(parts) != 3 or parts[1] not in linked_vaults:
                return None
            base, rel = linked_vaults[parts[1]], parts[2]

        base = base.resolve()
        target = (base / rel).resolve()
        if not target.is_relative_to(base) or target.suffix.lower() != ".md" or not target.is_file():
            return None
        return target

    # =========================================================================
    # TOOL: search_brain
    # =========================================================================
    @server.tool(
        name="search_brain",
        description=(
            "Search notes, project cards, decisions, and session logs. Returns a compact list "
            "(one line per note) by default; pass detail='snippet' for longer excerpts, then "
            "read_note for full content. Returns nothing when no note is relevant."
        ),
    )
    def search_brain(
        query: str,
        limit: int = 5,
        mode: Literal["hybrid", "dense", "bm25"] = "hybrid",
        scope: str = "all",
        detail: Literal["index", "snippet"] = "index",
    ) -> str:
        """Search notes in the Obsidian vault."""
        results = engine.search(query=query, limit=limit, mode=mode, scope=scope, one_per_note=True)
        if not results:
            return f"No relevant notes found for query: '{query}'"

        if detail == "index":
            lines = []
            for idx, r in enumerate(results, 1):
                breadcrumb = f" > {r.header_path}" if r.header_path else ""
                lines.append(
                    f"{idx}. **{r.title}{breadcrumb}** ({int(r.score * 100)}%) `{r.doc_id}`\n"
                    f"   {one_line(r.snippet, SEARCH_PREVIEW_CHARS)}"
                )
            return "\n".join(lines) + "\n\nUse read_note(path) for full content."

        formatted = []
        for idx, r in enumerate(results, 1):
            pct = int(r.score * 100)
            breadcrumb = f" > {r.header_path}" if r.header_path else ""
            tags_str = f" [Tags: {', '.join(r.tags)}]" if r.tags else ""
            entry = (
                f"### Result {idx}: {r.title}{breadcrumb} ({pct}% Match)\n"
                f"- **File:** `{r.doc_id}`{tags_str}\n"
                f"- **Snippet:**\n{r.snippet}\n"
            )
            formatted.append(entry)

        return "\n---\n".join(formatted)

    # =========================================================================
    # TOOL: read_note
    # =========================================================================
    @server.tool(
        name="read_note",
        description=(
            "Read a note by the path shown in search_brain results. Pass `heading` to read "
            "a single section instead of the whole note."
        ),
    )
    def read_note(path: str, heading: Optional[str] = None, max_chars: int = NOTE_MAX_CHARS) -> str:
        """Return a note, or one section of it, within a size budget."""
        note = resolve_note(path)
        if note is None:
            return f"Note '{path}' not found. Use the path exactly as search_brain returned it."

        content = note.read_text(encoding="utf-8", errors="replace")
        if heading:
            section = extract_section(content, heading)
            if section is None:
                headings = [line.lstrip("#").strip() for line in content.splitlines() if line.startswith("#")]
                return f"No heading matching '{heading}' in `{path}`. Headings: {'; '.join(headings[:30])}"
            content = section

        return truncate_to_budget(content, max_chars, READ_NOTE_HINT)

    # =========================================================================
    # TOOL: get_project_context
    # =========================================================================
    @server.tool(
        name="get_project_context",
        description="Retrieve the project card (overview, stack, structure, status) for a project in 10_Projects/.",
    )
    def get_project_context(project_name: str, max_chars: int = PROJECT_MAX_CHARS) -> str:
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
            fallback_results = engine.search(
                query=f"project {project_name}", limit=2, scope="all", one_per_note=True
            )
            if fallback_results:
                return (
                    f"Project file for '{project_name}' not found directly. Closest matches:\n\n"
                    + "\n\n".join(f"**{r.title}** (`{r.doc_id}`):\n{r.snippet}" for r in fallback_results)
                )
            return f"No documentation found for project '{project_name}' in '{DIR_PROJECTS}/'."

        content = found_file.read_text(encoding="utf-8", errors="replace")
        rel_path = found_file.relative_to(vault_path).as_posix()
        body = truncate_to_budget(content, max_chars, f"Call read_note('{rel_path}', heading=...) for the rest.")
        return f"# Project Context: `{rel_path}`\n\n{body}"

    # =========================================================================
    # TOOL: build_task_context (Context Assembly Engine)
    # =========================================================================
    @server.tool(
        name="build_task_context",
        description=(
            "Call first when starting work on a project: one compact briefing with user preferences, "
            "project state, active decisions, remembered facts, relevant notes, and recent sessions."
        ),
    )
    def build_task_context(task: str, project: str) -> str:
        """Assemble complete task briefing card."""
        core = [m["content"] for m in memory.core_memories(project)]
        memories = [m["content"] for m in memory.recall_for_briefing(task, project)]
        card = context_engine.build_task_context(
            task=task, project=project, memories=memories, core_memories=core
        )
        return card.to_markdown()

    # =========================================================================
    # TOOL: get_user_context
    # =========================================================================
    @server.tool(
        name="get_user_context",
        description="Retrieve global user preferences, coding persona, styling rules, and constraints.",
    )
    def get_user_context() -> str:
        """Retrieve user coding persona."""
        return context_engine.get_user_preferences()

    # =========================================================================
    # TOOL: get_decisions
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
    # TOOL: record_decision
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
    # TOOL: write_agent_log
    # =========================================================================
    @server.tool(
        name="write_agent_log",
        description="Record a session summary or progress log into 90_Agent_Inbox/ (append-only).",
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

        # json.dumps yields a double-quoted scalar, which is valid YAML for any input
        note_content = f"""---
id: "LOG-{timestamp_str}-{log_id}"
title: {json.dumps(summary, ensure_ascii=False)}
type: agent-log
author: {json.dumps(author, ensure_ascii=False)}
device: {json.dumps(config.device_name, ensure_ascii=False)}
created: "{now.isoformat()}"
tags: {json.dumps(all_tags, ensure_ascii=False)}
---

# 📝 {summary}

## Overview:
{details.strip()}

---
*Logged automatically by Central Brain Agent Protocol at {now.strftime('%Y-%m-%d %H:%M:%S UTC')}*
"""

        atomic_write_text(file_path, note_content)

        engine.index_vault(force_reindex=False)
        rel_path = file_path.relative_to(vault_path).as_posix()
        return f"Successfully recorded agent log into `{rel_path}` and indexed into Central Brain memory."

    # =========================================================================
    # TOOL: load_skill
    # =========================================================================
    @server.tool(
        name="load_skill",
        description="Load instructions and workflow procedures for an Agent Skill stored in 00_System/Agent_Skills/ or custom skill roots.",
    )
    def load_skill(skill_name: str) -> str:
        """Read SKILL.md for a requested skill name from vault or external roots."""
        skills_dir = vault_path / DIR_AGENT_SKILLS
        clean_name = skill_name.strip().replace(" ", "-").lower()
        external_roots = [Path(root).resolve() for root in config.custom_skill_roots]

        # A skill name is a folder name, never a path
        if _SKILL_NAME.match(clean_name):
            search_locations = [skills_dir / clean_name / "SKILL.md"]
            for root in external_roots:
                search_locations.append(root / clean_name / "SKILL.md")
                search_locations.append(root / "skills" / clean_name / "SKILL.md")

            for skill_file in search_locations:
                if skill_file.is_file():
                    skill_content = skill_file.read_text(encoding="utf-8", errors="replace")
                    return f"# Active Skill Instructions: `{clean_name}` (from `{skill_file}`)\n\n{skill_content}"

        all_skills: list[str] = []
        for root in [skills_dir, *external_roots]:
            if root.is_dir():
                all_skills.extend(
                    d.name for d in root.glob("*") if d.is_dir() and (d / "SKILL.md").is_file()
                )

        if all_skills:
            return (
                f"Skill '{skill_name}' not found.\n"
                f"Available active skills in vault & external roots: {', '.join(sorted(set(all_skills)))}"
            )
        return f"Skill '{skill_name}' not found and no skills are currently available."

    # =========================================================================
    # TOOLS: remember / recall / forget (long-term memory)
    # =========================================================================
    @server.tool(
        name="remember",
        description=(
            "Save one durable fact, preference, or lesson for future sessions (one fact per call, "
            "under 1000 characters). Use scope='PROJECT' with a project name for project-specific "
            "facts. Pass `supersedes` with an old memory id when this replaces it. Set `pinned` only "
            "for a fact every future session must see; pinned memories share a small budget."
        ),
    )
    def remember(
        content: str,
        scope: Literal["GLOBAL", "PROJECT", "TASK", "SESSION"] = "GLOBAL",
        project: Optional[str] = None,
        tags: Optional[List[str]] = None,
        supersedes: Optional[str] = None,
        pinned: bool = False,
    ) -> str:
        """Store a long-term memory."""
        try:
            result = memory.remember(
                content=content,
                scope=scope,
                project=project,
                tags=tags,
                source="mcp",
                supersedes=supersedes,
                pinned=pinned,
            )
        except ValueError as e:
            return f"Not saved: {e}"

        if not result["created"]:
            return f"Already remembered as `{result['id']}` ({result['status']})."
        if result["status"] == "pending":
            return (
                f"Saved as `{result['id']}`, waiting for the owner's approval. "
                "It is not visible to recall or briefings until approved."
            )
        note = f" Replaced `{result['superseded']}`." if result["superseded"] else ""
        return f"Remembered as `{result['id']}`.{note}"

    @server.tool(
        name="recall",
        description=(
            "Retrieve remembered facts relevant to a query. With `project`, returns that project's "
            "memories plus global ones. With an empty query, returns the most recent memories."
        ),
    )
    def recall(query: str = "", project: Optional[str] = None, limit: int = 5) -> str:
        """Search long-term memories."""
        memories = memory.recall(query, project=project, limit=limit)
        if not memories:
            return "No matching memories."

        lines = []
        for m in memories:
            where = m["project"] or m["scope"].lower()
            lines.append(f"- `{m['id']}` ({where}): {m['content']}")
        return "\n".join(lines)

    @server.tool(
        name="forget",
        description="Retire a memory by id when it is wrong or no longer true.",
    )
    def forget(memory_id: str) -> str:
        """Mark a memory as forgotten."""
        if memory.forget(memory_id.strip().strip("`")):
            return f"Forgot `{memory_id}`."
        return f"No memory with id `{memory_id}`."

    return server
