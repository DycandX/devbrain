# 10. Security, Privacy & Boundary Protocol (Work vs Personal)

Karena Central Brain Hub ini akan menghubungkan **Laptop Kantor**, **Laptop Pribadi**, dan **Jarvis Homeserver**, faktor privasi, kepatuhan data kerja (work compliance), dan proteksi rahasia (secrets/API keys) harus dirancang sejak awal.

---

## 1. Isolasi Data Kerja vs Pribadi (Work-Personal Isolation)

Terdapat dua strategi utama untuk memisahkan data sensitif kantor dari proyek pribadi:

### Strategi 1: Folder-Level Tagging & Selective Filtering (Recommended)
Semua tetap dalam satu vault terpusat, namun dikelompokkan dengan ketat:
* `10_Projects/Work/`: Hanya disinkronkan atau hanya diakses saat session berlabel `#work`.
* `10_Projects/Personal/`: Proyek riset dan personal.
* **Qdrant Metadata Filter:** Saat agent di laptop kantor melakukan query, filter payload `environment: "work"` diterapkan secara otomatis.

### Strategi 2: Multi-Vault / Selective Syncthing
* **Laptop Kantor:** Hanya menyinkronkan folder `Work/` dan `00_System/Rules/`.
* **Laptop Pribadi & Jarvis:** Menyinkronkan seluruh vault.

---

## 2. Automatic Secret & PII Sanitizer (Pembersih Kunci Rahasia)

AI Agent seringkali membaca file `.env` atau token saat melakukan debugging. Sebelum data disimpan ke Obsidian atau Vector DB, **Harvester & MCP Gateway WAJIB menjalankan Sanitizer Pipeline**:

```
[ Raw Transcript / Agent Output ]
                │
                ▼
      [ Regex Secret Redactor ]
  - API Keys (OpenAI `sk-...`, AWS `AKIA...`, GitHub `ghp_...`)
  - Private Keys (`-----BEGIN RSA PRIVATE KEY-----`)
  - JWT Tokens (`ey...`)
  - Password strings (`password=...`, `DB_PASS=...`)
                │
                ▼ (Replaced with `[REDACTED_SECRET]`)
[ Sanitized Output ] ──► [ Obsidian Vault & Qdrant ]
```

---

## 3. Network Security & Tailscale Access Control (ACL)

1. **Zero Public Ingress:** Server Jarvis tidak memiliki IP publik terbuka dan tidak memerlukan port forwarding di router rumah.
2. **Tailscale Device Authentication:** Hanya perangkat yang di-approve di dashboard Tailscale yang dapat mengirim paket ke IP `jarvis.tailnet`.
3. **Tailscale ACL Policy (Contoh):**
```json
{
  "acls": [
    // Izinkan semua laptop mengakses port MCP (8000) dan Syncthing (8384) di Jarvis
    {
      "action": "accept",
      "src": ["group:dev-devices"],
      "dst": ["tag:jarvis-server:8000", "tag:jarvis-server:8384"]
    }
  ]
}
```

---

## 4. Strategi Disaster Recovery & Backup

Untuk mencegah kehilangan catatan akibat kesalahan operasi agent atau kerusakan harddisk di Jarvis:

1. **Local Git Snapshot (Di Server):** Script cron di Jarvis menjalankan `git add . && git commit -m "Auto snapshot: $(date)"` setiap 6 jam.
2. **Encrypted Offsite Backup:** Backup folder `/vault` dan snapshot Qdrant secara terenkripsi ke cloud storage (Google Drive / S3 / Backblaze B2) menggunakan **Rclone** atau **Restic** sekali seminggu.
