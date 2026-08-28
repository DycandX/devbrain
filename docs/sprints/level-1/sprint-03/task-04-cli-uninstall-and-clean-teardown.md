# Task 04: CLI Uninstall & Clean Teardown Command

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 03 |
| **Status** | ✅ Done |
| **Target Files** | `src/devbrain/cli/commands/uninstall_cmd.py` |

---

## 1. Deskripsi Task
Mengimplementasikan perintah `devbrain uninstall` / `devbrain purge` untuk mencabut seluruh integrasi MCP dari sistem pengguna dan membersihkan cache vektor secara aman tanpa pernah menyentuh file catatan Markdown milik pengguna.

---

## 2. Rincian Pekerjaan
1. **Interactive Confirmation Prompt:**
   * Menampilkan ringkasan aksi pembersihan yang akan dilakukan.
   * Meminta konfirmasi eksplisit dari pengguna.
2. **Pembersihan Konfigurasi MCP:**
   * Menghapus blok `"central-brain"` dari file `~/.gemini/antigravity/mcp_config.json`.
   * Menghapus blok `"central-brain"` dari file `~/.claude.json`.
3. **Pembersihan Symlinks:**
   * Mencabut symlink skill di `~/.gemini/config/skills/` yang mengarah ke vault.
4. **Pembersihan Cache Vektor:**
   * Opsi untuk menghapus folder `.brain_data/` dan file `.brainrc.json`.
   * **Proteksi Mutlak:** Memberikan garansi bahwa folder catatan `00_System/`, `10_Projects/`, dll. **TIDAK DIHAPUS**.
5. **Petunjuk Akhir:**
   * Menampilkan instruksi untuk menghapus binary/package jika diinginkan (`pip uninstall devbrain`).

---

## 3. Kriteria Selesai (Acceptance Criteria)
* Menjalankan `devbrain uninstall` berhasil mencabut entri `central-brain` dari file MCP config.
* Semua file catatan Markdown di vault tetap utuh dan tidak rusak.
