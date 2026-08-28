# 25. Posisi Arsitektur Ingest/Harvester & Nomenklatur Perintah CLI

Dokumen ini mencatat evaluasi penempatan modul **Session Harvester / Ingestion Engine** di dalam roadmap level adopsi serta analisis komparasi **nomenklatur perintah CLI** (`devbrain ingest`, `capture`, `pull`, `distill`, `harvest`).

---

## 1. Penempatan Arsitektur: Level 1 vs Level 2

Dalam pembagian 3 Level Adopsi `devbrain`:

| Level | Fokus Utama | Mekanisme Ingesti Memori | Status & Karakteristik |
| :--- | :--- | :--- | :--- |
| **Level 1: Standalone Local (Zero-Friction Core)** | FastMCP Stdio Protocol Gateway + Hybrid Search (FastEmbed CPU + BM25) + Vault Scaffolder | **Active MCP Ingestion:** AI Agent secara sadar memanggil tool `@server.tool() write_agent_log()` saat sesi selesai. | Super-lean, zero background daemon luar, 100% terkontrol oleh prompt developer. |
| **Level 2: Automated Cloud Backup & Intelligent Ingestion** | Background Session Watcher + Secret Redactor Regex + LLM Distiller + Cloud/Git Backup | **Passive External Ingestion:** Daemon memindai folder internal IDE (`~/.gemini/brain/`, `~/.claude/projects/`) dan menarik artefak secara otomatis. | Otomatisasi penuh tanpa perlu instruksi sadar ke agent, dilengkapi penyaring keamanan API Key. |
| **Level 3: Distributed Multi-Device Mesh** | FastMCP SSE Gateway (Port 8000) + Qdrant Server + Syncthing over Tailscale + Web UI | **Mesh Network Ingestion:** Streaming session logs lintas laptop, tablet, dan 24/7 server. | Sentralisasi multi-device & multi-agent mesh. |

### 📌 Kesimpulan Penempatan:
Modul pemindai pasif folder luar ditempatkan pada **PRD Level 2 — Sprint 01 (Intelligent Ingestion & Harvester Engine)**. Hal ini menjaga **Level 1 Core** tetap ramping, cepat dibangun, stabil, dan bebas konflik proses background.

---

## 2. Analisis Nomenklatur Perintah CLI

Kata `harvest` (memanen) merupakan metafora yang baik, namun dalam perspektif antarmuka developer (DX - Developer Experience), terdapat beberapa opsi nama perintah:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    NOMENKLATUR PERINTAH INGESTI DEVBRAIN                    │
├──────────────────────┬────────────────────────┬─────────────────────────────┤
│ Perintah CLI         │ Kategori Nuansa        │ Karakteristik & DX          │
├──────────────────────┼────────────────────────┼─────────────────────────────┤
│ 1. devbrain ingest   │ Standar Data & RAG     │ [Rekomendasi Utama] Standar │
│                      │                        │ industri, sangat jelas.     │
│ 2. devbrain capture  │ Action-Oriented        │ Menangkap sesi aktif/baru.  │
│ 3. devbrain pull     │ Git / Developer        │ Analogi seperti git pull.   │
│ 4. devbrain import   │ Standar Utilitas       │ Bersifat eksplisit/manual.  │
│ 5. devbrain distill  │ Cognitive / AI Memory  │ Menekankan proses pemadatan │
│                      │                        │ dan pembersihan secret.     │
└──────────────────────┴────────────────────────┴─────────────────────────────┘
```

### Rekomendasi Sintaks CLI Level 2:
Perintah utama yang akan digunakan di Level 2 adalah:
```bash
# Mode manual: Ingest seluruh sesi baru yang belum tercatat di vault
devbrain ingest

# Mode spesifik: Ingest hanya dari Google Antigravity atau Claude Code
devbrain ingest --from antigravity
devbrain ingest --from claude

# Mode background watcher: Live memantau sesi luar secara pasif
devbrain ingest --watch
```
*(Alias pendukung seperti `devbrain pull` atau `devbrain capture` dapat didaftarkan sebagai alias opsional).*

---

## 3. Matriks Evolusi Ingesti Memori

```text
[ Level 1 Core (Aktif Saat Ini) ]
   AI Agent ──(Panggil MCP Tool)──▶ write_agent_log() ──▶ 90_Agent_Inbox/ ──▶ FastEmbed Index

[ Level 2 Ingest (Level Berikutnya) ]
   IDE Folder (~/.gemini/brain/) ──▶ devbrain ingest ──▶ Secret Redactor ──▶ 90_Agent_Inbox/ ──▶ Hybrid Index
```
