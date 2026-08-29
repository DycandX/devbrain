# 28. Klasifikasi Projek Internal vs External Cloned Repositori (Knowledge, Skills & References)

| Metadata | Nilai |
| :--- | :--- |
| **Topik** | Penanganan Projek Hasil Clone / Pihak Ketiga vs Projek Internal & Targeted Single Ingestion |
| **Status** | 💡 Brainstorming & Taxonomy Standard |
| **Terkait** | [07-taksonomi-vault-dan-standar-metadata.md](./07-taksonomi-vault-dan-standar-metadata.md), [27-workspace-project-harvester-dan-auto-seeding.md](./27-workspace-project-harvester-dan-auto-seeding.md) |
| **Tanggal** | 2026-08-29 |

---

## 1. Latar Belakang Masalah: Ragam Jenis Repositori di Komputer Developer

Di komputer seorang *software engineer*, terdapat berbagai jenis repositori:
1. **Projek Internal / Milik Sendiri:** Projek kantor, aplikasi freelance, atau produk SaaS pribadi yang sedang aktif dikembangkan.
2. **Projek Open-Source / Pihak Ketiga (Cloned Codebase):** Repositori publik (misal: `fastapi`, `langgraph`, `shadcn-ui`) yang di-clone untuk dipelajari arsitektur kodenya.
3. **Repo Kumpulan Agent Skills (AI Tools & Prompts):** Repositori open-source berisi koleksi skill agen (misal folder `skills/` atau `SKILL.md`).
4. **Repo Dokumentasi, Riset & Awesome-List:** Repositori yang murni berisi file Markdown (misal `awesome-llm-system`, `developer-roadmap`, buku teknis).
5. **Projek Fork / Kontribusi:** Repositori orang lain yang kita fork untuk membuat *Pull Request* / kontribusi open-source.

---

## 2. Solusi: Arsitektur *Auto-Inspector* & Pemisahan Taksonomi Vault

Saat pengguna meng-ingest satu repositori tertentu (`devbrain ingest project <path>`), subsistem **Auto-Inspector** memeriksa struktur folder repo untuk menentukan penempatan folder di Obsidian:

```mermaid
graph TD
    TargetRepo["Target Repo / Folder Baru"] --> Inspector["🔍 devbrain Auto-Inspector"]
    
    Inspector -->|Ada SKILL.md atau folder skills/| S["🛠️ 00_System/Agent_Skills/<br/>(type: 'agent-skill')"]
    Inspector -->|Mayoritas file .md / Docs / Awesome-List| K["📚 20_Knowledge/References/<br/>(type: 'knowledge-doc')"]
    Inspector -->|Source Code + Author Sendiri| P["📂 10_Projects/<Nama_Projek>/<br/>(type: 'project', role: 'owner')"]
    Inspector -->|Source Code + Author Luar (Clone)| E["📚 20_Knowledge/External_Repos/<br/>(type: 'reference-repo', role: 'study')"]
    Inspector -->|Repo Fork / Kontribusi| F["📂 10_Projects/<Nama_Projek>/<br/>(type: 'fork-project', role: 'contributor')"]
```

---

## 3. Matriks Klasifikasi Metadata Lengkap

| Kategori Repositori | Lokasi Penempatan di Vault | Metadata YAML (`type:` / `role:`) | Manfaat bagi Pengguna & AI Agent |
| :--- | :--- | :--- | :--- |
| **Active Project (Milik Sendiri)** | `10_Projects/<Project_Name>/README.md` | `type: "project"`<br/>`role: "owner"` | Menyimpan roadmap, tasks, arsitektur internal, dan riwayat sesi koding AI. |
| **Forked Contributor** | `10_Projects/<Project_Name>/README.md` | `type: "fork-project"`<br/>`role: "contributor"` | Melacak issue/PR yang sedang kita kerjakan untuk komunitas open-source. |
| **External Codebase (Studi/Clone)** | `20_Knowledge/External_Repos/<Repo_Name>/README.md` | `type: "reference-repo"`<br/>`role: "study"` | Menjadi kartu referensi arsitektur kode tanpa mengotori daftar projek aktif. |
| **Agent Skills / Tools Mesh** | `00_System/Agent_Skills/<skill-name>/` | `type: "agent-skill"` | Seluruh AI Agent (Antigravity, Claude, AGY) langsung dapat memakai skill baru via `load_skill()`. |
| **Knowledge / Awesome / Docs Repo** | `20_Knowledge/References/<Repo_Name>/` | `type: "knowledge-doc"` | Seluruh file Markdown di dalamnya di-chunk dan diindeks ke FastEmbed+BM25 untuk pencarian instan. |

---

## 4. Alur Targeted Single Ingestion (`devbrain ingest project`)

Jika developer baru saja membuat 1 projek baru atau baru saja clone 1 repo spesifik, developer tidak perlu memindai seluruh workspace:

```bash
# 1. Jalankan langsung dari dalam folder projek target
cd "E:/_PROJECT/MyNewApp"
devbrain ingest project .

# 2. Atau tentukan path direktori target dari mana saja
devbrain ingest project "E:/_PROJECT/MyNewApp"
```

### Opsi Flag Eksplisit (*Manual Type Override*):
Jika pengguna ingin memaksakan jenis penempatan tertentu tanpa melalui auto-detect:
```bash
# Paksa masuk ke 10_Projects/ sebagai Projek Aktif
devbrain ingest project "E:/_PROJECT/MyNewApp" --type project

# Paksa impor ke 00_System/Agent_Skills/ sebagai Agent Skill
devbrain ingest project "E:/_PROJECT/cloned-gemini-skills" --type skill

# Paksa impor ke 20_Knowledge/ sebagai Knowledge Base
devbrain ingest project "E:/_PROJECT/awesome-system-design" --type knowledge

# Paksa impor ke 20_Knowledge/External_Repos/ sebagai Referensi Clone
devbrain ingest project "E:/_PROJECT/fastapi-study" --type reference
```

---

## 5. Algoritma Deteksi Otomatis (*Heuristic Rules*)

1. **Pemeriksaan File Skill:**
   * Jika direktori root memiliki `SKILL.md` atau folder `skills/` yang berisi `SKILL.md` $\rightarrow$ Klasifikasi: `skill`.
2. **Pemeriksaan Dominasi Markdown (Docs / Knowledge):**
   * Jika >70% file yang ada berupa file `.md` dan tidak ditemukan manifest build seperti `package.json` / `pyproject.toml` $\rightarrow$ Klasifikasi: `knowledge`.
3. **Pemeriksaan Git Author (Projek Sendiri vs Clone Referensi):**
   * Jika memiliki manifest koding (`pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`):
     * Jika `git config user.email` cocok dengan salah satu author commit terakhir $\rightarrow$ Klasifikasi: `project`.
     * Jika tidak ada commit lokal dari developer dan remote URL milik organisasi/orang lain $\rightarrow$ Klasifikasi: `reference`.
