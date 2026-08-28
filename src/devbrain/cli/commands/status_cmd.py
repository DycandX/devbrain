"""Status and health check command for devbrain vault."""

from pathlib import Path
from typing import Optional

import typer
from rich.table import Table

from devbrain.cli.ui.console import console, print_banner, print_error
from devbrain.core.config import find_config, load_config
from devbrain.core.constants import (
    DIR_AGENT_SKILLS,
    DIR_DAILY,
    DIR_DECISIONS,
    DIR_INBOX,
    DIR_KNOWLEDGE,
    DIR_PROJECTS,
    DIR_SYSTEM,
)


def status_command(
    path: Optional[str] = typer.Option(
        None,
        "--vault",
        "-v",
        help="Manual path to vault (default: search for .brainrc.json automatically)",
    ),
):
    """Display vault status, active configuration parameters, and note counts."""
    print_banner()

    # 1. Locate Config File
    if path:
        config_path = Path(path).expanduser().resolve()
        if config_path.is_dir():
            config_path = config_path / ".brainrc.json"
    else:
        config_path = find_config()

    if not config_path or not config_path.is_file():
        print_error(
            "Configuration file .brainrc.json not found!\n"
            "Run [bold cyan]devbrain init[/bold cyan] first to set up your Obsidian vault."
        )
        raise typer.Exit(code=1)

    try:
        config = load_config(config_path)
    except Exception as e:
        print_error(f"Failed to load configuration: {e}")
        raise typer.Exit(code=1)

    vault_dir = config.resolve_vault_path()

    # 2. Count Markdown Documents
    all_md_files = list(vault_dir.rglob("*.md")) if vault_dir.is_dir() else []

    system_count = len(list((vault_dir / DIR_SYSTEM).rglob("*.md"))) if (vault_dir / DIR_SYSTEM).is_dir() else 0
    skills_count = len(list((vault_dir / DIR_AGENT_SKILLS).glob("*/SKILL.md"))) if (vault_dir / DIR_AGENT_SKILLS).is_dir() else 0
    projects_count = len(list((vault_dir / DIR_PROJECTS).rglob("*.md"))) if (vault_dir / DIR_PROJECTS).is_dir() else 0
    knowledge_count = len(list((vault_dir / DIR_KNOWLEDGE).rglob("*.md"))) if (vault_dir / DIR_KNOWLEDGE).is_dir() else 0
    decisions_count = len(list((vault_dir / DIR_DECISIONS).rglob("*.md"))) if (vault_dir / DIR_DECISIONS).is_dir() else 0
    inbox_count = len(list((vault_dir / DIR_INBOX).rglob("*.md"))) if (vault_dir / DIR_INBOX).is_dir() else 0
    daily_count = len(list((vault_dir / DIR_DAILY).rglob("*.md"))) if (vault_dir / DIR_DAILY).is_dir() else 0

    # 3. Render Status Table
    table = Table(title="📊 Central AI Brain Hub Status", border_style="cyan", show_header=True)
    table.add_column("Parameter", style="bold white", width=26)
    table.add_column("Configuration / Note Statistics", style="bold cyan")

    table.add_row("Vault Directory", str(vault_dir))
    table.add_row("Device Identifier", config.device_name)
    table.add_row("Embedding Provider", f"{config.embedding_provider} ({config.embedding_model})")
    table.add_row("Scope Filter", config.scope)
    table.add_row("Total Markdown Notes", f"{len(all_md_files)} files")
    table.add_row("  ├── 00_System (Rules & Context)", f"{system_count} files")
    table.add_row("  ├── Agent Skills Active", f"{skills_count} skills")
    table.add_row("  ├── 10_Projects (Active Context)", f"{projects_count} files")
    table.add_row("  ├── 20_Knowledge (Patterns & Bugs)", f"{knowledge_count} files")
    table.add_row("  ├── 30_Decisions (ADR Records)", f"{decisions_count} files")
    table.add_row("  ├── 90_Agent_Inbox (Logs)", f"{inbox_count} files")
    table.add_row("  └── 99_Daily (Daily Notes)", f"{daily_count} files")
    table.add_row("Last Updated", config.updated_at)

    console.print(table)
