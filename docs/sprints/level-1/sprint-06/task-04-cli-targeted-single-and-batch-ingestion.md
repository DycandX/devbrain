# Task 04: CLI Targeted Single & Batch Ingestion

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 06 (Graph Mesh, Workspace Harvester & Targeted Ingestion) |
| **Status** | ✅ Done |
| **Target Files** | `src/devbrain/cli/commands/ingest_cmd.py`, `src/devbrain/cli/main.py` |

---

## 1. Deskripsi Task
Memperluas antarmuka CLI `devbrain ingest` untuk mendukung:
1. Targeted Single Ingestion: `devbrain ingest project <path>`
2. Batch Workspace Ingestion: `devbrain ingest projects [--dir <path>]`
3. Full Ingestion: `devbrain ingest all`
4. Zero-Click Auto-Provisioning saat `devbrain ingest` (sesi AI) dijalankan.

---

## 2. Rincian Pekerjaan
1. **Perintah `devbrain ingest project <path>`:**
   * Mendukung path relatif (`.`) atau absolute.
   * Mendukung opsi `--type <auto|project|skill|knowledge|reference>` untuk *manual type override*.
   * Menampilkan Rich Table ringkasan hasil inspeksi dan seeding kartu.
2. **Perintah `devbrain ingest projects`:**
   * Membaca default `workspace_roots` dari `.brainrc.json` atau opsi `--dir <path>`.
   * Memindai seluruh repositori di dalam direktori tersebut secara paralel/sekuensial.
   * Menampilkan progress bar dan ringkasan batch table.
3. **Perintah `devbrain ingest all`:**
   * Menjalankan siklus penuh: scan seluruh repo fisik + panen seluruh sesi AI + tautkan seluruh graf.
4. **Auto-Provisioning Handler:**
   * Jika sesi AI memiliki `workspace_path` yang belum ada di `10_Projects/`, sistem otomatis membuatkan kartu projeknya secara transparan.

---

## 3. Kriteria Keberhasilan (Definition of Done)
* [ ] Perintah `devbrain ingest project .` berhasil meng-ingest direktori aktif.
* [ ] Perintah `devbrain ingest projects` berhasil memindai multi-projek dari root config.
* [ ] Rich Table memberikan output yang informatif, berwarna, dan rapi.
