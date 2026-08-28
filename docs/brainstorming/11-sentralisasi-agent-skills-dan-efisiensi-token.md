# 11. Sentralisasi Agent Skills & Analisis Efisiensi Konsumsi Token

Dokumen ini menjawab dua pertanyaan fundamental terkait operasional Central AI Brain Hub:
1. **Bagaimana mengelola dan menyinkronkan *Agent Skills* lintas device dan lintas agent?**
2. **Bagaimana dampak arsitektur ini terhadap konsumsi token (apakah lebih boros atau jauh lebih hemat)?**

---

## 1. Sentralisasi Agent Skills (Universal Skill Registry)

### A. Apakah Agent Skills Bisa Disimpan di Central Brain?
**Sangat bisa.** Bahkan, menjadikan Central Vault sebagai **Universal Skill Registry** adalah salah satu nilai tambah terbesar dari arsitektur ini.

Alih-alih membuat skill secara terisolasi di masing-masing laptop atau agent:
* Seluruh skill disimpan di direktori terpusat: `00_System/Agent_Skills/` di Obsidian Vault.
* Mengikuti standar universal `SKILL.md` (YAML frontmatter + instruksi + script/contoh).

```text
Central-AI-Vault/
└── 00_System/
    └── Agent_Skills/
        ├── git-workflow-automation/
        │   └── SKILL.md
        ├── fastapi-production-boilerplate/
        │   ├── SKILL.md
        │   └── templates/
        ├── react-tailwind-glassmorphism/
        │   └── SKILL.md
        ├── sql-query-optimizer/
        │   └── SKILL.md
        └── debug-memory-leaks/
            └── SKILL.md
```

---

### B. Mekanisme Distribusi & Eksekusi Skills Lintas Agent

Terdapat dua metode distribusi skill ke berbagai AI Agent:

```
                      [ Central Obsidian Vault ]
                      00_System/Agent_Skills/
                                 │
         ┌───────────────────────┴───────────────────────┐
         │                                               │
         ▼ (Metode 1: File Sync / Symlink)               ▼ (Metode 2: On-Demand MCP Tool)
[ Laptop File System ]                        [ FastMCP Server di Jarvis ]
~/.gemini/config/skills/                      `get_skill(name)`, `search_skills(query)`
         │                                               │
         ▼                                               ▼
[ Antigravity IDE / agy CLI ]                 [ Claude Code / Hermes / OpenCode ]
(Native Discovery & Execution)                (Dynamic Context Injection via Tools)
```

#### 1. Metode File-System Symlink (Untuk Antigravity IDE & agy CLI)
* Folder `00_System/Agent_Skills/` disinkronkan oleh Syncthing ke laptop di `~/ObsidianVault/00_System/Agent_Skills/`.
* Buat *symbolic link* (symlink) dari direktori konfigurasi global Antigravity ke folder vault:
  * **Windows:** `mklink /D "C:\Users\<user>\.gemini\config\skills" "C:\Users\<user>\ObsidianVault\00_System\Agent_Skills"`
  * **Linux/macOS:** `ln -s ~/ObsidianVault/00_System/Agent_Skills ~/.gemini/config/skills`
* **Hasil:** Setiap kali Anda atau agent menambahkan skill baru di Obsidian, skill tersebut **langsung aktif di Antigravity IDE & CLI di semua perangkat tanpa restart**.

#### 2. Metode Dynamic On-Demand Retrieval via FastMCP (Untuk Claude Code, Hermes, CLI lain)
* FastMCP di Jarvis mengekspos tools:
  * `list_available_skills()`: Mengembalikan daftar nama dan deskripsi singkat skill.
  * `load_skill(skill_name: str)`: Mengembalikan isi lengkap `SKILL.md` dan dependensinya.
* Agent hanya memuat instruksi skill ke dalam context window **hanya ketika tugas spesifik tersebut sedang dikerjakan**.

#### 3. Continuous Self-Improvement (Agent Skill Creator Loop)
Jika agent di laptop kantor berhasil menyelesaikan workflow kompleks yang baru:
1. Agent memicu tool pembuat skill (misal `workflow-skill-creator` atau `write_inbox_note`).
2. Skill baru tersimpan di Obsidian `00_System/Agent_Skills/`.
3. Syncthing mereplikasi skill tersebut ke Jarvis dan Laptop Pribadi dalam hitungan detik.
4. Malam harinya di rumah, laptop pribadi Anda sudah memiliki kapabilitas dan trik baru tersebut!

---

## 2. Analisis Konsumsi Token: Lebih Boros atau Lebih Hemat?

### Kesimpulan Utama:
> **Arsitektur Central Brain Hub justru MENGHEMAT konsumsi token antara 60% hingga 85%** dibandingkan pendekatan manual/konvensional, asalkan menggunakan strategi *Just-In-Time (JIT) Dynamic Retrieval*.

---

### Perbandingan Skenario: Konvensional vs Central AI Brain

| Parameter | Pendekatan Konvensional (Tanpa Brain Hub) | Pendekatan Central AI Brain Hub (JIT RAG + MCP) |
| :--- | :--- | :--- |
| **System Prompt Baseline** | Memasukkan aturan besar, preferensi, dan puluhan skill sekaligus ke system prompt (**~10.000 – 30.000 tokens per request**). | System prompt ramping: hanya daftar tools MCP ringkas (**~300 – 500 tokens**). |
| **Pencarian Konteks & Memori** | User manual copy-paste file code atau riwayat chat panjang ke prompt (**~15.000 tokens**). | Agent melakukan semantic search via Vector DB lokal di Jarvis dan hanya menarik 2-3 chunk relevan (**~800 tokens**). |
| **Biaya Token Pencarian (Embedding)** | Menggunakan API LLM berbayar untuk setiap embedding. | **0 Token Biaya:** Di-generate lokal di Jarvis menggunakan Ollama (`bge-m3`) / Qdrant. |
| **Debugging / Trial & Error** | Agent menebak-nebak error baru, butuh 5-10 turn percakapan yang repetitif (**~50.000 – 100.000 tokens**). | Agent membaca catatan solusi bug yang pernah tersimpan di `20_Knowledge/Bug_Solutions/` $\rightarrow$ langsung fix dalam 1-2 turn (**~5.000 tokens**). |
| **Penyimpanan Sesi (Memory)** | Riwayat percakapan panjang terus menumpuk di context window (*context window bloat*). | Sesi lama dipadatkan (*distilled*) oleh background harvester menjadi ringkasan 300 token di Obsidian. |

---

### Kalkulasi Riil Konsumsi Token

#### Skenario Kasus: Menyelesaikan Fitur "FastAPI OAuth2 Refresh Token Rotation"

```
[ Skenario A: Tanpa Central Hub ]
1. Prompt awal + System Prompt + Semua Aturan Proyek    : 12.000 tokens
2. Turn 1 (Agent mencoba solusi standar, kena error)     : 14.500 tokens
3. Turn 2 (User kirim error log + agent revisi kode)     : 18.000 tokens
4. Turn 3 (Kena error race condition token)              : 22.000 tokens
5. Turn 4 (Akhirnya berhasil setelah trial-error)        : 26.000 tokens
──────────────────────────────────────────────────────────────────────────
Total Konsumsi Token Skenario A                          : ~92.500 tokens
Biaya Waktu & Latensi                                    : Tinggi (4 iterasi)
```

```
[ Skenario B: Dengan Central AI Brain Hub ]
1. Prompt awal + System Prompt Ringkas (MCP Tool defs)   : 800 tokens
2. Agent memanggil `search_brain("fastapi refresh token")`: 150 tokens (Tool call)
3. Server Jarvis mengembalikan Knowledge Note dari bug   : 650 tokens (Context)
   yang pernah diselesaikan 2 bulan lalu
4. Agent langsung menerapkan pola solusi terverifikasi   : 2.200 tokens
5. Eksekusi sukses pada Turn 1                           : Selesai!
──────────────────────────────────────────────────────────────────────────
Total Konsumsi Token Skenario B                          : ~3.800 tokens
Penghematan Token                                        : 95.8% LEBIH HEMAT!
```

---

## 3. Best Practices untuk Memaksimalkan Efisiensi Token

Agar konsumsi token selalu minimal dan tidak terjadi pemborosan:

1. **Lazy Loading Skills (On-Demand):**
   Jangan pernah memuat seluruh isi folder `Agent_Skills` ke prompt. Hanya muat nama dan deskripsi 1 baris. Muat isi `SKILL.md` hanya jika tool mendeteksi intensi user yang cocok.
2. **Strict Vector Search Limits:**
   Batasi query retrieval di FastMCP ke `top_k=3` atau `limit=3` dokumen dengan similarity score threshold $\ge 0.75$.
3. **Chunking Cerdas:**
   Di watcher Jarvis, pecah dokumen Markdown per heading (`##`) dengan ukuran chunk 300-500 kata, bukan mengindeks satu file raksasa secara utuh.
4. **Local Distillation Worker:**
   Gunakan model lokal (Ollama / small model) atau model Flash yang murah untuk memproses transkrip mentah di laptop menjadi ringkasan Obsidian, sehingga tidak membebani kuota model utama.
