# Task 03: Self-Ingestion Guard

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 08 (Unified Ingestion UX & IDE Deep Links) |
| **Status** | ✅ Done |
| **Target Files** | `src/devbrain/harvester/service.py` |

---

## 1. Deskripsi Task
Menerapkan perlindungan *Self-Ingestion Guard* di `IngestionService` agar pemindaian batch pada root workspace tidak memproses folder Central Brain itu sendiri secara sirkular.

---

## 2. Rincian Pekerjaan
1. **Self-Check Heuristic:**
   * Di `ingest_workspace_projects()`:
     * Memeriksa apakah `item.resolve() == self.vault_path.resolve()`.
     * Jika sama, lewati (`continue`) agar tidak menciptakan kartu projek duplikat rekursif.

---

## 3. Kriteria Keberhasilan (Definition of Done)
* [ ] Menjalankan batch scan pada folder yang berisi vault aktif tidak memproses vault itu sendiri.
