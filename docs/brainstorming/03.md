Memory, konteks, convos nya antigravity ide ai agent, agy cli itu disimpan dimana?

Data **memory, konteks, artifacts, dan riwayat percakapan (convos)** pada ekosistem **Google Antigravity IDE** dan **Antigravity CLI (`agy`)** disimpan secara lokal di dalam file system pada level *User Home* dan *Project Workspace*.

---

### 1. Lokasi Utama (Global User Directory)

Seluruh riwayat, memori eksekusi, dan sesi disimpan di dalam direktori tersembunyi `~/.gemini/`:

* **Linux / macOS:** `~/.gemini/`
* **Windows:** `C:\Users\<Username>\.gemini\` (atau `%USERPROFILE%\.gemini\`)

Di dalam direktori tersebut, Antigravity memisahkan runtime IDE dan CLI:

* **Antigravity IDE:** `~/.gemini/antigravity/`
* **Antigravity CLI (`agy`):** `~/.gemini/antigravity-cli/`
* **Global Config & Skills:** `~/.gemini/config/` (atau `~/.gemini/config/skills/`, `~/.gemini/config/plugins/`)

---

### 2. Struktur Penyimpanan Konteks & Memory (`brain/`)

Setiap sesi kerja atau project memiliki folder memori khusus berbasis UUID di bawah direktori `brain/`:

```text
~/.gemini/antigravity/brain/<PROJECT_OR_CONVERSATION_ID>/
├── task.md                     # Daftar task, progress, dan status eksekusi
├── implementation_plan.md      # Rencana arsitektur dan langkah kerja agent
├── walkthrough.md              # Ringkasan hasil kerja dan verifikasi
├── scratch/                    # Temporary scratchpad (script tes, output diagnostik)
└── .system_generated/
    └── logs/
        └── transcript.jsonl    # Log interaksi lengkap (prompt, tool calls, error)

```

* **Artifacts (`.md`):** File Markdown kanonikal yang dibaca-tulis oleh agent secara mandiri untuk menjaga *long-context reasoning* sepanjang percakapan.
* **Transcripts (`transcript.jsonl`):** Berisi rekaman *step-by-step* interaksi antara user, model, dan pemanggilan tool dalam format JSON Lines yang efisien token.

---

### 3. Penyimpanan Riwayat Percakapan (Conversations)

* **Binary Session State (`.pb`):**
IDE menyimpan state percakapan lengkap dalam format Protocol Buffer di:
`~/.gemini/antigravity/conversations/*.pb`
* **CLI Session Index (`history.jsonl`):**
Untuk `agy cli`, daftar indeks seluruh sesi yang pernah dibuat (ID, timestamp, judul) dicatat di:
`~/.gemini/antigravity-cli/history.jsonl`

---

### 4. Konteks Level Proyek (Workspace Scope)

Selain direktori global, Antigravity membaca konteks lokal langsung dari root folder repository proyek yang sedang dibuka:

* `.agent/skills/` atau `.gemini/`: Menyimpan *Agent Skills*, custom instructions, dan rules khusus repositori tersebut.
* `mcp_config.json`: Konfigurasi koneksi MCP server (disimpan di `~/.gemini/antigravity/mcp_config.json` atau di level workspace).

---

### Relevansi untuk Central Second Brain

Jika ingin mengintegrasikan riwayat Antigravity/AGY ke dalam **Obsidian / Central Hub di Jarvis Server**:

1. Buat ingestion daemon yang memantau file `~/.gemini/antigravity/brain/**/transcript.jsonl` dan `*.md`.
2. Ekstrak ringkasan solusi, task log, atau code snippet dari file tersebut, lalu simpan otomatis ke folder `90_Agent_Inbox/` di Obsidian Vault.