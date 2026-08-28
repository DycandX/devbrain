# 21. Metode Sinkronisasi Obsidian Antar Device & Prosedur Uninstall Bersih

Dokumen ini membedah dua hal penting seputar operasional jangka panjang:
1. **Pilihan lengkap metode sinkronisasi Obsidian antar perangkat (Laptop Pribadi, Laptop Kantor, Server, & HP/Mobile).**
2. **Prosedur *Clean Uninstall* / Penghapusan `devbrain` tanpa merusak catatan Markdown milik pengguna.**

---

## 1. Pilihan Metode Sinkronisasi Obsidian Lintas Device (*Sync Across Devices*)

Karena data Obsidian adalah file teks Markdown biasa di folder lokal, Anda memiliki **kebebasan penuh 100% (Zero Lock-In)** untuk memilih cara sinkronisasi:

```
┌────────────────────────────────────────────────────────────────────────┐
│             OPSI SINKRONISASI OBSIDIAN ACROSS DEVICES                  │
├──────────────────────┬─────────────────────────────────────────────────┤
│ Metode Sync          │ Karakteristik & Rekomendasi                     │
├──────────────────────┼─────────────────────────────────────────────────┤
│ 1. Syncthing (P2P)   │ 🟢 **Rekomendasi Utama (Gratis, Cepat, P2P)**:  │
│    (via Tailscale)   │ Sinkronisasi sub-detik antar Laptop, Server, dan│
│                      │ Android secara private tanpa server pihak ke-3. │
├──────────────────────┼─────────────────────────────────────────────────┤
│ 2. Git Auto-Sync     │ 🟢 **Audit Trail Terbaik (Gratis)**:            │
│    (Plugin / Cron)   │ Menggunakan GitHub/GitLab private repo. Memiliki│
│                      │ riwayat versi lengkap jika ada salah hapus note.│
├──────────────────────┼─────────────────────────────────────────────────┤
│ 3. Self-Hosted       │ 🟡 **Real-time Live Sync (CouchDB)**:           │
│    LiveSync          │ Sinkronisasi level karakter/kata secara live,   │
│                      │ mendukung iOS, Android, Windows, Mac, Linux.    │
├──────────────────────┼─────────────────────────────────────────────────┤
│ 4. Official Obsidian │ 🟡 **Paling Praktis (Berbayar $4–$8/bulan)**:   │
│    Sync              │ Layanan cloud resmi Obsidian terenkripsi E2EE,  │
│                      │ setup 1-klik di semua perangkat termasuk iPhone.│
├──────────────────────┼─────────────────────────────────────────────────┤
│ 5. Cloud Drive       │ ⚠️ **Kurang Direkomendasikan untuk Multi-Agent**:│
│    (iCloud/GDrive)   │ Sering memicu file locking & duplicate conflict │
│                      │ saat AI menulis file dengan cepat.              │
└──────────────────────┴─────────────────────────────────────────────────┘
```

### Rekomendasi Setup Terbaik untuk Ekosistem `devbrain`:
1. **Untuk Sinkronisasi Utama:** Gunakan **Syncthing** yang berjalan di atas **Tailscale**. Sangat ringan, gratis selamanya, dan file langsung tereplikasi secara instan dalam hitungan milidetik saat Anda mengedit catatan.
2. **Untuk Safety Net / Backup:** Pasang auto-commit **Git** di server Jarvis sekali sehari.

---

## 2. Prosedur Uninstall & Pembersihan `devbrain` (*Clean Teardown*)

Bagaimana jika di kemudian hari pengguna ingin menghapus `devbrain` dari laptop atau servernya?

> **PRINSIP DASAR: CATATAN OBSIDIAN ANDA ADALAH MILIK ANDA 100%.**
> Menghapus `devbrain` **TIDAK AKAN PERNAH** menghapus file catatan Markdown (`.md`), ide, atau dokumen proyek Anda.

---

### A. Perintah Otomatis: `devbrain uninstall` / `devbrain purge`

CLI `devbrain` dilengkapi perintah *self-cleanup* yang ramah dan interaktif:

```text
$ devbrain uninstall

? Apakah Anda yakin ingin mencabut integrasi devbrain dari sistem ini? (Y/n): Y

[CLEANUP ACTIONS]
✔ Menghapus registrasi MCP dari Antigravity IDE (~/.gemini/antigravity/mcp_config.json)
✔ Menghapus registrasi MCP dari Claude Code (~/.claude.json)
✔ Mencabut symlink Agent Skills di ~/.gemini/config/skills/
✔ Menghentikan background service daemon devbrain
? Hapus cache database vektor (.brain_data/ & .brainrc.json)? (Y/n): Y
✔ Cache index vektor berhasil dibersihkan!

[CATATAN PENTING]
Seluruh file catatan Markdown Anda di folder vault TETAP AMAN dan TIDAK DISENTUH.
Untuk menghapus CLI package secara permanen, jalankan:
  npm uninstall -g devbrain   (atau: pip uninstall devbrain)
```

---

### B. Prosedur Manual (Jika Ingin Hapus Tanpa CLI)

Jika pengguna ingin menghapus semuanya secara manual tanpa menjalankan perintah CLI:

1. **Hapus Folder Cache & Config di Vault:**
   Hapus folder hidden `.brain_data/` dan file `.brainrc.json` di dalam folder vault. (Semua file `.md` lainnya tetap utuh).
2. **Hapus Konfigurasi MCP di AI Client:**
   Buka `~/.gemini/antigravity/mcp_config.json` atau `~/.claude.json`, lalu hapus blok `"central-brain"`.
3. **Hapus Package CLI:**
   ```bash
   npm uninstall -g devbrain  # atau: pip uninstall devbrain
   ```
4. **Hasil:** Laptop Anda kembali bersih 100% seperti semula tanpa meninggalkan jejak atau *orphan files*.

---

## 3. Kesimpulan

1. **Sinkronisasi Fleksibel:** Anda bebas menggunakan Syncthing, Git, atau Cloud Drive sesuai preferensi device (Android/iOS/PC).
2. **Zero Risk & Zero Lock-In:** Catatan Anda adalah file teks biasa. Anda bisa memasang `devbrain` kapan saja dan menghapusnya kapan saja tanpa khawatir kehilangan catatan berharga Anda.
