# 18. Alur Onboarding di Laptop Pribadi & Strategi Alur Development (`npm link` / Editable Mode)

Dokumen ini membedah dua hal praktis:
1. **Langkah demi langkah (*End-to-End Walkthrough*) saat Anda pertama kali mengaktifkan Central Brain di laptop pribadi.**
2. **Alur development (*Development Workflow*): Mengapa tidak perlu ribet build/publish ke NPM saat masih tahap coding, dan bagaimana teknik `npm link` / `pip -e` membuat proses development instan tanpa jeda waktu build.**

---

## 1. Alur Menjalankan di Laptop Pribadi (User Onboarding Flow)

Bagaimana urutan langkah jika Anda ingin langsung memakainya di laptop pribadi hari ini?

```
┌──────────────────────────────────────────────────────────────────────────┐
│              5 LANGKAH MUDAH DI LAPTOP PRIBADI (HANYA 3 MENIT)           │
│                                                                          │
│  [ Langkah 1 ] Download & Install Obsidian (Sekali saja)                 │
│  [ Langkah 2 ] Jalankan `devbrain init` (Pilih folder & mode embedding)  │
│  [ Langkah 3 ] Buka folder tersebut di aplikasi Obsidian                 │
│  [ Langkah 4 ] Jalankan `devbrain start` (MCP Hub aktif)                 │
│  [ Langkah 5 ] Buka Antigravity IDE / Claude (Langsung terhubung!)       │
└──────────────────────────────────────────────────────────────────────────┘
```

### Langkah Detail:
1. **Install Obsidian:**
   Download gratis dari [obsidian.md](https://obsidian.md) (atau via terminal Windows: `winget install Obsidian.Obsidian`).
2. **Inisialisasi Central Brain:**
   Buka terminal di laptop Anda, jalankan:
   ```bash
   devbrain init E:/MyDevBrainVault
   ```
   Sistem otomatis membuat struktur folder rapi (`00_System/`, `10_Projects/`, `20_Knowledge/`, `90_Agent_Inbox/`).
3. **Buka di Obsidian:**
   Buka Obsidian $\rightarrow$ Klik **"Open folder as vault"** $\rightarrow$ Pilih `E:/MyDevBrainVault`.
4. **Jalankan Background Engine:**
   ```bash
   devbrain start
   ```
5. **Mulai Bekerja dengan AI:**
   Buka Antigravity IDE. Tanyakan ke agent: *"Cek context proyek saya di Central Brain"*. Agent langsung membaca catatan Anda di Obsidian!

---

## 2. Alur Development: Apakah Ribet Jika Dijadikan Package? Build-nya Lama?

> **JAWABAN: TIDAK RIBET & BUILD-NYA INSTAN (<1 DETIK)!**

### Kesalahan Pemula vs Cara Developer Profesional:
* **Cara yang Salah (Ribet):** Setiap kali mengubah 1 baris kode, harus build ulang, naikkan versi, lalu publish ke registry npm/pip publik. Ini sangat lambat dan membuang waktu.
* **Cara Profesional (Local Link / Editable Mode):** Selama masa development, kita bekerja secara **LOKAL PENUH** menggunakan fitur **`npm link`** (Node.js) atau **`pip install -e .`** (Python).

---

## 3. Rahasia Development Cepat: `npm link` / `pip editable`

Dengan teknik ini, perintah `devbrain` langsung terdaftar di terminal laptop Anda dan mengarah ke folder source code proyek ini (`E:\_PROJECT\_Central AI Brain Hub`):

```
                                  [ TERMINAL DI MANA SAJA ]
                                      Ketik: `devbrain init`
                                                │
                                                ▼ (Symlink Instan)
[ Folder Proyek Kita: E:\_PROJECT\_Central AI Brain Hub\src\... ]
```

### Keuntungan Luar Biasa:
1. **Zero Waiting Time (0 Detik Build):**
   Saat Anda mengubah file kode di VS Code / Antigravity IDE $\rightarrow$ perubahan langsung aktif seketika saat Anda mengetik `devbrain` di terminal tanpa perlu build ulang!
2. **Tidak Perlu Akun / Publish ke NPM Dulu:**
   Kita baru mem-publish ke registry publik (NPM / PyPI) nanti ketika seluruh fitur sudah 100% matang, stabil, dan teruji.
3. **Hot Reloading saat Development:**
   Untuk Web UI Dashboard, kita menggunakan Vite / Next.js / FastAPI Hot-Reload sehingga perubahan tampilan UI langsung ter-refresh otomatis di browser.

---

## 4. Rencana Tahapan Eksekusi Development (Sprint Plan)

Untuk membangun proyek ini secara terstruktur dan cepat:

```text
[ SPRINT 1: Core Engine & Vault Scaffolder ]
├── Membuat CLI runner (`devbrain init` & `devbrain status`)
├── Logika auto-scaffolding folder vault template standar
└── Pembaca konfigurasi `.brainrc.json`

[ SPRINT 2: Hybrid Search & Vault Indexer ]
├── Mengadopsi FastEmbed & Qdrant/LanceDB dari riset _fxmedia
├── Script BM25 statistical search untuk kode & exact keyword
└── File watcher (Inotify/Watchdog) untuk mendeteksi perubahan file .md

[ SPRINT 3: FastMCP Gateway Server ]
├── Endpoint MCP Stdio & SSE (Port 8000)
├── Tools MCP: `search_brain`, `get_project_context`, `write_agent_log`, `load_skill`
└── Auto-register ke Antigravity IDE (~/.gemini/antigravity/mcp_config.json)

[ SPRINT 4: Multi-Device Connect & Web UI Inspector ]
├── Perintah CLI `devbrain connect <url>`
├── Web UI Dashboard sederhana (Glassmorphism RAG inspector)
└── Uji coba multi-device via Tailscale
```

---

## 5. Kesimpulan

1. **Pengalaman Pengguna (UX):** Sangat mudah — cukup install Obsidian sekali, lalu jalankan `devbrain init`.
2. **Pengalaman Developer (DX):** Sangat cepat — kita develop menggunakan *Local Editable Mode* sehingga setiap perubahan kode bisa langsung dites dalam hitungan detik tanpa hambatan build/packaging.
