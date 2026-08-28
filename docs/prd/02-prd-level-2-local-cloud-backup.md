# Product Requirements Document (PRD) - Level 2: Local + Cloud Backup

| Attribute | Detail |
| :--- | :--- |
| **Product Name** | `devbrain` (Central AI Brain Hub) |
| **Tier / Level** | **Level 2: Local + Automated Cloud Backup & Version History** |
| **Status** | Approved for Implementation |
| **Target Release** | Version 1.1.0 |
| **Prerequisites** | Level 1 (Standalone Local Core) |
| **Author** | Antigravity AI Engineering Team |

---

## 1. Ringkasan Eksekutif & Visi Produk

**Level 2: Local + Cloud Backup** dibangun di atas fondasi Level 1 dengan menambahkan lapisan **Jaring Pengaman & Riwayat Revisi Abadi (*Disaster Recovery & Version Control*)**. 

Tujuan utama Level 2 adalah:
1. Menjamin **Zero Data Loss**: Jika laptop pengguna hilang, rusak, atau terkena malware, seluruh catatan dan memori AI dapat dipulihkan dalam 1 perintah.
2. Menyediakan **Time Machine (Audit Trail)**: Pengguna dapat melihat riwayat perubahan catatan dari hari ke hari dan membatalkan (*revert*) perubahan jika AI Agent salah mengedit file.
3. Menjaga data tetap aman dengan **Regex Secret Redactor** sebelum data di-push ke cloud repository privat.

---

## 2. Target Pengguna & User Persona

* **Persona:** Software Engineer yang menggunakan Central Brain di laptop lokal, namun menginginkan rasa aman (*peace of mind*) bahwa catatannya ter-backup secara otomatis ke cloud privat (GitHub / GitLab / Cloud Archive).
* **Pain Point:** Khawatir harddisk laptop rusak, atau AI Agent secara tidak sengaja menimpa konten catatan penting.
* **Goal:** Otomatisasi backup berkala tanpa perlu mengetik perintah git manual setiap hari.

---

## 3. Diagram Arsitektur Level 2

```
┌────────────────────────────────────────────────────────────────────────┐
│                          LAPTOP PENGGUNA (LOCAL)                       │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    CORE LEVEL 1 (STANDALONE ENGINE)              │  │
│  │  - FastMCP Stdio Server + Local Hybrid Search (LanceDB + BM25)   │  │
│  │  - Local Obsidian Vault (00_System, 10_Projects, 90_Inbox, dll)  │  │
│  └──────────────────────────────────┬───────────────────────────────┘  │
│                                     │                                  │
│                                     ▼                                  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │               LEVEL 2 EXTENSION: BACKUP & REVISION ENGINE        │  │
│  │  - Secret Sanitizer : Regex Redactor (Filter API Keys & Passwords│  │
│  │  - Snapshot Engine  : Zip Compressor + AES-256 Encryption        │  │
│  │  - Git Auto-Sync    : Scheduled Inkremental Commit & Push        │  │
│  └──────────────────┬───────────────────────────────┬───────────────┘  │
└─────────────────────┼───────────────────────────────┼──────────────────┘
                      │ (Encrypted Archive)           │ (Git Push over HTTPS/SSH)
                      ▼                               ▼
     ┌────────────────────────────────┐   ┌──────────────────────────────┐
     │   Local / Cloud Backup Drive   │   │  Private GitHub / GitLab     │
     │   (Google Drive / Local Disk)  │   │  (Version History / Revert)  │
     └────────────────────────────────┘   └──────────────────────────────┘
```

---

## 4. Spesifikasi Kebutuhan Fungsional (*Functional Requirements*)

### FR-1: Snapshot Backup Engine (`devbrain backup create`)
* **FR-1.1:** CLI dapat membuat arsip snapshot terkompresi (`.zip` / `.tar.gz`) dari seluruh isi vault.
* **FR-1.2:** Metadata konfigurasi dan indeks vektor otomatis diikutsertakan agar saat di-restore tidak perlu re-indexing dari nol.
* **FR-1.3:** Opsi proteksi password / enkripsi AES-256 untuk snapshot sensitif (`--encrypt`).
* **FR-1.4:** Snapshot disimpan di folder `~/.devbrain/backups/` atau path kustom.

### FR-2: Fast Disaster Recovery (`devbrain backup restore`)
* **FR-2.1:** Pengguna dapat memulihkan seluruh catatan dan konfigurasi vault dari file arsip snapshot:
  ```bash
  devbrain backup restore --from my-vault-backup-2026-08-29.zip --target E:/RestoredVault
  ```
* **FR-2.2:** Melakukan validasi integritas checksum sebelum proses ekstraksi dimulai.

### FR-3: Automated Git Sync Engine (`devbrain backup sync`)
* **FR-3.1:** CLI dapat menginisialisasi repository Git lokal pada folder vault (`git init`) dan menghubungkannya ke remote URL privat.
* **FR-3.2:** Fitur **Auto-Commit & Auto-Push** yang dapat berjalan secara terjadwal (misal: setiap 30 menit atau saat sesi coding selesai).
* **FR-3.3:** Kompatibel penuh dengan plugin Obsidian populer **`obsidian-git`** (pengguna bisa memilih menggunakan Git via CLI `devbrain` atau via plugin Obsidian).

### FR-4: Secret Sanitizer & Privacy Boundary (Redactor)
* **FR-4.1:** Sebelum melakukan commit Git atau membuat snapshot, sistem menjalankan pemindaian Regex otomatis untuk mendeteksi data sensitif:
  * API Keys (OpenAI `sk-...`, Anthropic `sk-ant-...`, Google `AIza...`)
  * JWT Tokens, Private Keys (`-----BEGIN RSA PRIVATE KEY-----`)
  * Password dan string koneksi database.
* **FR-4.2:** String rahasia otomatis disensor menjadi `[REDACTED_API_KEY]` sebelum di-push ke remote repository.

---

## 5. Kebutuhan Non-Fungsional (*Non-Functional Requirements*)

| Parameter | Target Spesifikasi |
| :--- | :--- |
| **Waktu Backup Snapshot** | < 3 detik untuk vault berisi 2.000 file Markdown. |
| **Overhead CPU/RAM** | Proses backup berjalan di background thread dengan prioritas rendah (*low priority process*). |
| **Keamanan Kredensial** | SSH Key / Personal Access Token disimpan di OS Keychain lokal (bukan hardcoded). |
| **Integritas Data** | Zero corrupted files — jika terjadi error saat kompresi, operasi di-rollback. |

---

## 6. Spesifikasi Perintah CLI Level 2

```text
devbrain backup create [--encrypt] [--output <path>]  # Membuat snapshot cadangan ZIP
devbrain backup restore --from <archive.zip>          # Restore vault dari snapshot lama
devbrain backup list                                  # Melihat daftar snapshot lokal yang tersedia
devbrain backup sync [--remote <url>]                 # Memicu sync commit & push ke Git remote
devbrain backup status                                # Cek status repo Git (uncommitted changes, sync delay)
```

---

## 7. Kriteria Keberhasilan & Skenario Pengujian (*Acceptance Criteria*)

1. **Skenario 1 (Snapshot & Disaster Recovery):**
   * Pengguna menjalankan `devbrain backup create`.
   * File `.zip` terverifikasi utuh.
   * Folder vault sengaja dihapus, lalu dipulihkan dengan `devbrain backup restore`.
   * Seluruh catatan, struktur folder, dan konfigurasi kembali 100% seperti semula.
2. **Skenario 2 (Secret Sanitization):**
   * Catatan berisi API Key Google dimasukkan ke vault.
   * Saat `devbrain backup sync` berjalan, API Key disensor menjadi `[REDACTED_API_KEY]` di commit log Git remote.
