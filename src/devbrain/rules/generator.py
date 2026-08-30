"""Workspace Rules and Adapter Generator for DevBrain (AGENTS.md & CLAUDE.md)."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class RulesGenerator:
    """Generates standardized AGENTS.md and CLAUDE.md files with Hierarchy of Truth rules."""

    def __init__(self, vault_path: Optional[Path] = None):
        self.vault_path = Path(vault_path).resolve() if vault_path else None

    def generate_agents_md(
        self,
        project_name: str,
        tech_stack: Optional[list[str]] = None,
        custom_instructions: Optional[str] = None,
    ) -> str:
        """Generate content for AGENTS.md."""
        stack_str = ", ".join(tech_stack) if tech_stack else "Detected Project Stack"
        vault_ref = str(self.vault_path) if self.vault_path else "Central AI Brain Hub Vault"

        return f"""# {project_name} - AI Agent Operational Rules & Context

> **DevBrain PAIOS Standard Rule Contract**
> Generated on: `{datetime.now(timezone.utc).strftime("%Y-%m-%d")}`
> Central Brain Vault: `{vault_ref}`

---

## 🏛️ Hierarchy of Truth (Strict Priority)

When resolving conflicting information, all AI agents MUST adhere to this strict hierarchy:

1. **Current Working Codebase (Highest Authority):** Actual implementation code in this workspace reflects true current behavior.
2. **Central Brain ADRs & Obsidian Notes:** Documented architectural decisions in `30_Decisions/` and `10_Projects/{project_name}/`.
3. **This File (`AGENTS.md` / `CLAUDE.md`):** Operational rules, coding conventions, and testing commands.
4. **AI Chat / Session History (Lowest Authority):** Ephemeral conversation context that may contain hallucinated or obsolete ideas.

---

## 🛠️ Project Specifications & Stack
- **Project Name:** `{project_name}`
- **Primary Tech Stack:** `{stack_str}`
- **Documentation:** Always update `CHANGELOG.md` upon modifying core functionality.

---

## 📋 General Coding Standards & Rules
1. **Type Safety & Clean Architecture:** Use strict typing, avoid `any`/untyped patterns, and keep modules decoupled.
2. **Atomic Commits:** Make clean, descriptive git commits following standard Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`).
3. **No Unilateral Architecture Shifts:** If a task requires swapping core libraries or database engines, check `30_Decisions/` or propose an ADR first.
4. **Secret Protection:** Never commit `.env` files, credentials, or raw API keys.

---

## 🧠 DevBrain MCP Integration
When connected to the DevBrain FastMCP server, utilize these tools:
- `build_task_context(task, project)`: Retrieve situational briefing before starting complex tasks.
- `get_decisions(project)`: Check active Architecture Decision Records (ADRs).
- `load_skill(skill_name)`: Dynamically load reusable skills from Central Brain.
- `write_agent_log(project, title, summary)`: Persist session discoveries.

---
{custom_instructions.strip() if custom_instructions else ''}
"""

    def generate_claude_md(self, project_name: str, tech_stack: Optional[list[str]] = None) -> str:
        """Generate content for CLAUDE.md for Claude Code CLI."""
        return self.generate_agents_md(project_name, tech_stack)

    def write_rules_to_project(
        self,
        project_dir: Path,
        project_name: Optional[str] = None,
        tech_stack: Optional[list[str]] = None,
        overwrite: bool = False,
    ) -> dict[str, Path]:
        """Write AGENTS.md and CLAUDE.md to project directory."""
        p_dir = Path(project_dir).resolve()
        p_name = project_name or p_dir.name

        agents_file = p_dir / "AGENTS.md"
        claude_file = p_dir / "CLAUDE.md"

        written: dict[str, Path] = {}

        if not agents_file.exists() or overwrite:
            agents_content = self.generate_agents_md(p_name, tech_stack)
            with open(agents_file, "w", encoding="utf-8") as f:
                f.write(agents_content)
            written["AGENTS.md"] = agents_file

        if not claude_file.exists() or overwrite:
            claude_content = self.generate_claude_md(p_name, tech_stack)
            with open(claude_file, "w", encoding="utf-8") as f:
                f.write(claude_content)
            written["CLAUDE.md"] = claude_file

        return written
