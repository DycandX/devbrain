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
│   └── 18-onboarding-laptop-pribadi-dan-alur-development.md
└── changelog-plan/                # [Execution Plans] Implementation plan, task list, & progress log
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

### 3. Rencana Eksekusi & Changelog (`docs/changelog-plan/`)
* Setiap rencana implementasi teknis (*Implementation Plan* / *PRD*) dan catatan perubahan (*changelog*) disimpan di `docs/changelog-plan/`.

### 4. Git Version Control & Commit Protocol
* Setelah sesi pencatatan atau perancangan selesai, simpan perubahan ke git dengan commit message yang rapi dan deskriptif mengikuti standar conventional commits:
  * `docs(brainstorm): add 06-10 deep dive and update brainstorming index`
  * `docs(summary): update master blueprint with multi-device sync strategy`
  * `docs(governance): define documentation rules and repository structure in _index.md`

---

## 🧭 Navigasi Cepat

* 🏛️ **[Master Blueprint & Architecture](./_summary/00.md)**
* 🧠 **[Indeks Brainstorming Documents](./brainstorming/_index.md)**
