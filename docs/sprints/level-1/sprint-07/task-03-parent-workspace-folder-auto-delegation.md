# Task 03: Parent Workspace Folder Auto-Delegation

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 07 (Smart Codebase Synthesizer & README-less Project Harvester) |
| **Status** | ✅ Done |
| **Target Files** | `src/devbrain/harvester/inspector.py`, `src/devbrain/harvester/service.py`, `src/devbrain/cli/commands/ingest_cmd.py` |

---

## 1. Deskripsi Task
Mendeteksi ketika pengguna menjalankan `devbrain ingest project <folder>` pada sebuah folder container/induk yang tidak memiliki manifest di root tetapi memiliki 2 atau lebih subfolder projek, lalu secara otomatis mendelegasikannya menjadi batch scan subfolder projek.

---

## 2. Rincian Pekerjaan
1. **Container Workspace Detection:**
   * Di `inspector.py`: Jika folder root tidak punya manifest, tetapi subfoldernya memiliki file manifest/git $\rightarrow$ Klasifikasi: `RepoType.CONTAINER_WORKSPACE`.
2. **Auto-Delegation di `IngestionService`:**
   * Jika mendeteksi folder bertipe `CONTAINER_WORKSPACE`, service otomatis memanggil `ingest_workspace_projects(root_dirs=[repo_path])`.
3. **CLI Feedback:**
   * Menampilkan pesan ramah: *"Detected multi-project container workspace. Automatically scanning sub-projects..."*

---

## 3. Kriteria Keberhasilan (Definition of Done)
* [ ] Menjalankan `devbrain ingest project "E:/_PROJECT/_fxmedia"` otomatis meng-ingest sub-projek di dalamnya (`neo4j-express-demo`, `qdrant-local-demo`) tanpa menghasilkan note `UNKNOWN` yang kosong.
