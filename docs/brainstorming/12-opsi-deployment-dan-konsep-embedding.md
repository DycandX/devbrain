# 12. Opsi Deployment Fleksibel & Penjelasan Konsep Embedding

Dokumen ini mengklarifikasi konsep **Embedding (Vektor)**, kebutuhan resource (Lokal vs Cloud API), serta menyediakan **3 Mode Deployment** mulai dari setup paling instan di 1 laptop pribadi hingga arsitektur full homeserver.

---

## 1. Memahami Konsep "Embedding": Apa, Untuk Apa, & Butuh Apa?

### A. Apa itu Embedding?
**Embedding** adalah proses matematis untuk menerjemahkan teks (catatan, kode, solusi bug) menjadi deretan angka vektor (misal: 768 angka desimal).

* **Teks Biasa:** `"Cara rotasi JWT refresh token pada FastAPI"`
* **Hasil Vektor:** `[0.024, -0.118, 0.452, ..., -0.091]`

### B. Untuk Apa Embedding Digunakan?
Embedding digunakan untuk **Semantic Search (Pencarian Berdasarkan Makna)** di Vector DB, bukan sekadar mencocokkan kata kunci (*keyword matching*):
* Jika Anda mencari: *"mengatasi koneksi websocket terputus"*
* Pencarian keyword biasa (Ctrl+F) akan **gagal** jika catatan Anda berjudul *"Handling Socket Hangup in ASGI"*.
* **Semantic Search (Vector Search)** dapat mengenali bahwa kedua frasa tersebut memiliki **makna konsep yang sama** dan langsung mengembalikan catatan tersebut ke AI Agent.

### C. Apakah Membutuhkan LLM Lokal yang Berat (GPU Mahal)?
**TIDAK.** Ini adalah kesalahpahaman umum.
* Model LLM untuk *Chat/Reasoning* (seperti Llama-3-70B) memang membutuhkan RAM/VRAM besar.
* Namun **Model Embedding** (seperti `bge-small`, `bge-m3`, `all-MiniLM-L6-v2`) berukuran **SANGAT KECIL (~80MB – 400MB)**.
* Model embedding berjalan sangat cepat di **CPU laptop standar** tanpa membutuhkan GPU sama sekali.

---

## 2. Pilihan Mesin Embedding: Local vs Cloud API

Sistem ini didesain **Pluggable (Bebas Dipilih via `.env`)**:

| Metode Embedding | Cara Kerja & Setup | Kelebihan | Kekurangan |
| :--- | :--- | :--- | :--- |
| **Opsi 1: Cloud API (OpenAI / Gemini)** | Cukup masukkan `OPENAI_API_KEY` atau `GEMINI_API_KEY` di file `.env`. | - **Setup 0 detik** (tidak perlu install apapun).<br>- Sangat akurat & cepat.<br>- Biaya sangat murah ($0.02 untuk ratusan ribu kata). | Membutuhkan koneksi internet dan API key. |
| **Opsi 2: In-Process Python (`fastembed`)** *(Recommended)* | Berjalan langsung di dalam script Python via ONNX Runtime CPU. | - **100% Offline & Gratis**.<br>- **Tanpa install Ollama/Docker**.<br>- Sangat hemat RAM (~150MB). | Menggunakan sedikit komputasi CPU saat mengindeks file baru. |
| **Opsi 3: Ollama Server** | Menjalankan container/service Ollama lokal (`ollama pull bge-m3`). | - Bisa dipakai bersama untuk LLM lokal lain.<br>- Terisolasi di server Jarvis. | Perlu menjalankan service daemon Ollama. |

---

## 3. Tiga Mode Deployment (Dari 1 Laptop Pribadi hingga Homeserver)

Untuk memastikan setup **TIDAK RIBET**, sistem dirancang dengan 3 profil deployment:

```
┌────────────────────────────────────────────────────────────────────────┐
│               PROFIL 1: STANDALONE (1 LAPTOP PRIBADI)                  │
│       - Zero Docker, Zero Server, Zero Ribet                           │
│       - Obsidian Vault Lokal + Embedded Vector DB (LanceDB/Chroma)     │
│       - FastMCP dijalankan via script python / stdio                   │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ (Scale up jika butuh)
┌────────────────────────────────────────────────────────────────────────┐
│             PROFIL 2: MULTI-LAPTOP SYNC (PEER-TO-PEER)                 │
│       - Vault disinkronkan antar laptop via Syncthing / Git            │
│       - Masing-masing laptop menjalankan local embedded memory         │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ (Scale up ke 24/7 Hub)
┌────────────────────────────────────────────────────────────────────────┐
│             PROFIL 3: DEDICATED HOMESERVER (JARVIS SSOT)               │
│       - Docker Compose di Jarvis (Qdrant + FastMCP SSE)                │
│       - Seluruh device terhubung via Tailscale Private VPN             │
└────────────────────────────────────────────────────────────────────────┘
```

---

### Profil 1: Standalone (1 Laptop Pribadi - Super Ringan & Cepat)
Cocok jika Anda hanya ingin menggunakannya di 1 laptop kerja/pribadi tanpa setup server:

* **Struktur File:**
  ```text
  My-Obsidian-Vault/
  ├── .brain_data/           # Embedded vector database (otomatis terbuat)
  ├── 00_System/
  ├── 10_Projects/
  ├── 20_Knowledge/
  └── 90_Agent_Inbox/
  ```
* **Cara Menjalankan:**
  Cukup 1 perintah di terminal laptop:
  ```bash
  pip install -r requirements.txt
  python run_brain.py --vault "C:/Users/zulvikar/Documents/MyVault"
  ```
* **Koneksi ke Antigravity IDE / Claude Code:**
  Cukup daftarkan di `mcp_config.json` lokal:
  ```json
  {
    "mcpServers": {
      "central-brain": {
        "command": "python",
        "args": ["E:/_PROJECT/_Central AI Brain Hub/run_brain.py", "--vault", "E:/MyVault"]
      }
    }
  }
  ```
* **Keunggulan:** Langsung jalan dalam 2 menit, tanpa Docker, tanpa database server terpisah!

---

### Profil 2: Multi-Laptop Sync (P2P via Syncthing / Git)
Cocok jika punya Laptop Kantor + Laptop Pribadi tanpa server rumah:
1. Folder Vault di-sync menggunakan **Syncthing** antar kedua laptop.
2. Setiap laptop menjalankan Profil 1 secara lokal di background.
3. Karena data `.md` tersinkron secara otomatis, kedua laptop memiliki memori dan catatan yang selalu up-to-date.

---

### Profil 3: Dedicated Homeserver (Jarvis 24/7 Hub)
Cocok untuk setup jangka panjang yang selalu *standby* di rumah:
* Menggunakan Docker Compose (Qdrant + FastMCP SSE over Tailscale) seperti yang dijelaskan di dokumen [08-server-stack-jarvis-dan-fastmcp.md](./08-server-stack-jarvis-dan-fastmcp.md).

---

## 4. Rekomendasi Alur Implementasi

1. **Mulai dari Profil 1 (Standalone):** Buat versi script Python lokal yang membaca folder Obsidian dan menggunakan embedded vector (`fastembed` + `LanceDB`/`ChromaDB`) agar Anda bisa langsung merasakan manfaatnya di laptop hari ini.
2. **Upgrade ke Profil 2/3 (Multi-Device):** Saat Anda ingin menghubungkan laptop kantor atau homeserver Jarvis, tinggal aktifkan mode SSE / Syncthing tanpa perlu mengubah struktur catatan Obsidian Anda.
