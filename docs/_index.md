# 📚 Central AI Brain Hub - Documentation Hub & Governance

Dokumen ini mendefinisikan struktur direktori dokumentasi, tata kelola pencatatan (*documentation rules*), dan alur kerja pengembangan (*workflow governance*) untuk proyek **Central AI Brain Hub**.

---

## 📂 Struktur Direktori Dokumentasi (`docs/`)

```text
docs/
├── _index.md                      # [Root Governance] Panduan, aturan penulisan, dan indeks utama
├── _summary/                      # [Master Blueprints] Rangkuman eksekutif & arsitektur final
│   └── 00.md                      # Master Blueprint SSOT Multi-Agent & Multi-Device
├── brainstorming/                 # [Explorations] Hasil eksplorasi & sesi brainstorming teknis
│   ├── _index.md                  # Indeks navigasi seluruh dokumen brainstorming
│   ├── 01-arsitektur-dasar-central-brain.md
│   ├── 02-integrasi-obsidian-core-knowledge-base.md
│   ├── 03-penyimpanan-memory-antigravity-ide-cli.md
│   ├── 04-peta-penyimpanan-multi-agent-cli.md
│   ├── 05-komparasi-repo-open-source.md
│   ├── 06-siklus-hidup-data-dan-sync-multi-device.md
│   ├── 07-taksonomi-vault-dan-standar-metadata.md
│   ├── 08-server-stack-jarvis-dan-fastmcp.md
│   ├── 09-client-adapters-dan-distillation-pipeline.md
│   ├── 10-security-privacy-dan-boundary-protocol.md
│   ├── 11-sentralisasi-agent-skills-dan-efisiensi-token.md
│   ├── 12-opsi-deployment-dan-konsep-embedding.md
│   ├── 13-korelasi-projek-fxmedia-dan-hybrid-graph-rag.md
│   ├── 14-panduan-implementasi-praktis-dan-koneksi-obsidian.md
│   ├── 15-multi-vault-dan-strategi-adopsi-existing-vault.md
│   ├── 16-cli-architecture-dan-konsep-obsidian-sebagai-database.md
│   ├── 17-core-mechanics-server-deployment-dan-tech-stack.md
│   ├── 18-onboarding-laptop-pribadi-dan-alur-development.md
│   ├── 19-analisis-komprehensif-pemilihan-tech-stack.md
│   ├── 20-analisis-repo-obsidian-mcp-zettelkasten-dan-daftar-command.md
│   ├── 21-metode-sync-obsidian-dan-prosedur-uninstall-bersih.md
│   ├── 22-panduan-detail-syncthing-dan-git-auto-sync.md
│   └── 23-filosofi-zero-friction-dan-level-adopsi-gradual.md
├── prd/                           # [Product Requirements Documents] Spesifikasi produk 3 level
│   ├── _index.md                  # Indeks navigasi PRD
│   ├── 01-prd-level-1-standalone-local.md
│   ├── 02-prd-level-2-local-cloud-backup.md
│   └── 03-prd-level-3-multi-device-mesh.md
├── implementation-plan/           # [Implementation Plans] Rencana implementasi teknis
│   ├── _index.md                  # Indeks Implementation Plan
│   └── 01-implementation-plan-level-1-standalone.md
├── sprints/                       # [Sprint Plans] Implementation plan & sprint execution tasks
│   └── level-1/                   # Sprint tasks Level 1 Standalone Local
│       ├── _index.md              # Indeks sprint level 1
│       ├── sprint-01/             # Setup, Scaffolder, Config & CLI Init
│       ├── sprint-02/             # Hybrid Indexer & Real-time Watcher
│       ├── sprint-03/             # FastMCP Gateway & IDE Auto-Config
│       └── sprint-04/             # Tests, Benchmark & Release Readiness
└── changelog/                     # [Changelogs] Catatan riwayat perubahan versi
```

---

## 📋 Aturan & Standar Pencatatan (Recording Rules)

Setiap agen AI dan kontributor diwajibkan mematuhi aturan berikut saat melakukan riset, perancangan, atau brainstorming:

### 1. Sesi Brainstorming (`docs/brainstorming/`)
* **Pencatatan Lengkap:** Catat semua hasil eksplorasi ide, analisis teknis, dan perbandingan solusi ke dalam folder `docs/brainstorming/`.
* **Format Penamaan File:** Gunakan konvensi penomoran dua digit dan slug deskriptif:  
  `XX-nama-topik-spesifik.md` (contoh: `01-arsitektur-dasar-central-brain.md`, `06-siklus-hidup-data-dan-sync-multi-device.md`).
* **Update Indeks Brainstorming:** Setiap kali file baru dibuat, perbarui tabel daftar di [docs/brainstorming/_index.md](./brainstorming/_index.md).

### 2. Rangkuman & Blueprint Eksekutif (`docs/_summary/`)
* **Sintesis Terpusat:** Rangkum seluruh keputusan final, arsitektur sistem, dan roadmap strategis di file [docs/_summary/00.md](./_summary/00.md).
* **Single Source of Truth:** Dokumen `_summary/00.md` menjadi acuan utama sebelum masuk ke tahap eksekusi kode.

### 3. Rencana Eksekusi & Changelog Protocol (`docs/changelog/` & `docs/sprints/`)
* **Changelog Wajib:** Setiap rilis versi, penambahan fitur, perubahan arsitektur, atau perbaikan bug wajib dicatat di [docs/changelog/](./changelog/_index.md) dan `CHANGELOG.md`.
* **Sprint Tracking:** Kemajuan tugas teknis dipantau melalui kartu task di [docs/sprints/](./sprints/level-1/_index.md).

### 4. Git Version Control & Commit Protocol
* Setiap perubahan kode, fitur, dan dokumentasi disimpan ke git dengan commit message mengikuti standar conventional commits:
  * `feat(scope): ...` untuk penambahan fitur baru
  * `docs(scope): ...` untuk perubahan dokumentasi / changelog
  * `test(scope): ...` untuk penambahan unit test

---

## 🧭 Navigasi Cepat

* 🏛️ **[Master Blueprint & Architecture](./_summary/00.md)**
* 🧠 **[Indeks Brainstorming Documents](./brainstorming/_index.md)**
* 📄 **[Product Requirements Documents (PRD)](./prd/_index.md)**
* 🏃‍♂️ **[Sprint Execution Tasks](./sprints/level-1/_index.md)**
* 📜 **[Changelog & Release History](./changelog/_index.md)**
