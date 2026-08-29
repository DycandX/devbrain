# Task 01: Codebase Tree & Entrypoint Analyzer

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 07 (Smart Codebase Synthesizer & README-less Project Harvester) |
| **Status** | ✅ Done |
| **Target Files** | `src/devbrain/harvester/tree_analyzer.py`, `src/devbrain/harvester/manifest_parser.py` |

---

## 1. Deskripsi Task
Membangun engine analyzer statis yang memindai struktur file repository, menyaring folder yang diabaikan (`node_modules`, `.git`, `venv`, `__pycache__`, `target`, `dist`, `build`, dll.), mengekstrak file entrypoint (`server.js`, `main.py`, `app.py`, `index.ts`, `main.go`, `src/main.rs`), serta mengekstrak daftar executable scripts (`scripts` di `package.json`, `tool.poetry.scripts` di `pyproject.toml`).

---

## 2. Rincian Pekerjaan
1. **Directory Tree Generator (`src/devbrain/harvester/tree_analyzer.py`):**
   * Memindai file dan folder hingga kedalaman level 2 (max depth 2).
   * Mengabaikan folder build, venv, dan VCS.
   * Menghasilkan representasi ASCII Tree yang bersih dan rapi.
2. **Entrypoint & Infrastructure Detector:**
   * Mendeteksi file server/app: `server.js`, `app.js`, `index.js`, `main.py`, `app.py`, `manage.py`, `main.go`, `src/main.rs`.
   * Mendeteksi konfigurasi infra: `docker-compose.yml`, `Dockerfile`, `.env.example`, `Makefile`.
3. **Scripts & Commands Extractor (`src/devbrain/harvester/manifest_parser.py`):**
   * Menambahkan field `scripts: Dict[str, str]` pada `ParsedManifest`.
   * Mengekstrak script dari `package.json` (`dev`, `build`, `start`, `test`).

---

## 3. Kriteria Keberhasilan (Definition of Done)
* [ ] Modul `tree_analyzer.py` menghasilkan ASCII Tree tanpa menyertakan `node_modules` atau folder binary.
* [ ] Entrypoint utama dan file `.env.example` terdeteksi secara presisi.
* [ ] Runnable scripts terekstrak dari `package.json` dan `pyproject.toml`.
