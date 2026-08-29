# Implementation Plan: Unified DWIM Ingestion CLI & 4-Layer IDE Deep Links

| Metadata | Nilai |
| :--- | :--- |
| **Document ID** | `IPL-L1-EXT-03` |
| **Milestone** | Level 1 Extension: Unified Ingest CLI & IDE Deep Links (`v1.4.0-alpha`) |
| **Status** | 📝 Proposed Plan |
| **Brainstorming Reference** | [31-penyederhanaan-ux-cli-ingest-dan-koneksi-fisik-projek-ke-vault.md](../../brainstorming/31-penyederhanaan-ux-cli-ingest-dan-koneksi-fisik-projek-ke-vault.md) |
| **Target Version** | `v1.4.0-alpha` |

---

## 1. Executive Summary & Goals
Rencana implementasi ini bertujuan untuk:
1. **Mengeliminasi Seluruh Kebingungan CLI (`Unified Ingest DWIM`):** Menggabungkan seluruh alur ingest ke dalam satu perintah fleksibel `devbrain ingest [TARGET] [OPTIONS]`, yang otomatis mendeteksi apakah target adalah path folder projek tunggal, folder workspace multi-projek, atau sesi AI jika tanpa argumen, serta menerima flag `--dir` / `--path` secara toleran tanpa melempar error `No such option`.
2. **Memperkuat Koneksi Folder Fisik ke Vault (*IDE Deep Links*):** Menyematkan link protokol langsung `vscode://file/...` dan `file:///...` pada setiap kartu projek di `10_Projects/` agar developer dapat membuka codebase fisik di IDE dalam 1 klik dari Obsidian.
3. **Self-Ingestion Guard:** Menjaga agar pemindaian batch tidak memproses folder Central Brain itu sendiri secara sirkular.

---

## 2. Technical Architecture & File Changes

```
src/devbrain/
├── cli/
│   └── commands/
│       └── ingest_cmd.py         # [MODIFY] Unified Dynamic CLI Handler (DWIM Router)
├── harvester/
│   ├── project_harvester.py      # [MODIFY] Embed IDE Deep Links in Project Cards
│   └── service.py                # [MODIFY] Self-Ingestion Guard & Consolidated Ingestion API
└── core/
    └── constants.py              # [MODIFY] Standard link schemas
```

---

## 3. Detailed Sprint & Task Breakdown (Sprint 08)

### 🔹 Task 01: Unified Dynamic CLI Ingest Router (`DWIM Engine`)
* **File:** `src/devbrain/cli/commands/ingest_cmd.py`
* **Implementasi:**
  * Callback `ingest_callback` menerima `target: Optional[str]`, `directory: Optional[str]`, `path: Optional[str]`.
  * **Routing Logic:**
    1. Jika `target == "all"` $\rightarrow$ Jalankan Full Ingestion (Workspace + Sesi AI + Graf).
    2. Jika ada `target` / `directory` / `path` (berisi path folder):
       - Periksa tipe folder.
       - Jika single repo $\rightarrow$ Ingest single project.
       - Jika multi-project container $\rightarrow$ Auto-delegate batch sub-projects.
    3. Jika tidak ada path yang diberikan $\rightarrow$ Ingest sesi AI (Antigravity & Claude Code).
  * Sub-perintah lama (`project`, `projects`, `all`) tetap dipertahankan sebagai alias untuk backward compatibility.

### 🔹 Task 02: Interactive IDE Deep Links & File Protocol Integration
* **File:** `src/devbrain/harvester/project_harvester.py`
* **Implementasi:**
  * Di dalam `seed_project_to_vault()`:
    * Tambahkan blok tautan cepat di bawah header kartu projek:
      ```markdown
      > 🔗 **Quick Actions:** [🚀 Open in IDE](vscode://file/E:/_PROJECT/_fxmedia/neo4j-express-demo) | [📁 Open in Explorer](file:///E:/_PROJECT/_fxmedia/neo4j-express-demo)
      ```
    * Tautan ini kompatibel dengan VS Code, Cursor, Antigravity IDE, dan Windows Explorer.

### 🔹 Task 03: Self-Ingestion Guard & Robust Directory Resolution
* **File:** `src/devbrain/harvester/service.py`
* **Implementasi:**
  * Di dalam `ingest_workspace_projects()`:
    * Periksa `if item.resolve() == self.vault_path.resolve(): continue`.
    * Mengabaikan folder vault aktif agar tidak menciptakan kartu projek duplikat rekursif.

### 🔹 Task 04: Comprehensive Test Suite & Release `v1.4.0-alpha`
* **File:** `tests/test_unified_ingest.py`, `CHANGELOG.md`, `docs/changelog/v1.4.0-alpha.md`
* **Implementasi:**
  * Unit test untuk:
    1. `devbrain ingest <single_repo_path>`
    2. `devbrain ingest --dir <workspace_container_path>`
    3. `devbrain ingest --path <single_repo_path>`
    4. `devbrain ingest all`
    5. `devbrain ingest` (session harvester fallback)
    6. Verifikasi keberadaan tautan `vscode://file/` di file markdown yang dihasilkan.
  * Memastikan seluruh 40+ pytest tests lulus 100%.

---

## 4. Verification & Testing Matrix

| Scenario | Command | Expected Outcome |
| :--- | :--- | :--- |
| **Single Project (Positional)** | `python -m devbrain.cli.main ingest "E:/_PROJECT/_TEST/HowToBeAProgrammer"` | Auto-seeds `20_Knowledge/References/HowToBeAProgrammer/README.md` |
| **Single Project (Flag --dir)** | `python -m devbrain.cli.main ingest --dir "E:/_PROJECT/_TEST/HowToBeAProgrammer"` | Berhasil tanpa error `No such option` |
| **Multi-Project Container** | `python -m devbrain.cli.main ingest "E:/_PROJECT/_fxmedia"` | Auto-scans and seeds 2 sub-projects |
| **AI Sessions Ingestion** | `python -m devbrain.cli.main ingest` | Ingests Antigravity & Claude Code sessions |
| **IDE Deep Link Verification** | Inspect `10_Projects/neo4j-express-demo/README.md` | Contains `[🚀 Open in IDE](vscode://file/...)` |
