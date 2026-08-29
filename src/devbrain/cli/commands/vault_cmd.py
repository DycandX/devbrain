"""CLI commands for managing multi-vault federation and linked external vaults."""

from pathlib import Path
from typing import Optional

from rich.table import Table
import typer

from devbrain.cli.ui.console import (
    console,
    print_banner,
    print_error,
    print_info,
    print_success,
    print_warning,
)
from devbrain.core.config import BrainConfig, find_config, load_config
from devbrain.core.vault_federation import VaultFederationManager
from devbrain.engine.hybrid_search import HybridEngine

vault_app = typer.Typer(
    name="vault",
    help="Manage multi-vault federation, external vault linking, and directory mounting.",
    no_args_is_help=True,
)


def _get_manager(vault: Optional[str]) -> tuple[VaultFederationManager, BrainConfig, Path]:
    """Helper to locate configuration and instantiate VaultFederationManager."""
    if vault:
        vault_p = Path(vault).resolve()
        config_p = vault_p / ".brainrc.json"
        if config_p.is_file():
            config = load_config(config_p)
        else:
            config = BrainConfig(vault_path=str(vault_p))
    else:
        config_p = find_config()
        if not config_p or not config_p.is_file():
            print_error("Configuration file .brainrc.json not found! Run 'devbrain init' first.")
            raise typer.Exit(code=1)
        config = load_config(config_p)

    vault_dir = config.resolve_vault_path()
    manager = VaultFederationManager(vault_path=vault_dir, config=config)
    return manager, config, vault_dir


@vault_app.command("link")
def link_vault_cmd(
    target_path: str = typer.Argument(
        ...,
        help="Absolute or relative path to the external Obsidian vault directory",
    ),
    alias: Optional[str] = typer.Option(
        None,
        "--alias",
        "-a",
        help="Custom short alias tag for this vault (default: folder name)",
    ),
    mount: bool = typer.Option(
        False,
        "--mount",
        "-m",
        help="Mount folder into 20_Knowledge/Linked_Vaults/<alias> via directory junction",
    ),
    vault: Optional[str] = typer.Option(
        None,
        "--vault",
        "-v",
        help="Manual path to Central Brain vault",
    ),
):
    """Link an external Obsidian vault into Central Brain federation."""
    print_banner()
    manager, config, vault_dir = _get_manager(vault)

    target_dir = Path(target_path).resolve()
    if not target_dir.is_dir():
        print_error(f"Target directory does not exist: {target_dir}")
        raise typer.Exit(code=1)

    try:
        chosen_alias, resolved_path, is_mounted = manager.link_vault(
            target_path=target_dir,
            alias=alias,
            mount=mount,
        )
    except Exception as e:
        print_error(f"Failed to link vault: {e}")
        raise typer.Exit(code=1)

    print_success(f"Successfully linked vault [bold white]'{chosen_alias}'[/bold white] to Central Brain!")
    console.print(f"  • [bold cyan]Target Path:[/bold cyan] {resolved_path}")
    if is_mounted:
        console.print(f"  • [bold green]Obsidian Mount:[/bold green] 20_Knowledge/Linked_Vaults/{chosen_alias}/")
    else:
        console.print("  • [dim]Federated Memory Indexing: Active (0 MB duplicate disk space)[/dim]")


@vault_app.command("unlink")
def unlink_vault_cmd(
    alias: str = typer.Argument(
        ...,
        help="Alias of the linked vault to disconnect",
    ),
    vault: Optional[str] = typer.Option(
        None,
        "--vault",
        "-v",
        help="Manual path to Central Brain vault",
    ),
):
    """Unlink an external vault and cleanly remove junction mounts."""
    print_banner()
    manager, config, vault_dir = _get_manager(vault)

    success = manager.unlink_vault(alias=alias, clean_mount=True)
    if success:
        print_success(f"Successfully unlinked vault '{alias}' from Central Brain federation.")
    else:
        print_warning(f"Vault with alias '{alias}' was not found in linked vaults list.")


@vault_app.command("list")
def list_vaults_cmd(
    vault: Optional[str] = typer.Option(
        None,
        "--vault",
        "-v",
        help="Manual path to Central Brain vault",
    ),
):
    """Display all linked external vaults, disk status, note counts, and mount states."""
    print_banner()
    manager, config, vault_dir = _get_manager(vault)

    vaults = manager.list_linked_vaults()

    table = Table(title=f"🌐 Multi-Vault Federation Hub ({len(vaults)} Linked Vaults)", border_style="cyan")
    table.add_column("Alias", style="bold white")
    table.add_column("Target Path", style="dim cyan")
    table.add_column("Notes", style="bold green", justify="right")
    table.add_column("Disk Status", style="magenta")
    table.add_column("Obsidian Mount", style="yellow")

    # Add Central Brain itself as first row
    try:
        central_notes = len(list(vault_dir.rglob("*.md")))
    except Exception:
        central_notes = 0

    table.add_row(
        "central (Primary)",
        str(vault_dir),
        str(central_notes),
        "[green]Active Root[/green]",
        "[green]Root Vault[/green]",
    )

    for v in vaults:
        status_text = "[green]Available[/green]" if v.exists else "[red]Missing[/red]"
        mount_text = "[green]Mounted[/green]" if v.is_mounted else "[dim]Memory-Only[/dim]"
        table.add_row(
            v.alias,
            str(v.target_path),
            str(v.note_count),
            status_text,
            mount_text,
        )

    console.print()
    console.print(table)
    console.print()


@vault_app.command("sync")
def sync_vaults_cmd(
    vault: Optional[str] = typer.Option(
        None,
        "--vault",
        "-v",
        help="Manual path to Central Brain vault",
    ),
):
    """Synchronize and re-index notes across Central Vault and all linked external vaults."""
    print_banner()
    manager, config, vault_dir = _get_manager(vault)

    linked_paths = config.resolve_linked_vaults()
    engine = HybridEngine(
        vault_path=vault_dir,
        embedding_model=config.embedding_model,
        ignored_patterns=config.ignored_paths,
        linked_vaults=linked_paths,
    )

    with console.status("[bold cyan]Re-indexing Central Vault & all linked vaults...[/bold cyan]"):
        res = engine.index_vault(force_reindex=False)

    print_success(f"Multi-Vault Sync Complete: {res['processed']} files processed, {res['total_chunks']} total chunks active in hybrid memory.")
