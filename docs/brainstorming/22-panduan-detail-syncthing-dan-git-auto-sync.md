# 22. Panduan Mendalam: Mekanisme Sinkronisasi Syncthing & Git Auto-Sync

Dokumen ini membedah secara teknis dan praktis cara kerja, alur setup, penanganan konflik, serta kombinasi terbaik dari dua metode sinkronisasi utama untuk Obsidian & Central Brain Hub: **Syncthing (P2P Real-time)** dan **Git Auto-Sync (Versioned Backup)**.

---

## 1. Syncthing: Sinkronisasi P2P Real-Time (Tanpa Cloud Pihak Ketiga)

### A. Cara Kerja Syncthing di Balik Layar
**Syncthing** adalah aplikasi sinkronisasi berkas *peer-to-peer* (P2P) open-source yang aman dan terdesentralisasi:

```
[ Laptop Pribadi ]  ◄──(P2P Block-Level Sync via Tailscale)──►  [ Homeserver Jarvis ]
         ▲                                                              ▲
         │                                                              │
         └──────────(P2P Block-Level Sync)──────────► [ Laptop Kantor ]
```

1. **Continuous Event-Driven Watcher:**
   Begitu Anda atau AI Agent menyimpan file `.md` di laptop, OS memicu event perubahan $\rightarrow$ Syncthing langsung mendeteksinya dalam waktu <0.5 detik.
2. **Block-Level Delta Transfer:**
   Jika Anda hanya mengubah 1 paragraf pada file catatan yang besar, Syncthing hanya mengirim beberapa byte blok yang berubah saja (sangat hemat bandwidth).
3. **End-to-End TLS Encryption:**
   Data ditransmisikan langsung antar device melalui jaringan privat **Tailscale** tanpa pernah singgah di server pihak ketiga.

---

### B. Langkah Setup Praktis Syncthing

1. **Install Syncthing:**
   * Di Windows: Download [Syncthing Windows](https://syncthing.net) atau `winget install Syncthing.Syncthing` (tersedia juga GUI tray app: *SyncTrayzor*).
   * Di Server Linux: Jalankan via Docker atau `apt install syncthing`.
   * Di Android: Install dari Google Play Store / F-Droid.
2. **Pairing Antar Device:**
   * Buka Web GUI Syncthing (`http://localhost:8384`).
   * Scan Device ID atau masukkan ID device server/laptop Anda.
3. **Bagikan Folder Vault Obsidian:**
   * Klik **"Add Folder"** $\rightarrow$ Pilih path folder vault Anda (misal `E:/MyVault`).
   * Centang device penerima yang ingin disinkronkan.
4. **Konfigurasi `.stignore` (File yang Tidak Perlu Disinkron):**
   Buat file `.stignore` di root vault agar Syncthing tidak menyinkronkan file cache lokal yang tidak perlu:
   ```text
   .brain_data/
   .git/
   .obsidian/workspace.json
   .obsidian/workspace-mobile.json
   ```

---

### C. Bagaimana Syncthing Menangani Konflik Edit?
* Jika Laptop A dan Laptop B mengedit file yang sama secara bersamaan saat offline, Syncthing tidak akan menimpa data Anda secara brutal.
* Syncthing menyimpan file versi terbaru dan membuat file cadangan bernama:
  `catatan_proyek.sync-conflict-20260829-120000-LAPTOP.md`
* **Di `devbrain`:** Karena kita menggunakan arsitektur **Append-Only UUID Partitioning** (`90_Agent_Inbox/{device-id}_{uuid}.md`), AI Agent antar device tidak pernah menimpa file yang sama, sehingga **konflik sync 100% dieliminasi secara otomatis**.

---

## 2. Git Auto-Sync: Pencatatan Riwayat & Jaring Pengaman (Version Control)

### A. Cara Kerja Git Auto-Sync
Git bekerja bukan hanya sebagai sinkronisasi, melainkan sebagai **buku kas sejarah (*Audit Trail Ledger*)** dari seluruh evolusi pengetahuan Anda.

```
[ Folder Vault ] ──(Auto-Commit tiap 10 menit)──► [ Git Repository Lokal ] ──(Auto-Push)──► [ Private GitHub / GitLab ]
```

---

### B. Dua Cara Mengaktifkan Git Auto-Sync

#### Opsi 1: Menggunakan Plugin Obsidian `obsidian-git` (Paling Populer & Mudah)
1. Di Obsidian: Buka **Settings $\rightarrow$ Community Plugins $\rightarrow$ Cari "Obsidian Git" $\rightarrow$ Install & Enable**.
2. **Pengaturan Otomatis:**
   * **Vault backup interval:** `10` (Artinya otomatis auto-commit & push setiap 10 menit).
   * **Auto Pull on Startup:** Aktifkan (Otomatis menarik catatan terbaru saat Obsidian dibuka).
   * **Commit Message Format:** `vault backup: %datetime%`

#### Opsi 2: Menggunakan Background Script / Cron di Server Jarvis
Jika di server tidak ada aplikasi Obsidian, server cukup menjalankan script bash sederhana via cron atau `devbrain backup`:
```bash
#!/bin/bash
cd /opt/second-brain/vault
git add -A
if ! git diff-index --quiet HEAD; then
    git commit -m "auto-backup: $(date '+%Y-%m-%d %H:%M:%S')"
    git push origin master
fi
```

---

### C. Keunggulan Unik Git Auto-Sync:
1. **Time Machine (Riwayat Revisi Tak Terbatas):**
   Jika seminggu kemudian Anda menyadari bahwa sebuah catatan penting terhapus atau salah diedit oleh AI Agent, Anda tinggal membuka *Git History* dan me-restore file tersebut dalam 1 klik.
2. **Cloud Backup Gratis & Privat:**
   Disimpan aman di private repository GitHub / GitLab.

---

## 3. Komparasi Head-to-Head: Syncthing vs Git Auto-Sync

| Fitur / Karakteristik | **Syncthing** | **Git Auto-Sync** |
| :--- | :--- | :--- |
| **Kecepatan Sinkronisasi** | 🟢 **Instan (<1 detik, live P2P)** | 🟡 Terjadwal (tiap 5–15 menit). |
| **Ketergantungan Internet** | 🟢 Bisa full offline via WiFi/LAN lokal. | 🟡 Butuh koneksi internet ke GitHub. |
| **Riwayat Versi / Revert** | 🟡 Terbatas (hanya backup conflict). | 🟢 **Sempurna (Full Git Commit History)**. |
| **Kemudahan di HP / Android** | 🟢 Sangat mudah (aplikasi Syncthing resmi). | 🟡 Butuh setup SSH key / personal token. |
| **Penanganan Konflik** | Otomatis buat file `.sync-conflict`. | Perlu git merge jika ada tabrakan commit. |

---

## 4. Arsitektur Kombinasi Terbaik (*The Ultimate Hybrid Workflow*)

Untuk mendapatkan kecepatan sinkronisasi instan sekaligus keamanan backup abadi, kita menggabungkan keduanya:

```
┌────────────────────────────────────────────────────────────────────────┐
│               THE PERFECT HYBRID SYNC & BACKUP STRATEGY                │
│                                                                        │
│  1. SINKRONISASI AKTIF (SYNCTHING OVER TAILSCALE):                     │
│     * Menghubungkan Laptop OMEN ◄──► Laptop Kantor ◄──► Server Jarvis  │
│     * Perubahan catatan tersinkronisasi dalam 0.5 detik.              │
│                                                                        │
│  2. JARING PENGAMAN PASIF (GIT AUTO-BACKUP DI SERVER):                 │
│     * Hanya Server Jarvis yang menjalankan `git auto-commit & push`    │
│       ke Private GitHub setiap jam 00:00 malam.                        │
│     * Laptop klien TIDAK PERLU repot mikir git merge / push!          │
└────────────────────────────────────────────────────────────────────────┘
```

Dengan strategi ini:
* Di laptop, Anda dan AI Agent merasakan pengalaman yang **sangat cepat dan mulus tanpa jeda**.
* Di server, data Anda **terbackup otomatis ke GitHub dengan aman setiap hari**.
