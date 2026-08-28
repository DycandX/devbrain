# Task 01: Integration & Unit Tests (Pytest Suite)

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 04 |
| **Status** | ✅ Done |
| **Target Files** | `tests/test_config.py`, `tests/test_parser.py`, `tests/test_hybrid_search.py`, `tests/test_mcp_tools.py`, `tests/test_cli.py` |

---

## 1. Deskripsi Task
Membangun rangkaian unit test dan integration test komprehensif menggunakan `pytest` untuk memverifikasi seluruh komponen Level 1 (Config, Scaffolder, Parser, Chunker, FastEmbed, BM25, Watchdog, FastMCP Tools, CLI Commands).

---

## 2. Rincian Pekerjaan
1. **`test_config.py` & `test_scaffolder.py`:**
   * Test pembuatan config `.brainrc.json` dan verifikasi bahwa file tidak ditimpa jika sudah ada.
   * Test scaffolding direktori vault.
2. **`test_parser.py` & `test_chunker.py`:**
   * Test ekstraksi YAML frontmatter dan pemotongan heading Markdown.
3. **`test_hybrid_search.py`:**
   * Test akurasi kombinasi Dense FastEmbed + Sparse BM25.
   * Test pencarian exact keyword vs semantic similarity.
4. **`test_mcp_tools.py`:**
   * Test pemanggilan tool `search_brain`, `get_project_context`, `write_agent_log`, `load_skill` melalui FastMCP client mock.
5. **`test_cli.py`:**
   * Menggunakan `typer.testing.CliRunner` untuk menguji perintah `devbrain init`, `devbrain status`, `devbrain search`, `devbrain index`.

---

## 3. Kriteria Selesai (Acceptance Criteria)
* Seluruh test suite (`pytest`) lulus 100% dengan test coverage > 85%.
