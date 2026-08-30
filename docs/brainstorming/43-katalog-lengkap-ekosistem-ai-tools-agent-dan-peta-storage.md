# 43. Katalog Lengkap Ekosistem AI Coding Tools, Agentic Frameworks & Peta Lokasi Storage OS

| Metadata | Nilai |
| :--- | :--- |
| **Topik** | Katalog Komprehensif AI Tools, Coding Agents & Agentic Frameworks (Antigravity, Claude Code, Cursor, Hermes Agent, CrewAI, AutoGen, LangGraph, MetaGPT, Cline, Aider, OpenCode), Peta Path Storage OS & Spesifikasi Ingesti |
| **Status** | 💡 Brainstorming & Complete Reference Map |
| **Referensi** | [04-peta-penyimpanan-multi-agent-cli.md](./04-peta-penyimpanan-multi-agent-cli.md), [24-lokasi-storage-harvester-dan-katalog-data-ingesti.md](./24-lokasi-storage-harvester-dan-katalog-data-ingesti.md), [36-katalog-ingesti-mekanisme-harvester-dan-efisiensi-resource.md](./36-katalog-ingesti-mekanisme-harvester-dan-efisiensi-resource.md) |
| **Tanggal** | 2026-08-30 |

---

## 1. Peta Taksonomi Ekosistem AI Developer

```mermaid
graph TD
    DevBrain["🧠 DevBrain Central Ingestion Engine"]
    
    subgraph Cat1["💻 1. AI-First IDEs"]
        I1["Google Antigravity IDE"]
        I2["Cursor IDE"]
        I3["Windsurf IDE"]
    end
    
    subgraph Cat2["⚡ 2. Terminal Coding Agents"]
        C1["Claude Code CLI"]
        C2["OpenAI Codex / OpenCode"]
        C3["Aider CLI"]
        C4["GitHub Copilot CLI"]
    end
    
    subgraph Cat3["🔌 3. Editor Extensions"]
        E1["Cline / Roo-Code"]
        E2["Continue.dev"]
    end

    subgraph Cat4["🤖 4. Autonomous Agentic AI Frameworks"]
        A1["Hermes Agent (NousResearch)"]
        A2["CrewAI Framework"]
        A3["Microsoft AutoGen & Studio"]
        A4["LangGraph / LangChain Agents"]
        A5["MetaGPT & ChatDev"]
    end

    Cat1 --> DevBrain
    Cat2 --> DevBrain
    Cat3 --> DevBrain
    Cat4 --> DevBrain
```

---

## 2. Peta Detail Lokasi Storage AI Tools & Coding Agents

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
  * **Windows:** `C:\Users\<User>\.claude\projects\<project-hash>\`, `C:\Users\<User>\.claude.json`
  * **Linux / macOS:** `~/.claude/projects/`, `~/.claude.json`
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
  * **Windows:** `AppData\Roaming\Cursor\User\workspaceStorage\<workspace-id>\`, `C:\Users\<User>\.cursor\`
  * **Linux / macOS:** `~/.config/Cursor/User/workspaceStorage/<workspace-id>/`, `~/.cursor/`
  * **Workspace Lokal:** `.cursorrules`, `.cursor/rules/*.mdc`, `.cursor/prompts/`
* **File & Data yang Di-ingest ke Vault:**
  * `.cursorrules` & `.cursor/rules/*.mdc`: Aturan koding spesifik projek.
  * Composer & Chat History di SQLite workspace storage (`state.vscdb`).
* **Folder Tujuan di Vault:** `90_Agent_Inbox/Cursor/` & `10_Projects/<Project>/`.

---

### 🌟 4. Windsurf IDE (Codeium Cascade)
* **Kategori:** Agentic IDE by Codeium.
* **Lokasi Folder di OS:**
  * **Windows:** `C:\Users\<User>\.codeium\windsurf\`, `AppData\Roaming\Windsurf\User\workspaceStorage\`
  * **Linux / macOS:** `~/.codeium/windsurf/`
  * **Workspace Lokal:** `.windsurfrules`, `.windsurf/`
* **File & Data yang Di-ingest ke Vault:**
  * Cascade chat logs & task summaries.
  * File `.windsurfrules` (konvensi styling dan arsitektur projek).
* **Folder Tujuan di Vault:** `90_Agent_Inbox/Windsurf/`.

---

### 🌟 5. Cline & Roo-Code (VS Code Extension)
* **Kategori:** Open-Source Autonomous Extension for VS Code.
* **Lokasi Folder di OS:**
  * **Windows:** `AppData\Roaming\Code\User\globalStorage\saoudrizwan.claude-dev\tasks\`
  * **Linux / macOS:** `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/tasks/`
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
  * **Workspace Level:** `.aider.chat.history.md`, `.aider.input.history`
  * **Global Config:** `~/.aider.conf.yml`
* **File & Data yang Di-ingest ke Vault:**
  * `.aider.chat.history.md`: Catatan lengkap diskusi pair programming & commit git.
* **Folder Tujuan di Vault:** `90_Agent_Inbox/Aider/`.

---

### 🌟 7. OpenAI Codex / OpenCode / Continue.dev / GitHub Copilot
* **Lokasi Folder di OS:**
  * OpenCode: `~/.opencode/sessions/`
  * Continue: `~/.continue/sessions/*.json`, `~/.continue/config.json`
  * Copilot CLI: `AppData\Local\github-copilot\`
* **File & Data yang Di-ingest:** Session histories, tool executions, dan custom prompt configurations.
* **Folder Tujuan di Vault:** `90_Agent_Inbox/OpenCode/` & `90_Agent_Inbox/Continue/`.

---

## 3. Peta Detail Autonomous Agentic AI Frameworks

Framework multi-agent otonom menghasilkan trajektori penalaran (*reasoning trajectories*), pembagian tugas (*task decomposition*), dan state checkpoints yang sangat bernilai untuk disimpan ke Central Brain:

---

### 🤖 8. Hermes Agent (NousResearch Autonomous Agent)
* **Kategori:** Open-Source Autonomous Agent & Tool-Use Engine (Hermes-3 / Function Calling).
* **Lokasi Folder di OS:**
  * **Windows:** `C:\Users\<User>\.hermes\`, `C:\Users\<User>\AppData\Roaming\Hermes\`
  * **Linux / macOS:** `~/.hermes/sessions/`, `~/.hermes/memories/`
  * **Workspace Lokal:** `.hermes/`, `hermes_config.yaml`
* **File & Data yang Di-ingest ke Vault:**
  * `sessions/<session-id>/cot_trace.jsonl`: *Chain-of-Thought (CoT)* jejak penalaran agen saat mengeksekusi tools.
  * `memories/long_term_memory.json`: Fakta-fakta yang dipelajari Hermes dari percakapan pengguna.
  * `scratchpad.md`: Catatan sementara agen saat menganalisis bug atau merancang script.
* **Folder Tujuan di Vault:** `90_Agent_Inbox/Hermes_Agent/` & `20_Knowledge/Agent_Reasoning/`.

---

### 🤖 9. CrewAI Framework (Multi-Agent Role-Playing)
* **Kategori:** Framework orkestrasi tim multi-agent dengan pembagian peran (Researcher, Writer, Coder, QA).
* **Lokasi Folder di OS:**
  * **Workspace Lokal:** `.crewai/`, `db/crewai.db`, `output/`
  * **Global Storage:** `~/.crewai/cache/`
* **File & Data yang Di-ingest ke Vault:**
  * `crewai_task_output.md`: Laporan hasil akhir pengerjaan tugas dari seluruh kru agen.
  * `crewai_state.json`: State memory antar-agen (misal temuan Researcher yang diserahkan ke Coder).
  * `crew_definitions.yaml`: Definisi peran agen, tools yang diberikan, dan tujuan (*goals*).
* **Folder Tujuan di Vault:** `90_Agent_Inbox/CrewAI/` & `10_Projects/<Project>/Agents/`.

---

### 🤖 10. Microsoft AutoGen & AutoGen Studio
* **Kategori:** Multi-Agent Conversation Framework & Studio UI.
* **Lokasi Folder di OS:**
  * **Windows:** `C:\Users\<User>\.autogenstudio\`, `C:\Users\<User>\.autogen\`
  * **Linux / macOS:** `~/.autogenstudio/`
  * **File:** `database.sqlite` (berisi sessions, agents, workflows, skills), `skills/*.py`
* **File & Data yang Di-ingest ke Vault:**
  * Group Chat History (`sessions` di SQLite): Transkrip diskusi antar-agen AutoGen.
  * Generated Python Skills (`skills/*.py`): Fungsi Python yang berhasil ditulis dan divalidasi oleh agen.
* **Folder Tujuan di Vault:** `90_Agent_Inbox/AutoGen/` & `00_System/Agent_Skills/AutoGen/`.

---

### 🤖 11. LangGraph & LangChain Local Agents
* **Kategori:** Graph-Based State Machine Autonomous Agents.
* **Lokasi Folder di OS:**
  * **Workspace Lokal:** `.langgraph/`, `checkpoints.sqlite`, `langgraph_state.json`
* **File & Data yang Di-ingest ke Vault:**
  * `checkpoints.sqlite`: Snapshot graf state (node eksekusi, human-in-the-loop approvals).
  * Agent run summaries & tool call payloads.
* **Folder Tujuan di Vault:** `90_Agent_Inbox/LangGraph/`.

---

### 🤖 12. MetaGPT & ChatDev (Simulasi Perusahaan Software Multi-Agent)
* **Kategori:** Multi-Agent Software Development Simulation (Product Manager $\rightarrow$ Architect $\rightarrow$ Engineer $\rightarrow$ QA).
* **Lokasi Folder di OS:**
  * **Workspace Lokal:** `workspace/docs/`, `workspace/resources/`
* **File & Data yang Di-ingest ke Vault:**
  * `prd.md`: Dokumen Product Requirements yang dirumuskan oleh AI Product Manager.
  * `system_design.md` & `architecture.md`: Diagram arsitektur & sequence diagram buatan AI Architect.
  * `task.md` & `code_summary.md`: Pembagian modul koding dan implementasi.
* **Folder Tujuan di Vault:** `10_Projects/<Project>/Architecture/` & `30_Decisions/`.

---

## 4. Matriks Data: Apa yang WAJIB Di-ingest vs DILARANG (Ignored)

```text
┌───────────────────────────────────────────────────┬───────────────────────────────────────────────────┐
│            ✅ WAJIB DI-INGEST KE VAULT            │              ❌ DILARANG / DI-IGNORE              │
├───────────────────────────────────────────────────┼───────────────────────────────────────────────────┤
│ • Task checklists & milestones (task.md)          │ • Binaries, node_modules/, venv/, .git/           │
│ • Technical plans (implementation_plan.md)        │ • Raw browser cache & Chromium session dumps      │
│ • Architecture decisions (ADRs & .cursorrules)    │ • Token otentikasi login / API Keys mentah        │
│ • CoT Reasoning Traces (Hermes cot_trace.jsonl)   │ • Telemetry / log debugging internal aplikasi     │
│ • Generated Multi-Agent PRD & System Designs      │ • Socket IPC / temporary lock files               │
│ • Reusable Agent Skills (SKILL.md & AutoGen .py)  │ • Model weight checkpoints (.bin / .onnx > 50MB)  │
│ • Prompt-response summaries (transcript.jsonl)    │ • Temporary test artifacts > 10 MB                │
└───────────────────────────────────────────────────┴───────────────────────────────────────────────────┘
```

---

## 5. Keamanan Otomatis: Pipeline Sanitasi Rahasia (*Secret Redaction*)

Sebelum file apa pun dari lokasi di atas disimpan ke Vault Obsidian, DevBrain menjalankan **Regex Sanitizer**:
* `sk-ant-...` $\rightarrow$ `[REDACTED_ANTHROPIC_KEY]`
* `AIzaSy...` $\rightarrow$ `[REDACTED_GEMINI_KEY]`
* `ghp_...` $\rightarrow$ `[REDACTED_GITHUB_TOKEN]`
* `Bearer ...` $\rightarrow$ `[REDACTED_AUTH_TOKEN]`
* `postgres://user:pass@host` $\rightarrow$ `postgres://user:[REDACTED]@host`

---

## 6. Kesimpulan

Dengan memetakan seluruh ekosistem **AI IDEs**, **Terminal Agents**, dan **Autonomous Agentic Frameworks (Hermes, CrewAI, AutoGen, LangGraph, MetaGPT)**:
1. **DevBrain menjadi Universal Knowledge Hub** yang dapat memanen tidak hanya sesi tanya-jawab koding biasa, melainkan juga **alur penalaran tingkat tinggi (*Reasoning Traces*)**, **desain sistem multi-agent**, dan **skill Python baru** yang dihasilkan oleh agen otonom.
2. Semua AI di laptop Anda langsung mewarisi memori bersama tanpa batas platform.
