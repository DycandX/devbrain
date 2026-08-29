# 🧠 devbrain — Central AI Second Brain Hub

> **Single Source of Truth (SSOT) for Multi-Agent Coding & Obsidian.**

`devbrain` connects your AI coding assistants (**Google Antigravity IDE**, **Claude Code**, **Hermes**, **OpenCode**) directly to a local **Obsidian Vault** using the **Model Context Protocol (MCP)** and high-speed **Hybrid Semantic Search** (FastEmbed CPU ONNX + Rank-BM25).

---

## ⚡ 30-Second Quickstart

### 1. Install `devbrain` in Editable Development Mode
```bash
cd "E:\_PROJECT\_Central AI Brain Hub"
pip install -e .
```
*(Once installed, you can use the global `devbrain` command directly from any folder)*

### 2. Initialize or Attach Your Obsidian Vault
```bash
devbrain init E:/MyObsidianVault
```
*(Or via Python module directly: `python -m devbrain.cli.main init E:/MyObsidianVault`)*

*What happens under the hood:*
* Scaffolds the standard 07 Obsidian taxonomy (`00_System/`, `10_Projects/`, `20_Knowledge/`, `30_Decisions/`, `90_Agent_Inbox/`, `99_Daily/`, `.brainignore`).
* Automatically registers the `central-brain` FastMCP server into **Google Antigravity IDE** (`~/.gemini/antigravity/mcp_config.json`) and **Claude Code** (`~/.claude.json`).

### 3. Verify Vault Health
```bash
devbrain status
```

---

## 🧪 Development & Interactive Demo Guide
For complete copy-pasteable testing commands without global installation, check out [**`DEMO.md`**](DEMO.md).

---

## 🤖 AI Agent FastMCP Pairing

Once initialized, your AI assistants in Antigravity IDE and Claude Code automatically gain access to 4 native memory tools:

| MCP Tool | Purpose | Example Interaction |
| :--- | :--- | :--- |
| `search_brain(query, limit, scope)` | Semantic hybrid search across all vault notes | *"Search our architectural guidelines on JWT authentication"* |
| `get_project_context(project_name)` | Retrieve active project specs, backlog, and architecture from `10_Projects/` | *"Load context and requirements for the auth_service project"* |
| `write_agent_log(summary, details, tags)` | Record session walkthroughs and decisions to `90_Agent_Inbox/` | *"Save summary of this debugging session to Central Brain"* |
| `load_skill(skill_name)` | Load modular multi-step workflow instructions from `00_System/Agent_Skills/` | *"Load the docker-deployment skill"* |

---

## 💻 CLI Command Reference

`devbrain` comes with a unified developer CLI built on `Typer` and `Rich`:

```text
Usage: devbrain [OPTIONS] COMMAND [ARGS]...

Commands:
  init        Interactively initialize a new vault or attach an existing vault.
  status      Display vault status, configuration, and note statistics.
  search      Perform semantic, keyword, or hybrid search across indexed notes.
  index       Index or re-index Markdown files into FastEmbed & BM25 local stores.
  ingest      Harvest AI agent sessions, targeted projects, and workspace repos into vault.
  pull        Alias for 'ingest'.
  serve       Launch the FastMCP Protocol Server for Antigravity IDE and Claude.
  skill       Manage, scaffold, and sync modular AI Agent Skills.
  uninstall   Safely unregister FastMCP servers from IDEs and clean caches.
```

### Ingestion & Graph Harvester Commands:
```bash
# Ingest 1 specific project or cloned repo
devbrain ingest project "E:/_PROJECT/_Central AI Brain Hub"

# Batch scan all local repositories in a workspace folder
devbrain ingest projects --dir "E:/_PROJECT"

# Harvest AI agent sessions from Antigravity IDE & Claude Code
devbrain ingest

# Full Ingestion: Scan repos + Harvest sessions + Connect graph mesh
devbrain ingest all
```

---

## 🏗️ Vault Directory Taxonomy (07 Standard)

```text
MyObsidianVault/
├── 00_System/               # Rules, personas, agent skills, and global context
│   ├── Agent_Skills/        # Modular SKILL.md directories
│   ├── personas/            # Agent role definitions
│   └── rules/               # Coding style and security standards
├── 10_Projects/             # Active project specifications, roadmaps & dynamic Dataview dashboards
├── 20_Knowledge/            # Evergreen knowledge, patterns, and external cloned study repos
│   ├── External_Repos/      # Architecture cards for third-party cloned codebases
│   └── References/          # Ingested Markdown documentation and research books
├── 30_Decisions/            # Architecture Decision Records (ADRs)
├── 90_Agent_Inbox/          # Append-only agent session logs and walkthroughs
├── 99_Daily/                # Daily developer notes and scratchpad
├── .brain_data/             # Local vector index (vectors.npy, index_metadata.json, ingested_sessions.json)
├── .brainrc.json            # Vault configuration
└── .brainignore             # Excluded files and directories
```

---

## 📊 Performance & Benchmarks (Level 1 Core)

* **Semantic Search Engine:** FastEmbed CPU ONNX (`BAAI/bge-small-en-v1.5`, 384 dimensions, 100% offline, 0 GPU).
* **Keyword Search Engine:** Rank-BM25 with token normalization.
* **Search Latency (p50 / Median):** **< 10.0 ms**
* **Search Latency (p95):** **< 20.0 ms**
* **RAM Footprint (Idle):** **~85 MB**
* **RAM Footprint (Active Query):** **~135 MB**

---

## 🗺️ Adoption Levels & Roadmap

* **✅ Level 1 (Released `v1.0.0-alpha`):** Standalone Local Zero-Friction Core (FastMCP Stdio, FastEmbed CPU, BM25, Watchdog live watcher, Typer CLI).
* **✅ Level 1.1 - 1.2 (Released `v1.2.0-alpha`):** Multi-Agent Ingestion, Secret Redactor Sanitizer, Project Workspace Harvester, Auto-Inspector, and Auto-Entity Linker Graph Mesh.
* **⏳ Level 2 (Next Phase):** Automated Cloud Backup & Version History (Git auto-sync daemon, Rclone/S3/B2 encrypted offsite backup, conflict-free sync).
* **⏳ Level 3 (Distributed Mesh):** Homeserver FastMCP SSE Gateway (Port 8000), Qdrant Server, Syncthing over Tailscale, Web UI Dashboard.

---

## 📜 Changelog & Releases
All release notes are tracked in [`CHANGELOG.md`](CHANGELOG.md) and [`docs/changelog/`](docs/changelog/_index.md).
