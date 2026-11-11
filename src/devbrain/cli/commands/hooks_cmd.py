"""Hooks command group: install devbrain's Claude Code hooks per project, and run them."""

import json
from pathlib import Path
import sys
from typing import Optional

import typer

from devbrain.cli.ui.console import print_error, print_info, print_success
from devbrain.core.config import find_config, load_config
from devbrain.integrations import claude_hooks

hooks_app = typer.Typer(help="Claude Code hooks: briefing at session start, harvest at session end.", no_args_is_help=True)


def _vault(vault: Optional[str]) -> Path:
    if vault:
        return Path(vault).expanduser().resolve()
    cfg_file = find_config()
    if not cfg_file:
        print_error("No .brainrc.json found. Pass --vault.")
        raise typer.Exit(code=1)
    return load_config(cfg_file).resolve_vault_path()


@hooks_app.command("install")
def install_cmd(
    project_dir: str = typer.Argument(".", help="Project folder to install the hooks in"),
    vault: Optional[str] = typer.Option(None, "--vault", "-v", help="Path to Obsidian vault"),
):
    """Add SessionStart and SessionEnd hooks to <project>/.claude/settings.local.json."""
    vault_path = _vault(vault)
    path = claude_hooks.install(Path(project_dir), vault_path)
    print_success(f"Hooks installed in {path}")
    project = claude_hooks.find_project_for_path(vault_path, str(Path(project_dir).resolve()))
    if project:
        print_info(f"Sessions here will be briefed with project card '{project}'.")
    else:
        print_info("No project card matches this folder yet; run 'devbrain ingest project .' so the briefing has content.")


@hooks_app.command("uninstall")
def uninstall_cmd(project_dir: str = typer.Argument(".", help="Project folder")):
    """Remove devbrain's hooks from a project, keeping any other hooks."""
    if claude_hooks.uninstall(Path(project_dir)):
        print_success("devbrain hooks removed.")
    else:
        print_info("No devbrain hooks were installed here.")


@hooks_app.command("status")
def status_cmd(
    project_dir: str = typer.Argument(".", help="Project folder"),
    vault: Optional[str] = typer.Option(None, "--vault", "-v", help="Path to Obsidian vault"),
):
    """Show which devbrain hooks are installed and which project card the folder maps to."""
    events = claude_hooks.installed_events(Path(project_dir))
    print_info(f"Installed hooks: {', '.join(events) if events else 'none'}")
    project = claude_hooks.find_project_for_path(_vault(vault), str(Path(project_dir).resolve()))
    print_info(f"Project card: {project or 'none matches this folder'}")


@hooks_app.command("run", hidden=True)
def run_cmd(
    event: str = typer.Argument(..., help="session-start or session-end"),
    vault: Optional[str] = typer.Option(None, "--vault", "-v"),
):
    """Entry point called by Claude Code. Reads the hook payload from stdin.

    Never fails loudly: a hook error must not block the user's session.
    """
    try:
        raw = sys.stdin.read() if not sys.stdin.isatty() else ""
        payload = json.loads(raw) if raw.strip() else {}
        vault_path = _vault(vault)
        if event == "session-start":
            output = claude_hooks.run_session_start(payload, vault_path)
            if output:
                sys.stdout.write(output)
        elif event == "session-end":
            claude_hooks.run_session_end(payload, vault_path)
    except Exception as e:  # noqa: BLE001
        sys.stderr.write(f"devbrain hook {event} skipped: {e}\n")
