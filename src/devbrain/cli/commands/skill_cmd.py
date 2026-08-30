"""Skill command managing AI Agent Skills in 00_System/Agent_Skills/ and external roots."""

import os
from pathlib import Path
from typing import Optional

from rich.table import Table
import typer

from devbrain.cli.ui.console import console, print_banner, print_error, print_info, print_success
from devbrain.core.config import find_config, load_config, save_config
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


@skill_app.command(name="list", help="List all active Agent Skills in the vault and external roots.")
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

    table = Table(title="🤖 Active Central Brain Agent Skills", border_style="cyan")
    table.add_column("Skill Name", style="bold white", width=22)
    table.add_column("Source", style="magenta", width=14)
    table.add_column("Description", style="cyan")
    table.add_column("Path", style="dim white")

    count = 0
    if skills_dir.is_dir():
        for sf in skills_dir.glob("*/SKILL.md"):
            skill_name = sf.parent.name
            try:
                with open(sf, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                fm, _ = parse_frontmatter(content)
                desc = fm.get("description", "(No description)")
            except Exception:
                desc = "(Error reading metadata)"
            rel_path = sf.relative_to(vault_dir).as_posix()
            table.add_row(skill_name, "Vault", str(desc), rel_path)
            count += 1

    for ext_root in config.custom_skill_roots:
        p = Path(ext_root).resolve()
        if p.is_dir():
            for sf in p.glob("*/SKILL.md"):
                skill_name = sf.parent.name
                try:
                    with open(sf, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()
                    fm, _ = parse_frontmatter(content)
                    desc = fm.get("description", "(No description)")
                except Exception:
                    desc = "(External skill)"
                table.add_row(skill_name, "External", str(desc), str(sf))
                count += 1

    if count == 0:
        console.print(f"\n[bold yellow]No active skills found in:[/bold yellow] `{skills_dir}`\n")
        console.print("Create one using: [bold cyan]devbrain skill add <name>[/bold cyan]\n")
        return

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


@skill_app.command(name="link", help="Register an external skill folder into Central Brain.")
def link_skill(
    path: Path = typer.Argument(..., help="Path to external skill folder (e.g. E:/_PROJECT/_agent-skill)"),
    global_link: bool = typer.Option(False, "--global", "-g", help="Also symlink to Antigravity global config"),
    vault: Optional[str] = typer.Option(None, "--vault", "-v", help="Manual path to vault"),
):
    """Link an external skill directory to Central Brain configuration."""
    print_banner()
    ext_path = path.resolve()
    if not ext_path.is_dir():
        print_error(f"Directory not found: {ext_path}")
        raise typer.Exit(1)

    config_path = Path(vault).resolve() / ".brainrc.json" if vault else find_config()
    if not config_path or not config_path.is_file():
        print_error("Configuration file .brainrc.json not found! Run 'devbrain init' first.")
        raise typer.Exit(code=1)

    config = load_config(config_path)
    path_str = str(ext_path)
    if path_str not in config.custom_skill_roots:
        config.custom_skill_roots.append(path_str)
        save_config(config, config_path)
        print_success(f"Registered external skill root: [bold cyan]{path_str}[/bold cyan]")
    else:
        print_info(f"External skill root already registered: {path_str}")

    if global_link:
        global_skills_dir = Path.home() / ".gemini" / "config" / "skills"
        global_skills_dir.mkdir(parents=True, exist_ok=True)
        dest_link = global_skills_dir / ext_path.name
        if not dest_link.exists():
            try:
                os.symlink(ext_path, dest_link, target_is_directory=True)
                print_success(f"Linked {ext_path.name} to global Antigravity config ({dest_link}).")
            except Exception as e:
                print_info(f"Note: Symlink creation skipped ({e}).")


@skill_app.command(name="attach", help="Attach a skill to a specific project (.agents/skills/).")
def attach_skill(
    skill_name: str = typer.Argument(..., help="Name of skill to attach"),
    project_dir: Path = typer.Option(Path("."), "--project", "-p", help="Target project directory"),
    vault: Optional[str] = typer.Option(None, "--vault", "-v", help="Manual path to vault"),
):
    """Mount a Central Brain skill into project workspace .agents/skills/."""
    print_banner()
    config_path = Path(vault).resolve() / ".brainrc.json" if vault else find_config()
    if not config_path or not config_path.is_file():
        print_error("Configuration file .brainrc.json not found! Run 'devbrain init' first.")
        raise typer.Exit(code=1)

    config = load_config(config_path)
    vault_dir = config.resolve_vault_path()

    clean_name = skill_name.strip().replace(" ", "-").lower()
    source_skill = vault_dir / DIR_AGENT_SKILLS / clean_name

    if not source_skill.is_dir():
        # Check custom roots
        for ext_root in config.custom_skill_roots:
            cand = Path(ext_root) / clean_name
            if cand.is_dir():
                source_skill = cand
                break

    if not source_skill.is_dir():
        print_error(f"Skill '{clean_name}' not found in vault or custom skill roots.")
        raise typer.Exit(1)

    target_agents_dir = project_dir.resolve() / ".agents" / "skills" / clean_name
    target_agents_dir.parent.mkdir(parents=True, exist_ok=True)

    if target_agents_dir.exists():
        print_info(f"Skill already attached at: {target_agents_dir}")
        return

    try:
        os.symlink(source_skill, target_agents_dir, target_is_directory=True)
        print_success(f"Successfully attached skill '{clean_name}' to [bold]{target_agents_dir}[/bold]")
    except Exception:
        # Fallback to creating a proxy SKILL.md
        target_agents_dir.mkdir(parents=True, exist_ok=True)
        src_file = source_skill / "SKILL.md"
        if src_file.is_file():
            with open(src_file, "r", encoding="utf-8") as f:
                content = f.read()
            with open(target_agents_dir / "SKILL.md", "w", encoding="utf-8") as f:
                f.write(content)
        print_success(f"Mounted skill '{clean_name}' into [bold]{target_agents_dir}[/bold]")


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
    for sf in skill_folders:
        dest_link = global_skills_dir / sf.name
        if not dest_link.exists():
            try:
                os.symlink(sf, dest_link, target_is_directory=True)
            except Exception:
                pass

    print_success(f"Synced {len(skill_folders)} vault skills to Antigravity global directory ({global_skills_dir}).")
