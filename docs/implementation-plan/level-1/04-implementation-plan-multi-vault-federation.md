# Implementation Plan: Multi-Vault Federation & Command `devbrain vault link`

| Metadata | Nilai |
| :--- | :--- |
| **Document ID** | `IPL-L1-EXT-04` |
| **Milestone** | Level 1 Extension: Multi-Vault Federation & Federated Search (`v1.5.0-alpha`) |
| **Status** | 📝 Proposed Plan |
| **Brainstorming Reference** | [32-multi-vault-federation-dan-command-vault-link.md](../../brainstorming/32-multi-vault-federation-dan-command-vault-link.md) |
| **Target Version** | `v1.5.0-alpha` |

---

## 1. Executive Summary & Goals
Rencana implementasi ini bertujuan untuk:
1. **Multi-Vault Federation Management:** Memungkinkan Central Brain menghubungkan, mendaftarkan, dan mengelola vault-vault Obsidian eksternal lainnya di komputer developer tanpa memindahkan atau menduplikasi file fisik aslinya.
2. **Federated Semantic & Hybrid Search:** Meng-upgrade engine pencarian `FastEmbed + BM25` serta tool FastMCP `search_brain()` agar mampu memindai Central Vault dan seluruh Linked Vaults secara serempak (*Multi-Vault Querying*).
3. **Obsidian Sidebar Mounting (`--mount`):** Menyediakan integrasi Windows Directory Junction / Symlink ke `20_Knowledge/Linked_Vaults/<alias>/` sehingga folder vault eksternal langsung muncul di sidebar dan Graph View Obsidian Central Brain.
4. **CLI Sub-App `devbrain vault`:** Menyediakan perintah `link`, `unlink`, `list`, dan `sync`.

---

## 2. Technical Architecture & File Changes

```
src/devbrain/
├── core/
│   ├── config.py                 # [MODIFY] Add linked_vaults schema to BrainConfig
│   └── vault_federation.py       # [NEW] Multi-Vault Federation & Junction Mount Manager
├── engine/
│   └── hybrid_search.py          # [MODIFY] Multi-Vault Federated Indexing & Search Scope
├── mcp_server/
│   └── server.py                 # [MODIFY] search_brain tool federated querying
└── cli/
    ├── main.py                   # [MODIFY] Register vault_app
    └── commands/
        └── vault_cmd.py          # [NEW] CLI `devbrain vault [link|unlink|list|sync]`
```

---

## 3. Detailed Sprint & Task Breakdown (Sprint 09)

### 🔹 Task 01: Multi-Vault Schema & Federation Manager
* **Files:** `src/devbrain/core/config.py`, `src/devbrain/core/vault_federation.py`
* **Implementasi:**
  * Tambahkan `linked_vaults: Dict[str, str] = field(default_factory=dict)` pada `BrainConfig`.
  * Bangun `VaultFederationManager`:
    * `link_vault(vault_path, target_vault, alias, mount=False)`: Validasi direktori, simpan alias ke `.brainrc.json`, dan buat Windows Junction di `20_Knowledge/Linked_Vaults/<alias>` jika `--mount` aktif.
    * `unlink_vault(vault_path, alias, clean_mount=True)`: Hapus dari config dan bersihkan symlink junction tanpa menyentuh file asli.
    * `list_linked_vaults(vault_path)`: Mengembalikan metadata path, status keberadaan, jumlah catatan `.md`, dan status mount.

### 🔹 Task 02: Federated Hybrid Search Engine & FastMCP Gateway
* **Files:** `src/devbrain/engine/hybrid_search.py`, `src/devbrain/mcp_server/server.py`
* **Implementasi:**
  * Di `HybridEngine`:
    * Tambahkan kemampuan memindai dan mengindeks file dari Central Vault + semua path di `config.linked_vaults`.
    * Parameter `scope: Optional[str]`:
      * `scope="all"` (default): Cari di seluruh vault (Central + Linked Vaults).
      * `scope="local"` / `scope="central"`: Hanya cari di Central Vault.
      * `scope="<alias>"`: Hanya cari di linked vault spesifik.
  * Di `mcp_server/server.py`:
    * Update tool `search_brain(query, limit, scope)` agar mendukung pencarian federasi lintas vault.

### 🔹 Task 03: CLI Sub-App `devbrain vault`
* **Files:** `src/devbrain/cli/commands/vault_cmd.py`, `src/devbrain/cli/main.py`
* **Implementasi:**
  * Buat `vault_app = typer.Typer(name="vault", help="Manage multi-vault federation and linked vaults.")`.
  * Perintah:
    * `devbrain vault link <path> [--alias <name>] [--mount]`: Hubungkan vault eksternal.
    * `devbrain vault unlink <alias>`: Putuskan koneksi vault.
    * `devbrain vault list`: Tampilkan tabel Rich daftar vault, jumlah note, dan status mount.
    * `devbrain vault sync`: Re-index seluruh vault yang terhubung secara serempak.

### 🔹 Task 04: Automated Test Suite & Release `v1.5.0-alpha`
* **Files:** `tests/test_vault_federation.py`, `CHANGELOG.md`, `docs/changelog/v1.5.0-alpha.md`
* **Implementasi:**
  * Test linking vault dan verifikasi `config.linked_vaults`.
  * Test unlinking vault dan pelepasan junction mount.
  * Test federated search menemukan dokumen di Central Vault dan Linked Vault secara serempak.
  * Test CLI commands (`vault link`, `vault list`, `vault unlink`, `vault sync`).
  * Memastikan seluruh 45+ pytest tests lulus 100%.

---

## 4. Verification & Testing Matrix

| Scenario | Command | Expected Outcome |
| :--- | :--- | :--- |
| **Link Vault (Memory Only)** | `devbrain vault link "E:/_PROJECT/_TEST/HowToBeAProgrammer" --alias "how-to"` | Vault terdaftar di `.brainrc.json` |
| **Link Vault (With Mount)** | `devbrain vault link "E:/Work_Notes" --alias "work" --mount` | Folder muncul di `20_Knowledge/Linked_Vaults/work/` |
| **List Linked Vaults** | `devbrain vault list` | Menampilkan tabel Rich seluruh vault yang terhubung |
| **Federated Search (All)** | `devbrain search "programmer judgment" --scope all` | Menemukan catatan dari `HowToBeAProgrammer` dan Central Vault |
| **Unlink Vault** | `devbrain vault unlink "how-to"` | Dihapus dari config, file asli tetap utuh di disk |
