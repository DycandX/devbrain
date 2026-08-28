# 14. Panduan Implementasi Praktis & Cara Kerja Koneksi Obsidian

Dokumen ini memberikan jawaban gamblang, praktis, dan bebas istilah rumit mengenai **bagaimana sistem ini sebenarnya bekerja di dunia nyata**, program apa saja yang perlu dibuat, serta bagaimana Obsidian terhubung dengan AI Agent dan Server.

---

## 1. Inti Konsep: Apa Sebenarnya Central AI Brain Hub?

Secara sederhana, sistem ini adalah **jembatan dua arah antara Manusia (melalui catatan Markdown) dan AI Agent (melalui protokol MCP & Vector Search)**.

* **Bagi Manusia:** Ini adalah **Obsidian Vault** biasa berisi kumpulan folder dan file Markdown (`.md`) tempat Anda mencatat proyek, membaca ringkasan sesi AI, dan melihat grafik relasi.
* **Bagi AI Agent (Antigravity, Claude Code, Hermes, dll.):** Ini adalah **Central API / MCP Server** tempat mereka bisa bertanya (*"bagaimana pola auth di proyek ini?"*), membaca rules, dan menitipkan catatan solusi bug baru.

```
┌──────────────────────────────────────────────────────────────────────────┐
│                            CARA KERJA UTAMA                              │
│                                                                          │
│   [ Manusia / Anda ]                        [ AI Agent (Antigravity) ]   │
│          │                                               │               │
│     (Buka UI)                                     (Panggil MCP)          │
│          ▼                                               ▼               │
│   ┌──────────────┐                             ┌───────────────────┐     │
│   │ Obsidian App │                             │ Central Brain Hub │     │
│   │ (GUI Visual) │                             │   (Python / MCP)  │     │
│   └──────┬───────┘                             └─────────┬─────────┘     │
│          │                                               │               │
│          ▼                                               ▼               │
│   ════════════════════════════════════════════════════════════════════   │
│   FOLDER VAULT BERSAMA (File System: E:/MyCentralBrainVault/*.md)        │
│   ════════════════════════════════════════════════════════════════════   │
│                                  │                                       │
│                                  ▼                                       │
│                       [ Watcher & Vector DB ]                            │
│                  (Otomatis mengindeks isi Markdown)                      │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Program Apa Saja yang Sebenarnya Kita Buat?

Kita tidak membuat aplikasi GUI baru dari nol (karena UI sudah ditangani oleh Obsidian). Kita hanya membuat **3 modul backend Python yang sangat ringan**:

### Modul 1: `mcp_brain_server.py` (Protocol Gateway)
* **Fungsi:** Server FastMCP yang menyediakan tools untuk AI Agent.
* **Tools yang disediakan:**
  * `search_brain(query)`: Melakukan hybrid search (Qdrant + BM25) ke seluruh isi vault.
  * `get_project_context(project_name)`: Mengambil file PRD & arsitektur proyek.
  * `write_agent_log(title, content, tags)`: Menulis file Markdown baru ke folder `90_Agent_Inbox/`.
  * `load_skill(skill_name)`: Mengambil instruksi `SKILL.md` dari `00_System/Agent_Skills/`.

### Modul 2: `vault_indexer.py` (Watcher & Hybrid Engine)
* **Fungsi:** Daemon background yang memantau folder vault.
* **Cara Kerja:** Setiap kali Anda atau Agent membuat/mengubah file `.md`, script ini otomatis memecah teks menjadi potongan kecil (*chunks*), membuat vektor (*FastEmbed/bge-m3*), dan meng-upsert ke Qdrant/LanceDB & indeks BM25.

### Modul 3: `session_harvester.py` (Local Auto-Distiller)
* **Fungsi:** Script lokal di laptop yang memantau riwayat sesi Antigravity (`~/.gemini/antigravity/brain/`) atau Claude Code.
* **Cara Kerja:** Saat sesi selesai, ia otomatis meringkas keputusan teknis dan menyimpannya sebagai file `.md` di `90_Agent_Inbox/` di Obsidian.

---

## 3. Bagaimana Cara Menghubungkan Obsidian dengan Program Central Brain?

**Keduanya terhubung secara alami melalui SISTEM FOLDER (File System yang Sama).** Tidak perlu plugin aneh atau konfigurasi rumit:

1. Anda membuat satu folder di laptop, misalnya: `E:/MyBrainVault/`.
2. Buka aplikasi **Obsidian** $\rightarrow$ pilih **"Open folder as vault"** $\rightarrow$ arahkan ke `E:/MyBrainVault/`.
3. Jalankan script **Central Brain Hub** dengan menunjuk ke folder yang sama:
   `python mcp_brain_server.py --vault "E:/MyBrainVault"`
4. **Hasilnya:**
   * Jika Anda mengetik catatan baru di Obsidian $\rightarrow$ script Central Brain langsung mengindeksnya agar bisa dicari oleh AI.
   * Jika AI Agent menulis solusi bug via MCP $\rightarrow$ file `.md` baru langsung muncul di Obsidian Anda detik itu juga!

---

## 4. Apakah Harus Install Obsidian Dulu? Apa Saja Persiapannya?

### Di Laptop Anda (Client / User Device):
1. **Install Obsidian:** Ya, download dari [obsidian.md](https://obsidian.md/) (gratis untuk penggunaan personal). Ini dipakai di laptop pribadi/kerja Anda untuk melihat dan mengelola catatan.
2. **Install Python (3.10+):** Untuk menjalankan script backend `mcp_brain_server.py`.
3. **Plugin Obsidian yang Direkomendasikan (Opsional):**
   * **Dataview Plugin:** Agar bisa membuat tabel rekap otomatis aktivitas agent di dashboard.

---

## 5. Untuk di Server (Homeserver Jarvis), Apakah Harus Install Obsidian Juga?

> **JAWABAN: TIDAK PERLU SAMA SEKALI!**

### Mengapa Tidak Perlu Obsidian di Server?
* Obsidian adalah **aplikasi tampilan visual (GUI)** untuk manusia, sedangkan server beroperasi secara *headless* (tanpa layar/monitor).
* Di Server Jarvis / VPS, vault Obsidian **hanyalah sebuah folder direktori biasa** di Linux (contoh: `/opt/second-brain/vault/`).

### Apa Saja yang Berjalan di Server?
Hanya service backend ringan via Docker:
1. **Container Qdrant:** Database vektor.
2. **Container FastMCP Server:** Menjalankan script Python backend (Port 8000).
3. **Container Syncthing:** Menjaga agar folder `/opt/second-brain/vault/` di server selalu sama persis (tersinkron real-time) dengan folder `E:/MyBrainVault/` di laptop Anda.

---

## 6. Ringkasan Alur Operasional Harian

1. **Pagi hari di Laptop:** Anda membuka Obsidian, membuat rencana kerja di `10_Projects/Project-A/tasks.md`.
2. **Siang hari saat Coding:** Anda membuka Antigravity IDE. Agent Antigravity otomatis membaca rules dan tasks dari Central Brain melalui MCP.
3. **Selesai Coding:** Solusi arsitektur yang dibuat Antigravity otomatis tersimpan ke `90_Agent_Inbox/antigravity/` di Obsidian.
4. **Malam hari di Rumah:** Anda membuka Obsidian (di laptop pribadi atau mobile), melihat semua rekap pekerjaan yang rapi, dan menghubungkannya dengan `[[Wikilinks]]`.
