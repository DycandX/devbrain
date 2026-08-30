"""CLI command for Context Assembly Engine (devbrain context)."""

import json
from pathlib import Path
from typing import Optional

from rich.markdown import Markdown
from rich.panel import Panel
import typer

from devbrain.cli.ui.console import console
from devbrain.context.builder import ContextAssemblyEngine
from devbrain.core.config import find_config, load_config


def context_command(
    project: str = typer.Argument(..., help="Target project name in 10_Projects/"),
    task: str = typer.Option("General project context & development", "--task", "-t", help="Target task description"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON structure"),
    vault: Optional[Path] = typer.Option(None, "--vault", "-v", help="Path to Obsidian vault"),
):
    """Assemble a rich situational task briefing card combining User Persona, Project State, ADRs, and Knowledge."""
    vault_path = _resolve_vault(vault)
    engine = ContextAssemblyEngine(vault_path)

    card = engine.build_task_context(task=task, project=project)

    if json_output:
        console.print(json.dumps(card.to_dict(), indent=2, ensure_ascii=False))
    else:
        md = Markdown(card.to_markdown())
        console.print(Panel(md, title=f"🧠 Task Briefing: {project}", border_style="cyan"))


def _resolve_vault(vault: Optional[Path]) -> Path:
    """Resolve vault path from argument, config file, or current directory."""
    if vault:
        return vault.resolve()

    cfg_file = find_config()
    if cfg_file:
        cfg = load_config(cfg_file)
        return cfg.resolve_vault_path()

    return Path.cwd().resolve()
