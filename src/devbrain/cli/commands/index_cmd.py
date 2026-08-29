"""Index command for manually indexing vault files."""

from pathlib import Path
from typing import Optional

import typer
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeRemainingColumn
from rich.table import Table

from devbrain.cli.ui.console import console, print_banner, print_error, print_success
from devbrain.core.config import find_config, load_config
from devbrain.engine.hybrid_search import HybridEngine


def index_command(
    reindex: bool = typer.Option(
        False,
        "--reindex",
        "-r",
        help="Force full re-indexing of all vault files from scratch",
    ),
    vault: Optional[str] = typer.Option(None, "--vault", "-v", help="Manual path to vault"),
):
    """Index or re-index Obsidian Markdown files into FastEmbed & BM25 local stores."""
    print_banner()

    # 1. Locate Config File
    if vault:
        config_path = Path(vault).expanduser().resolve()
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
    engine = HybridEngine(
        vault_path=vault_dir,
        embedding_model=config.embedding_model,
        ignored_patterns=config.ignored_paths,
        linked_vaults=config.resolve_linked_vaults(),
    )

    console.print(f"\n[bold yellow]🔍 Scanning vault at: [underline]{vault_dir}[/underline][/bold yellow]")
    if reindex:
        console.print("[bold red]⚠ Force reindex enabled: Clearing previous cache...[/bold red]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Indexing notes...", total=None)

        def on_progress(filename: str, current: int, total: int):
            progress.update(task, total=total, completed=current, description=f"Processing {filename}")

        stats = engine.index_vault(force_reindex=reindex, on_progress=on_progress)

    print_success("Indexing completed successfully!\n")

    table = Table(title="📑 Indexing Statistics", border_style="cyan")
    table.add_column("Metric", style="bold white")
    table.add_column("Value", style="bold cyan")
    table.add_row("Processed / Updated Files", f"{stats['processed']} files")
    table.add_row("Removed Stale Files", f"{stats['deleted']} files")
    table.add_row("Total Active Chunks in Index", f"{stats['total_chunks']} chunks")
    table.add_row("Storage Location", str(engine.storage.data_dir))

    console.print(table)
    console.print()
