# Task 04: Perintah CLI Search & Index Commands

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 02 |
| **Status** | ✅ Done |
| **Target Files** | `src/devbrain/cli/commands/search_cmd.py`, `src/devbrain/cli/commands/index_cmd.py` |

---

## 1. Deskripsi Task
Mengimplementasikan perintah CLI `devbrain search "<query>"` untuk menguji pencarian hybrid langsung dari terminal dengan rendering UI berwarna, serta perintah `devbrain index [--reindex]` untuk melakukan indexing manual seluruh vault.

---

## 2. Rincian Pekerjaan
1. **Command `devbrain search "<query>"` (`search_cmd.py`):**
   * Flags:
     * `--limit / -n`: Jumlah hasil teratas (default: 5).
     * `--mode`: Pilihan metode pencarian (`hybrid`, `vector`, `bm25` - default: `hybrid`).
     * `--scope`: Filter scope catatan (`all`, `work`, `personal` - default: `all`).
   * UI Formatting:
     * Menampilkan hasil dalam panel Rich Box dengan skor relevansi persen.
     * Cuplikan teks disorot sintaksisnya (*syntax highlight* Markdown).
     * Menampilkan path relatif file dan heading breadcrumb (misal: `10_Projects/auth.md > Arsitektur JWT`).
2. **Command `devbrain index` (`index_cmd.py`):**
   * Menelusuri seluruh file `.md` di folder vault secara rekursif.
   * Menampilkan Rich Progress Bar dengan estimasi waktu selesai.
   * Flag `--reindex`: Menghapus cache lama di `.brain_data/` dan membangun ulang indeks dari awal.

---

## 3. Kriteria Selesai (Acceptance Criteria)
* Perintah `devbrain index` berhasil memindai dan mengindeks seluruh file `.md` dalam vault.
* Perintah `devbrain search "arsitektur"` menampilkan panel hasil pencarian berwarna yang rapi dan informatif di terminal.
