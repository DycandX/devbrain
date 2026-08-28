# Product Requirements Document (PRD) - Level 1: Standalone Local

| Attribute | Detail |
| :--- | :--- |
| **Product Name** | `devbrain` (Central AI Brain Hub) |
| **Tier / Level** | **Level 1: Standalone Local (Zero-Friction Core)** |
| **Status** | Approved for Implementation |
| **Target Release** | Version 1.0.0-alpha |
| **Author** | Antigravity AI Engineering Team |

---

## 1. Ringkasan Eksekutif & Visi Produk

**Level 1 Standalone Local** adalah fondasi utama dan inti dari sistem `devbrain`. Fokus tier ini adalah memberikan pengalaman **Zero-Friction (Tanpa Ribet)** bagi seorang software developer yang ingin menghubungkan AI coding agent miliknya (**Antigravity IDE**, **Claude Code**, **Hermes Agent**, **OpenCode**) dengan **Obsidian Vault** lokal di 1 laptop.

Tujuan utama Level 1 adalah:
1. Setup selesai dalam waktu **kurang dari 30 detik**.
2. **100% Offline, Gratis, & Privat** tanpa ketergantungan pada server eksternal, Docker, Tailscale, atau koneksi internet.
3. Menjadi *Single Source of Truth* (SSOT) memori proyek dan skill registry untuk AI Agent di mesin lokal.

---

## 2. Target Pengguna & User Persona

* **Persona:** Solo Developer / Software Engineer yang menggunakan IDE berbasis AI (seperti Antigravity IDE atau Cursor/Claude Code) pada laptop pribadinya (Windows / macOS / Linux).
* **Pain Point:** AI Agent sering "lupa" keputusan arsitektur proyek saat sesi chat ditutup, memakan token berulang kali untuk membaca instruksi yang sama, dan tidak ada tampilan visual untuk membaca memori AI.
* **Goal:** Menjalankan 1 perintah CLI, langsung memiliki Obsidian Vault yang terindeks dan terhubung secara otomatis ke AI Agent.

---

## 3. Diagram Arsitektur Level 1 (In-Process Stdio Architecture)

```
┌────────────────────────────────────────────────────────────────────────┐
│                          LAPTOP PENGGUNA (LOCAL)                       │
│                                                                        │
│  ┌───────────────────────┐             ┌────────────────────────────┐  │
│  │   Antigravity IDE /   │             │   Obsidian Desktop App     │  │
│  │   Claude Code         │             │   (Visual GUI & Graph)     │  │
│  └──────────┬────────────┘             └─────────────┬──────────────┘  │
│             │ (Stdio Protocol)                       │ (Direct File Read)
│             ▼                                        ▼                 │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                     `devbrain` CLI / MCP Core                    │  │
│  │  - CLI Interface    : Typer + Rich (Interactive Terminal)       │  │
│  │  - MCP Protocol     : FastMCP (Stdio Subprocess)                │  │
│  │  - Hybrid Engine    : FastEmbed (CPU ONNX) + Rank-BM25          │  │
│  │  - Vector Cache     : Local Embedded LanceDB / Disk Cache       │  │
│  │  - File Watcher     : Watchdog (Auto-index .md events)          │  │
│  └──────────────────────────────────┬───────────────────────────────┘  │
│                                     │                                  │
│                                     ▼ (Direct Disk I/O)                │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │               LOCAL OBSIDIAN VAULT (Folder di Harddisk)          │  │
│  │  ├── 00_System/ (Rules, Workflows, Agent_Skills/)                │  │
│  │  ├── 10_Projects/ (Active Projects Context & Architecture)       │  │
│  │  ├── 20_Knowledge/ (Tech Stack Docs & Snipets)                   │  │
│  │  ├── 90_Agent_Inbox/ (Append-Only Log Harian AI)                 │  │
│  │  ├── .brain_data/ (Vektor index cache - hidden)                  │  │
│  │  └── .brainrc.json (File konfigurasi vault)                      │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Spesifikasi Kebutuhan Fungsional (*Functional Requirements*)

### FR-1: Interactive Initialization Wizard (`devbrain init`)
* **FR-1.1:** CLI harus menyediakan wizard interaktif ramah pemula menggunakan antarmuka terminal `Rich`.
* **FR-1.2:** Pengguna dapat menentukan lokasi folder vault (default: `~/DevBrainVault` atau path kustom).
* **FR-1.3:** Jika folder kosong atau baru, CLI otomatis melakukan **Auto-Scaffolding** struktur direktori standar:
  * `00_System/Agent_Skills/`
  * `10_Projects/`
  * `20_Knowledge/`
  * `90_Agent_Inbox/`
* **FR-1.4:** Jika folder sudah berisi catatan (existing vault), CLI menerapkan aturan **Non-Destructive Attachment** (tidak menghapus atau mengubah file catatan yang sudah ada).
* **FR-1.5:** Pilihan mode embedding:
  * *Option 1 (Default):* Local CPU FastEmbed (`BAAI/bge-small-en-v1.5` / `bge-m3` via ONNX Runtime, 0 GPU, $0 cost).
  * *Option 2:* Cloud API (Google Gemini / OpenAI - input API Key disimpan di `.env` lokal).
  * *Option 3:* Ollama Local Server (input URL host).
* **FR-1.6:** Menghasilkan file konfigurasi lokal `.brainrc.json` di root vault.

### FR-2: Auto-Configurator AI Client
* **FR-2.1:** CLI harus secara otomatis mendeteksi keberadaan file konfigurasi AI di mesin pengguna:
  * Antigravity IDE: `~/.gemini/antigravity/mcp_config.json`
  * Claude Code: `~/.claude.json`
* **FR-2.2:** Menambahkan entri server MCP `central-brain` secara otomatis tanpa memerlukan campur tangan edit JSON manual oleh pengguna.

### FR-3: FastMCP Toolset (Active AI Capabilities)
Ketika AI Agent terhubung via MCP Stdio, `devbrain` mengekspos 4 tools standar:
1. `search_brain(query: str, limit: int = 5, scope: str = "all")`:
   * Melakukan pencarian Hybrid (Dense Vector + Sparse BM25) ke seluruh dokumen `.md`.
   * Mengembalikan judul file, path, cuplikan konten yang relevan, dan skor kesamaan.
2. `get_project_context(project_name: str)`:
   * Mengambil file konteks spesifik dari `10_Projects/{project_name}.md` atau membaca seluruh folder proyek terkait.
3. `write_agent_log(summary: str, details: str, tags: list[str])`:
   * Menyimpan ringkasan sesi kerja, keputusan arsitektur, atau bugfix yang berhasil diselesaikan ke `90_Agent_Inbox/{timestamp}_{uuid}.md`.
4. `load_skill(skill_name: str)`:
   * Mengambil instruksi lengkap file `SKILL.md` dari `00_System/Agent_Skills/{skill_name}/` secara *Just-In-Time* (menghemat token context window).

### FR-4: Real-time Vault Watcher & Indexer
* **FR-4.1:** Menggunakan `watchdog` untuk memantau event `on_created`, `on_modified`, dan `on_deleted` pada file `.md`.
* **FR-4.2:** Mengabaikan file dan folder yang tercantum di `.brainignore` atau folder internal (`.brain_data/`, `.obsidian/`).
* **FR-4.3:** Memperbarui indeks vektor dan tabel BM25 secara inkremental dalam waktu <1 detik setelah file disimpan.

### FR-5: Clean Teardown & Uninstall (`devbrain uninstall`)
* **FR-5.1:** Menyediakan perintah pembersihan otomatis yang mencabut konfigurasi MCP dari Antigravity & Claude.
* **FR-5.2:** Menjamin bahwa file catatan Markdown milik pengguna **tidak pernah disentuh atau dihapus**.

---

## 5. Kebutuhan Non-Fungsional (*Non-Functional Requirements*)

| Parameter | Target Spesifikasi |
| :--- | :--- |
| **Waktu Inisialisasi** | < 30 detik dari eksekusi `devbrain init` hingga siap pakai. |
| **Latensi Pencarian** | < 20 milidetik untuk query hybrid search pada vault dengan 1.000 dokumen. |
| **Konsumsi Memori (RAM)** | < 120 MB RAM saat idle, ~180 MB saat model FastEmbed CPU ONNX aktif. |
| **Ketergantungan Eksternal** | 0 Docker, 0 Cloud Server, 0 Tailscale, 0 Syncthing (100% Standalone). |
| **Keamanan & Privasi** | 100% data tersimpan lokal di harddisk, 0 telemetri rahasia keluar ke internet. |
| **Kompatibilitas OS** | Windows 10/11 (PowerShell & CMD), macOS (Apple Silicon & Intel), Linux (Ubuntu/Debian/Arch). |

---

## 6. Spesifikasi Perintah CLI Level 1

```text
devbrain init [path]       # Inisialisasi vault baru atau attach existing vault
devbrain status            # Cek status indeks, jumlah catatan, dan konfigurasi aktif
devbrain search "<query>"  # Tes pencarian hybrid langsung dari terminal
devbrain index [--reindex] # Re-index manual seluruh vault
devbrain skill list        # Menampilkan daftar skill yang ada di vault
devbrain skill add <name>  # Membuat template folder skill baru
devbrain uninstall         # Mencabut konfigurasi MCP & membersihkan cache
```

---

## 7. Kriteria Keberhasilan & Skenario Pengujian (*Acceptance Criteria*)

1. **Skenario 1 (Fresh Install):**
   * Pengguna menjalankan `devbrain init E:/MyVault`.
   * Struktur folder `00_System/`, `10_Projects/`, dll. berhasil dibuat.
   * File `~/.gemini/antigravity/mcp_config.json` terisi konfigurasi `central-brain`.
   * Antigravity IDE dapat memanggil tool `search_brain` dan mendapatkan hasil yang akurat.
2. **Skenario 2 (Existing Vault Attachment):**
   * Pengguna menunjuk folder Obsidian yang sudah berisi 500 catatan lama.
   * `devbrain` mengindeks seluruh catatan tanpa mengubah satu pun file asli.
3. **Skenario 3 (Zero Background Overhead):**
   * Saat IDE ditutup, proses `devbrain` Stdio otomatis berhenti (0 MB background RAM).
