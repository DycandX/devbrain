"""Search command for testing hybrid queries directly from terminal."""

from pathlib import Path
from typing import Optional

import typer
from rich.panel import Panel
from rich.text import Text

from devbrain.cli.ui.console import console, print_banner, print_error, print_info
from devbrain.core.config import find_config, load_config
from devbrain.engine.hybrid_search import HybridEngine


def search_command(
    query: str = typer.Argument(..., help="Search query (natural language or keywords)"),
    limit: int = typer.Option(5, "--limit", "-n", help="Maximum number of top results to return"),
    mode: str = typer.Option(
        "hybrid",
        "--mode",
        "-m",
        help="Search mode: 'hybrid', 'dense' (FastEmbed), or 'bm25' (keyword)",
    ),
    scope: str = typer.Option("all", "--scope", "-s", help="Scope filter ('all', 'work', 'personal', or tag)"),
    vault: Optional[str] = typer.Option(None, "--vault", "-v", help="Manual path to vault"),
):
    """Perform semantic or keyword hybrid search across Obsidian vault notes."""
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

    # 2. Check if index exists or run initial index
    with console.status(f"[bold cyan]Searching Central Brain for: '{query}' ({mode} mode)...[/bold cyan]"):
        results = engine.search(query=query, limit=limit, mode=mode, scope=scope)

    if not results:
        # If no chunks in index, check if vault needs initial indexing
        if not engine.chunks:
            print_info("No indexed chunks found. Running automatic vault indexing...")
            with console.status("[bold green]Indexing vault files...[/bold green]"):
                stats = engine.index_vault()
            print_info(f"Indexed {stats['total_chunks']} chunks. Re-running search...")
            results = engine.search(query=query, limit=limit, mode=mode, scope=scope)

    if not results:
        console.print(f"\n[bold yellow]No matching notes found for:[/bold yellow] [italic]{query}[/italic]\n")
        return

    # 3. Render Results
    console.print(f"\n[bold white]Top {len(results)} Search Results for:[/bold white] [bold cyan]'{query}'[/bold cyan]\n")

    for idx, r in enumerate(results, 1):
        pct = int(r.score * 100)
        score_badge = f"[bold green]{pct}% Match[/bold green]" if pct >= 70 else f"[bold yellow]{pct}% Match[/bold yellow]"
        
        breadcrumb = f" > [dim]{r.header_path}[/dim]" if r.header_path else ""
        header_text = f"#{idx} [bold white]{r.title}[/bold white]{breadcrumb} ({score_badge})"
        
        body_text = Text()
        body_text.append(f"File: {r.file_path}\n", style="cyan")
        if r.tags:
            body_text.append(f"Tags: {', '.join(r.tags)}\n", style="dim magenta")
        body_text.append("\n" + r.snippet, style="white")

        console.print(Panel(body_text, title=header_text, border_style="cyan", expand=False))
        console.print()
