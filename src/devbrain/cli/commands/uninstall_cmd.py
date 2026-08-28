"""Uninstall and clean teardown command for devbrain."""

from pathlib import Path
import shutil
from typing import Optional

import typer
from rich.prompt import Confirm

from devbrain.cli.ui.console import console, print_banner, print_error, print_info, print_success, print_warning
from devbrain.core.client_config import remove_all_mcp_configs
from devbrain.core.config import find_config, load_config
from devbrain.core.constants import BRAIN_DATA_DIR, CONFIG_FILENAME


def uninstall_command(
    purge: bool = typer.Option(
        False,
        "--purge",
        "-p",
        help="Also remove .brain_data/ vector cache and .brainrc.json (never deletes markdown notes)",
    ),
    vault: Optional[str] = typer.Option(None, "--vault", "-v", help="Manual path to vault"),
):
    """Safely unregister MCP server from IDEs and clean up cache files."""
    print_banner()

    console.print("\n[bold red]🗑️ devbrain Uninstallation & Teardown Wizard[/bold red]\n")

    confirmed = Confirm.ask(
        "Are you sure you want to unregister devbrain MCP servers from your IDEs?",
        default=False,
    )
    if not confirmed:
        print_info("Uninstallation cancelled.")
        return

    # 1. Unregister from IDEs
    with console.status("[bold green]Unregistering FastMCP server from Antigravity & Claude Code...[/bold green]"):
        cleaned_configs = remove_all_mcp_configs()

    print_success(f"Removed central-brain MCP server from {len(cleaned_configs)} IDE configuration files.")

    # 2. Handle Purge
    if purge:
        config_path = Path(vault).resolve() / CONFIG_FILENAME if vault else find_config()
        if config_path and config_path.is_file():
            try:
                config = load_config(config_path)
                vault_dir = config.resolve_vault_path()

                # Remove .brain_data cache directory
                data_dir = vault_dir / BRAIN_DATA_DIR
                if data_dir.is_dir():
                    shutil.rmtree(data_dir)
                    print_success(f"Removed local vector index cache at: {data_dir}")

                # Remove .brainrc.json
                config_path.unlink()
                print_success(f"Removed configuration file: {config_path}")

            except Exception as e:
                print_error(f"Error purging local data: {e}")

    # 3. Final Notice
    console.print("\n" + "─" * 60)
    print_success("devbrain has been cleanly unregistered from your system.")
    print_info("Your Markdown notes and Obsidian Vault remain 100% intact and untouched.")
    console.print("\n[bold white]To completely remove the Python CLI package, run:[/bold white]")
    console.print("  [bold cyan]pip uninstall devbrain[/bold cyan]")
    console.print("─" * 60 + "\n")
