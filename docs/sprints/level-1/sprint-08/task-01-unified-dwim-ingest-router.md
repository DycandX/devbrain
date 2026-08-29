# Task 01: Unified Dynamic DWIM Ingest CLI Router

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 08 (Unified Ingestion UX & IDE Deep Links) |
| **Status** | ✅ Done |
| **Target Files** | `src/devbrain/cli/commands/ingest_cmd.py` |

---

## 1. Deskripsi Task
Membangun router CLI dinamis pada perintah `devbrain ingest` yang toleran dan secara otomatis mendeteksi niat pengguna (*Do What I Mean principle*), menerima input posisi maupun flag `--dir` / `--path` tanpa error `No such option`.

---

## 2. Rincian Pekerjaan
1. **Dynamic Parameter Handling:**
   * Menerima argumen opsional `target: Optional[str]`, `directory: Optional[str]`, dan `path: Optional[str]`.
   * Konsolidasi path: jika salah satu dari ketiganya diisi, gunakan path tersebut.
2. **Intelligent Dispatch Logic:**
   * Jika target adalah `"all"` $\rightarrow$ Jalankan `ingest all`.
   * Jika target adalah path folder:
     * Jika folder adalah projek/repositori tunggal $\rightarrow$ Jalankan single project ingestion.
     * Jika folder adalah container workspace multi-projek $\rightarrow$ Jalankan batch scan sub-projek.
   * Jika tidak ada path / target $\rightarrow$ Jalankan panen sesi AI agent (Antigravity & Claude Code).
3. **Backward Compatibility:**
   * Sub-perintah `devbrain ingest project`, `devbrain ingest projects`, dan `devbrain ingest all` tetap aktif.

---

## 3. Kriteria Keberhasilan (Definition of Done)
* [ ] `devbrain ingest <path>` langsung meng-ingest projek atau container.
* [ ] `devbrain ingest --dir <path>` dan `devbrain ingest --path <path>` berfungsi tanpa error flag.
* [ ] `devbrain ingest` tanpa argumen memanen sesi AI.
