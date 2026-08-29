# 🧪 Panduan Demo & Development Mode `devbrain`

Dokumen ini berisi panduan **eksekusi langsung (*copy-pasteable*)** untuk mendemokan dan menguji seluruh fitur `devbrain` (`v1.4.0-alpha`) di lingkungan lokal / development.

---

## ⚡ Cara 1: Mengaktifkan Command Global `devbrain` (Direkomendasikan)

Jika Anda ingin perintah `devbrain` bisa dipanggil langsung dari terminal mana saja tanpa awalan `python -m`:

1. Buka terminal di folder repository ini (`E:\_PROJECT\_Central AI Brain Hub`):
2. Jalankan perintah instalasi mode editable (*development link*):
   ```bash
   pip install -e .
   ```
3. Setelah selesai, cek apakah perintah `devbrain` sudah aktif:
   ```bash
   devbrain --version
   ```

---

## 🛠️ Cara 2: Menjalankan Mode Python Module (`python -m devbrain.cli.main`)

Jika Anda belum menjalankan `pip install -e .` atau ingin menjalankan langsung dari source code, gunakan format:

> **Format Dasar:**  
> `python -m devbrain.cli.main <perintah> [opsi...]`  
> *(Jalankan perintah di bawah dari direktori `E:\_PROJECT\_Central AI Brain Hub`)*

---

## 🚀 Skenario Pengujian Fitur Lengkap (Step-by-Step)

### 1. Inisialisasi Demo Vault
Membuat struktur vault Obsidian baru lengkap dengan 7 folder standar:
```bash
python -m devbrain.cli.main init "E:/_PROJECT/_Central AI Brain Hub/demo_vault"
```

---

### 2. Cek Status & Kesehatan Vault
Melihat metrik catatan, direktori yang terindeks, dan status konfigurasi:
```bash
python -m devbrain.cli.main status --vault "E:/_PROJECT/_Central AI Brain Hub/demo_vault"
```

---

### 3. Unified Ingest: Ingest 1 Projek Koding atau Repo Panduan (Otomatis & Fleksibel!)
Format baru sangat toleran. Anda bisa memasukkan path langsung atau memakai `--dir`:

```bash
# Ingest projek koding Python
python -m devbrain.cli.main ingest "E:/_PROJECT/_Central AI Brain Hub" --vault "E:/_PROJECT/_Central AI Brain Hub/demo_vault"

# Ingest repo panduan Markdown (menggunakan flag --dir)
python -m devbrain.cli.main ingest --dir "E:/_PROJECT/_TEST/HowToBeAProgrammer" --vault "E:/_PROJECT/_Central AI Brain Hub/demo_vault"
```

---

### 4. Unified Ingest: Ingest Folder Induk (Container Workspace)
Jika Anda memasukkan folder induk yang berisi beberapa sub-projek, sistem otomatis memindai semuanya:

```bash
# Otomatis memindai semua sub-projek di dalam _fxmedia
python -m devbrain.cli.main ingest "E:/_PROJECT/_fxmedia" --vault "E:/_PROJECT/_Central AI Brain Hub/demo_vault"
```

---

### 5. Ingest Sesi AI & Hubungkan Graf (Auto-Entity Linker)
Tanpa argumen path, `devbrain ingest` otomatis memanen sesi koding Antigravity & Claude Code:

```bash
# Opsi A: Preview sesi yang terdeteksi (Dry-Run)
python -m devbrain.cli.main ingest --dry-run --vault "E:/_PROJECT/_Central AI Brain Hub/demo_vault"

# Opsi B: Ingest sesi dan tautkan relasi graf projek & timeline harian
python -m devbrain.cli.main ingest --vault "E:/_PROJECT/_Central AI Brain Hub/demo_vault"
```

---

### 6. Full Ingestion Sekaligus (`ingest all`)
Menjalankan siklus penuh: **Scan repo lokal + Panen sesi AI + Sinkronisasi graf**:
```bash
python -m devbrain.cli.main ingest all --vault "E:/_PROJECT/_Central AI Brain Hub/demo_vault"
```

---

### 7. Pengujian Hybrid Search (FastEmbed + BM25)
Mencari pengetahuan di dalam vault menggunakan gabungan pencarian semantik dan kata kunci:
```bash
# Pencarian query semantik
python -m devbrain.cli.main search "FastMCP protocol gateway and memory tools" --vault "E:/_PROJECT/_Central AI Brain Hub/demo_vault"

# Pencarian arsitektur
python -m devbrain.cli.main search "manifest parser and project harvester" --vault "E:/_PROJECT/_Central AI Brain Hub/demo_vault"
```

---

### 8. Manajemen Agent Skills
Melihat dan membuat skill agen modular di `00_System/Agent_Skills/`:
```bash
# Menampilkan daftar skill yang terpasang
python -m devbrain.cli.main skill list --vault "E:/_PROJECT/_Central AI Brain Hub/demo_vault"

# Membuat template skill baru
python -m devbrain.cli.main skill add "my-docker-skill" --description "Panduan deploy docker" --vault "E:/_PROJECT/_Central AI Brain Hub/demo_vault"
```

---

### 👁️ 9. Melihat Hasil Visual & 1-Click IDE Launch di Obsidian:

1. Buka folder `E:/_PROJECT/_Central AI Brain Hub/demo_vault` sebagai Vault di aplikasi **Obsidian**.
2. **Buka file `10_Projects/_Central_AI_Brain_Hub/README.md`:**
   * Klik tautan **`[🚀 Open in IDE (VS Code / Antigravity)]`** $\rightarrow$ Projek fisik langsung terbuka di editor IDE Anda!
   * Lihat pohon direktori **ASCII Tree** yang bersih dari `node_modules` / `venv`.
   * Lihat tabel **Dataview dinamis** yang menampilkan riwayat sesi AI.
3. **Graph View (`Ctrl + G`):**
   * Lihat graf pengetahuan yang padat dan saling terhubung tanpa ada simpul terisolasi (*zero orphan nodes*).
