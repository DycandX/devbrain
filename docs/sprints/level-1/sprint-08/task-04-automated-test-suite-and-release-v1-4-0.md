# Task 04: Automated Test Suite & Release v1.4.0-alpha

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 08 (Unified Ingestion UX & IDE Deep Links) |
| **Status** | ✅ Done |
| **Target Files** | `tests/test_unified_ingest.py`, `CHANGELOG.md`, `docs/changelog/v1.4.0-alpha.md` |

---

## 1. Deskripsi Task
Menyusun pengujian unit dan CLI untuk memverifikasi fungsionalitas Unified Ingest Router (DWIM), parameter `--dir` dan `--path`, pembuatan tautan IDE, dan perlindungan self-ingestion, serta merilis `v1.4.0-alpha`.

---

## 2. Rincian Pekerjaan
1. **Automated Pytest Suite (`tests/test_unified_ingest.py`):**
   * Test positional path invocation.
   * Test `--dir` flag tolerance.
   * Test `--path` flag tolerance.
   * Test IDE link embedding in project markdown cards.
   * Test self-ingestion guard.
2. **Regression Verification:**
   * Memastikan seluruh 40+ pytest tests lulus 100%.
3. **Release Documentation & Git Commit:**
   * Update changelog dan release `v1.4.0-alpha`.

---

## 3. Kriteria Keberhasilan (Definition of Done)
* [ ] 100% tests lulus.
* [ ] Release `v1.4.0-alpha` terdokumentasi dan di-commit ke Git.
