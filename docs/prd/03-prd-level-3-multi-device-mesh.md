# Product Requirements Document (PRD) - Level 3: Distributed Multi-Device Mesh

| Attribute | Detail |
| :--- | :--- |
| **Product Name** | `devbrain` (Central AI Brain Hub) |
| **Tier / Level** | **Level 3: Distributed Multi-Device Mesh & 24/7 Central Server** |
| **Status** | Approved for Implementation |
| **Target Release** | Version 2.0.0 |
| **Prerequisites** | Level 1 & Level 2 Core |
| **Author** | Antigravity AI Engineering Team |

---

## 1. Ringkasan Eksekutif & Visi Produk

**Level 3: Distributed Multi-Device Mesh** adalah wujud terlengkap dari visi **Central Second Brain Hub**. Tier ini dirancang khusus untuk skenario *power user* yang memiliki beberapa perangkat aktif (**Laptop Pribadi**, **Laptop Kantor**, **Homeserver Jarvis 24/7**, dan **Smartphone**) dan membutuhkan:

1. **Satu Otak Terpusat (Central Brain SSOT)** yang selalu aktif 24 jam sehari di server rumah (Jarvis).
2. **Sinkronisasi Otomatis Sub-Detik** antar perangkat menggunakan **Syncthing di atas jaringan privat Tailscale**.
3. **Koneksi Remote Instan (`devbrain connect`)** dari IDE di laptop klien ke server tanpa perlu setup jaringan yang rumit.
4. **Web UI Dashboard Bawaan** untuk memantau aktivitas multi-agent secara visual dan menguji pencarian semantik (RAG Chunk Inspector).

---

## 2. Target Pengguna & User Persona

* **Persona:** Power User / Senior Engineer yang bekerja secara fleksibel di banyak device (misal: coding di Laptop Kantor saat siang, lanjut di Laptop Gaming/Pribadi saat malam, sementara server rumah menjalankan bot/agent otomatis).
* **Pain Point:** Konteks pekerjaan terpecah-pecah (*fragmented memory*). Apa yang dipelajari AI di laptop kantor tidak terbawa saat coding di rumah.
* **Goal:** Satu *knowledge base* tunggal yang selalu sinkron dan bisa diakses dari perangkat mana pun secara aman.

---

## 3. Diagram Arsitektur Level 3 (Distributed Mesh Architecture)

```
                       ┌──────────────────────────────────────────────────┐
                       │          HOMESERVER JARVIS (24/7 DAEMON)         │
                       │                                                  │
                       │  ┌────────────────────────────────────────────┐  │
                       │  │   FastMCP Server Gateway (SSE Port 8000)   │  │
                       │  │   - Auth Token Gatekeeper & Scoping        │  │
                       │  │   - Multi-Agent Concurrency Coordinator    │  │
                       │  └──────────────────────┬─────────────────────┘  │
                       │                         │                        │
                       │  ┌──────────────────────┼─────────────────────┐  │
                       │  │   Hybrid Search      │   Web Dashboard     │  │
                       │  │   - Qdrant Docker    │   - Port 3000       │  │
                       │  │   - FastEmbed BGE-m3 │   - RAG Inspector   │  │
                       │  │   - Rank-BM25 Engine │   - Live Telemetry  │  │
                       │  └──────────────────────┴─────────────────────┘  │
                       │                         ▲                        │
                       │  ┌──────────────────────┴─────────────────────┐  │
                       │  │   Central Vault Storage (/opt/vault)       │  │
                       │  │   - Syncthing Node (P2P Listener)          │  │
                       │  │   - Git Auto-Backup Nightly Cron           │  │
                       │  └────────────────────────────────────────────┘  │
                       └─────────────────────────▲────────────────────────┘
                                                 │
                   ┌─────────────────────────────┴────────────────────────────┐
                   │                  TAILSCALE ENCRYPTED MESH                │
                   └──────────────┬───────────────────────────┬───────────────┘
                                  │                           │
          (devbrain connect)      │                           │ (devbrain connect)
                                  ▼                           ▼
        ┌───────────────────────────────────┐       ┌───────────────────────────────────┐
        │       LAPTOP PRIBADI (OMEN)       │       │        LAPTOP KANTOR (WORK)       │
        │                                   │       │                                   │
        │  - Antigravity IDE (Remote MCP)   │       │  - Claude Code / Cursor (Remote)  │
        │  - Obsidian GUI Client            │       │  - Obsidian GUI Client            │
        │  - Syncthing Local Node (Instant) │       │  - Syncthing Local Node (Instant) │
        │  - Scope Filter: `personal, work` │       │  - Scope Filter: `work` (isolated)│
        └───────────────────────────────────┘       └───────────────────────────────────┘
```

---

## 4. Spesifikasi Kebutuhan Fungsional (*Functional Requirements*)

### FR-1: FastMCP SSE Gateway Server (`devbrain serve`)
* **FR-1.1:** Menjalankan MCP Server dengan transport Server-Sent Events (SSE) pada host `0.0.0.0` dan port default `8000`.
* **FR-1.2:** Dilengkapi sistem autentikasi Bearer Token (`--auth-token <secret>`).
* **FR-1.3:** Mendukung ratusan koneksi AI agent secara simultan (*concurrent connection handling*).
* **FR-1.4:** Dapat dijalankan sebagai daemon background permanen via `systemd` atau container Docker.

### FR-2: Client Auto-Connect & Pairing (`devbrain connect`)
* **FR-2.1:** Pada laptop klien, pengguna dapat menyambungkan IDE ke server hanya dengan 1 perintah:
  ```bash
  devbrain connect http://jarvis.tailnet:8000 --token "my-secret-token"
  ```
* **FR-2.2:** Perintah ini otomatis menguji konektivitas (*handshake ping*), memverifikasi token, dan memperbarui konfigurasi MCP di Antigravity IDE & Claude Code klien.

### FR-3: Syncthing Mesh Integration (Real-time File Sync)
* **FR-3.1:** Menyediakan panduan dan otomasi pairing folder vault via Syncthing over Tailscale.
* **FR-3.2:** Menggunakan partisi **Append-Only UUID** (`90_Agent_Inbox/{device_id}_{uuid}.md`) sehingga sinkronisasi bebas dari *file conflict* saat banyak agent aktif bersamaan.
* **FR-3.3:** Menerapkan `.stignore` standar pada folder indeks dan cache sementara.

### FR-4: Web UI Dashboard & Telemetry (`devbrain ui` / `devbrain dashboard`)
* **FR-4.1:** Web dashboard interaktif berbasis Dark Glassmorphism pada port `3000`.
* **FR-4.2: RAG Chunk Inspector:**
  * Pengguna dapat mengetik query pencarian di browser dan melihat chunk dokumen yang diambil, skor kesamaan (*similarity score*), serta perbandingan hasil Dense Vector vs Sparse BM25 (mengadopsi modul dari `_fxmedia`).
* **FR-4.3: Live Agent Telemetry:**
  * Menampilkan grafik riwayat pemanggilan tool MCP oleh AI Agent secara real-time.
* **FR-4.4: Vault Health Monitor:**
  * Menampilkan statistik jumlah dokumen terindeks, ukuran database Qdrant, dan status node Syncthing.

### FR-5: Boundary & Context Isolation (Work vs Personal)
* **FR-5.1:** Mendukung metadata scoping (`scope: work` vs `scope: personal`).
* **FR-5.2:** Pada laptop kantor, AI Agent dibatasi hanya dapat mencari dan membaca dokumen berlabel `scope: work`.

---

## 5. Kebutuhan Non-Fungsional (*Non-Functional Requirements*)

| Parameter | Target Spesifikasi |
| :--- | :--- |
| **Latensi Remote Search** | < 50 milidetik via Tailscale VPN antar laptop dan server rumah. |
| **Kecepatan Sinkronisasi Berkas** | < 1 detik dari saat file disimpan di laptop klien hingga tiba di server. |
| **Ketersediaan Server (Uptime)** | 99.9% uptime pada server Jarvis dengan auto-restart service (`systemd`). |
| **Keamanan Jaringan** | 100% trafik terenkripsi via WireGuard (Tailscale) + Token Gatekeeper pada API MCP. |
| **Kapasitas Skalabilitas** | Mampu menangani hingga 100.000 dokumen Markdown dan ribuan request agent per hari. |

---

## 6. Spesifikasi Perintah CLI Level 3

```text
devbrain serve [--port 8000] [--sse] [--auth-token <token>] [--daemon] # Jalankan server di Jarvis
devbrain connect <url> --token <token>                                  # Sambungkan laptop klien ke Jarvis
devbrain disconnect                                                     # Putus sambungan remote
devbrain status                                                         # Menampilkan status node & latensi sync
devbrain ui [--port 3000]                                               # Buka Web Dashboard di browser
devbrain peer list                                                      # Cek daftar device yang terhubung
```

---

## 7. Kriteria Keberhasilan & Skenario Pengujian (*Acceptance Criteria*)

1. **Skenario 1 (Remote Pairing & Live Query):**
   * Server Jarvis menjalankan `devbrain serve --daemon`.
   * Laptop OMEN di kantor menjalankan `devbrain connect http://jarvis:8000`.
   * Antigravity IDE di laptop kantor memanggil `search_brain("konfigurasi database")`.
   * Server memproses query dan mengembalikan konteks dari catatan di Jarvis dalam waktu <50ms.
2. **Skenario 2 (Multi-Device Memory Continuity):**
   * AI Agent di laptop kantor menyimpan solusi bug ke inbox vault.
   * File tersinkron ke server Jarvis via Syncthing.
   * Saat malam hari, pengguna membuka laptop pribadi di rumah; AI Agent di rumah langsung mengetahui solusi bug tersebut tanpa perlu dijelaskan ulang!
3. **Skenario 3 (Web UI Testing):**
   * Pengguna membuka `http://localhost:3000` di browser dan dapat melakukan tes pencarian dokumen secara visual serta melihat skor relevansi chunk.
