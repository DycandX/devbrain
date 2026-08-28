# 09. Client Agent Adapters & Distillation Pipeline

Bagaimana menghubungkan berbagai AI Client (Antigravity IDE, agy CLI, Claude Code, Hermes, OpenCode) ke Central Brain Hub di Jarvis secara praktis?

Ada dua pilar integrasi:
1. **Active Integration (MCP):** Agent secara sadar memanggil tools untuk membaca context dan mencatat memori saat berinteraksi.
2. **Passive Harvester (Background Daemon):** Script lokal di laptop yang memanen riwayat sesi selesai secara otomatis tanpa perlu intervensi manual.

---

## 1. Konfigurasi Active MCP di Berbagai Client

Semua client di laptop cukup diarahkan ke endpoint SSE MCP Gateway di Jarvis Homeserver via Tailscale:
URL Endpoint: `http://jarvis.tailnet:8000/sse` (atau `http://100.x.y.z:8000/sse`)

### A. Konfigurasi Google Antigravity IDE & agy CLI
Di Antigravity, MCP server didaftarkan di file `~/.gemini/antigravity/mcp_config.json` atau di level global config `~/.gemini/config/mcp_config.json`:

```json
{
  "mcpServers": {
    "central-ai-brain": {
      "url": "http://jarvis.tailnet:8000/sse",
      "headers": {
        "Authorization": "Bearer your-super-secret-tailscale-token"
      }
    }
  }
}
```

### B. Konfigurasi Claude Code & Claude Desktop
Di `~/.claude.json` atau `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "central-brain": {
      "url": "http://jarvis.tailnet:8000/sse",
      "headers": {
        "Authorization": "Bearer your-super-secret-tailscale-token"
      }
    }
  }
}
```

### C. Konfigurasi Hermes Agent / Custom Python Agent
```python
from mcp import ClientSession, SseServerParameters
from mcp.client.sse import sse_client

server_params = SseServerParameters(
    url="http://jarvis.tailnet:8000/sse",
    headers={"Authorization": "Bearer your-super-secret-tailscale-token"}
)

async with sse_client(server_params.url, headers=server_params.headers) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        # Query Central Knowledge
        res = await session.call_tool("search_brain", {"query": "JWT auth retry mechanism"})
        print(res.content)
```

---

## 2. Passive Ingestion & Distillation Daemon (`local-harvester`)

Terkadang kita sedang coding cepat dan agent tidak sempat memanggil MCP tool secara manual. Untuk menangkap seluruh solusi emas yang dihasilkan selama sesi kerja, pasang background daemon ringan di laptop.

```
[ Antigravity / Claude Coding Session ]
                  │
                  ▼ (writes local logs)
   ~/.gemini/antigravity/brain/<UUID>/transcript.jsonl
                  │
                  ▼ (triggers file watcher)
     [ local-harvester daemon ]
                  │
                  ▼ (calls LLM to extract key insights)
    "Distill this conversation into:
     1. Problem 2. Key Decision 3. Solution Pattern"
                  │
                  ▼
  [ Writes formatted .md to Obsidian Vault ]
  -> 90_Agent_Inbox/antigravity/2026-08-28_agy-conv-xxx.md
                  │
                  ▼ (Syncthing pushes to Jarvis in <1s)
       [ Jarvis Qdrant Vectorizes It ]
```

### Pseudocode Ingestion Watcher (`harvester.py`)

```python
import os
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCH_DIR = os.path.expanduser("~/.gemini/antigravity/brain")
VAULT_INBOX = os.path.expanduser("~/ObsidianVault/90_Agent_Inbox/antigravity")

class TranscriptHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith("walkthrough.md") or event.src_path.endswith("transcript.jsonl"):
            self.process_session(os.path.dirname(event.src_path))

    def process_session(self, session_dir):
        # 1. Baca walkthrough.md & transcript ringkas
        # 2. Kirim ke lightweight LLM (misal: Gemini Flash / local Ollama)
        # 3. Format menjadi Markdown dengan standard YAML Frontmatter
        # 4. Tulis ke VAULT_INBOX/<date>_<session_id>.md
        pass

if __name__ == "__main__":
    observer = Observer()
    observer.schedule(TranscriptHandler(), WATCH_DIR, recursive=True)
    observer.start()
```

---

## 3. Manfaat Kombinasi Active + Passive

1. **Zero Context Loss:** Setiap problem-solving yang pernah dilakukan AI di laptop manapun otomatis diabadikan.
2. **Instant Cross-Device Availability:** Anda memecahkan bug di laptop kantor jam 16:00, jam 20:00 Anda membuka laptop pribadi, Antigravity IDE langsung mengetahui konteks dan solusi tersebut.
3. **Clean Human Overview:** Di Obsidian, Anda tinggal membuka folder `90_Agent_Inbox/` untuk melihat ringkasan apa saja yang telah dikerjakan oleh agent Anda seharian.
