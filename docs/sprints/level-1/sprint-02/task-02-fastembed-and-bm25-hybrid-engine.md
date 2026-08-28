# Task 02: FastEmbed & Rank-BM25 Hybrid Search Engine

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 02 |
| **Status** | ✅ Done |
| **Target Files** | `src/devbrain/engine/embeddings.py`, `src/devbrain/engine/bm25.py`, `src/devbrain/engine/hybrid_search.py`, `src/devbrain/engine/storage.py` |

---

## 1. Deskripsi Task
Mengimplementasikan mesin pencarian *Hybrid Search* (Dense Vector via FastEmbed CPU ONNX + Sparse Keyword via Rank-BM25) dengan local embedded storage berbasis file di `.brain_data/`.

---

## 2. Rincian Pekerjaan
1. **Local Embedding Provider (`embeddings.py`):**
   * Menggunakan `fastembed.TextEmbedding` model `BAAI/bge-small-en-v1.5` (384 dimensi, ~130MB model size) atau `BAAI/bge-m3`.
   * Berjalan 100% lokal di CPU via ONNX Runtime.
   * Fungsi `embed_documents(texts: list[str]) -> list[list[float]]` dan `embed_query(query: str) -> list[float]`.
2. **Sparse BM25 Indexer (`bm25.py`):**
   * Tokenisasi teks kode dan bahasa alami (case-insensitive, preserving code symbols & snake_case).
   * Membangun index `BM25Okapi`.
   * Fungsi `search_bm25(query: str, top_k: int = 20) -> list[SearchResult]`.
3. **Local Vector & Document Storage (`storage.py`):**
   * Menyimpan vector matrix dan metadata chunk di `.brain_data/index.json` / SQLite / LanceDB lokal.
   * Mendukung operasi CRUD: `add_chunks()`, `remove_by_doc_id()`, `get_all_chunks()`.
4. **Hybrid Search Fusion (`hybrid_search.py`):**
   * Algoritma **Reciprocal Rank Fusion (RRF)** atau **Weighted Score Normalization**:
     $$\text{Score}(d) = 0.6 \times \text{DenseScore}(d) + 0.4 \times \text{BM25Score}(d)$$
   * Mengembalikan hasil teratas dengan format: title, file_path, header_path, snippet, combined_score.

---

## 3. Kriteria Selesai (Acceptance Criteria)
* Pencarian semantik berhasil menemukan konsep yang maknanya mirip meski kata kunci berbeda.
* Pencarian keyword exact (seperti nama variabel `auth_middleware`) berhasil ditemukan dengan skor tinggi via BM25.
* Latensi hybrid search < 20ms pada 1.000 dokumen.
