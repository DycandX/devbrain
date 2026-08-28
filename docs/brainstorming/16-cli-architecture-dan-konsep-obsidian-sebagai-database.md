# 16. Konsep Obsidian sebagai Document Database & Desain CLI Interface (`npm` / `pip`)

Dokumen ini membedah hakikat sebenarnya dari **Obsidian**, bagaimana Obsidian bertindak sebagai **Document Database yang ramah manusia dan AI**, serta merancang arsitektur **CLI Tool (NPM / Python)** untuk inisialisasi, konfigurasi, backup, dan manajemen central brain secara praktis.

---

## 1. Apa Itu Obsidian Sebenarnya? (Dalam Penggunaan Normal)

Dalam penggunaan sehari-hari oleh jutaan pengguna di dunia:
* **Obsidian** adalah **aplikasi pencatat (*note-taking*) dan manajemen pengetahuan (*Personal Knowledge Management / Second Brain*)**.
* **Keunikan Utama Obsidian:**
  1. **100% Local & Markdown Murni:** Semua catatan disimpan sebagai file `.md` biasa di harddisk laptop Anda. Tidak ada database biner tertutup, tidak ada lock-in perusahaan, dan bisa dibuka di Notepad/VS Code kapan saja.
  2. **Bi-directional Linking (`[[Wikilinks]]`):** Anda bisa menghubungkan Catatan A ke Catatan B.
  3. **Graph View:** Menampilkan visualisasi jaring laba-laba interaktif yang memperlihatkan bagaimana semua topik dan ide Anda saling berhubungan.
  4. **Ekosistem Plugin:** Ribuan plugin komunitas (seperti Dataview, Canvas, Kanban).

---

## 2. Di Sini, Obsidian Bertindak sebagai "Document Database": Bagaimana Konsepnya?

Dalam proyek **Central AI Brain Hub**, kita memanfaatkan filosofi **"File-over-App"**:

> **Folder Vault Obsidian adalah DATABASE DOKUMEN kita.**
> * **Manusia** melihatnya sebagai antarmuka visual grafis (Obsidian UI).
> * **AI Agent** melihatnya sebagai basis data pengetahuan terstruktur (via FastMCP).

```
┌────────────────────────────────────────────────────────────────────────┐
│              ANALOGI: OBSIDIAN SEBAGAI DOCUMENT DATABASE               │
├────────────────────────────────┬───────────────────────────────────────┤
│ Konsep Database Tradisional    │ Ekuivalen di Obsidian Vault           │
├────────────────────────────────┼───────────────────────────────────────┤
│ Table / Collection             │ Folder (misal: `10_Projects/`, `20_K`)│
│ Row / Record / Document        │ File `.md` (misal: `auth_jwt.md`)     │
│ Schema / Column Attributes     │ YAML Frontmatter di awal file `.md`   │
│ Foreign Key / Graph Relations  │ `[[Wikilinks]]` (relasi antar note)   │
│ SQL Query / Filter View        │ Plugin Dataview (`TABLE WHERE...`)    │
│ Search Index                   │ Vector DB (Qdrant) + BM25             │
└────────────────────────────────┴───────────────────────────────────────┘
```

### Mengapa Ini Jauh Lebih Unggul dari Database Biasa (SQL/NoSQL)?
* Jika menggunakan database SQL murni, Anda **tidak bisa membuka dan membaca catatan secara visual** tanpa aplikasi admin khusus.
* Dengan Obsidian sebagai database dokumen, **Anda bisa mengedit isi catatan dengan santai di laptop**, dan perubahan itu **detik itu juga langsung dimengerti oleh AI Agent**!

---

## 3. Bentuk Program: Desain CLI Universal (`devbrain` / `npm` / `pip`)

Untuk membuat instalasi dan pengoperasian menjadi **super instan (Zero-Friction)**, program Central Brain Hub dibungkus dalam bentuk **CLI Tool Universal** bernama: `devbrain` (atau `central-brain`).

Pengguna cukup menginstalnya melalui `npm` atau `pip`:
```bash
# Opsi 1: Jalankan langsung via NPX (Node.js)
npx devbrain init

# Opsi 2: Install via Pip / UV (Python)
pip install devbrain-cli
```

---

## 4. Daftar Perintah CLI (`devbrain` Commands Specification)

CLI ini dirancang dengan perintah-perintah yang sangat intuitif dan otomatis:

```text
devbrain [command] [options]

COMMANDS UTAMA:
  init [path]         Inisialisasi vault baru atau attach ke vault lama secara interaktif
  start / serve       Menjalankan background indexer & MCP server (Stdio / SSE)
  status              Menampilkan status vault, jumlah catatan terindeks, dan status AI
  index [--reindex]   Memaksa pembaruan indeks vector & BM25 seluruh catatan
  search <query>      Mencari catatan langsung dari terminal menggunakan Hybrid Search
  backup [create/res] Membuat cadangan arsip terenkripsi atau restore dari snapshot
  skill [list/add]    Manajemen Agent Skills di folder 00_System/Agent_Skills/
  config [get/set]    Melihat atau mengubah konfigurasi (port, embedding, scope)
```

---

### Contoh Alur Kerja Perintah CLI

#### 1. Inisialisasi Vault (`devbrain init`)
Menjalankan wizard ramah di terminal:
```text
$ npx devbrain init
? Masukkan lokasi folder Obsidian Vault: E:/MyVault
? Pilih Mode Embedding:
  ❯ 1. Local CPU FastEmbed (100% Offline, Gratis, Tanpa GPU) [Recommended]
    2. Cloud API (Google Gemini / OpenAI)
    3. Ollama Local Server
? Apakah ingin membuat folder template default (00_System, 10_Projects, dll)? (Y/n): Y
? Masukkan Device Name: laptop-omen

[SUCCESS] Vault terhubung! Konfigurasi disimpan di E:/MyVault/.brainrc.json
[INFO] Daftarkan endpoint MCP ke Antigravity IDE di ~/.gemini/antigravity/mcp_config.json
```

#### 2. Menjalankan Server & Background Watcher (`devbrain start`)
```text
$ devbrain start
[READY] Central Brain Hub aktif!
├── Vault Path: E:/MyVault (124 Catatan terindeks)
├── Hybrid Search Engine: LanceDB Vector + BM25 Active
├── MCP Protocol: Stdio & SSE (http://127.0.0.1:8000/sse)
└── Watcher: Aktif memantau perubahan file .md
```

#### 3. Pencarian Cepat via Terminal (`devbrain search`)
```text
$ devbrain search "JWT refresh token rotation"
Hasil Ditemukan (Skor Relevansi: 0.94):
1. [20_Knowledge/Bug_Solutions/jwt_rotation.md] (Score: 0.94)
   "Gunakan in-memory Redis blacklist saat me-revoke refresh token..."
2. [30_Decisions/ADR-004-jwt-auth.md] (Score: 0.88)
```

#### 4. Backup & Snapshot Otomatis (`devbrain backup`)
```bash
# Membuat snapshot cadangan instan
devbrain backup create --output "E:/Backups/brain_2026-08-29.zip"

# Restore dari snapshot lama jika terjadi kesalahan
devbrain backup restore --from "E:/Backups/brain_2026-08-29.zip"
```

---

## 5. Struktur Konfigurasi (`.brainrc.json` / `brain.config.yaml`)

File konfigurasi disimpan di root vault atau direktori user (`~/.brainrc.json`), mendukung konfigurasi manual maupun otomatis:

```json
{
  "version": "1.0",
  "device_id": "laptop-omen",
  "scope": "all",
  "vault_path": "E:/MyCentralBrainVault",
  "embedding": {
    "provider": "fastembed",
    "model": "bge-small-en-v1.5"
  },
  "vector_store": {
    "engine": "lancedb",
    "storage_path": "./.brain_data"
  },
  "mcp": {
    "transport": "sse",
    "port": 8000,
    "auth_token": "env:BRAIN_AUTH_TOKEN"
  },
  "watcher": {
    "auto_index": true,
    "debounce_ms": 1000,
    "ignore_patterns": [".git/**", "Pribadi/**", ".obsidian/**"]
  }
}
```

---

## 6. Kesimpulan

Dengan membungkus seluruh arsitektur ke dalam **Universal CLI (`devbrain`)**:
1. **Instalasi Zero-Ribet:** Pengguna cukup jalankan `npx devbrain init`.
2. **Obsidian Menjadi UI Visual:** Pengguna tetap menikmati pengalaman mencatat dan visualisasi grafik di Obsidian.
3. **AI Agent Memiliki Standard Interface:** Semua AI Agent langsung terhubung melalui satu perintah dan satu format protokol MCP.
