# 24. Lokasi Storage Harvester Tiap AI Agent & Katalog Data Ingesti Vault

Dokumen ini menyajikan panduan komprehensif mengenai **peta lokasi folder data (*storage path*)** dari berbagai AI Agent, AI CLI, dan AI Tools, algoritma **auto-discovery harvester**, serta klasifikasi **katalog data apa saja yang perlu dimasukkan ke dalam Obsidian Vault**.

---

## 1. Peta Lokasi Storage AI Agent, AI CLI & Tools Lintas OS

Setiap AI coding tool menyimpan sesi, percakapan, dan artefaknya di lokasi standar sistem operasi:

| AI Tool / Agent | Windows Storage Path | macOS / Linux Storage Path | Format Data Mentah |
| :--- | :--- | :--- | :--- |
| **Google Antigravity IDE** | `%USERPROFILE%\.gemini\antigravity-ide\brain\<uuid>\`<br>`%USERPROFILE%\.gemini\antigravity\brain\<uuid>\` | `~/.gemini/antigravity-ide/brain/<uuid>/`<br>`~/.gemini/antigravity/brain/<uuid>/` | Markdown artifacts (`task.md`, `implementation_plan.md`, `walkthrough.md`) & `transcript.jsonl` |
| **Google Antigravity CLI (`agy`)** | `%USERPROFILE%\.gemini\antigravity-cli\` | `~/.gemini/antigravity-cli/` | `history.jsonl`, `conversations.json` |
| **Claude Code (Anthropic CLI)** | `%USERPROFILE%\.claude\projects\`<br>`%USERPROFILE%\.claude.json` | `~/.claude/projects/`<br>`~/.claude.json` | JSON session logs & project transcript |
| **Aider (CLI Pair Programmer)** | `[ProjectRoot]\.aider.chat.history.md`<br>`%USERPROFILE%\.aider.conf.yml` | `[ProjectRoot]/.aider.chat.history.md`<br>`~/.aider.conf.yml` | Markdown murni per-repositori |
| **Cline / Roo Code (VS Code)** | `%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\` | `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/` | `tasks/<task_id>/api_conversation_history.json`, `ui_messages.json` |
| **Cursor IDE** | `%APPDATA%\Cursor\User\workspaceStorage\` | `~/.config/Cursor/User/workspaceStorage/` | SQLite (`state.vscdb`) & JSON prompt history |
| **Hermes Agent** | `%USERPROFILE%\.hermes\` | `~/.hermes/` | SQLite database (`hermes.db`) & JSON session logs |
| **OpenCode / OpenHands** | `%USERPROFILE%\.openhands\` / `%USERPROFILE%\.opencode\` | `~/.openhands/` / `~/.opencode/` | JSON session states & Docker container logs |

---

## 2. Cara Menemukan Lokasi Folder Secara Dinamis (Harvester Discovery Engine)

Dalam implementasi `devbrain`, pencarian folder harvester tidak di-hardcode ke satu user melainkan menggunakan modul **Dynamic Path Resolver**:

```python
import os
from pathlib import Path

def discover_agent_paths() -> dict[str, list[Path]]:
    """Otomatis memindai lokasi folder AI Agent yang terpasang di sistem."""
    home = Path.home()
    appdata = Path(os.getenv("APPDATA", home / "AppData" / "Roaming"))
    
    agent_paths = {
        "antigravity_ide": [
            home / ".gemini" / "antigravity-ide" / "brain",
            home / ".gemini" / "antigravity" / "brain",
        ],
        "antigravity_cli": [
            home / ".gemini" / "antigravity-cli",
        ],
        "claude_code": [
            home / ".claude" / "projects",
            home / ".claude",
        ],
        "cline": [
            appdata / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "tasks",
            home / ".config" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "tasks",
        ],
        "hermes": [
            home / ".hermes",
        ]
    }
    
    # Filter hanya folder yang benar-benar ada di laptop
    active_paths = {}
    for agent_name, paths in agent_paths.items():
        found = [p for p in paths if p.is_dir()]
        if found:
            active_paths[agent_name] = found
            
    return active_paths
```

---

## 3. Katalog Data: Apa yang HARUS vs TIDAK BOLEH Masuk ke Vault?

Tidak semua data mentah agent layak disimpan di Obsidian. Jika semua raw streaming text dimasukkan, vault akan cepat penuh (*bloated*) dan pencarian semantik menjadi bias (*noisy*).

### ✅ A. Data yang WAJIB / DIREKOMENDASIKAN Masuk ke Vault:

| Kategori Data | Contoh Dokumen | Target Folder Vault | Manfaat bagi AI & Manusia |
| :--- | :--- | :--- | :--- |
| **1. Session Summary & Walkthroughs** | `walkthrough.md`, `task.md` | `90_Agent_Inbox/antigravity/` | Mengetahui apa saja yang dikerjakan sesi kemarin, file apa yang diubah, dan hasil tesnya. |
| **2. Architecture Decisions (ADR)** | `ADR-001-use-fastmcp.md` | `30_Decisions/` | Mencegah agent baru membongkar keputusan desain arsitektur yang sudah disepakati sebelumnya. |
| **3. Bug Solutions & Root Causes** | `fastapi_websocket_leak.md` | `20_Knowledge/Bug_Solutions/` | Solusi debugging instan jika error serupa muncul lagi di masa depan di proyek lain. |
| **4. Project Specs & Context** | `auth_service/README.md` | `10_Projects/` | Menjadi panduan Single Source of Truth (SSOT) tentang requirement dan roadmap proyek. |
| **5. Reusable Skills & Prompts** | `SKILL.md` (e.g. docker-deploy) | `00_System/Agent_Skills/` | Prosedur multi-step standar yang dapat dijalankan secara konsisten oleh seluruh agent. |
| **6. Global Rules & Guidelines** | `general_rules.md` | `00_System/rules/` | Standar keamanan, gaya coding, dan batasan privasi yang wajib dipatuhi agent. |

---

### ❌ B. Data yang TIDAK BOLEH / DILARANG Masuk ke Vault:

| Kategori Data yang Ditolak | Alasan Ditolak | Solusi / Penanganan |
| :--- | :--- | :--- |
| **1. Raw Secrets, API Keys, Passwords** | Bahaya keamanan & privasi jika sync atau terkirim ke LLM. | **Secret Redaction Regex:** Otomatis diganti dengan `[REDACTED_API_KEY]`. |
| **2. Raw Streaming Token Chunks** | Menghabiskan storage dan mengotori indeks BM25 / Vector. | Hanya ambil *final assistant response* atau file Markdown terstruktur. |
| **3. Full Terminal Logs (Ribuan Baris)** | Output verbose `npm install`, build trace, raw `grep`. | Ekstrak hanya ringkasan status sukses/gagal dan error message kuncinya. |
| **4. Binary & Cache Blobs** | Format `.pb`, `.bin`, `.pyc`, SQLite binary database. | Di-ignore melalui aturan `.brainignore`. |

---

## 4. Alur Kerja Distilasi Harvester (Pipeline Ingesti Otomatis)

```text
[ AI Agent Selesai Coding ]
         │
         ▼
[ Step 1: Harvester Listener mendeteksi file walkthrough.md / transcript.jsonl baru ]
         │
         ▼
[ Step 2: Redaction Filter (Hapus API Keys, Token, Kredensial) ]
         │
         ▼
[ Step 3: Metadata Enricher (Tambah Frontmatter YAML: id, author, device, tags) ]
         │
         ▼
[ Step 4: Simpan ke 90_Agent_Inbox/<agent-name>/YYYY-MM-DD_<uuid>.md ]
         │
         ▼
[ Step 5: FastEmbed & BM25 Incremental Indexer memperbarui memori Central Brain ]
```

---

## 5. Hubungan dengan Dokumen Brainstorming Sebelumnya

Topik ini melengkapi dan memperdalam dokumen brainstorming yang sudah ada:
* 📄 [03-penyimpanan-memory-antigravity-ide-cli.md](./03-penyimpanan-memory-antigravity-ide-cli.md) — Bedah internal file system Google Antigravity IDE & `agy`.
* 📄 [04-peta-penyimpanan-multi-agent-cli.md](./04-peta-penyimpanan-multi-agent-cli.md) — Matriks perbandingan lokasi Claude Code, Hermes, Aider, Cline.
* 📄 [09-client-adapters-dan-distillation-pipeline.md](./09-client-adapters-dan-distillation-pipeline.md) — Konsep pipeline passive harvester vs active MCP.
* 📄 [10-security-privacy-dan-boundary-protocol.md](./10-security-privacy-dan-boundary-protocol.md) — Sanitasi secret redaction dan boundary data.
