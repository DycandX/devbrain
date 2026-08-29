# 🧪 Panduan Demo & Development Mode `devbrain`

Dokumen ini berisi panduan **eksekusi langsung (*copy-pasteable*)** untuk mendemokan dan menguji seluruh fitur `devbrain` (`v1.2.0-alpha`) di lingkungan lokal / development.

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
# Inisialisasi vault demo
python -m devbrain.cli.main init "E:/_PROJECT/_Central AI Brain Hub/demo_vault"
```

---

### 2. Cek Status & Kesehatan Vault
Melihat metrik catatan, direktori yang terindeks, dan status konfigurasi:
```bash
python -m devbrain.cli.main status --vault "E:/_PROJECT/_Central AI Brain Hub/demo_vault"
```

---

### 3. Targeted Single Ingest: Ingest 1 Projek Koding Tertentu
Menginspeksi manifest dan meng-auto-seed kartu projek ke `10_Projects/`:
```bash
# Opsi A: Preview hasil inspeksi (Dry-Run)
python -m devbrain.cli.main ingest project "E:/_PROJECT/_Central AI Brain Hub" --dry-run --vault "E:/_PROJECT/_Central AI Brain Hub/demo_vault"

# Opsi B: Tulis kartu projek langsung ke dalam vault
python -m devbrain.cli.main ingest project "E:/_PROJECT/_Central AI Brain Hub" --vault "E:/_PROJECT/_Central AI Brain Hub/demo_vault"
```

---

### 4. Batch Scan Seluruh Workspace: Scan Semua Repo di Folder `_PROJECT`
Memindai seluruh repositori lokal dan mengklasifikasikan secara otomatis:
```bash
# Opsi A: Preview daftar repo yang terdeteksi
python -m devbrain.cli.main ingest projects --dir "E:/_PROJECT" --dry-run --vault "E:/_PROJECT/_Central AI Brain Hub/demo_vault"

# Opsi B: Batch ingest seluruh repositori lokal ke vault
python -m devbrain.cli.main ingest projects --dir "E:/_PROJECT" --vault "E:/_PROJECT/_Central AI Brain Hub/demo_vault"
```

---

### 5. Ingest Sesi AI & Hubungkan Graf (Auto-Entity Linker)
Menyerap sesi koding Google Antigravity & Claude Code, menyaring secret/API key, dan menyisipkan `[[Wikilinks]]`:
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

### 👁️ 9. Melihat Hasil Visual di Obsidian:

1. Buka folder `E:/_PROJECT/_Central AI Brain Hub/demo_vault` sebagai Vault di aplikasi **Obsidian**.
2. **Graph View (`Ctrl + G`):**
   * Lihat bagaimana seluruh catatan saling terhubung (simpul projek `_Central_AI_Brain_Hub` dikelilingi oleh sesi koding AI).
3. **Buka file `10_Projects/_Central_AI_Brain_Hub/README.md`:**
   * Lihat tabel **Dataview dinamis** yang secara otomatis menampilkan daftar riwayat sesi AI yang baru saja di-ingest!
