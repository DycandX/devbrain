# Task 03: Perintah CLI Init Wizard & Status Command

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 01 |
| **Status** | ✅ Done |
| **Target Files** | `src/devbrain/cli/commands/init_cmd.py`, `src/devbrain/cli/commands/status_cmd.py` |

---

## 1. Deskripsi Task
Mengimplementasikan wizard interaktif `devbrain init` untuk memandu user memilih lokasi vault dan preferensi embedding, serta perintah `devbrain status` untuk menampilkan ringkasan kondisi vault.

---

## 2. Rincian Pekerjaan
1. **Interactive Wizard `devbrain init [path]` (`init_cmd.py`):**
   * Prompt lokasi folder vault (jika tidak dispesifikasikan sebagai argumen).
   * Cek apakah folder baru/kosong atau existing vault.
   * Prompt pilihan mode embedding menggunakan `rich.prompt`:
     * 1: Local FastEmbed (CPU ONNX) [Default]
     * 2: Cloud API (Gemini / OpenAI)
     * 3: Ollama Server
   * Eksekusi `scaffolder.scaffold_vault()`.
   * Simpan `.brainrc.json`.
   * Panggil modul auto-configurator IDE (Antigravity & Claude Code) untuk mendaftarkan MCP Stdio.
   * Tampilkan panel sukses berwarna hijau dengan petunjuk langkah selanjutnya.
2. **Command `devbrain status` (`status_cmd.py`):**
   * Membaca `.brainrc.json`.
   * Menghitung total file `.md` di folder vault.
   * Menampilkan tabel status menggunakan `rich.table.Table`:
     * Lokasi Vault
     * Mode Embedding & Model Aktif
     * Total Dokumen
     * Status Integrasi Antigravity & Claude MCP.

---

## 3. Kriteria Selesai (Acceptance Criteria)
* Menjalankan `devbrain init` di folder baru berhasil menyelesaikan wizard interaktif tanpa crash.
* Menjalankan `devbrain status` menampilkan ringkasan informasi vault secara rapi di terminal.
