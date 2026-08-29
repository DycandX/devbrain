"""Unified Ingestion CLI Commands for Sessions, Targeted Projects, and Workspaces."""

from pathlib import Path
import time
from typing import Optional

from rich.table import Table
import typer

from devbrain.cli.ui.console import console, print_banner, print_error, print_info, print_success, print_warning
from devbrain.core.config import find_config, load_config
from devbrain.harvester.inspector import RepoType
from devbrain.harvester.service import IngestionService

ingest_app = typer.Typer(
    name="ingest",
    help="Harvest and seed AI agent sessions and local repositories into Obsidian Vault.",
    invoke_without_command=True,
)


@ingest_app.callback()
def default_ingest_callback(
    ctx: typer.Context,
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
    """Default callback when running `devbrain ingest` without subcommand (harvests AI sessions)."""
    if ctx.invoked_subcommand is not None:
        return

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
                    print_success(f"[{time.strftime('%H:%M:%S')}] Ingested {res.ingested} new sessions ({res.linked_projects} graph links connected).")
                time.sleep(interval)
        except KeyboardInterrupt:
            console.print("\n[yellow]Watcher stopped.[/yellow]")
            return

    # One-shot execution
    with console.status("[bold green]Scanning system for AI agent sessions & connecting graph...[/bold green]"):
        result = service.run_ingestion(sources=sources, limit=limit, dry_run=dry_run)

    table = Table(title="🚜 AI Session Ingestion Report", border_style="cyan")
    table.add_column("Metric", style="bold white")
    table.add_column("Value", style="bold cyan")

    table.add_row("Total Discovered Sessions", str(result.discovered))
    table.add_row("New Sessions Ingested", f"[green]{result.ingested}[/green]")
    table.add_row("Already Ingested / Skipped", str(result.skipped))
    table.add_row("Project Nodes Connected", f"[magenta]{result.linked_projects}[/magenta]")
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


@ingest_app.command("project")
def ingest_single_project_cmd(
    target_path: str = typer.Argument(
        ".",
        help="Path to repository or project directory to ingest (default: current dir '.')",
    ),
    target_type: Optional[str] = typer.Option(
        None,
        "--type",
        "-t",
        help="Explicit repository type override ('project', 'reference', 'skill', 'knowledge')",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Inspect repository without writing to vault",
    ),
    vault: Optional[str] = typer.Option(
        None,
        "--vault",
        "-v",
        help="Manual path to Obsidian vault",
    ),
):
    """Targeted ingestion for a single project, skill, or reference repository."""
    print_banner()

    repo_dir = Path(target_path).resolve()
    if not repo_dir.is_dir():
        print_error(f"Target path does not exist or is not a directory: {repo_dir}")
        raise typer.Exit(code=1)

    config_path = Path(vault).resolve() / ".brainrc.json" if vault else find_config()
    if not config_path or not config_path.is_file():
        print_error("Configuration file .brainrc.json not found! Run 'devbrain init' first.")
        raise typer.Exit(code=1)

    config = load_config(config_path)
    vault_dir = config.resolve_vault_path()
    service = IngestionService(vault_path=vault_dir, config=config)

    with console.status(f"[bold green]Inspecting and harvesting '{repo_dir.name}'...[/bold green]"):
        metadata, created_file = service.ingest_single_project(
            repo_path=repo_dir,
            explicit_type=target_type,
            dry_run=dry_run,
        )

    table = Table(title=f"📦 Repository Inspection: {metadata.name}", border_style="cyan")
    table.add_column("Property", style="bold white")
    table.add_column("Details", style="bold cyan")

    table.add_row("Repository Name", metadata.name)
    table.add_row("Classified Type", f"[bold green]{metadata.repo_type.value.upper()}[/bold green]")
    table.add_row("Classification Reason", metadata.type_reason)
    table.add_row("Languages", ", ".join(metadata.languages))
    table.add_row("Tech Stack", ", ".join(metadata.stack_tags) or "Standard")
    table.add_row("Git Remote", metadata.git_remote or "Local Repository")
    table.add_row("Target Location", str(created_file) if created_file else "DRY-RUN (No file written)")

    console.print()
    console.print(table)
    console.print()

    if created_file and not dry_run:
        print_success(f"Successfully seeded note for '{metadata.name}' at:\n[bold white]{created_file}[/bold white]")


@ingest_app.command("projects")
def ingest_workspace_projects_cmd(
    directory: Optional[str] = typer.Option(
        None,
        "--dir",
        "-d",
        help="Specific workspace folder to scan (defaults to configured workspace_roots)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Scan and preview without writing to vault",
    ),
    vault: Optional[str] = typer.Option(
        None,
        "--vault",
        "-v",
        help="Manual path to Obsidian vault",
    ),
):
    """Batch scan workspace root folders for Git repositories and codebases."""
    print_banner()

    config_path = Path(vault).resolve() / ".brainrc.json" if vault else find_config()
    if not config_path or not config_path.is_file():
        print_error("Configuration file .brainrc.json not found! Run 'devbrain init' first.")
        raise typer.Exit(code=1)

    config = load_config(config_path)
    vault_dir = config.resolve_vault_path()
    service = IngestionService(vault_path=vault_dir, config=config)

    roots = [Path(directory).resolve()] if directory else None

    with console.status("[bold green]Scanning workspace roots for codebases and repositories...[/bold green]"):
        results = service.ingest_workspace_projects(root_dirs=roots, dry_run=dry_run)

    table = Table(title=f"🗂️ Workspace Repositories Batch Scan ({len(results)} Found)", border_style="cyan")
    table.add_column("Repository", style="bold white")
    table.add_column("Type", style="bold cyan")
    table.add_column("Stack", style="magenta")
    table.add_column("Vault Destination", style="green")

    for meta, created_path in results:
        table.add_row(
            meta.name,
            meta.repo_type.value,
            ", ".join(meta.stack_tags[:3]) or "Standard",
            created_path.name if created_path else "Dry-Run",
        )

    console.print()
    console.print(table)
    console.print()

    if not dry_run and results:
        print_success(f"Successfully batch-seeded {len(results)} repositories into Obsidian Vault.")
    elif not results:
        print_info("No Git repositories or project manifests found in target directories.")


@ingest_app.command("all")
def ingest_all_cmd(
    vault: Optional[str] = typer.Option(
        None,
        "--vault",
        "-v",
        help="Manual path to Obsidian vault",
    ),
):
    """Full Ingestion: scan all workspace projects, harvest AI sessions, and link the graph."""
    print_banner()
    console.print("[bold cyan]🔄 Running Full Synchronous Ingestion Cycle...[/bold cyan]\n")

    config_path = Path(vault).resolve() / ".brainrc.json" if vault else find_config()
    if not config_path or not config_path.is_file():
        print_error("Configuration file .brainrc.json not found! Run 'devbrain init' first.")
        raise typer.Exit(code=1)

    config = load_config(config_path)
    vault_dir = config.resolve_vault_path()
    service = IngestionService(vault_path=vault_dir, config=config)

    # 1. Ingest Projects
    p_results = service.ingest_workspace_projects()
    print_success(f"Step 1: Scanned & seeded {len(p_results)} workspace projects into 10_Projects/ & 20_Knowledge/.")

    # 2. Ingest Sessions & Connect Graph
    s_result = service.run_ingestion()
    print_success(f"Step 2: Ingested {s_result.ingested} AI sessions ({s_result.linked_projects} graph links connected).")

    print_success("\n🎉 Full Ingestion Complete! Vault memory & graph connections are fully synchronized.")
