# 43. Katalog Lengkap Ekosistem AI Coding Tools, Agents & Peta Lokasi Storage OS

| Metadata | Nilai |
| :--- | :--- |
| **Topik** | Katalog Komprehensif AI Tools & Agents (Antigravity, Claude Code, Codex, Cursor, Windsurf, Cline, Aider, OpenCode, Continue), Peta Path Storage OS & Spesifikasi Data Ingesti |
| **Status** | 💡 Brainstorming & Complete Reference Map |
| **Referensi** | [04-peta-penyimpanan-multi-agent-cli.md](./04-peta-penyimpanan-multi-agent-cli.md), [24-lokasi-storage-harvester-dan-katalog-data-ingesti.md](./24-lokasi-storage-harvester-dan-katalog-data-ingesti.md), [36-katalog-ingesti-mekanisme-harvester-dan-efisiensi-resource.md](./36-katalog-ingesti-mekanisme-harvester-dan-efisiensi-resource.md) |
| **Tanggal** | 2026-08-30 |

---

## 1. Tabel Ringkasan Ekosistem AI Tools & Coding Agents

```mermaid
graph TD
    DevBrain["🧠 DevBrain Central Ingestion Engine"]
    
    subgraph Category_IDE["💻 1. AI-First IDEs"]
        I1["Antigravity IDE"]
        I2["Cursor IDE"]
        I3["Windsurf IDE"]
    end
    
    subgraph Category_CLI["⚡ 2. Terminal Coding Agents"]
        C1["Claude Code CLI"]
        C2["Codex / ChatGPT CLI"]
        C3["Aider CLI"]
        C4["OpenCode CLI"]
        C5["GitHub Copilot CLI"]
    end
    
    subgraph Category_Ext["🔌 3. VS Code / JetBrains Extensions"]
        E1["Cline / Roo-Code"]
        E2["Continue.dev"]
    end

    Category_IDE --> DevBrain
    Category_CLI --> DevBrain
    Category_Ext --> DevBrain
```

---

## 2. Peta Detail Lokasi File, Folder & Spesifikasi Data Ingesti

---

### 🌟 1. Google Antigravity IDE & Antigravity CLI (`agy`)
* **Kategori:** AI-First Autonomous Coding IDE & CLI Assistant.
* **Lokasi Folder di OS:**
  * **Windows:**
    * Global Config & Skills: `C:\Users\<User>\.gemini\config\`
    * Sessions & Brain: `C:\Users\<User>\.gemini\antigravity-ide\brain\<conversation-id>\`
    * App Data: `C:\Users\<User>\AppData\Roaming\Antigravity\`
  * **Linux / macOS:**
    * `~/.gemini/antigravity-ide/brain/<conversation-id>/`
    * `~/.gemini/config/skills/`
  * **Workspace Lokal:** `.agents/skills/`, `.agents/rules/`
* **File & Data yang Di-ingest ke Vault:**
  * `task.md` / `task.json`: Checklist rencana tugas dan milestone.
  * `implementation_plan.md`: Rancangan arsitektur teknis sebelum coding.
  * `walkthrough.md`: Hasil akhir, file yang diubah, dan verifikasi test.
  * `transcript.jsonl`: Riwayat percakapan prompt & respons model.
* **Folder Tujuan di Vault:** `90_Agent_Inbox/Antigravity/` & `00_System/Agent_Skills/`.

---

### 🌟 2. Anthropic Claude Code CLI (`claude`)
* **Kategori:** Autonomous Terminal Coding Agent.
* **Lokasi Folder di OS:**
  * **Windows:**
    * `C:\Users\<User>\.claude\`
    * `C:\Users\<User>\.claude\projects\<project-hash>\`
    * Global Config: `C:\Users\<User>\.claude.json`
  * **Linux / macOS:**
    * `~/.claude/`
    * `~/.claude/projects/`
    * `~/.claude.json`
  * **Workspace Lokal:** `CLAUDE.md`, `.claude/`
* **File & Data yang Di-ingest ke Vault:**
  * Session transcript log (`.json` / `.jsonl`): Riwayat chat, command bash yang dijalankan.
  * Diffs & patches code modifications.
  * File instruksi projek `CLAUDE.md`.
* **Folder Tujuan di Vault:** `90_Agent_Inbox/Claude_Code/`.

---

### 🌟 3. Cursor IDE
* **Kategori:** AI-Powered Fork of VS Code.
* **Lokasi Folder di OS:**
  * **Windows:**
    * `C:\Users\<User>\AppData\Roaming\Cursor\User\workspaceStorage\<workspace-id>\`
    * Global Rules: `C:\Users\<User>\.cursor\`
  * **Linux / macOS:**
    * `~/.config/Cursor/User/workspaceStorage/<workspace-id>/`
    * `~/.cursor/`
  * **Workspace Lokal:** `.cursorrules`, `.cursor/rules/`, `.cursor/prompts/`
* **File & Data yang Di-ingest ke Vault:**
  * `.cursorrules` & `.cursor/rules/*.mdc`: Aturan koding spesifik projek.
  * Composer & Chat History di SQLite workspace storage (`state.vscdb`).
* **Folder Tujuan di Vault:** `90_Agent_Inbox/Cursor/` & `10_Projects/<Project>/`.

---

### 🌟 4. Windsurf IDE (Codeium Cascade)
* **Kategori:** Agentic IDE by Codeium.
* **Lokasi Folder di OS:**
  * **Windows:**
    * `C:\Users\<User>\.codeium\windsurf\`
    * `C:\Users\<User>\AppData\Roaming\Windsurf\User\workspaceStorage\`
  * **Linux / macOS:**
    * `~/.codeium/windsurf/`
  * **Workspace Lokal:** `.windsurfrules`, `.windsurf/`
* **File & Data yang Di-ingest ke Vault:**
  * Cascade chat logs & task summaries.
  * File `.windsurfrules` (konvensi styling dan arsitektur projek).
* **Folder Tujuan di Vault:** `90_Agent_Inbox/Windsurf/`.

---

### 🌟 5. Cline & Roo-Code (VS Code AI Autonomous Extension)
* **Kategori:** Open-Source Autonomous Extension for VS Code.
* **Lokasi Folder di OS:**
  * **Windows:**
    * `C:\Users\<User>\AppData\Roaming\Code\User\globalStorage\saoudrizwan.claude-dev\`
    * `C:\Users\<User>\AppData\Roaming\Code\User\globalStorage\rooveterinaryinc.roo-cline\`
  * **Linux / macOS:**
    * `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/tasks/`
    * `~/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/tasks/`
  * **Workspace Lokal:** `.clinerules`, `.roomodes`
* **File & Data yang Di-ingest ke Vault:**
  * `tasks/<task-id>/api_conversation_history.json`: Log lengkap eksekusi task.
  * `tasks/<task-id>/task_metadata.json`: Timestamp, token count, status task.
  * `.clinerules`: Instruksi sistem untuk agen koding.
* **Folder Tujuan di Vault:** `90_Agent_Inbox/Cline/`.

---

### 🌟 6. Aider CLI (`aider`)
* **Kategori:** Git-Integrated AI Pair Programming CLI.
* **Lokasi Folder di OS:**
  * **Windows / Linux / macOS (Workspace Level):**
    * Riwayat Chat: `.aider.chat.history.md` (di root setiap git repo yang memakai Aider).
    * Input History: `.aider.input.history`
    * Tags Cache: `.aider.tags.cache.v3`
    * Global Config: `~/.aider.conf.yml`
* **File & Data yang Di-ingest ke Vault:**
  * `.aider.chat.history.md`: Catatan lengkap diskusi pair programming & commit git yang dihasilkan.
* **Folder Tujuan di Vault:** `90_Agent_Inbox/Aider/`.

---

### 🌟 7. OpenAI Codex / ChatGPT CLI / OpenCode
* **Kategori:** Terminal & Web-linked AI Coding Agents.
* **Lokasi Folder di OS:**
  * **Windows:**
    * `C:\Users\<User>\.opencode\`
    * `C:\Users\<User>\.openai\`
  * **Linux / macOS:**
    * `~/.opencode/`
    * `~/.openai/`
* **File & Data yang Di-ingest ke Vault:**
  * Session logs (`session.json`), prompt histories, dan tool calls execution.
* **Folder Tujuan di Vault:** `90_Agent_Inbox/OpenCode/`.

---

### 🌟 8. Continue.dev
* **Kategori:** Open-source AI code assistant for VS Code & JetBrains.
* **Lokasi Folder di OS:**
  * **Windows:** `C:\Users\<User>\.continue\`
  * **Linux / macOS:** `~/.continue/`
  * **File:** `~/.continue/config.json`, `~/.continue/sessions/*.json`, `~/.continue/index/`
* **File & Data yang Di-ingest ke Vault:**
  * Riwayat sesi chat koding (`sessions/*.json`).
  * Custom Prompts & Slash Commands (`config.json` / `prompts/`).
* **Folder Tujuan di Vault:** `90_Agent_Inbox/Continue/`.

---

### 🌟 9. GitHub Copilot CLI & Workspace
* **Kategori:** AI developer assistant CLI by GitHub.
* **Lokasi Folder di OS:**
  * **Windows:** `C:\Users\<User>\AppData\Local\github-copilot\`
  * **Linux / macOS:** `~/.config/github-copilot/`
* **File & Data yang Di-ingest ke Vault:**
  * Explanation history & command generation logs.
* **Folder Tujuan di Vault:** `90_Agent_Inbox/GitHub_Copilot/`.

---

## 3. Matriks Data: Apa yang WAJIB Di-ingest vs DILARANG (Ignored)

```text
┌───────────────────────────────────────────────┬───────────────────────────────────────────────┐
│          ✅ WAJIB DI-INGEST KE VAULT          │          ❌ DILARANG / DI-IGNORE              │
├───────────────────────────────────────────────┼───────────────────────────────────────────────┤
│ • Task checklists & milestones (task.md)      │ • Binaries, node_modules/, venv/, .git/       │
│ • Technical plans (implementation_plan.md)    │ • Raw browser cache & Chromium session dumps  │
│ • Architecture decisions (ADRs & .cursorrules)│ • Token otentikasi login / API Keys mentah    │
│ • Code diffs & modification summaries         │ • Telemetry / log debugging internal aplikasi │
│ • Reusable Agent Skills (SKILL.md)            │ • Socket IPC / temporary lock files           │
│ • Prompt-response summaries (transcript.jsonl)│ • Temporary test artifacts > 10 MB            │
└───────────────────────────────────────────────┴───────────────────────────────────────────────┘
```

---

## 4. Keamanan Otomatis: Pipeline Sanitasi Rahasia (*Secret Redaction*)

Sebelum file apa pun dari lokasi di atas disimpan ke Vault Obsidian, DevBrain menjalankan **Regex Sanitizer**:
* `sk-ant-...` $\rightarrow$ `[REDACTED_ANTHROPIC_KEY]`
* `AIzaSy...` $\rightarrow$ `[REDACTED_GEMINI_KEY]`
* `ghp_...` $\rightarrow$ `[REDACTED_GITHUB_TOKEN]`
* `Bearer ...` $\rightarrow$ `[REDACTED_AUTH_TOKEN]`
* `postgres://user:pass@host` $\rightarrow$ `postgres://user:[REDACTED]@host`

---

## 5. Kesimpulan

Dengan memetakan seluruh lokasi fisik dari 9 ekosistem AI tools terbesar ini, **DevBrain memiliki kemampuan pemanenan menyeluruh (*Universal Harvester*)**:
1. Tidak peduli Anda coding menggunakan **Antigravity IDE**, **Claude Code**, **Cursor**, **Cline**, atau **Aider CLI**, seluruh riwayat berharga dan keputusan arsitektur akan otomatis terkumpul ke satu tempat: **Central Brain Hub**.
2. Semua AI di laptop Anda langsung mewarisi memori bersama tanpa perlu di-briefing ulang dari nol.
