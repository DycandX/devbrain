"""Main entry point for devbrain CLI."""

from typing import Optional

import typer

from devbrain import __version__
from devbrain.cli.commands.init_cmd import init_command
from devbrain.cli.commands.status_cmd import status_command
from devbrain.cli.ui.console import console

app = typer.Typer(
    name="devbrain",
    help="Central AI Second Brain Hub — Single Source of Truth for Multi-Agent Coding & Obsidian.",
    no_args_is_help=True,
    add_completion=False,
)

# Register Sub-Commands
app.command(
    name="init",
    help="Interactively initialize a new vault or attach an existing Obsidian vault.",
)(init_command)

app.command(
    name="status",
    help="Display vault status, configuration parameters, and note statistics.",
)(status_command)


def version_callback(value: bool):
    if value:
        console.print(f"[bold cyan]devbrain[/bold cyan] version [bold white]{__version__}[/bold white]")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-V",
        help="Show devbrain version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
):
    """devbrain: Central AI Second Brain Hub CLI."""
    pass


if __name__ == "__main__":
    app()
