"""Rich terminal console utilities for devbrain CLI."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
error_console = Console(stderr=True)


def print_banner():
    """Print the ASCII/styled banner for devbrain."""
    banner_text = (
        "[bold cyan]🧠 devbrain[/bold cyan] [bold white]— Central AI Second Brain Hub[/bold white]\n"
        "[dim]Single Source of Truth for Multi-Agent Coding & Obsidian[/dim]"
    )
    console.print(Panel(banner_text, border_style="cyan", expand=False))


def print_success(message: str):
    """Print a success message."""
    console.print(f"[bold green]✔[/bold green] {message}")


def print_info(message: str):
    """Print an informational message."""
    console.print(f"[bold blue]ℹ[/bold blue] {message}")


def print_warning(message: str):
    """Print a warning message."""
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")


def print_error(message: str):
    """Print an error message to stderr."""
    error_console.print(f"[bold red]✖ Error:[/bold red] {message}")
