# 07. Taksonomi Vault Obsidian & Standar Metadata AI-Human (Ontology & Schema)

Agar AI Agent dan Manusia dapat membaca, menavigasi, dan memelihara catatan dengan mulus di Obsidian, diperlukan **standar taksonomi direktori** dan **skema metadata (YAML Frontmatter)** yang ketat.

---

## 1. Struktur Direktori Vault (Hybrid PARA & Agent Inbox)

Struktur ini dirancang agar manusia nyaman menggunakan Obsidian Graph View & Dataview, sementara AI agent memiliki jalur navigasi yang jelas dan aman.

```text
Central-AI-Vault/
├── .obsidian/                    # Konfigurasi, tema, dan plugin Obsidian
├── 00_System/                    # [READ-ONLY AGENT] Rule, Persona, dan System Instructions
│   ├── rules/                    # Rules umum (coding style, security constraints)
│   ├── personas/                 # Persona agent (Backend Architect, Code Reviewer, DevOps)
│   └── global_context.md         # Ringkasan profil user, stack teknologi, preferensi
│
├── 10_Projects/                  # [READ/WRITE DOCS] Active & Inactive Projects
│   ├── _Project_Index.md         # Hub indeks semua proyek aktif
│   ├── Project-A/
│   │   ├── README.md             # Overview, roadmap, tech stack
│   │   ├── prd.md                # Product Requirements Document
│   │   ├── architecture.md       # Desain sistem & diagram
│   │   └── tasks.md              # Backlog dan milestone
│   └── Project-B/
│
├── 20_Knowledge/                 # [SSOT KNOWLEDGE] Evergreen Notes & Solusi Teknis
│   ├── Architecture_Patterns/    # Microservices, Event-driven, Clean Architecture
│   ├── Bug_Solutions/            # Solusi error unik yang pernah dipecahkan agent
│   ├── Frameworks_Tools/         # Catatan FastAPI, Qdrant, Tailscale, React, Docker
│   └── Security_Checklists/      # Aturan sanitasi data, JWT best practices
│
├── 30_Decisions/                 # [ADR] Architecture Decision Records
│   ├── ADR-001-use-qdrant.md
│   └── ADR-002-syncthing-over-tailscale.md
│
├── 90_Agent_Inbox/               # [AGENT WRITE ZONE] Zona Drop Agent Lintas Device
│   ├── antigravity/              # Sesi hasil extract Antigravity IDE & agy CLI
│   ├── claude-code/              # Transkrip & solusi dari Claude Code
│   ├── hermes/                   # Autonomous task output dari Hermes
│   └── manual_review/            # Catatan agent yang membutuhkan validasi manusia
│
└── 99_Daily/                     # Daily Notes & Log interaksi harian
    └── 2026-08-28.md
```

---

## 2. Standar Metadata (YAML Frontmatter Schema)

Setiap catatan yang dibuat oleh agent atau manusia harus memiliki blok YAML Frontmatter yang konsisten di bagian paling atas dokumen.

### A. Catatan Knowledge / Solusi Teknis (`20_Knowledge/`)
```yaml
---
id: "KNOW-2026-08-28-01"
title: "Mengatasi Memory Leak pada FastAPI WebSockets"
type: knowledge-pattern
category: backend
tags:
  - fastapi
  - websockets
  - debugging
  - python
created_at: 2026-08-28T20:30:00+07:00
updated_at: 2026-08-28T20:30:00+07:00
author: "antigravity-ide"
verified_by_human: true
related_projects:
  - "[[10_Projects/Project-A/README|Project-A]]"
summary: "Penjelasan cara mengelola disconnect handler WebSocket pada FastAPI untuk mencegah penumpukan dangling connection objects."
---
```

### B. Catatan Sesi Agent (`90_Agent_Inbox/`)
```yaml
---
id: "SESSION-20260828-AGY-009"
session_id: "agy-conv-0aebfe86"
title: "Refactor Database Connection Pool & Retry Logic"
type: agent-session-log
agent: "antigravity-ide" # atau claude-code, hermes, agy-cli
device: "omen-laptop"    # laptop-kerja, homeserver-jarvis
project: "Central AI Brain Hub"
tags:
  - agent-session
  - refactor
  - database
timestamp: 2026-08-28T20:45:00+07:00
status: "completed" # completed | partial | failed | needs-review
artifacts:
  - "implementation_plan.md"
  - "walkthrough.md"
summary: "Berhasil menambahkan exponential backoff pada koneksi PostgreSQL pgvector."
---
```

### C. Architecture Decision Record (`30_Decisions/`)
```yaml
---
id: "ADR-003"
title: "Penggunaan FastMCP Over SSE untuk Remote Gateway"
type: adr
status: "accepted" # draft | accepted | superseded
deciders:
  - "zulvikar"
  - "antigravity"
date: 2026-08-28
tags:
  - architecture
  - mcp
  - networking
---
# Konteks
Memilih protokol transport MCP antara Client (Laptop) dan Server (Jarvis).

# Keputusan
Menggunakan Server-Sent Events (SSE) di atas Tailscale VPN dengan Bearer Auth Token.

# Konsekuensi
- Memudahkan koneksi multi-client tanpa perlu membuka port SSH Stdio berulang.
```

---

## 3. Konvensi Graph Linking (`[[Wikilinks]]`) untuk AI Graph-RAG

Salah satu keunggulan terbesar Obsidian adalah relasi grafis melalui Wikilinks. Agar AI Agent dapat melakukan *multi-hop reasoning* (menghubungkan satu konteks ke konteks lain):

1. **Explicit Entity Linking:**
   Saat agent menulis catatan baru tentang database, agent harus menambahkan link ke konsep yang sudah ada:
   *Contoh:* *"Implementasi ini menggunakan [[20_Knowledge/Frameworks_Tools/Qdrant|Qdrant Vector DB]] dengan embedding model BGE-large."*
2. **Backlinking Proyek:**
   Setiap catatan di Inbox wajib menyertakan link ke halaman project yang relevan di `10_Projects/`.
3. **Graph Traversal di MCP Server:**
   MCP Server di Jarvis dapat menyediakan tool `get_linked_notes(note_path)` sehingga agent bisa menelusuri dokumen turunan yang terhubung dalam graf Obsidian.

---

## 4. Visualisasi & Monitoring Dashboard di Obsidian (UI Human)

Dengan plugin **Dataview** di Obsidian, Anda dapat membuat halaman dashboard pemantau aktivitas semua AI Agent secara real-time.

### Dashboard Contoh: `00_System/Agent_Dashboard.md`
```markdown
# 🤖 Multi-Agent Activity Center

## 📥 Sesi Agent Terbaru yang Membutuhkan Review
\`\`\`dataview
TABLE agent, device, project, summary, timestamp
FROM "90_Agent_Inbox"
WHERE status = "needs-review" OR verified_by_human = false
SORT timestamp DESC
LIMIT 10
\`\`\`

## 💡 Knowledge Base Baru yang Ditambahkan Minggu Ini
\`\`\`dataview
TABLE author, category, tags, summary
FROM "20_Knowledge"
WHERE created_at >= date(today) - dur(7 days)
SORT created_at DESC
\`\`\`
```
