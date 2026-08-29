# Task 01: Auto-Inspector, Repo Scanner & Manifest Parser

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 06 (Graph Mesh, Workspace Harvester & Targeted Ingestion) |
| **Status** | ✅ Done |
| **Target Files** | `src/devbrain/harvester/inspector.py`, `src/devbrain/harvester/manifest_parser.py`, `src/devbrain/harvester/project_harvester.py` |

---

## 1. Deskripsi Task
Membangun subsistem cerdas pemindaian repositori lokal, auto-inspector untuk mengenali jenis repositori secara otomatis (Active Project, Cloned Reference, Agent Skill, atau Knowledge Docs), dan parser manifest dependensi (`pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, `Dockerfile`).

---

## 2. Rincian Pekerjaan
1. **Auto-Inspector Jenis Repositori (`src/devbrain/harvester/inspector.py`):**
   * Mendeteksi file `SKILL.md` atau folder `skills/` $\rightarrow$ Klasifikasi: `skill`.
   * Mendeteksi repositori yang >70% berupa file Markdown (`docs/`, `awesome-*`) $\rightarrow$ Klasifikasi: `knowledge`.
   * Mendeteksi repositori koding:
     * Jika `git config user.email` cocok dengan author commit $\rightarrow$ Klasifikasi: `project` (Internal Active).
     * Jika tidak ada commit dari user & remote publik $\rightarrow$ Klasifikasi: `reference` (Cloned Study Repo).
2. **Manifest Dependency Parser (`src/devbrain/harvester/manifest_parser.py`):**
   * **Python:** Parse `pyproject.toml` (poetry/hatch/flit/setuptools), `requirements.txt`, `Pipfile`.
   * **Node/TS:** Parse `package.json` (`dependencies`, `devDependencies`, `scripts`).
   * **Rust & Go:** Parse `Cargo.toml` (`[dependencies]`), `go.mod`.
   * **DevOps:** Deteksi `Dockerfile` dan `docker-compose.yml`.
3. **Git Repository Metadata Scanner (`src/devbrain/harvester/project_harvester.py`):**
   * Ekstrak Git Remote URL, branch aktif, latest commit hash, timestamp, dan author.
   * Ekstrak ringkasan dan deskripsi dari root `README.md`.

---

## 3. Kriteria Keberhasilan (Definition of Done)
* [ ] Modul `inspector.py` mampu membedakan 4 jenis repo dengan akurasi 100%.
* [ ] Modul `manifest_parser.py` berhasil mengekstrak nama paket, versi, dan tech stack dari Python, Node/TS, Rust, dan Go.
* [ ] Modul `project_harvester.py` menghasilkan objek dataclass `ScannedProjectMetadata` yang lengkap dan terstruktur.
