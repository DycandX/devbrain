"""Serve command launching Model Context Protocol (MCP) server for IDE agents."""

from pathlib import Path
from typing import Optional

import typer

from devbrain.cli.ui.console import error_console
from devbrain.core.config import find_config, load_config
from devbrain.engine.hybrid_search import HybridEngine
from devbrain.mcp_server.server import create_mcp_server
from devbrain.watcher.vault_watcher import VaultWatcher


def serve_command(
    stdio: bool = typer.Option(
        True,
        "--stdio/--no-stdio",
        help="Use standard I/O transport for MCP (default for Antigravity & Claude Code)",
    ),
    vault: Optional[str] = typer.Option(
        None,
        "--vault",
        "-v",
        help="Manual path to Obsidian vault (default: search .brainrc.json automatically)",
    ),
    watch: bool = typer.Option(
        True,
        "--watch/--no-watch",
        help="Re-index notes automatically when they change on disk (e.g. edited in Obsidian)",
    ),
):
    """Launch the Central Brain FastMCP Server for AI Agent pair-programming."""
    # 1. Locate Config File
    if vault:
        config_path = Path(vault).expanduser().resolve()
        if config_path.is_dir():
            config_path = config_path / ".brainrc.json"
    else:
        config_path = find_config()

    if not config_path or not config_path.is_file():
        error_console.print(
            "Configuration file .brainrc.json not found! "
            "Run 'devbrain init' first to set up your Obsidian vault."
        )
        raise typer.Exit(code=1)

    try:
        config = load_config(config_path)
    except Exception as e:
        error_console.print(f"Failed to load configuration: {e}")
        raise typer.Exit(code=1)

    vault_dir = config.resolve_vault_path()

    # Inform on stderr so stdout remains pure JSON-RPC
    error_console.print(f"[Central Brain MCP] Initializing server for vault: {vault_dir}")

    engine = HybridEngine.from_config(vault_dir, config)
    server = create_mcp_server(vault_dir, config=config, engine=engine)

    watcher = VaultWatcher(engine) if watch else None
    if watcher:
        watcher.start()
        error_console.print("[Central Brain MCP] Watching vault for changes.")

    # 2. Run MCP Transport
    transport = "stdio" if stdio else "sse"
    error_console.print(f"[Central Brain MCP] Running with {transport} transport...")

    try:
        server.run(transport=transport)
    finally:
        if watcher:
            watcher.stop()
