# 40. Panduan Praktis Sinkronisasi Obsidian: Windows & Mobile (Android / iOS) dengan Ekosistem DevBrain

| Metadata | Nilai |
| :--- | :--- |
| **Topik** | Metode Sinkronisasi Obsidian Windows ke Mobile, Komparasi Opsi (Remotely Save vs Syncthing vs Git), Integrasi DevBrain & Aturan Ignore Machine Layer |
| **Status** | 💡 Brainstorming & Practical Guide |
| **Referensi** | [21-metode-sync-obsidian-dan-prosedur-uninstall-bersih.md](./21-metode-sync-obsidian-dan-prosedur-uninstall-bersih.md), [22-panduan-detail-syncthing-dan-git-auto-sync.md](./22-panduan-detail-syncthing-dan-git-auto-sync.md), [39.md](./39.md) |
| **Tanggal** | 2026-08-30 |

---

## 1. Hubungan Sinkronisasi Mobile dengan Sistem DevBrain

Saat menghubungkan Obsidian di **Windows (Laptop/PC)** ke **Mobile (Android / iPhone)**, ada 2 layer data di dalam Vault:

```text
               ┌─────────────────────────────────────────┐
               │         OBSIDIAN VAULT DEVBRAIN         │
               ├─────────────────────────────────────────┤
               │ 📄 HUMAN LAYER (WAJIB DISYNC KE HP):   │
               │   • 00_System/ (Preferences & Prompts)  │
               │   • 10_Projects/ (Project Cards & Wiki) │
               │   • 20_Knowledge/ (Catatan & Guides)    │
               │   • 30_Decisions/ (Architecture ADRs)   │
               │   • 90_Agent_Inbox/ (Session Logs)      │
               │   • .obsidian/ (Plugin & Theme Settings)│
               ├─────────────────────────────────────────┤
               │ ⚙️ MACHINE LAYER (JANGAN DISYNC KE HP):  │
               │   • .brain_data/ (SQLite & ONNX Vector) │
               │   • demo_vault/ (Temporary Sandbox)     │
               └─────────────────────────────────────────┘
```

> **Aturan Emas:**
> Di HP kita hanya membaca dan mencatat Markdown secara visual. File binary mesin (`.brain_data/`) tidak perlu disinkronkan ke HP agar hemat kuota & storage.

---

## 2. Komparasi 4 Metode Sinkronisasi Windows $\leftrightarrow$ Mobile

| Metode Sync | Biaya | Kelebihan | Kekurangan | Rekomendasi Penggunaan |
| :--- | :--- | :--- | :--- | :--- |
| **1. Remotely Save (Plugin)** | 🆓 Gratis | **Paling Praktis.** Tidak butuh install aplikasi tambahan di HP. Sync langsung via Google Drive/OneDrive/Dropbox. | Sync berjalan saat Obsidian dibuka. | 🏆 **Paling Cocok untuk Pemula (Simpel & Cepat)** |
| **2. Syncthing (P2P)** | 🆓 Gratis | **Super Cepat & Real-time.** Sinkronisasi lokal tanpa lewat cloud pihak ketiga, 100% privat. | Butuh install app Syncthing di Windows & Syncthing-Fork di Android. | 🚀 **Paling Cocok untuk Power User & Offline Sync** |
| **3. Obsidian Git** | 🆓 Gratis | Riwayat versi komplit (commit & rollback) di GitHub. | Setup di HP sedikit lebih teknis dibanding Remotely Save. | 💻 Cocok untuk developer murni |
| **4. Obsidian Sync (Official)** | 💲 Berbayar | 1-Click login resmi, enkripsi end-to-end. | Berbayar bulanan ($4 - $8/bln). | Bagi yang ingin serba otomatis berbayar |

---

## 3. Panduan Langkah Praktis: Cara Paling Mudah (Metode Remotely Save)

Jika Anda ingin cara **paling mudah tanpa install aplikasi lain di HP**, gunakan plugin **Remotely Save**:

```text
[ Obsidian Windows ] ──(Sync)──► [ OneDrive / Google Drive ] ──(Sync)──► [ Obsidian Android / iOS ]
```

### Langkah di Windows:
1. Buka Obsidian di Laptop $\rightarrow$ Masuk ke **Settings (Ikon Gir)** $\rightarrow$ **Community plugins** $\rightarrow$ Matikan *Restricted mode*.
2. Klik **Browse** $\rightarrow$ Cari plugin **Remotely Save** $\rightarrow$ Klik **Install** lalu **Enable**.
3. Buka menu pengaturan **Remotely Save**:
   * Pilih Cloud Service: **OneDrive** (atau **Google Drive / Dropbox / WebDAV**).
   * Klik tombol **Auth** untuk menghubungkan akun cloud Anda.
   * Aktifkan:
     * Toggle **Sync on Startup** (Sync otomatis saat buka Obsidian).
     * Toggle **Auto Run** (misal tiap 5 atau 10 menit).
4. Klik ikon panah melingkar di bilah kiri Obsidian untuk melakukan upload sync pertama.

### Langkah di Mobile (Android / iPhone):
1. Buka aplikasi **Obsidian** di HP $\rightarrow$ Pilih **Create new vault** (Beri nama sama, misal `DevBrain`, simpan di folder lokal Documents HP).
2. Di Obsidian HP, masuk ke **Settings** $\rightarrow$ **Community plugins** $\rightarrow$ Install & aktifkan **Remotely Save**.
3. Hubungkan ke akun cloud yang sama (OneDrive / Google Drive).
4. Tekan tombol **Sync** $\rightarrow$ Seluruh catatan proyek, knowledge base, dan log AI dari laptop Anda akan otomatis ter-download ke HP!

---

## 4. Panduan Alternatif: Metode Syncthing (Real-Time P2P Lokal)

Jika Anda tidak ingin data catatan melewati cloud (100% lokal & privat):

1. **Di Windows:** Install **Syncthing** (atau SyncTrayzor).
2. **Di Android:** Install aplikasi **Syncthing-Fork** dari Google Play Store / F-Droid.
3. **Hubungkan Perangkat:** Scan QR code Device ID antara Laptop dan HP.
4. **Share Folder Vault:**
   * Di Windows Syncthing: Tambahkan folder Vault DevBrain sebagai *Shared Folder*.
   * Di tab *Ignore Patterns*, masukkan:
     ```text
     .brain_data
     .git
     ```
   * Di HP: Buka Syncthing-Fork $\rightarrow$ Terima shared folder tersebut dan arahkan ke folder vault di HP.
5. Catatan akan tersinkronisasi seketika (< 1 detik) setiap kali ada perubahan file saat laptop dan HP berada di jaringan Wi-Fi yang sama (atau via Tailscale).

---

## 5. Ringkasan Rekomendasi

* **Jika ingin yang paling santai tanpa pusing:** Pakai **Metode 1 (Remotely Save via OneDrive/Google Drive)**.
* **Jika ingin privasi 100% dan instan di jaringan rumah:** Pakai **Metode 2 (Syncthing-Fork)**.
