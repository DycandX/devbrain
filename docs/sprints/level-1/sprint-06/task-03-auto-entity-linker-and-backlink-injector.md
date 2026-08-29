# Task 03: Auto-Entity Linker & Backlink Injector

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 06 (Graph Mesh, Workspace Harvester & Targeted Ingestion) |
| **Status** | ✅ Done |
| **Target Files** | `src/devbrain/harvester/entity_linker.py`, `src/devbrain/harvester/service.py` |

---

## 1. Deskripsi Task
Membangun subsistem **Auto-Entity Linker Engine** yang mengeliminasi *orphan nodes* di Obsidian Graph View dengan menghubungkan catatan sesi AI ke kartu projek induk (`10_Projects/`), catatan harian (`99_Daily/`), kartu teknologi (`20_Knowledge/`), dan menginjeksi *bidirectional backlinks* ke file README projek.

---

## 2. Rincian Pekerjaan
1. **Workspace Path Matcher:**
   * Mengekstrak metadata `workspace_path` dari sesi AI.
   * Mencocokkan dengan `local_path` seluruh kartu projek yang terdaftar di `10_Projects/`.
   * Otomatis menyisipkan `[[10_Projects/<Project>/README|<Project>]]` ke dalam note sesi.
2. **Chronological & Daily Matcher:**
   * Mengonversi `created` timestamp sesi menjadi link catatan harian `[[99_Daily/YYYY-MM-DD|YYYY-MM-DD]]`.
3. **Tech Entity & Keyword Matcher:**
   * Memindai kata kunci teknologi (`FastMCP`, `Docker`, `Pytest`, `FastEmbed`, `React`, dll.) di dalam walkthrough dan menautkannya ke note yang relevan di `20_Knowledge/`.
4. **Bidirectional Backlink Injector:**
   * Membaca file `10_Projects/<Project>/README.md` dan menambahkan entri sesi terbaru ke bagian `### 📜 Sesi AI Terkini` secara otomatis dan idempotensial (tanpa duplikasi).

---

## 3. Kriteria Keberhasilan (Definition of Done)
* [ ] Setiap sesi yang di-ingest memiliki minimal 2 garis relasi graf (`[[Project]]` dan `[[Daily]]`).
* [ ] Obsidian Graph View menampilkan note projek sebagai simpul pusat (*hub node*) yang dikelilingi oleh sesi koding terkait.
* [ ] File `10_Projects/<Project>/README.md` terupdate otomatis dengan riwayat sesi AI terbaru.
