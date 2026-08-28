# Task 02: Benchmarking, Latency & Memory Profiling

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 04 |
| **Status** | Todo |
| **Target Files** | `benchmarks/benchmark_search.py`, `benchmarks/generate_mock_vault.py` |

---

## 1. Deskripsi Task
Melakukan pengujian performa, latensi pencarian, dan konsumsi memori (RAM profiling) pada vault tiruan yang berisi 1.000 file catatan Markdown untuk memastikan target non-fungsional Level 1 tercapai.

---

## 2. Rincian Pekerjaan
1. **Mock Vault Generator (`generate_mock_vault.py`):**
   * Membuat 1.000 file Markdown sintetis dengan berbagai panjang, tag, dan struktur heading.
2. **Indexing Benchmark:**
   * Mengukur waktu yang dibutuhkan untuk mengindeks 1.000 dokumen dari nol menggunakan FastEmbed CPU ONNX.
   * Target: < 60 detik pada CPU laptop modern.
3. **Search Latency Benchmark (`benchmark_search.py`):**
   * Menjalankan 100 query pencarian hybrid acak dan mengukur p50, p95, dan p99 latency.
   * Target: p95 latency < 20 milidetik.
4. **RAM Footprint Profiling:**
   * Mengukur penggunaan memori via `tracemalloc` / `psutil` saat idle vs saat aktif query.
   * Target: Idle < 120 MB RAM, Active < 180 MB RAM.

---

## 3. Kriteria Selesai (Acceptance Criteria)
* Laporan benchmark menunjukkan latensi pencarian < 20ms dan konsumsi RAM di bawah 180MB.
