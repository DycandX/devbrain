"""Status and health check command for devbrain vault."""

from pathlib import Path
from typing import Optional

import typer
from rich.table import Table

from devbrain.cli.ui.console import console, print_banner, print_error
from devbrain.core.config import find_config, load_config
from devbrain.core.constants import (
    DIR_AGENT_SKILLS,
    DIR_INBOX,
    DIR_KNOWLEDGE,
    DIR_PROJECTS,
    DIR_SYSTEM,
)


def status_command(
    path: Optional[str] = typer.Option(
        None,
        "--vault",
        "-v",
        help="Path manual ke vault (default: cari .brainrc.json otomatis)",
    ),
):
    """Menampilkan status, konfigurasi, dan jumlah catatan di vault."""
    print_banner()

    # 1. Cari Config
    if path:
        config_path = Path(path).expanduser().resolve()
        if config_path.is_dir():
            config_path = config_path / ".brainrc.json"
    else:
        config_path = find_config()

    if not config_path or not config_path.is_file():
        print_error(
            "File konfigurasi .brainrc.json tidak ditemukan!\n"
            "Jalankan [bold cyan]devbrain init[/bold cyan] terlebih dahulu untuk menyiapkan vault."
        )
        raise typer.Exit(code=1)

    try:
        config = load_config(config_path)
    except Exception as e:
        print_error(f"Gagal memuat konfigurasi: {e}")
        raise typer.Exit(code=1)

    vault_dir = config.resolve_vault_path()

    # 2. Hitung Dokumen
    all_md_files = list(vault_dir.rglob("*.md")) if vault_dir.is_dir() else []
    
    system_count = len(list((vault_dir / DIR_SYSTEM).rglob("*.md"))) if (vault_dir / DIR_SYSTEM).is_dir() else 0
    skills_count = len(list((vault_dir / DIR_AGENT_SKILLS).glob("*/SKILL.md"))) if (vault_dir / DIR_AGENT_SKILLS).is_dir() else 0
    projects_count = len(list((vault_dir / DIR_PROJECTS).rglob("*.md"))) if (vault_dir / DIR_PROJECTS).is_dir() else 0
    knowledge_count = len(list((vault_dir / DIR_KNOWLEDGE).rglob("*.md"))) if (vault_dir / DIR_KNOWLEDGE).is_dir() else 0
    inbox_count = len(list((vault_dir / DIR_INBOX).rglob("*.md"))) if (vault_dir / DIR_INBOX).is_dir() else 0

    # 3. Tampilkan Tabel Ringkasan
    table = Table(title="📊 Status Central AI Brain Hub", border_style="cyan", show_header=True)
    table.add_column("Parameter", style="bold white", width=25)
    table.add_column("Nilai Konfigurasi / Statistik", style="bold cyan")

    table.add_row("Vault Directory", str(vault_dir))
    table.add_row("Device Identifier", config.device_name)
    table.add_row("Embedding Provider", f"{config.embedding_provider} ({config.embedding_model})")
    table.add_row("Scope Filter", config.scope)
    table.add_row("Total Markdown Notes", f"{len(all_md_files)} file")
    table.add_row("  ├── 00_System (Rules)", f"{system_count} file")
    table.add_row("  ├── Agent Skills Active", f"{skills_count} skills")
    table.add_row("  ├── 10_Projects (Context)", f"{projects_count} file")
    table.add_row("  ├── 20_Knowledge", f"{knowledge_count} file")
    table.add_row("  └── 90_Agent_Inbox (Logs)", f"{inbox_count} file")
    table.add_row("Terakhir Diperbarui", config.updated_at)

    console.print(table)
