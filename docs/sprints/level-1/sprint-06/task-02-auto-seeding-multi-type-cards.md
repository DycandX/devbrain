# Task 02: Auto-Seeding Multi-Type Cards (Projects, Knowledge, Skills)

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 06 (Graph Mesh, Workspace Harvester & Targeted Ingestion) |
| **Status** | ✅ Done |
| **Target Files** | `src/devbrain/harvester/project_harvester.py`, `src/devbrain/core/scaffolder.py` |

---

## 1. Deskripsi Task
Membangun engine formatter dan writer untuk meng-auto-seed kartu catatan terstandarisasi ke dalam Obsidian Vault sesuai hasil klasifikasi:
* **Active Projects:** `10_Projects/<Project_Name>/README.md`
* **External Reference Repos:** `20_Knowledge/External_Repos/<Repo_Name>/README.md`
* **Agent Skills Mesh:** `00_System/Agent_Skills/<skill-name>/`
* **Knowledge Docs:** `20_Knowledge/References/<Repo_Name>/`

---

## 2. Rincian Pekerjaan
1. **Standardized Project Card Formatter:**
   * Menulis kartu projek lengkap dengan frontmatter YAML (`id`, `title`, `type: "project"`, `role: "owner" | "contributor"`, `status: "active"`, `language`, `stack`, `git_remote`, `local_path`, `tags`).
   * Menyisipkan blok query **Obsidian Dataview** dinamis yang otomatis menampilkan riwayat sesi AI terkini yang terkait dengan projek tersebut.
2. **External Study Reference Card Formatter:**
   * Menulis kartu referensi di `20_Knowledge/External_Repos/<Repo>/README.md` (`type: "reference-repo"`, `role: "study"`).
   * Meringkas arsitektur dan kegunaan codebase tanpa menyalin ribuan file kode mentah.
3. **Agent Skill Importer:**
   * Menyalin atau menautkan folder skill yang ditemukan ke `00_System/Agent_Skills/<skill-name>/`.
   * Memastikan validitas `SKILL.md` agar langsung terbaca oleh tool FastMCP `load_skill()`.
4. **Knowledge Docs Ingestor:**
   * Menyalin hierarki dokumentasi markdown ke `20_Knowledge/References/<Repo>/`.
   * Memicu incremental indexer FastEmbed + BM25 agar langsung dapat dicari.

---

## 3. Kriteria Keberhasilan (Definition of Done)
* [ ] Kartu projek terbuat secara otomatis di `10_Projects/` dengan frontmatter YAML valid dan Dataview query.
* [ ] Repo referensi masuk ke `20_Knowledge/External_Repos/` tanpa mengotori `10_Projects/`.
* [ ] Skill eksternal langsung terdaftar di `00_System/Agent_Skills/` dan siap dipanggil AI Agent.
