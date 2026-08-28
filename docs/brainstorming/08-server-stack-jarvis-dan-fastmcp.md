# 08. Arsitektur Central Server Stack di Jarvis & Remote MCP Gateway

Jarvis Homeserver berfungsi sebagai **jantung pemrosesan dan Single Source of Truth (SSOT)**. Seluruh data diindeks, disimpan, dan disajikan melalui interface standar MCP (Model Context Protocol).

---

## 1. Topologi Layanan di Jarvis Homeserver

```
               [ Tailscale Private Mesh Network ]
                               │
               (MagicDNS: jarvis.tailnet / 100.x.y.z)
                               │
       ┌───────────────────────┴───────────────────────┐
       │                                               │
(Port 8000: MCP Server)                      (Port 8384: Syncthing)
       │                                               │
       ▼                                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                   DOCKER ENVIRONMENT DI JARVIS                   │
│                                                                  │
│  ┌────────────────────────┐         ┌─────────────────────────┐  │
│  │   central-mcp-gateway  │         │   syncthing-daemon      │  │
│  │ (FastMCP Python Server)│         │   (Vault Sync Manager)  │  │
│  └───────────┬────────────┘         └───────────┬─────────────┘  │
│              │                                  │                │
│              ▼                                  ▼                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Shared Volume: /opt/second-brain/vault (Obsidian Markdown)  │ │
│  └──────────────────────────────┬──────────────────────────────┘ │
│                                 │                                │
│                                 ▼                                │
│  ┌────────────────────────┐         ┌─────────────────────────┐  │
│  │   vault-auto-ingestor  │         │   qdrant-vector-db      │  │
│  │  (Embedding & Watcher) ├───upsert───► (Port 6333: Vectors) │  │
│  └────────────────────────┘         └─────────────────────────┘  │
│                                                                  │
│  ┌────────────────────────┐                                      │
│  │   ollama-embedder      │                                      │
│  │ (bge-m3 / nomic-embed) ◄──generate embeddings─────────────────│
│  └────────────────────────┘                                      │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. Definisi `docker-compose.yml` Lengkap

Berikut konfigurasi stack container yang siap dijalankan di Jarvis Homeserver:

```yaml
version: '3.8'

services:
  # 1. Vector Database untuk Semantic Search
  qdrant:
    image: qdrant/qdrant:latest
    container_name: brain-qdrant
    restart: unless-stopped
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - ./data/qdrant_storage:/qdrant/storage
    environment:
      - QDRANT__SERVICE__HTTP_PORT=6333

  # 2. Local Embedding Engine (Zero Cloud Cost & Private)
  ollama:
    image: ollama/ollama:latest
    container_name: brain-ollama
    restart: unless-stopped
    ports:
      - "11434:11434"
    volumes:
      - ./data/ollama_models:/root/.ollama

  # 3. FastMCP Gateway Server (Endpoint untuk semua AI Agent)
  mcp-gateway:
    build:
      context: ./mcp-gateway
      dockerfile: Dockerfile
    container_name: brain-mcp-gateway
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - VAULT_PATH=/vault
      - QDRANT_URL=http://qdrant:6333
      - EMBEDDING_PROVIDER=ollama # atau openai
      - OLLAMA_URL=http://ollama:11434
      - EMBEDDING_MODEL=bge-m3
      - AUTH_TOKEN=your-super-secret-tailscale-token
    volumes:
      - /opt/second-brain/vault:/vault:rw
    depends_on:
      - qdrant
      - ollama

  # 4. Background Ingestion & Watchdog Daemon
  vault-ingestor:
    build:
      context: ./vault-ingestor
      dockerfile: Dockerfile
    container_name: brain-vault-ingestor
    restart: unless-stopped
    environment:
      - VAULT_PATH=/vault
      - QDRANT_URL=http://qdrant:6333
      - OLLAMA_URL=http://ollama:11434
      - EMBEDDING_MODEL=bge-m3
    volumes:
      - /opt/second-brain/vault:/vault:ro
    depends_on:
      - qdrant
      - ollama

  # 5. Syncthing untuk Replikasi Vault Real-Time
  syncthing:
    image: syncthing/syncthing:latest
    container_name: brain-syncthing
    restart: unless-stopped
    network_mode: host
    environment:
      - PUID=1000
      - PGID=1000
    volumes:
      - /opt/second-brain/vault:/var/syncthing/vault
      - ./data/syncthing_config:/var/syncthing/config
```

---

## 3. Spesifikasi Tool FastMCP Gateway

MCP Server di Jarvis menyediakan sekumpulan tools terstandarisasi untuk semua agent (Antigravity IDE, Claude Code, Hermes, dsb.):

| Tool Name | Parameter | Deskripsi & Kegunaan |
| :--- | :--- | :--- |
| `search_brain` | `query: str, project?: str, limit?: int` | Melakukan hybrid semantic search di Qdrant + filtering berdasarkan project / tags. |
| `get_project_context` | `project_name: str` | Mengambil README, PRD, architecture, dan ADR terbaru dari project yang diminta. |
| `read_note` | `relative_path: str` | Membaca file Markdown spesifik dari dalam vault Obsidian. |
| `write_agent_log` | `agent_name: str, title: str, content: str, project: str, tags: list[str]` | Menulis catatan log hasil kerja atau solusi baru ke `90_Agent_Inbox/<agent_name>/`. |
| `record_adr` | `title: str, context: str, decision: str, consequences: str` | Membuat file ADR baru di `30_Decisions/` dengan format standar. |
| `get_system_rules` | `category?: str` | Mengambil system instructions, coding standard, dan persona dari `00_System/`. |

---

## 4. Keamanan & Akses Jaringan (Tailscale Mesh)

1. **No Public Port-Forwarding:** Port 8000 dan 6333 **TIDAK** dibuka ke internet publik.
2. **Tailscale Network Isolation:** Hanya perangkat yang berada di dalam Tailnet pribadi (`laptop-zulvikar`, `work-laptop`, `jarvis-server`) yang memiliki rute IP menuju server.
3. **Bearer Token Authentication:** Setiap request dari AI Client di laptop wajib menyertakan header authorization token:
   `Authorization: Bearer <AUTH_TOKEN>`
