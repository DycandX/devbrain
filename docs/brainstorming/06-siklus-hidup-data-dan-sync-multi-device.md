# 06. Siklus Hidup Data, Conflict Resolution & Multi-Device Sync Architecture

Untuk membangun Central Second Brain yang terhubung ke banyak device (Laptop Pribadi, Laptop Kerja, Jarvis Homeserver, Mobile) dan banyak AI Agent yang bekerja secara simultan, tantangan terbesar bukanlah penyimpanan data, melainkan **sinkronisasi tanpa konflik (conflict-free sync)** dan **integritas data**.

---

## 1. Tantangan Multi-Device & Multi-Agent

Jika Laptop A menjalankan Antigravity IDE, Laptop B menjalankan Claude Code, dan Jarvis Server menjalankan Hermes Agent:
1. **Simultaneous Writes:** Dua agent menulis ke note/file yang sama pada detik yang sama $\rightarrow$ terjadi merge conflict atau file overwrite.
2. **File Locking di Obsidian:** Obsidian mengunci file yang sedang diedit user, sehingga agent yang mencoba menulis via filesystem bisa gagal atau menghasilkan file duplikat (`filename (conflicted copy).md`).
3. **Bandwidth & Latency:** Mengirim seluruh vault bolak-balik setiap detik membebani resource.

---

## 2. Strategi Arsitektur Sinkronisasi: Hybrid Storage & Ingestion

Kita membagi data menjadi dua kategori:
* **Static / Human-Curated Knowledge (Vault Git/Syncthing):** Catatan permanen, dokumentasi arsitektur, panduan proyek.
* **Dynamic / Agent-Generated Stream (Append-Only Event Log):** Sesi percakapan, transkrip, tool outputs, short-term memory.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        LAPTOP / CLIENT DEVICE                          │
│                                                                        │
│  [ Antigravity / Claude / CLI ] ──(Local Session)──► [ Local Memory ]  │
│                 │                                          │           │
│         (Active MCP Call)                           (Auto Watcher)     │
│                 │                                          │           │
└─────────────────┼──────────────────────────────────────────┼───────────┘
                  │                                          │
       Tailscale Private Mesh                     Tailscale HTTPS / SSE
                  │                                          │
                  ▼                                          ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        JARVIS HOMESERVER (SSOT)                        │
│                                                                        │
│  ┌───────────────────────┐                  ┌───────────────────────┐  │
│  │   FastMCP Hub Gateway │                  │ Ingestion / Distiller │  │
│  │ (Read & Write Tools)  │                  │  (Background Worker)  │  │
│  └───────────┬───────────┘                  └───────────┬───────────┘  │
│              │                                          │              │
│              ▼                                          ▼              │
│  ┌───────────────────────┐                  ┌───────────────────────┐  │
│  │      Vector DB        │                  │ Central Obsidian      │  │
│  │   (Qdrant / Mem0)     │                  │ Vault (Filesystem)    │  │
│  └───────────────────────┘                  └───────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Strategi Conflict-Free Multi-Device Sync

### A. Pola "Append-Only & UUID Partitioning" untuk Agent
Agent **DILARANG** mengedit satu file bersama yang sama secara langsung (seperti satu file `notes.md` besar). Sebagai gantinya:
* Setiap sesi agent menulis ke file mandiri berbasis UUID/Timestamp:
  `90_Agent_Inbox/<tool-name>/<YYYY-MM-DD>_<session-uuid>.md`
* File bersifat **Immutable / Append-Only**.
* Karena setiap file memiliki nama unik berdasarkan hash/UUID, Syncthing atau Git **tidak akan pernah mengalami merge conflict**.

### B. Evaluasi Solusi Sinkronisasi Vault

| Metode Sync | Kelebihan | Kekurangan | Rekomendasi |
| :--- | :--- | :--- | :--- |
| **Syncthing** (P2P Mesh via Tailscale) | Real-time (sub-detik), otomatis tanpa commit manual, sangat hemat resource. | Konflik file jika 2 device mengedit baris yang sama persis (menghasilkan file `.sync-conflict`). | **Pilihan Utama** untuk sinkronisasi folder Vault harian. |
| **Git Auto-Sync** (git-sync / cron) | Memiliki riwayat versi lengkap (commit history), mudah di-rollback jika agent merusak file. | Ada jeda waktu (polling interval), perlu penanganan khusus saat terjadi git merge conflict. | **Pilihan Backup / Audit Trail** (Jalankan auto-commit berkala di Jarvis). |
| **Obsidian Self-Hosted LiveSync (CouchDB)** | Native sync Obsidian tingkat baris (operational transformation), support mobile mulus. | Setup CouchDB lebih rumit, agent di luar Obsidian harus menggunakan API CouchDB untuk integrasi. | Opsional jika butuh real-time sync level kata di Obsidian Mobile. |

**Rekomendasi Arsitektur Terbaik:**
1. Gunakan **Syncthing** yang berjalan di atas interface **Tailscale** untuk sinkronisasi folder Vault Obsidian antar Laptop dan Jarvis Server.
2. Di Jarvis Server, pasang script cron Git harian untuk membuat snapshot / commit riwayat sebagai safety net.

---

## 4. Siklus Hidup Data (Data Lifecycle: From Prompt to Permanent Knowledge)

```
[ 1. Execution ]
Agent (Antigravity/Claude Code) mengeksekusi tugas coding di laptop.
Output sesi terekam di local storage (~/.gemini/ atau ~/.claude/).
       │
       ▼
[ 2. Local Harvester / Watcher ]
Daemon ringan di laptop mendeteksi sesi selesai -> mengekstrak ringkasan penting:
- Problem Statement & Solution
- Code Patterns & Decisions
- Architecture Notes
       │
       ▼
[ 3. Vault Ingestion (Obsidian) ]
Disimpan sebagai file markdown terstruktur di folder 90_Agent_Inbox/ di Vault lokal.
Syncthing langsung mereplikasi file ini ke Jarvis Homeserver dalam < 1 detik.
       │
       ▼
[ 4. Server Embeddings & Graph Linking ]
Watcher di Jarvis Homeserver mendeteksi file baru -> memecah chunk ->
mengirim ke Vector DB (Qdrant) & mengekstrak entitas ke Memory Engine (Mem0).
       │
       ▼
[ 5. Knowledge Synthesis (Human-in-the-Loop) ]
User membuka Obsidian di laptop/mobile -> melihat catatan di Inbox ->
Menghubungkan catatan menggunakan [[Wikilinks]] ke Project Utama atau Knowledge Base.
       │
       ▼
[ 6. Universal Retrieval by Next Agent ]
Besoknya, saat agent lain (misal: Hermes Agent di laptop kerja) diberi tugas:
Agent memanggil MCP `search_knowledge("auth middleware patterns")` ->
Langsung mendapatkan context yang dipelajari kemarin!
```

---

## 5. Mekanisme Safe-Writing & Anti-Corrupt

Untuk memastikan AI Agent tidak merusak knowledge base:
1. **Read-Only untuk Dokumen Inti (Default):** Agent secara default hanya diberi izin membaca folder `00_System/`, `10_Projects/`, dan `20_Knowledge/`.
2. **Write-Restricted ke Inbox:** Agent hanya diperbolehkan menulis file baru di folder `90_Agent_Inbox/` atau membuat sub-folder baru di `90_Agent_Inbox/<agent_name>/`.
3. **Atomic Writes:** Setiap proses penulisan file oleh MCP Server menggunakan teknik atomic write (tulis ke file temporary `.tmp` terlebih dahulu, lalu di-rename) untuk menghindari file corrupt saat sync berlangsung.
