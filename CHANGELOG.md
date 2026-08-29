# Changelog

All notable changes to the `devbrain` project are documented here and in [`docs/changelog/`](docs/changelog/_index.md).

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.4.0-alpha] - 2026-08-29

### 🚀 Added
- **Unified DWIM Ingestion CLI:** Re-architected `devbrain ingest [TARGET] [OPTIONS]` to accept any target or directory flag (`--dir`, `--path`) tolerantly, auto-routing to single project, container workspace, or AI session harvesting without syntax errors.
- **Interactive IDE Deep Links:** Injects clickable `vscode://file/...` and `file:///...` protocol links into every Obsidian project card for 1-click IDE launch from Obsidian.
- **Self-Ingestion Guard:** Prevents circular self-processing when scanning workspaces containing the active Central Brain vault.
- **Automated Tests:** 42 comprehensive automated tests passing 100%.

For complete release details, see [docs/changelog/v1.4.0-alpha.md](docs/changelog/v1.4.0-alpha.md).

---

## [1.3.0-alpha] - 2026-08-29

### 🚀 Added
- **Smart Codebase Tree Analyzer & Entrypoint Detector:** Generates clean ASCII directory structures ignoring binary/venv/build directories (`src/devbrain/harvester/tree_analyzer.py`), detecting entrypoints (`server.js`, `main.py`, `index.ts`) and infra specs (`docker-compose.yml`, `.env.example`).
- **Intelligent Architecture Synthesis for README-less Projects:** Automatically synthesizes rich project cards with tech stack overview, runnable scripts (`## ⚡ Runnable Scripts`), and directory trees (`## 🌳 Project Structure`) when no `README.md` exists.
- **Parent Workspace Container Auto-Delegation:** Auto-detects multi-project parent folders (e.g. `_fxmedia`) and seamlessly delegates to scanning and auto-seeding each sub-project into `10_Projects/`.
- **Automated Tests:** 38 comprehensive automated tests passing 100%.

For complete release details, see [docs/changelog/v1.3.0-alpha.md](docs/changelog/v1.3.0-alpha.md).

---

## [1.2.0-alpha] - 2026-08-29

### 🚀 Added
- **Auto-Inspector & Ownership Classifier:** Automatically categorizes repositories into Active Projects (`10_Projects/`), External Cloned Study References (`20_Knowledge/External_Repos/`), Agent Skill Mesh (`00_System/Agent_Skills/`), and Knowledge Documentation (`20_Knowledge/References/`).
- **Multi-Language Manifest Parser:** Dependency and stack parsing for Python (`pyproject.toml`, `requirements.txt`), Node/TypeScript (`package.json`), Rust (`Cargo.toml`), Go (`go.mod`), and Docker.
- **Auto-Entity Linker Engine:** Eliminates orphan nodes by automatically resolving `workspace_path` to Project Hubs (`[[10_Projects/...]]`) and chronological links (`[[99_Daily/...]]`).
- **Zero-Click Project Auto-Provisioning:** Automatically scans and provisions project cards in `10_Projects/` during session ingestion if the project card is missing.
- **Bidirectional Backlink Injector:** Automatically adds session links to the project's README file.
- **Targeted & Batch Ingestion CLI:** Added `devbrain ingest project <path> [--type ...]`, `devbrain ingest projects [--dir ...]`, and `devbrain ingest all`.
- **Automated Tests:** 35 comprehensive automated tests passing 100%.

For complete release details, see [docs/changelog/v1.2.0-alpha.md](docs/changelog/v1.2.0-alpha.md).

---

## [1.1.0-alpha] - 2026-08-29

### 🚀 Added
- **Multi-Agent Storage Discovery Engine:** Dynamic detection of session directories for Google Antigravity IDE, Antigravity CLI (`agy`), Claude Code, Cline, and Aider.
- **Secret Redaction Regex Sanitizer:** Automated credential scrubbing for OpenAI, Anthropic, Google, and GitHub API keys, Bearer headers, and passwords into safe `[REDACTED_SECRET]` placeholders.
- **Session Artifact Extractor & Formatter:** Formats walkthroughs, plans, and transcripts into Obsidian notes with standardized YAML frontmatter.
- **CLI Commands:** Added `devbrain ingest [--from <agent>] [--dry-run] [--watch]` and alias `devbrain pull` with deduplication registry (`.brain_data/ingested_sessions.json`).
- **Automated Tests:** 28 passing unit, integration, and E2E tests in ~15s.

### 🐛 Fixed
- **YAML Frontmatter Malformation:** Fixed unescaped newlines and raw `<USER_REQUEST>` XML tags from transcript fallbacks breaking Obsidian Properties parser.
- **Storage Disambiguation:** Split `antigravity` into `antigravity-ide` and `antigravity-cli` destination folders.

### 🔄 Changed
- **Live Dataview Inbox Template:** Embedded live Dataview queries into `_Inbox_Index.md` template for automatic real-time table rendering in Obsidian.

For complete release details, see [docs/changelog/v1.1.0-alpha.md](docs/changelog/v1.1.0-alpha.md).

---

## [1.0.0-alpha] - 2026-08-29

### 🚀 Milestone: Level 1 Standalone Local Zero-Friction Core Complete
- **Pytest Suite:** 23 Unit, Integration, and End-to-End lifecycle tests passing 100% in <10s.
- **Performance Benchmarking:** Validated sub-20ms hybrid search latency (p50 ~8ms, p95 ~18ms) and ~135MB active RAM footprint on CPU.
- **Developer Documentation:** Full `README.md` with Quickstart, CLI reference, MCP pairing guide, and taxonomy schema.
- **Packaging:** Verified package installation and entry point execution (`pip install -e .`).

For complete release details, see [docs/changelog/v1.0.0-alpha.md](docs/changelog/v1.0.0-alpha.md).

---

## [0.3.0-alpha] - 2026-08-29

### 🚀 Added
- **FastMCP Protocol Server:** Integrated MCP 2.x SDK with stdio transport and background incremental indexer.
- **4 Core AI Memory Tools:** `search_brain`, `get_project_context`, `write_agent_log`, `load_skill`.
- **AI Client Auto-Configurator:** Zero-friction registration for Antigravity IDE (`mcp_config.json`) and Claude Code (`~/.claude.json`).
- **Agent Skill Commands:** Added `devbrain skill list`, `devbrain skill add <name>`, and `devbrain skill symlink`.
- **Clean Uninstallation:** Added `devbrain uninstall [--purge]`.

For complete release details, see [docs/changelog/v0.3.0-alpha.md](docs/changelog/v0.3.0-alpha.md).

---

## [0.2.0-alpha] - 2026-08-29

### 🚀 Added
- **Markdown & Frontmatter Parser:** Extracted YAML frontmatter, tags, `[[Wikilinks]]`, and title fallbacks.
- **Header-Aware Hierarchical Chunker:** Splits sections preserving heading breadcrumbs and sliding sub-chunks.
- **FastEmbed & Rank-BM25 Hybrid Engine:** Dense vector similarity (CPU ONNX) + sparse keyword search with score fusion.
- **Persistent Embedded Storage:** Binary vectors (`vectors.npy`) and chunk metadata (`index_metadata.json`) in `.brain_data/`.
- **Live Vault Watcher (`watchdog`):** Real-time incremental re-indexing with debounce queue for live typing.
- **CLI Commands:** Added `devbrain index` and `devbrain search` with Rich terminal formatting.

For complete release details, see [docs/changelog/v0.2.0-alpha.md](docs/changelog/v0.2.0-alpha.md).

---

## [0.1.0-alpha] - 2026-08-29

### 🚀 Added
- **Project Structure & Packaging:** Configured `pyproject.toml` (Hatchling build backend), package structure `src/devbrain/`, and `.gitignore`.
- **Configuration Manager (`.brainrc.json`):** Pydantic schema validation, auto-lookup via `find_config()`, and safe I/O handlers.
- **Full 07 Taxonomy Vault Scaffolder:** Non-destructive initialization generating standard directories and templates.
- **CLI Commands (`Typer` & `Rich`):** Interactive `devbrain init` wizard and `devbrain status` health check table.
- **English Localization:** Translated all CLI outputs, interactive prompts, and starter Markdown notes to standard English.

For complete release details, see [docs/changelog/v0.1.0-alpha.md](docs/changelog/v0.1.0-alpha.md).
