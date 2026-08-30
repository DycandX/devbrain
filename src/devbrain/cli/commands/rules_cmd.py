"""CLI command for Workspace Rules generator (devbrain rules)."""

from pathlib import Path
from typing import Optional

import typer

from devbrain.cli.ui.console import console
from devbrain.core.config import find_config, load_config
from devbrain.rules.generator import RulesGenerator

rules_app = typer.Typer(
    name="rules",
    help="Generate standardized AGENTS.md and CLAUDE.md workspace rules.",
    no_args_is_help=True,
)


@rules_app.command(name="init")
def rules_init(
    project_dir: Path = typer.Argument(Path("."), help="Path to project repository directory"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Project name override"),
    overwrite: bool = typer.Option(False, "--overwrite", "-f", help="Overwrite existing rules files"),
    vault: Optional[Path] = typer.Option(None, "--vault", "-v", help="Path to Obsidian vault"),
):
    """Generate standardized AGENTS.md and CLAUDE.md rule contracts in the target repository."""
    vault_path = _resolve_vault(vault)
    target_dir = project_dir.resolve()

    if not target_dir.is_dir():
        console.print(f"[red]Target directory not found: {target_dir}[/red]")
        raise typer.Exit(1)

    generator = RulesGenerator(vault_path)
    written = generator.write_rules_to_project(
        project_dir=target_dir,
        project_name=name,
        overwrite=overwrite,
    )

    if not written:
        console.print(f"[yellow]Rules files already exist in {target_dir}. Use --overwrite to replace them.[/yellow]")
        return

    console.print(f"[green]✓ Successfully generated AI Agent rules in: [bold]{target_dir}[/bold][/green]")
    for fname, path in written.items():
        console.print(f"  [cyan]• {fname}[/cyan] -> [dim]{path}[/dim]")


def _resolve_vault(vault: Optional[Path]) -> Optional[Path]:
    """Resolve vault path from argument, config file, or None."""
    if vault:
        return vault.resolve()

    cfg_file = find_config()
    if cfg_file:
        cfg = load_config(cfg_file)
        return cfg.resolve_vault_path()

    return None
