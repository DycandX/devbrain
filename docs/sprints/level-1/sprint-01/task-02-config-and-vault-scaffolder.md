# Task 02: Config Schema (`.brainrc.json`) & Vault Scaffolder

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 01 |
| **Status** | Todo |
| **Target Files** | `src/devbrain/core/config.py`, `src/devbrain/core/scaffolder.py`, `src/devbrain/core/constants.py` |

---

## 1. Deskripsi Task
Membangun modul manajemen konfigurasi berbasis Pydantic (`.brainrc.json`) dan logika auto-scaffolding folder vault template standar untuk Obsidian.

---

## 2. Rincian Pekerjaan
1. **Schema Konfigurasi `BrainConfig` (`config.py`):**
   * Fields:
     * `vault_path: Path` (Path absolut vault)
     * `device_name: str` (Identifier device, misal: `laptop-omen`)
     * `embedding_provider: Literal["fastembed", "gemini", "openai", "ollama"]`
     * `embedding_model: str` (Default: `BAAI/bge-small-en-v1.5`)
     * `ignored_paths: list[str]` (Default: `.brain_data`, `.obsidian`, `.git`, `.stversions`)
     * `scope: str` (Default: `all`)
   * Fungsi: `load_config(path: Path) -> BrainConfig`, `save_config(config: BrainConfig, path: Path)`.
2. **Vault Scaffolder (`scaffolder.py`):**
   * Fungsi `scaffold_vault(vault_path: Path, is_new: bool = True)`:
     * Membuat direktori:
       * `00_System/Agent_Skills/`
       * `10_Projects/`
       * `20_Knowledge/`
       * `90_Agent_Inbox/`
     * Menulis file starter markdown:
       * `00_System/rules.md` (System instructions dasar)
       * `00_System/Agent_Skills/example_skill/SKILL.md` (Contoh format skill)
       * `10_Projects/_index.md` (Peta proyek aktif)
       * `.brainignore` (Daftar file yang diabaikan dari indexer)
   * Logika protektif: Jika folder vault sudah ada isi catatan (existing vault), jangan timpa file yang sudah ada (*Non-Destructive Attachment*).

---

## 3. Kriteria Selesai (Acceptance Criteria)
* Unit test untuk load & save `.brainrc.json`.
* Fungsi `scaffold_vault` berhasil membuat struktur folder lengkap dan starter markdown pada direktori baru.
