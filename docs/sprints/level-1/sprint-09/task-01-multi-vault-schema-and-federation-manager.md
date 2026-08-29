# Task 01: Multi-Vault Schema & Federation Manager

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 09 (Multi-Vault Federation & devbrain vault link) |
| **Status** | ✅ Done |
| **Target Files** | `src/devbrain/core/config.py`, `src/devbrain/core/vault_federation.py` |

---

## 1. Deskripsi Task
Membangun modul `VaultFederationManager` dan memperluas skema `BrainConfig` untuk mendaftarkan, menghubungkan, memutuskan, dan memetakan (*mount directory junction*) vault-vault Obsidian eksternal ke dalam Central Brain.

---

## 2. Rincian Pekerjaan
1. **Config Schema Extension (`src/devbrain/core/config.py`):**
   * Tambahkan `linked_vaults: Dict[str, str] = field(default_factory=dict)` pada `BrainConfig`.
2. **Federation Manager Core (`src/devbrain/core/vault_federation.py`):**
   * `link_vault(vault_path, target_vault_path, alias, mount=False)`:
     * Validasi keberadaan folder target.
     * Sanitasi alias (alphanumeric).
     * Simpan pemetaan `alias -> target_path` di `.brainrc.json`.
     * Jika `mount=True`, buat Windows Directory Junction (`_winapi.CreateJunction` / `mklink /J`) atau symlink POSIX di `20_Knowledge/Linked_Vaults/<alias>`.
   * `unlink_vault(vault_path, alias, clean_mount=True)`:
     * Hapus alias dari `.brainrc.json`.
     * Hapus folder junction mount jika ada (tanpa menyentuh folder fisik asli).
   * `list_linked_vaults(vault_path)`:
     * Menghitung jumlah file `.md`, mengecek ketersediaan folder di disk, dan status junction mount.

---

## 3. Kriteria Keberhasilan (Definition of Done)
* [ ] Vault eksternal berhasil dicatat di `.brainrc.json`.
* [ ] Junction mount di `20_Knowledge/Linked_Vaults/<alias>` berhasil dibuat dan dihapus dengan aman.
* [ ] File asli di vault eksternal tidak pernah terhapus atau rusak.
