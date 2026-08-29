# Task 05: Automated Test Suite & Release v1.2.0-alpha

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 06 (Graph Mesh, Workspace Harvester & Targeted Ingestion) |
| **Status** | ✅ Done |
| **Target Files** | `tests/test_project_ingestion.py`, `tests/test_entity_linker.py`, `CHANGELOG.md`, `docs/changelog/v1.2.0-alpha.md` |

---

## 1. Deskripsi Task
Menyusun rangkaian unit & integration tests komprehensif untuk memverifikasi fitur Auto-Inspector, Project Harvester, Auto-Entity Linker, dan CLI Targeted Ingestion, serta mendokumentasikan rilis resmi `v1.2.0-alpha`.

---

## 2. Rincian Pekerjaan
1. **Test Suite `tests/test_project_ingestion.py`:**
   * Test manifest parsing (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`).
   * Test auto-inspector classification (Active Project vs Reference Repo vs Skill vs Docs).
   * Test targeted single ingestion CLI command (`devbrain ingest project`).
   * Test batch workspace scanning (`devbrain ingest projects`).
2. **Test Suite `tests/test_entity_linker.py`:**
   * Test `workspace_path` to Project Card linking.
   * Test timestamp to Daily note `[[99_Daily/YYYY-MM-DD]]` linking.
   * Test bidirectional backlink injection into Project README.
3. **Full Pytest Regression Run:**
   * Memastikan seluruh 35+ tests di repository lulus 100% tanpa error.
4. **Changelog & Documentation Update:**
   * Membuat catatan rilis `docs/changelog/v1.2.0-alpha.md`.
   * Memperbarui `CHANGELOG.md` dan `docs/changelog/_index.md`.

---

## 3. Kriteria Keberhasilan (Definition of Done)
* [ ] 100% test baru (7+ unit & integration tests) lulus di `pytest`.
* [ ] Seluruh suite pengujian (35+ tests) berjalan dalam <20 detik.
* [ ] CHANGELOG dan rilis `v1.2.0-alpha` terdokumentasi lengkap dan di-commit ke Git.
