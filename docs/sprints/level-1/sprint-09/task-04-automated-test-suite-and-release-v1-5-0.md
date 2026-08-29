# Task 04: Automated Test Suite & Release `v1.5.0-alpha`

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 09 (Multi-Vault Federation & devbrain vault link) |
| **Status** | ✅ Done |
| **Target Files** | `tests/test_vault_federation.py`, `src/devbrain/__init__.py`, `CHANGELOG.md`, `docs/changelog/v1.5.0-alpha.md` |

---

## 1. Deskripsi Task
Menulis suite pengujian otomatis untuk memvalidasi operasi linking, unlinking, junction mounting, dan federated search, serta merilis versi `v1.5.0-alpha`.

---

## 2. Rincian Pekerjaan
1. **Automated Pytest (`tests/test_vault_federation.py`):**
   * Test linking single vault and verify `.brainrc.json`.
   * Test junction mounting in `20_Knowledge/Linked_Vaults/`.
   * Test unlinking and safe junction removal.
   * Test federated hybrid search retrieving documents across multiple linked vaults.
   * Test CLI commands (`vault link`, `vault list`, `vault unlink`, `vault sync`).
2. **Version Bump & Changelog:**
   * Bump version di `src/devbrain/__init__.py` ke `"1.5.0-alpha"`.
   * Tulis `docs/changelog/v1.5.0-alpha.md`, update `docs/changelog/_index.md`, `CHANGELOG.md`, dan `docs/_summary/00.md`.
   * Commit seluruh hasil pekerjaan ke Git.

---

## 3. Kriteria Keberhasilan (Definition of Done)
* [ ] Seluruh 45+ automated tests lulus 100%.
* [ ] Versi package naik ke `v1.5.0-alpha`.
