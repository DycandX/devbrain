"""Interactive initialization wizard command for devbrain."""

from pathlib import Path
import socket
from typing import Optional

import typer
from rich.prompt import Confirm, Prompt

from devbrain.cli.ui.console import console, print_banner, print_info, print_success
from devbrain.core.config import BrainConfig, save_config
from devbrain.core.constants import CONFIG_FILENAME, DEFAULT_EMBEDDING_MODEL
from devbrain.core.scaffolder import scaffold_vault


def init_command(
    path: Optional[str] = typer.Argument(
        None,
        help="Obsidian Vault directory path (default: interactive prompt)",
    ),
    template: bool = typer.Option(
        True,
        "--template/--no-template",
        help="Automatically generate standard folder hierarchy (00_System, 10_Projects, etc.)",
    ),
):
    """Setup and connect an Obsidian Vault with devbrain interactively."""
    print_banner()
    console.print("\n[bold yellow]🚀 Starting devbrain Initialization Wizard...[/bold yellow]\n")

    # 1. Resolve Vault Path
    if not path:
        default_path = str(Path.home() / "DevBrainVault")
        path_input = Prompt.ask(
            "[bold white]Enter Obsidian Vault directory path[/bold white]",
            default=default_path,
        )
    else:
        path_input = path

    vault_path = Path(path_input).expanduser().resolve()

    # 2. Check Existing Config
    existing_config_file = vault_path / CONFIG_FILENAME
    if existing_config_file.is_file():
        console.print(f"[bold cyan]ℹ Existing configuration detected at {existing_config_file}[/bold cyan]")
        overwrite = Confirm.ask(
            "Do you want to overwrite existing configuration?",
            default=False,
        )
        if not overwrite:
            print_info("Initialization aborted. Keeping existing configuration.")
            return

    # 3. Select Embedding Mode
    console.print("\n[bold white]Select Embedding Engine Mode:[/bold white]")
    console.print("  [cyan]1[/cyan]. Local CPU FastEmbed (100% Offline, Free, Zero-GPU) [bold green][Recommended][/bold green]")
    console.print("  [cyan]2[/cyan]. Cloud API (Google Gemini / OpenAI)")
    console.print("  [cyan]3[/cyan]. Ollama Local Server")

    choice = Prompt.ask("Choice", choices=["1", "2", "3"], default="1")

    ollama_host = None
    if choice == "1":
        provider = "fastembed"
        model_name = DEFAULT_EMBEDDING_MODEL
    elif choice == "2":
        provider = "gemini"
        model_name = "models/embedding-001"
    else:
        provider = "ollama"
        ollama_host = Prompt.ask("Enter Ollama Host URL", default="http://localhost:11434")
        model_name = Prompt.ask("Enter Ollama Embedding Model", default="bge-m3")

    # 4. Device Identifier Tag
    default_device = socket.gethostname().lower()
    device_name = Prompt.ask("Enter a device identifier for this machine", default=default_device)

    # 5. Scaffold Vault Directory Hierarchy
    is_new = not vault_path.exists() or len(list(vault_path.glob("*"))) == 0
    if template:
        with console.status("[bold green]Setting up standard vault directory hierarchy...[/bold green]"):
            created_items = scaffold_vault(vault_path, is_new=is_new)
        print_success(f"Vault structure created ({len(created_items)} new items).")

    # 6. Save .brainrc.json
    config = BrainConfig(
        vault_path=str(vault_path),
        device_name=device_name,
        embedding_provider=provider,
        embedding_model=model_name,
        ollama_host=ollama_host,
    )
    saved_path = save_config(config, vault_path)
    print_success(f"Configuration saved to: [bold cyan]{saved_path}[/bold cyan]")

    # 7. Auto-configure IDEs (Antigravity & Claude Code)
    from devbrain.core.client_config import configure_antigravity, configure_claude
    with console.status("[bold green]Registering FastMCP server in AI coding assistants...[/bold green]"):
        ag_configs = configure_antigravity(vault_path)
        claude_config = configure_claude(vault_path)

    print_success(f"Registered FastMCP server in Antigravity IDE ({len(ag_configs)} configs updated).")
    print_success(f"Registered FastMCP server in Claude Code ({claude_config}).")

    # 8. Completion Summary
    console.print("\n" + "─" * 60)
    console.print("[bold green]🎉 Initialization Complete! Your Central AI Brain is ready.[/bold green]")
    console.print("\n[bold white]Next Steps:[/bold white]")
    console.print(f"  1. Open Obsidian, click [bold cyan]'Open folder as vault'[/bold cyan] and navigate to: [underline]{vault_path}[/underline]")
    console.print("  2. Run [bold cyan]devbrain status[/bold cyan] to verify vault statistics and health.")
    console.print("  3. Open [bold cyan]Antigravity IDE[/bold cyan] or [bold cyan]Claude Code[/bold cyan] to start coding with your AI Agent!")
    console.print("─" * 60 + "\n")
