"""CLI command group for Architecture Decision Records (devbrain adr)."""

from pathlib import Path
from typing import Optional

from rich.table import Table
import typer

from devbrain.adr.manager import ADRManager
from devbrain.cli.ui.console import console
from devbrain.core.config import find_config, load_config

adr_app = typer.Typer(
    name="adr",
    help="Manage Architecture Decision Records (ADRs) to preserve architectural consistency.",
    no_args_is_help=True,
)


@adr_app.command(name="new")
def adr_new(
    title: str = typer.Argument(..., help="Title of the architecture decision"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Target project name"),
    context: str = typer.Option("", "--context", "-c", help="Context and problem description"),
    decision: str = typer.Option("", "--decision", "-d", help="Decision outcome and chosen solution"),
    consequences: str = typer.Option("", "--consequences", help="Key consequences or trade-offs"),
    alternatives: str = typer.Option("", "--alternatives", help="Alternatives evaluated"),
    status: str = typer.Option("accepted", "--status", help="ADR status (accepted, draft, deprecated)"),
    vault: Optional[Path] = typer.Option(None, "--vault", "-v", help="Path to Obsidian vault"),
):
    """Create a new Architecture Decision Record (ADR) in 30_Decisions/."""
    vault_path = _resolve_vault(vault)
    manager = ADRManager(vault_path)

    res = manager.create_decision(
        title=title,
        project=project,
        context=context,
        decision=decision,
        consequences=consequences,
        alternatives=alternatives,
        status=status,
    )

    console.print(f"[green]✓ Created Architecture Decision Record: [bold]{res['id']}[/bold] - {res['title']}[/green]")
    console.print(f"  [dim]Saved to: {res['file_path']}[/dim]")
    if project:
        console.print(f"  [dim]Linked to project: [[{project}]][/dim]")


@adr_app.command(name="list")
def adr_list(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Filter by project name"),
    status: Optional[str] = typer.Option("accepted", "--status", help="Filter by status (accepted, draft, all)"),
    vault: Optional[Path] = typer.Option(None, "--vault", "-v", help="Path to Obsidian vault"),
):
    """List Architecture Decision Records in the vault."""
    vault_path = _resolve_vault(vault)
    manager = ADRManager(vault_path)

    filter_status = None if status == "all" else status
    decisions = manager.list_decisions(project=project, status=filter_status)

    if not decisions:
        proj_str = f" for project '{project}'" if project else ""
        console.print(f"[yellow]No ADRs found{proj_str}. Create one with 'devbrain adr new \"<title>\"'.[/yellow]")
        return

    table = Table(title="Architecture Decision Records (ADR)", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="bold yellow", width=10)
    table.add_column("Title", style="white")
    table.add_column("Project", style="green", width=18)
    table.add_column("Status", style="magenta", width=12)
    table.add_column("Date", style="dim", width=12)

    for d in decisions:
        table.add_row(
            d.get("id", "ADR"),
            d.get("title", ""),
            d.get("project") or "Global",
            d.get("status", "accepted"),
            d.get("date", ""),
        )

    console.print(table)


def _resolve_vault(vault: Optional[Path]) -> Path:
    """Resolve vault path from argument, config file, or current directory."""
    if vault:
        return vault.resolve()

    cfg_file = find_config()
    if cfg_file:
        cfg = load_config(cfg_file)
        return cfg.resolve_vault_path()

    return Path.cwd().resolve()
