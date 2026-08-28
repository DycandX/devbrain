# Task 01: Markdown Parser & Header-Aware Chunker

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 02 |
| **Status** | Todo |
| **Target Files** | `src/devbrain/engine/parser.py`, `src/devbrain/engine/chunker.py`, `src/devbrain/engine/models.py` |

---

## 1. Deskripsi Task
Membangun modul parser Markdown untuk mengekstraksi YAML frontmatter, tag, `[[Wikilinks]]`, dan melakukan pemotongan (*chunking*) teks berbasis hirarki heading (`#`, `##`, `###`) agar konteks semantik tetap utuh.

---

## 2. Rincian Pekerjaan
1. **Data Models (`models.py`):**
   * `Document`: `id: str`, `file_path: str`, `title: str`, `frontmatter: dict`, `tags: list[str]`, `wikilinks: list[str]`, `raw_content: str`, `updated_at: float`.
   * `DocumentChunk`: `chunk_id: str`, `doc_id: str`, `file_path: str`, `header_path: str` (misal: "Arsitektur > Database"), `content: str`, `tags: list[str]`.
2. **Markdown & Frontmatter Parser (`parser.py`):**
   * Parsing metadata YAML di bagian atas file (menggunakan `PyYAML`).
   * Ekstraksi regex untuk tag `#tag` dan `[[Wikilinks]]`.
   * Deteksi judul file dari nama file atau `# Heading 1` pertama.
3. **Header-Aware Chunker (`chunker.py`):**
   * Memotong dokumen berdasarkan heading Markdown (`#`, `##`, `###`).
   * Jika ada bagian yang melebihi batas token (default: 500 token), lakukan sub-chunking dengan sliding window overlap (50 token).
   * Selalu menyertakan path heading pada metadata chunk untuk menjaga konteks semantik.

---

## 3. Kriteria Selesai (Acceptance Criteria)
* Parser berhasil memisahkan frontmatter YAML dan isi body Markdown.
* Chunker memecah file Markdown panjang menjadi potongan-potongan logis yang memiliki label hierarki heading.
