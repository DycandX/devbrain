# Task 03: CLI Ingest Command & Continuous Watcher Daemon

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 05 (Ingestion & Vault Seeding) |
| **Status** | ⏳ Todo |
| **Target Files** | `src/devbrain/cli/commands/ingest_cmd.py`, `src/devbrain/harvester/service.py` |

---

## 1. Deskripsi Task
Membangun perintah antarmuka CLI `devbrain ingest` (dengan alias `devbrain pull` dan `devbrain harvest`) untuk melakukan initial vault seeding secara interaktif atau menjalankan continuous session watcher di background.

---

## 2. Rincian Pekerjaan
1. **Perintah CLI `devbrain ingest`:**
   * Opsi yang didukung:
     * `--from [antigravity|claude|cline|all]`: Memilih sumber spesifik.
     * `--limit <n>`: Membatasi jumlah sesi terbaru yang di-ingest (default: semua sesi baru).
     * `--dry-run`: Melihat daftar sesi yang akan di-ingest tanpa menulis file ke vault.
     * `--watch`: Menjalankan background loop/watcher yang otomatis meng-ingest sesi baru saat terdeteksi.
     * `--vault <path>`: Path manual ke Obsidian Vault.
2. **Ingestion Service Orchestrator (`service.py`):**
   * Mengkoordinasikan alur: `Discovery` $\rightarrow$ `Deduplication` (cek ID sesi yang sudah pernah di-ingest) $\rightarrow$ `Extraction` $\rightarrow$ `Secret Sanitization` $\rightarrow$ `Write to 90_Agent_Inbox/<source>/` $\rightarrow$ `Trigger Indexer`.
   * Melacak riwayat sesi yang telah di-ingest di `.brain_data/ingested_sessions.json` agar tidak terjadi duplikasi.
3. **Penyajian Output Visual (Rich Progress & Table):**
   * Menampilkan summary table sesi yang berhasil diserap ke dalam vault.

---

## 3. Kriteria Selesai (Acceptance Criteria)
* Perintah `devbrain ingest` berjalan mulus, menampilkan progres visual, dan mencatat file baru ke dalam `90_Agent_Inbox/`.
* Tidak ada file duplikat saat `devbrain ingest` dijalankan berulang kali.
