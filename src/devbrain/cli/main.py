"""Main entry point for devbrain CLI."""

from typing import Optional

import typer

from devbrain import __version__
from devbrain.cli.commands.adr_cmd import adr_app
from devbrain.cli.commands.context_cmd import context_command
from devbrain.cli.commands.index_cmd import index_command
from devbrain.cli.commands.ingest_cmd import unified_ingest_command
from devbrain.cli.commands.init_cmd import init_command
from devbrain.cli.commands.rules_cmd import rules_app
from devbrain.cli.commands.search_cmd import search_command
from devbrain.cli.commands.serve_cmd import serve_command
from devbrain.cli.commands.skill_cmd import skill_app
from devbrain.cli.commands.status_cmd import status_command
from devbrain.cli.commands.uninstall_cmd import uninstall_command
from devbrain.cli.commands.vault_cmd import vault_app
from devbrain.cli.ui.console import console


def version_callback(value: bool):
    """Callback for --version option."""
    if value:
        console.print(f"[bold cyan]devbrain[/bold cyan] version [bold green]{__version__}[/bold green]")
        raise typer.Exit()


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
    help="Harvest and seed AI agent sessions and local repositories into Obsidian Vault.",
)(unified_ingest_command)

app.command(
    name="pull",
    help="Alias for 'ingest' — harvest sessions & projects into vault.",
)(unified_ingest_command)

app.command(
    name="serve",
    help="Launch the FastMCP Protocol Server for Antigravity IDE and Claude Code.",
)(serve_command)

app.add_typer(
    adr_app,
    name="adr",
    help="Manage Architecture Decision Records (ADRs) to preserve architectural consistency.",
)

app.command(
    name="context",
    help="Assemble situational awareness briefing cards for AI Agents.",
)(context_command)

app.add_typer(
    rules_app,
    name="rules",
    help="Generate standardized AGENTS.md and CLAUDE.md workspace rules.",
)

app.add_typer(
    skill_app,
    name="skill",
    help="Manage Agent Skills in 00_System/Agent_Skills/ and configure client symlinks.",
)

app.add_typer(
    vault_app,
    name="vault",
    help="Manage multi-vault federation, external vault linking, and directory mounting.",
)

app.command(
    name="uninstall",
    help="Cleanly teardown devbrain configurations from Antigravity IDE and Claude Code.",
)(uninstall_command)


@app.callback()
def main_callback(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-V",
        help="Show devbrain version number and exit.",
        callback=version_callback,
        is_eager=True,
    ),
):
    """Entry callback for handling global options like --version."""
    pass


def main():
    """CLI application entry point."""
    app()


if __name__ == "__main__":
    main()
