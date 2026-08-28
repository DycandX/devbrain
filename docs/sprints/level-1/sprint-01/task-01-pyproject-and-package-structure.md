# Task 01: Setup Proyek & Struktur Package Python (`devbrain`)

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 01 |
| **Status** | ✅ Done |
| **Target Files** | `pyproject.toml`, `src/devbrain/__init__.py`, `src/devbrain/cli/main.py`, `.gitignore` |

---

## 1. Deskripsi Task
Menginisialisasi konfigurasi packaging Python menggunakan `pyproject.toml` dengan standar modern (Hatchling / Flit / setuptools), mendefinisikan dependensi inti, dan menyiapkan CLI entry point bernama `devbrain`.

---

## 2. Rincian Pekerjaan
1. **Buat `pyproject.toml`:**
   * Package Name: `devbrain`
   * Version: `0.1.0`
   * Dependencies:
     * `typer[all]>=0.12.0` (CLI Framework dengan Rich UI)
     * `rich>=13.7.0` (Terminal styling & tables)
     * `pydantic>=2.7.0` (Config schema validation)
     * `pydantic-settings>=2.2.0`
     * `watchdog>=4.0.0` (File system watcher)
     * `fastembed>=0.3.0` (Local CPU ONNX embeddings)
     * `rank-bm25>=0.2.2` (Sparse search)
     * `mcp>=1.0.0` / `fastmcp>=0.1.0` (Model Context Protocol)
     * `pyyaml>=6.0.1` (Frontmatter parser)
   * Scripts entry point:
     ```toml
     [project.scripts]
     devbrain = "devbrain.cli.main:app"
     ```
2. **Struktur Direktori `src/`:**
   * `src/devbrain/__init__.py`
   * `src/devbrain/cli/__init__.py`
   * `src/devbrain/cli/main.py` (Typer root app dengan sub-command dasar)
   * `src/devbrain/cli/ui/console.py` (Rich console instance)
3. **Verifikasi Awal:**
   * Menjalankan `pip install -e .`
   * Menjalankan `devbrain --help` di terminal dan melihat help banner yang rapi.

---

## 3. Kriteria Selesai (Acceptance Criteria)
* Perintah `devbrain --help` menampilkan daftar command awal dan versi.
* Package dapat di-install via pip editable mode tanpa error dependensi.
