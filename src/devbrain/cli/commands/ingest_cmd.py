"""Ingest command for seeding and continuous harvesting of AI agent sessions."""

from pathlib import Path
import time
from typing import Optional

from rich.table import Table
import typer

from devbrain.cli.ui.console import console, print_banner, print_error, print_info, print_success, print_warning
from devbrain.core.config import find_config, load_config
from devbrain.harvester.service import IngestionService


def ingest_command(
    from_source: str = typer.Option(
        "all",
        "--from",
        "-f",
        help="Source agent to ingest from ('antigravity', 'claude-code', or 'all')",
    ),
    limit: Optional[int] = typer.Option(
        None,
        "--limit",
        "-n",
        help="Maximum number of sessions to ingest",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview discoverable sessions without writing files to vault",
    ),
    watch: bool = typer.Option(
        False,
        "--watch",
        "-w",
        help="Continuously monitor and ingest new sessions in background loop",
    ),
    interval: int = typer.Option(
        15,
        "--interval",
        help="Polling interval in seconds when running with --watch (default: 15s)",
    ),
    vault: Optional[str] = typer.Option(
        None,
        "--vault",
        "-v",
        help="Manual path to Obsidian vault",
    ),
):
    """Harvest and seed AI Agent sessions into Obsidian 90_Agent_Inbox/."""
    print_banner()

    config_path = Path(vault).resolve() / ".brainrc.json" if vault else find_config()
    if not config_path or not config_path.is_file():
        print_error("Configuration file .brainrc.json not found! Run 'devbrain init' first.")
        raise typer.Exit(code=1)

    config = load_config(config_path)
    vault_dir = config.resolve_vault_path()

    service = IngestionService(vault_path=vault_dir, config=config)

    sources = [from_source.strip().lower()] if from_source.lower() != "all" else None

    if dry_run:
        print_warning("Running in DRY-RUN mode (no files will be written to disk)...")

    if watch:
        console.print(f"[bold green]👀 Watching for new AI sessions every {interval}s... (Press Ctrl+C to stop)[/bold green]\n")
        try:
            while True:
                res = service.run_ingestion(sources=sources, limit=limit, dry_run=False)
                if res.ingested > 0:
                    print_success(f"[{time.strftime('%H:%M:%S')}] Ingested {res.ingested} new sessions ({res.total_redactions} secrets redacted).")
                time.sleep(interval)
        except KeyboardInterrupt:
            console.print("\n[yellow]Watcher stopped.[/yellow]")
            return

    # Normal one-shot execution
    with console.status("[bold green]Scanning system for AI agent sessions...[/bold green]"):
        result = service.run_ingestion(sources=sources, limit=limit, dry_run=dry_run)

    table = Table(title="🚜 AI Session Ingestion Report", border_style="cyan")
    table.add_column("Metric", style="bold white")
    table.add_column("Value", style="bold cyan")

    table.add_row("Total Discovered Sessions", str(result.discovered))
    table.add_row("New Sessions Ingested", f"[green]{result.ingested}[/green]")
    table.add_row("Already Ingested / Skipped", str(result.skipped))
    table.add_row("Secrets & API Keys Redacted", f"[yellow]{result.total_redactions}[/yellow]")

    console.print()
    console.print(table)
    console.print()

    if result.ingested > 0 and not dry_run:
        print_success(f"Successfully seeded {result.ingested} session notes into 90_Agent_Inbox/ and updated index.")
    elif result.discovered == 0:
        print_info("No external agent sessions found on this machine.")
    elif result.ingested == 0 and not dry_run:
        print_info("All discovered sessions are already up to date in vault memory.")
