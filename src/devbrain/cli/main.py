"""Main entry point for devbrain CLI."""

from typing import Optional

import typer

from devbrain import __version__
from devbrain.cli.commands.index_cmd import index_command
from devbrain.cli.commands.ingest_cmd import ingest_command
from devbrain.cli.commands.init_cmd import init_command
from devbrain.cli.commands.search_cmd import search_command
from devbrain.cli.commands.serve_cmd import serve_command
from devbrain.cli.commands.skill_cmd import skill_app
from devbrain.cli.commands.status_cmd import status_command
from devbrain.cli.commands.uninstall_cmd import uninstall_command
from devbrain.cli.ui.console import console

app = typer.Typer(
    name="devbrain",
    help="Central AI Second Brain Hub — Single Source of Truth for Multi-Agent Coding & Obsidian.",
    no_args_is_help=True,
    add_completion=False,
)

# Register Core Commands
app.command(
    name="init",
    help="Interactively initialize a new vault or attach an existing Obsidian vault.",
)(init_command)

app.command(
    name="status",
    help="Display vault status, configuration parameters, and note statistics.",
)(status_command)

app.command(
    name="search",
    help="Perform semantic, keyword, or hybrid search across indexed vault notes.",
)(search_command)

app.command(
    name="index",
    help="Index or re-index Obsidian Markdown files into FastEmbed & BM25 local stores.",
)(index_command)

app.command(
    name="ingest",
    help="Harvest and seed external AI Agent sessions into Obsidian 90_Agent_Inbox/.",
)(ingest_command)

app.command(
    name="pull",
    help="Alias for 'ingest' — pull AI sessions from Antigravity/Claude into vault.",
)(ingest_command)

app.command(
    name="serve",
    help="Launch the FastMCP Protocol Server for Antigravity IDE and Claude Code.",
)(serve_command)

app.command(
    name="uninstall",
    help="Safely unregister FastMCP servers from IDEs and clean up local caches.",
)(uninstall_command)

# Register Sub-Apps
app.add_typer(skill_app, name="skill")


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
