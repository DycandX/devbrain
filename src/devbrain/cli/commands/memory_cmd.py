"""Memory command group: review pending writes, pin core memories, edit, and audit."""

from pathlib import Path
from typing import List, Optional

from rich.table import Table
import typer

from devbrain.cli.ui.console import console, print_error, print_info, print_success
from devbrain.core.config import find_config, load_config
from devbrain.memory.manager import MemoryManager

memory_app = typer.Typer(help="Review, pin, and audit agent memories.", no_args_is_help=True)

VaultOption = typer.Option(None, "--vault", "-v", help="Path to Obsidian vault")


def _manager(vault: Optional[Path]) -> MemoryManager:
    if vault:
        return MemoryManager(vault.expanduser().resolve())
    cfg_file = find_config()
    if not cfg_file:
        print_error("No .brainrc.json found. Pass --vault.")
        raise typer.Exit(code=1)
    return MemoryManager(load_config(cfg_file).resolve_vault_path())


def _print_memories(memories: list, title: str) -> None:
    if not memories:
        print_info(f"No {title.lower()}.")
        return
    table = Table(title=title, header_style="bold cyan")
    table.add_column("ID", no_wrap=True)
    table.add_column("Where", no_wrap=True)
    table.add_column("Pin", justify="center")
    table.add_column("Content")
    for m in memories:
        table.add_row(m["id"], m["project"] or m["scope"].lower(), "📌" if m.get("pinned") else "", m["content"])
    console.print(table)


def _each(ids: List[str], manager: MemoryManager, action, label: str) -> None:
    """Apply an action to the given ids, or to every pending memory for 'all'."""
    targets = [m["id"] for m in manager.list("pending")] if ids == ["all"] else ids
    if not targets:
        print_info("Nothing pending.")
        return
    for memory_id in targets:
        try:
            action(memory_id)
            print_success(f"{label} {memory_id}")
        except (KeyError, ValueError) as e:
            print_error(f"{memory_id}: {e}")


@memory_app.command("list")
def list_cmd(
    status: str = typer.Option("active", "--status", "-s", help="active, pending, superseded, forgotten, rejected"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project memories plus global ones"),
    vault: Optional[Path] = VaultOption,
):
    """List memories by status."""
    _print_memories(_manager(vault).list(status, project), f"{status.capitalize()} memories")


@memory_app.command("pending")
def pending_cmd(vault: Optional[Path] = VaultOption):
    """List memories waiting for approval."""
    _print_memories(_manager(vault).list("pending"), "Pending memories")


@memory_app.command("approve")
def approve_cmd(ids: List[str] = typer.Argument(..., help="Memory ids, or 'all'"), vault: Optional[Path] = VaultOption):
    """Approve pending memories so agents can see them."""
    manager = _manager(vault)
    _each(ids, manager, manager.approve, "Approved")


@memory_app.command("reject")
def reject_cmd(ids: List[str] = typer.Argument(..., help="Memory ids, or 'all'"), vault: Optional[Path] = VaultOption):
    """Reject pending memories. They stay in the database as 'rejected'."""
    manager = _manager(vault)
    _each(ids, manager, manager.reject, "Rejected")


@memory_app.command("pin")
def pin_cmd(memory_id: str, vault: Optional[Path] = VaultOption):
    """Add a memory to the core memory shown in every briefing."""
    manager = _manager(vault)
    _each([memory_id], manager, manager.pin, "Pinned")


@memory_app.command("unpin")
def unpin_cmd(memory_id: str, vault: Optional[Path] = VaultOption):
    """Remove a memory from the core memory."""
    manager = _manager(vault)
    _each([memory_id], manager, lambda m: manager.pin(m, False), "Unpinned")


@memory_app.command("edit")
def edit_cmd(
    memory_id: str,
    old: str = typer.Option(..., "--old", help="Exact text to replace (must occur once)"),
    new: str = typer.Option(..., "--new", help="Replacement text"),
    vault: Optional[Path] = VaultOption,
):
    """Replace one span of a memory's text."""
    manager = _manager(vault)
    _each([memory_id], manager, lambda m: manager.patch(m, old, new, source="cli"), "Edited")


@memory_app.command("forget")
def forget_cmd(memory_id: str, vault: Optional[Path] = VaultOption):
    """Retire a memory."""
    if _manager(vault).forget(memory_id, source="cli"):
        print_success(f"Forgot {memory_id}")
    else:
        print_error(f"No memory with id {memory_id}")


@memory_app.command("ledger")
def ledger_cmd(
    memory_id: Optional[str] = typer.Argument(None, help="Limit to one memory"),
    limit: int = typer.Option(30, "--limit", "-n"),
    vault: Optional[Path] = VaultOption,
):
    """Show the history of memory writes, approvals, edits, and blocked attempts."""
    entries = _manager(vault).ledger(memory_id, limit)
    if not entries:
        print_info("The ledger is empty.")
        return
    table = Table(title="Memory ledger", header_style="bold cyan")
    for column in ("When", "Action", "Memory", "Source", "Detail"):
        table.add_column(column, overflow="fold")
    for e in entries:
        table.add_row(e["at"][:19], e["action"], e["memory_id"] or "-", e["source"] or "-", (e["detail"] or "")[:120])
    console.print(table)
