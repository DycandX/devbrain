# Task 02: Federated Hybrid Search Engine & FastMCP Gateway

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 09 (Multi-Vault Federation & devbrain vault link) |
| **Status** | ✅ Done |
| **Target Files** | `src/devbrain/engine/hybrid_search.py`, `src/devbrain/mcp_server/server.py` |

---

## 1. Deskripsi Task
Memperluas mesin pencarian hybrid `FastEmbed + BM25` serta tool FastMCP `search_brain()` agar mampu mengindeks dan mencari dokumen secara serempak melintasi Central Vault dan seluruh Linked Vaults yang terdaftar.

---

## 2. Rincian Pekerjaan
1. **Multi-Vault Indexing & Scoping (`src/devbrain/engine/hybrid_search.py`):**
   * Perluas `HybridEngine.index_vault()` agar secara otomatis memindai Central Vault dan linked vaults jika `include_linked=True`.
   * Simpan metadata `vault_alias: str` pada setiap chunk dokumen yang terindeks (`"central"` vs `"<alias>"`).
   * Tambahkan parameter `scope: Optional[str]` pada `HybridEngine.search()`:
     * `scope="all"` (default): Pencarian mencakup seluruh dokumen di Central & Linked Vaults.
     * `scope="central"` / `scope="local"`: Hanya dokumen di Central Vault.
     * `scope="<alias>"`: Hanya dokumen pada linked vault tertentu.
2. **FastMCP Gateway Tool Update (`src/devbrain/mcp_server/server.py`):**
   * Perbarui tool `search_brain(query, limit, scope)` untuk meneruskan parameter `scope` ke `HybridEngine`.

---

## 3. Kriteria Keberhasilan (Definition of Done)
* [ ] Query `search_brain` dapat menemukan dokumen dari linked vault yang terdaftar.
* [ ] Parameter `scope` dapat memfilter hasil pencarian secara presisi.
