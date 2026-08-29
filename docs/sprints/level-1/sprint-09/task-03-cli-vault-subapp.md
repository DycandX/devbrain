# Task 03: CLI Sub-App `devbrain vault`

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 09 (Multi-Vault Federation & devbrain vault link) |
| **Status** | ✅ Done |
| **Target Files** | `src/devbrain/cli/commands/vault_cmd.py`, `src/devbrain/cli/main.py` |

---

## 1. Deskripsi Task
Membangun sub-aplikasi CLI `devbrain vault` yang menyediakan antarmuka baris perintah interaktif dan tabel Rich untuk mengelola linked vaults.

---

## 2. Rincian Pekerjaan
1. **CLI Commands (`src/devbrain/cli/commands/vault_cmd.py`):**
   * `devbrain vault link <path> [--alias <name>] [--mount]`: Mendaftarkan vault eksternal dengan auto-alias jika tidak diberikan.
   * `devbrain vault unlink <alias>`: Memutuskan koneksi vault.
   * `devbrain vault list`: Menampilkan tabel Rich status seluruh linked vaults (Path, Status Disk, Jumlah Notes, Mounted).
   * `devbrain vault sync`: Re-index seluruh vault secara serempak.
2. **Main Registration (`src/devbrain/cli/main.py`):**
   * Daftarkan `app.add_typer(vault_app, name="vault")`.

---

## 3. Kriteria Keberhasilan (Definition of Done)
* [ ] Perintah `devbrain vault link`, `unlink`, `list`, dan `sync` berjalan tanpa error.
* [ ] Rich Table menampilkan status linked vault secara informatif.
