"""Skill command managing AI Agent Skills in 00_System/Agent_Skills/."""

import os
from pathlib import Path
from typing import Optional

import typer
from rich.table import Table

from devbrain.cli.ui.console import console, print_banner, print_error, print_info, print_success
from devbrain.core.config import find_config, load_config
from devbrain.core.constants import DIR_AGENT_SKILLS
from devbrain.engine.parser import parse_frontmatter

skill_app = typer.Typer(
    name="skill",
    help="Manage, scaffold, and sync modular AI Agent Skills in 00_System/Agent_Skills/.",
    no_args_is_help=True,
)

SKILL_TEMPLATE = """---
name: {skill_name}
description: Detailed description of what this AI Agent Skill does and when to use it.
---

# {title_name} Skill

Provide step-by-step instructions for AI Agents using this skill.

## 🎯 Workflow Steps:
1. Verify required prerequisites and environment tools.
2. Read project context from `10_Projects/`.
3. Execute the workflow procedure.
4. Record summary of changes to `90_Agent_Inbox/`.
"""


@skill_app.command(name="list", help="List all active Agent Skills in the vault.")
def list_skills(
    vault: Optional[str] = typer.Option(None, "--vault", "-v", help="Manual path to vault"),
):
    print_banner()

    config_path = Path(vault).resolve() / ".brainrc.json" if vault else find_config()
    if not config_path or not config_path.is_file():
        print_error("Configuration file .brainrc.json not found! Run 'devbrain init' first.")
        raise typer.Exit(code=1)

    config = load_config(config_path)
    vault_dir = config.resolve_vault_path()
    skills_dir = vault_dir / DIR_AGENT_SKILLS

    if not skills_dir.is_dir():
        print_info(f"No skills directory found at: {skills_dir}")
        return

    skill_files = list(skills_dir.glob("*/SKILL.md"))
    if not skill_files:
        console.print(f"\n[bold yellow]No active skills found in:[/bold yellow] `{skills_dir}`\n")
        console.print("Create one using: [bold cyan]devbrain skill add <name>[/bold cyan]\n")
        return

    table = Table(title="🤖 Active Central Brain Agent Skills", border_style="cyan")
    table.add_column("Skill Name", style="bold white", width=22)
    table.add_column("Description", style="cyan")
    table.add_column("Path", style="dim white")

    for sf in skill_files:
        skill_name = sf.parent.name
        try:
            with open(sf, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            fm, _ = parse_frontmatter(content)
            desc = fm.get("description", "(No description)")
        except Exception:
            desc = "(Error reading metadata)"

        rel_path = sf.relative_to(vault_dir).as_posix()
        table.add_row(skill_name, str(desc), rel_path)

    console.print(table)
    console.print()


@skill_app.command(name="add", help="Create a new Agent Skill template in the vault.")
def add_skill(
    name: str = typer.Argument(..., help="Name of the new skill (e.g. docker-deployment, api-audit)"),
    vault: Optional[str] = typer.Option(None, "--vault", "-v", help="Manual path to vault"),
):
    print_banner()

    config_path = Path(vault).resolve() / ".brainrc.json" if vault else find_config()
    if not config_path or not config_path.is_file():
        print_error("Configuration file .brainrc.json not found! Run 'devbrain init' first.")
        raise typer.Exit(code=1)

    config = load_config(config_path)
    vault_dir = config.resolve_vault_path()
    skills_dir = vault_dir / DIR_AGENT_SKILLS

    clean_name = name.strip().replace(" ", "-").lower()
    target_dir = skills_dir / clean_name
    target_file = target_dir / "SKILL.md"

    if target_file.is_file():
        print_error(f"Skill '{clean_name}' already exists at: {target_file}")
        raise typer.Exit(code=1)

    target_dir.mkdir(parents=True, exist_ok=True)
    title_name = clean_name.replace("-", " ").replace("_", " ").title()
    content = SKILL_TEMPLATE.format(skill_name=clean_name, title_name=title_name)

    with open(target_file, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

    print_success(f"Created new skill template at: [bold cyan]{target_file}[/bold cyan]")


@skill_app.command(name="symlink", help="Link vault skills to Antigravity global skills folder.")
def symlink_skills(
    vault: Optional[str] = typer.Option(None, "--vault", "-v", help="Manual path to vault"),
):
    print_banner()

    config_path = Path(vault).resolve() / ".brainrc.json" if vault else find_config()
    if not config_path or not config_path.is_file():
        print_error("Configuration file .brainrc.json not found! Run 'devbrain init' first.")
        raise typer.Exit(code=1)

    config = load_config(config_path)
    vault_dir = config.resolve_vault_path()
    skills_dir = vault_dir / DIR_AGENT_SKILLS

    global_skills_dir = Path.home() / ".gemini" / "config" / "skills"
    global_skills_dir.mkdir(parents=True, exist_ok=True)

    skill_folders = [d for d in skills_dir.glob("*") if d.is_dir() and (d / "SKILL.md").is_file()]
    linked_count = 0

    for sf in skill_folders:
        dest_link = global_skills_dir / sf.name
        if not dest_link.exists():
            try:
                # Try creating symlink or junction
                os.symlink(sf, dest_link, target_is_directory=True)
                linked_count += 1
            except Exception:
                pass

    print_success(f"Synced {len(skill_folders)} vault skills to Antigravity global directory ({global_skills_dir}).")
