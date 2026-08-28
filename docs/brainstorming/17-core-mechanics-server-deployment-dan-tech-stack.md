# 17. Core Mechanics, Server Deployment, Multi-Device Connect & Pemilihan Tech Stack

Dokumen ini mengklarifikasi secara detail mengenai struktur fisik Obsidian, mekanisme deployment server via CLI, cara menghubungkan antar device, kegunaan Web UI Dashboard, alur wizard konfigurasi, serta komparasi bahasa pemrograman terbaik untuk **`devbrain`**.

---

## 1. Apakah Data Obsidian Murni Hanya Struktur Folder & File `.md`?

> **JAWABAN: YA, 100% BENAR.**

Di dalam harddisk Anda, sebuah "Vault Obsidian" secara fisik hanyalah:
```text
My-Obsidian-Vault/
├── .obsidian/               # Folder tersembunyi (hanya setting tema, hotkey & plugin UI)
├── 00_System/               # Folder biasa
│   ├── rules.md             # File teks biasa
│   └── Agent_Skills/
├── 10_Projects/             # Folder biasa
│   └── project_a.md         # File teks biasa
└── 20_Knowledge/            # File teks biasa
```

* Tidak ada format file binary aneh.
* Jika Anda membuka file-file tersebut menggunakan **Notepad**, **VS Code**, atau terminal `cat`, isinya adalah teks Markdown biasa.
* Obsidian hanyalah aplikasi antarmuka grafis yang bertugas merender teks Markdown tersebut agar terlihat indah (tabel, grafis, checkbox, link, gambar).

---

## 2. Bagaimana Cara Deploy `devbrain` di Server (Jarvis / VPS)?

Karena `devbrain` adalah CLI package, menjalankannya di server Linux (Homeserver/VPS) sangat sederhana tanpa perlu layar GUI:

### Opsi A: Server Mode via CLI Langsung (`systemd` / background daemon)
```bash
# 1. Install CLI
npm install -g devbrain  # atau: pip install devbrain

# 2. Inisialisasi vault di server
devbrain init /opt/second-brain/vault --server

# 3. Jalankan service server 24/7 (SSE MCP Gateway di port 8000)
devbrain serve --port 8000 --host 0.0.0.0 --auth-token "my-secure-token" --daemon
```

### Opsi B: Docker One-Liner
```bash
docker run -d \
  --name devbrain-hub \
  -p 8000:8000 \
  -v /opt/second-brain/vault:/vault \
  -e AUTH_TOKEN="my-secure-token" \
  devbrain/hub:latest
```

---

## 3. Bagaimana Cara Menghubungkan Device Lain (Laptop Kantor/Pribadi)?

Kita merancang perintah CLI **`devbrain connect`** dan **`devbrain mcp-config`** agar koneksi antar device semudah 1 klik!

```
[ Laptop Klien ] ───(devbrain connect http://jarvis:8000)───► [ Jarvis Server ]
```

### 1. Perintah Sambung Otomatis (`devbrain connect`)
Di laptop kerja atau laptop pribadi, Anda cukup menjalankan:
```bash
devbrain connect http://jarvis.tailnet:8000 --token "my-secure-token"
```
Perintah ini akan:
* Melakukan *handshake ping* ke server Jarvis.
* Memverifikasi token autentikasi.
* Otomatis mendaftarkan endpoint MCP ke Antigravity IDE (`~/.gemini/antigravity/mcp_config.json`) dan Claude Code (`~/.claude.json`) secara instan tanpa Anda harus mengedit JSON manual!

### 2. Status Monitoring Antar Device (`devbrain status`)
```text
$ devbrain status
[STATUS HUB] Terhubung ke: http://jarvis.tailnet:8000
├── Mode: Remote Client (SSE Transport)
├── Latensi: 18ms (via Tailscale)
├── Total Dokumen di Hub: 450 Notes (Terindeks)
└── Integrasi Lokal:
    ├── Antigravity IDE : TERHUBUNG (MCP Active)
    └── Claude Code     : TERHUBUNG (MCP Active)
```

---

## 4. Apakah Perlu Tampilan Web UI (`devbrain dashboard`)?

> **SANGAT BERMANFAAT SEBAGAI PENDAMPING OBSIDIAN.**

Meskipun Obsidian adalah UI utama untuk membaca dan mengedit catatan, memiliki **Web UI Dashboard bawaan (`devbrain ui` / `devbrain dashboard`)** memberikan banyak keuntungan teknis:

```
$ devbrain ui --port 3000
[WEB DASHBOARD] Berjalan di http://localhost:3000
```

### Fitur-Fitur Kunci di Web UI Dashboard:
1. **RAG & Chunk Inspector (Seperti yang Anda buat di `_fxmedia`):**
   * Menguji semantic search secara live di browser.
   * Melihat nilai skor relevansi (*similarity score*) dan potongan chunk dokumen yang dipakai AI.
2. **Multi-Agent Live Telemetry:**
   * Memantau log aktivitas real-time: AI agent mana yang sedang query context, skill apa yang dipanggil, dan catatan apa yang baru saja disimpan.
3. **Quick Browser Access:**
   * Bisa dibuka dari browser HP/Tablet tanpa perlu membuka Obsidian.
4. **Dark Glassmorphism Modern UI:**
   * Menampilkan statistik jumlah dokumen, health check Vector DB, dan status sinkronisasi.

---

## 5. Alur Konfigurasi Awal (`devbrain init` Wizard)

Perintah `devbrain init` bekerja secara interaktif dengan logika cerdas:

```text
$ devbrain init

1. [Lokasi Vault]
   ? Masukkan path folder Obsidian Vault [Default: ~/DevBrainVault]: E:/MyVault

2. [Pilihan Mode Embedding]
   ? Pilih mesin embedding:
     ❯ 1. Local FastEmbed (CPU ONNX, 100% Offline, Gratis, Tanpa GPU) [Default]
       2. Cloud API (Google Gemini / OpenAI)
       3. Ollama Local Server

   >> JIKA MEMILIH CLOUD API:
      ? Masukkan Provider: [Gemini / OpenAI]: Gemini
      ? Masukkan GEMINI_API_KEY: ******************** (Otomatis disimpan di .env aman)

   >> JIKA MEMILIH OLLAMA:
      ? Masukkan URL Host Ollama [Default: http://localhost:11434]: 
      ? Masukkan Model Embedding [Default: bge-m3]: 

3. [Struktur Folder & Scaffolding]
   ? Folder terdeteksi baru/kosong. Buat template folder standar (00_System, 10_Projects, dll)? (Y/n): Y

4. [Device Tag]
   ? Beri nama device ini [Default: laptop-omen]: laptop-omen

[SUCCESS] File konfigurasi .brainrc.json berhasil dibuat!
```

---

## 6. Pemilihan Bahasa Pemrograman: Python vs TypeScript / Node.js

Untuk memastikan sistem **Ringan, Cepat, Andal (*Reliable*), dan Aman**:

### Komparasi Arsitektur:

| Kriteria | **Opsi 1: TypeScript / Node.js** | **Opsi 2: Python (FastAPI + Typer)** |
| :--- | :--- | :--- |
| **Distribusi CLI** | **Sangat Unggul:** Bisa langsung `npx devbrain init` tanpa perlu instalasi Python runtime. | Butuh `pip install` atau `pipx`. |
| **Ekosistem AI / RAG** | Bagus (Transformers.js, LanceDB JS, `@modelcontextprotocol/sdk`). | **Sangat Matang:** Qdrant, FastEmbed, LangChain, BM25 (Rank-BM25), PyMuPDF. |
| **Resource & Kecepatan** | Ringan, startup time sangat instan (<50ms). | Ringan jika menggunakan `FastEmbed` CPU & FastMCP. |
| **Keamanan & Sandboxing** | Sangat aman untuk CLI packaging & cross-platform. | Aman, isolasi dependensi via virtual environment / Docker. |

### Rekomendasi Arsitektur Terbaik:

> **Pendekatan Paling Solid & Elegan:**
> 1. **Core Engine & Server:** Dibangun dengan **Python (FastAPI + FastMCP + FastEmbed / Qdrant + BM25)** karena library pemrosesan dokumen, chunking Markdown, dan semantic search di Python jauh lebih matang dan sudah teruji di proyek `_fxmedia` Anda.
> 2. **CLI Wrapper & Installer:** Dibungkus dalam executable CLI yang rapi (menggunakan **Python `Typer` + `Rich`** untuk tampilan terminal berwarna modern, atau Node.js wrapper) sehingga instalasi dan pengoperasiannya tetap 1 perintah.
