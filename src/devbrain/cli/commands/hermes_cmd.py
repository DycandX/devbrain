"""Hermes command group: connect devbrain to Hermes Agent as its shared memory."""

from pathlib import Path
from typing import Optional

import typer

from devbrain.cli.ui.console import console, print_error, print_info, print_success
from devbrain.core.config import find_config, load_config
from devbrain.integrations import hermes

hermes_app = typer.Typer(help="Connect devbrain to Hermes Agent (MCP server and shared skills).", no_args_is_help=True)


def _vault(vault: Optional[str]) -> Path:
    if vault:
        return Path(vault).expanduser().resolve()
    cfg_file = find_config()
    if not cfg_file:
        print_error("No .brainrc.json found. Pass --vault.")
        raise typer.Exit(code=1)
    return load_config(cfg_file).resolve_vault_path()


def _home(home: Optional[str]) -> Path:
    path = Path(home).expanduser().resolve() if home else hermes.hermes_home()
    if path is None or not (path / "config.yaml").is_file():
        print_error("Hermes home not found. Pass --home or set HERMES_HOME.")
        raise typer.Exit(code=1)
    return path


@hermes_app.command("connect")
def connect_cmd(
    vault: Optional[str] = typer.Option(None, "--vault", "-v", help="Path to Obsidian vault"),
    home: Optional[str] = typer.Option(None, "--home", help="Hermes home (default: HERMES_HOME or %LOCALAPPDATA%\\hermes)"),
    share_skills: bool = typer.Option(True, "--share-skills/--no-share-skills", help="Let Hermes read the vault's skills"),
):
    """Register devbrain in Hermes' config.yaml. A backup of the config is written first."""
    result = hermes.connect(_vault(vault), _home(home), share_skills=share_skills)
    print_success(f"devbrain registered as MCP server '{hermes.SERVER_NAME}' in {result['config']}")
    if result["skills_dir"]:
        print_success(f"Hermes reads skills from {result['skills_dir']}")
    print_info(f"Backup: {result['backup']}")
    print_info("Restart Hermes (gateway and open chats) to load the change.")


@hermes_app.command("disconnect")
def disconnect_cmd(
    vault: Optional[str] = typer.Option(None, "--vault", "-v", help="Path to Obsidian vault"),
    home: Optional[str] = typer.Option(None, "--home", help="Hermes home"),
):
    """Remove devbrain from Hermes' config.yaml."""
    result = hermes.disconnect(_home(home), _vault(vault))
    if result["backup"]:
        print_success(f"devbrain removed from {result['config']} (backup: {result['backup']})")
    else:
        print_info("devbrain was not configured in Hermes.")


@hermes_app.command("status")
def status_cmd(home: Optional[str] = typer.Option(None, "--home", help="Hermes home")):
    """Show whether Hermes is connected to devbrain."""
    path = _home(home)
    info = hermes.status(path)
    console.print(f"Hermes home: {path}")
    console.print(f"MCP server '{hermes.SERVER_NAME}': {'configured' if info['server'] else 'not configured'}")
    console.print(f"Shared skill folders: {', '.join(info['external_dirs']) or 'none'}")
    console.print(f"Hermes write approval — memory: {info['write_approval']['memory']}, skills: {info['write_approval']['skills']}")
