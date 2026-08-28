"""Interactive initialization wizard command for devbrain."""

from pathlib import Path
import socket
from typing import Optional

import typer
from rich.prompt import Confirm, Prompt

from devbrain.cli.ui.console import console, print_banner, print_info, print_success
from devbrain.core.config import BrainConfig, find_config, load_config, save_config
from devbrain.core.constants import CONFIG_FILENAME, DEFAULT_EMBEDDING_MODEL
from devbrain.core.scaffolder import scaffold_vault


def init_command(
    path: Optional[str] = typer.Argument(
        None,
        help="Path lokasi direktori Obsidian Vault (default: interaktif)",
    ),
    template: bool = typer.Option(
        True,
        "--template/--no-template",
        help="Otomatis buat folder standar (00_System, 10_Projects, dll)",
    ),
):
    """Setup & hubungkan Obsidian Vault dengan devbrain secara interaktif."""
    print_banner()
    console.print("\n[bold yellow]🚀 Memulai Wizard Inisialisasi devbrain...[/bold yellow]\n")

    # 1. Tentukan Path Vault
    if not path:
        default_path = str(Path.home() / "DevBrainVault")
        path_input = Prompt.ask(
            "[bold white]Masukkan path folder Obsidian Vault[/bold white]",
            default=default_path,
        )
    else:
        path_input = path

    vault_path = Path(path_input).expanduser().resolve()

    # 2. Cek Existing Config
    existing_config_file = vault_path / CONFIG_FILENAME
    if existing_config_file.is_file():
        console.print(f"[bold cyan]ℹ Konfigurasi lama terdeteksi di {existing_config_file}[/bold cyan]")
        overwrite = Confirm.ask(
            "Apakah Anda ingin memperbarui konfigurasi yang sudah ada?",
            default=False,
        )
        if not overwrite:
            print_info("Inisialisasi dibatalkan. Menggunakan konfigurasi yang sudah ada.")
            return

    # 3. Pilihan Mode Embedding
    console.print("\n[bold white]Pilih Mode Embedding Engine:[/bold white]")
    console.print("  [cyan]1[/cyan]. Local CPU FastEmbed (100% Offline, Gratis, Tanpa GPU) [bold green][Recommended][/bold green]")
    console.print("  [cyan]2[/cyan]. Cloud API (Google Gemini / OpenAI)")
    console.print("  [cyan]3[/cyan]. Ollama Local Server")
    
    choice = Prompt.ask("Pilihan", choices=["1", "2", "3"], default="1")
    
    ollama_host = None
    if choice == "1":
        provider = "fastembed"
        model_name = DEFAULT_EMBEDDING_MODEL
    elif choice == "2":
        provider = "gemini"
        model_name = "models/embedding-001"
    else:
        provider = "ollama"
        ollama_host = Prompt.ask("Masukkan URL Ollama Host", default="http://localhost:11434")
        model_name = Prompt.ask("Masukkan Model Embedding Ollama", default="bge-m3")

    # 4. Device Tag Identifier
    default_device = socket.gethostname().lower()
    device_name = Prompt.ask("Beri nama identifier device ini", default=default_device)

    # 5. Scaffolding Folder Vault
    is_new = not vault_path.exists() or len(list(vault_path.glob("*"))) == 0
    if template:
        with console.status("[bold green]Menyiapkan struktur direktori vault...[/bold green]"):
            created_items = scaffold_vault(vault_path, is_new=is_new)
        print_success(f"Struktur folder berhasil disiapkan ({len(created_items)} item baru).")

    # 6. Simpan .brainrc.json
    config = BrainConfig(
        vault_path=str(vault_path),
        device_name=device_name,
        embedding_provider=provider,
        embedding_model=model_name,
        ollama_host=ollama_host,
    )
    saved_path = save_config(config, vault_path)
    print_success(f"Konfigurasi disimpan di: [bold cyan]{saved_path}[/bold cyan]")

    # 7. Informasi Selesai
    console.print("\n" + "─" * 60)
    console.print("[bold green]🎉 Inisialisasi Selesai! Central Brain Anda Telah Siap.[/bold green]")
    console.print("\n[bold white]Langkah Selanjutnya:[/bold white]")
    console.print(f"  1. Buka aplikasi Obsidian, pilih [bold cyan]'Open folder as vault'[/bold cyan] dan arahkan ke: [underline]{vault_path}[/underline]")
    console.print("  2. Jalankan [bold cyan]devbrain status[/bold cyan] untuk memeriksa kondisi vault.")
    console.print("  3. Buka [bold cyan]Antigravity IDE[/bold cyan] untuk mulai berinteraksi dengan AI Agent!")
    console.print("─" * 60 + "\n")
