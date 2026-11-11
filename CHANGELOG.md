# Changelog

All notable changes to the `devbrain` project are documented here and in [`docs/changelog/`](docs/changelog/_index.md).

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.11.0-alpha] - 2026-11-11 (Unreleased)

### 🚀 Added
- **Memory content guard:** `remember` refuses text that reads as instructions to an agent, runs code or sends data elsewhere, contains credentials, or hides Unicode characters.
- **Write approval:** with `memory.write_approval`, new memories wait as `pending` and stay invisible until approved.
- **`devbrain memory`:** `list`, `pending`, `approve`, `reject`, `pin`, `unpin`, `edit`, `forget`, `ledger`.
- **Core memory:** pinned memories appear in every briefing within a character budget per project and for global memories; `remember` gains `pinned`.
- **Memory ledger:** append-only record of every write, approval, edit, pin, and blocked attempt.

### 📊 Measured
- Guard: 16 malicious samples refused, 8 look-alike ordinary facts accepted.
- **Automated Tests:** 132 passing.

For complete details, see [docs/changelog/v1.11.0-alpha.md](docs/changelog/v1.11.0-alpha.md).

---

## [1.10.0-alpha] - 2026-11-11 (Unreleased)

### 🚀 Added
- **`devbrain lint`:** checks every note against a shared frontmatter schema and known defects; `--fix` repairs them by editing frontmatter line by line.
- **`devbrain adr supersede <old> <new>`:** marks a decision as replaced and links both notes; briefings show only accepted decisions.

### 🐛 Fixed
- Antigravity session titles no longer carry the `<USER_SETTINGS_CHANGE>` notice; whole harness tag blocks are dropped.
- Session notes no longer link to daily notes that do not exist.
- Project cards get `aliases`, so Obsidian lists them by name instead of "README"; they also keep their `created` time across rescans.
- Session links on project cards no longer pick up a stray `(Live Dataview):` suffix.
- Frontmatter values are written with `json.dumps`, fixing invalid YAML from Windows paths and Markdown badges.
- Dataview, Tasks, Bases, and query blocks are no longer indexed.

### 📊 Measured
- Main vault migrated: 142 of 143 notes repaired; 30 broken daily links, 34 noisy session notes, and 3 invalid frontmatter blocks removed.
- **Automated Tests:** 100 passing.

For complete details, see [docs/changelog/v1.10.0-alpha.md](docs/changelog/v1.10.0-alpha.md).

---

## [1.9.0-alpha] - 2026-11-11 (Unreleased)

### 🚀 Added
- **Nested workspace scan:** batch scanning descends into folders that hold several projects (up to 3 levels), instead of looking only one level below the workspace root.
- **Project groups:** a multi-project folder becomes the group of its projects (`group` in frontmatter, `group/<name>` tag). Labels and sandbox status are configurable per folder in `.brainrc.json` (`project_groups`).
- **Sandboxes:** groups whose name starts with `test`, `sandbox`, `playground`, `scratch`, `tmp`, or `temp` are marked sandbox. Their cards stay searchable but never enter another project's briefing.
- **More project types:** Flutter (`pubspec.yaml`), PHP / Laravel (`composer.json`), Java (`pom.xml`, Gradle), .NET (`*.csproj`, `*.sln`), C / C++ (`CMakeLists.txt`, `Makefile`).

### 🐛 Fixed
- **Vault folders** (`.brainrc.json`, or `.obsidian` without a code manifest) are no longer scanned as projects.
- **Card name clashes:** two projects with the same name get separate cards instead of overwriting each other; scaffold default names such as `laravel` fall back to the folder name.
- **Rescanning a project** no longer drops the session links collected on its card.
- **Dry runs** of a batch scan now report what would be created; they returned nothing before.

### 📊 Measured
- On a real workspace of 45 top-level folders, the scan finds 65 projects (about 26 before) in roughly 19 seconds.
- **Automated Tests:** 91 passing.

For complete details, see [docs/changelog/v1.9.0-alpha.md](docs/changelog/v1.9.0-alpha.md).

---

## [1.8.1-alpha] - 2026-11-10 (Unreleased)

### 🐛 Fixed
Found by running `build_task_context` against a real vault for the first time.
- **Project summary** no longer starts with raw YAML frontmatter cut mid-sentence; it now gives path, status, the first prose sentence of the overview, and runnable scripts.
- **Project descriptions** skip README badges and images (`first_prose_paragraph`), in both the harvester and the briefing.
- **Relevant notes** are selected instead of taking the top three search hits: the project's own notes first, notes from elsewhere only when the semantic and keyword rankers agree (fused score of at least 0.6), and never session logs linked to another project.
- **Recent sessions** are matched through their Project Hub link and sorted by creation date; the section was always empty before.

### 📊 Measured
- On the real vault, cosine similarity separates relevant from irrelevant top hits by only about 0.05, so a similarity floor alone cannot gate a briefing; ranker agreement can.
- **Automated Tests:** 83 passing.

For complete details, see [docs/changelog/v1.8.1-alpha.md](docs/changelog/v1.8.1-alpha.md).

---

## [1.8.0-alpha] - 2026-11-10 (Unreleased)

### 🚀 Added
- **Long-term memory:** MCP tools `remember`, `recall`, and `forget`. SQLite holds the record; each active memory is mirrored as a note in `00_System/Memories/` so it is visible in Obsidian and searchable. Project-scoped memories stay within their project, and superseded or forgotten memories drop out of recall.
- **Size-capped tool output:** `search_brain` returns one line per note by default (`detail="snippet"` for excerpts); new `read_note(path, heading, max_chars)` reads a note or a single section; `get_project_context` and user preferences are capped and say how to fetch the rest.
- **`devbrain usage`:** per-project Claude Code token usage (context, cache hit ratio, output, tool calls, calls to `central-brain`) read from local transcripts.
- `build_task_context` includes remembered facts relevant to the task.

### 🐛 Fixed
- **SQLite connection leak:** connections were never closed, which kept `brain.db` locked on Windows.
- **Path containment:** `load_skill` accepts only plain skill names, and `read_note` refuses paths outside the vault.

### 📊 Measured
- 12 tool definitions cost about 1,470 tokens per session; index-mode search output is 37% smaller than snippet mode.
- **Automated Tests:** 75 passing.

For complete details, see [docs/changelog/v1.8.0-alpha.md](docs/changelog/v1.8.0-alpha.md).

---

## [1.7.0-alpha] - 2026-11-10 (Unreleased)

### 🐛 Fixed
- **Test suite overwrote real IDE configs:** every `pytest` run rewrote `~/.claude.json` and the Antigravity `mcp_config.json` files to point `central-brain` at a temporary vault. Tests now run against an isolated home directory.
- **IDE config writes:** now atomic; an unparseable config is left untouched instead of being replaced; only existing Antigravity locations are written.
- **Dependencies:** `mcp>=2.0.0` (the code uses the 2.x `MCPServer` API), `numpy` declared, unused `pydantic-settings` removed, package version aligned with `__version__`.
- **`write_agent_log`:** titles containing quotes no longer produce invalid YAML frontmatter.
- **Rules template:** documents the real `write_agent_log(summary, details, tags)` signature.
- **Engine construction:** harvesters built the search engine without the vault config, which could mix vectors from two embedding models in one index.

### 🚀 Added
- **Retrieval evaluation harness** (`benchmarks/eval_retrieval.py`): 16 notes and 38 Indonesian and English queries, reporting hit@1, hit@3, MRR, and abstain rate.
- **Reciprocal Rank Fusion with a relevance gate:** hybrid search fuses ranks instead of mismatched scores and returns nothing when no chunk is relevant.
- **Multilingual embedding model by default** (`paraphrase-multilingual-MiniLM-L12-v2`); the index records its model and rebuilds when it changes.
- **Vault watcher in `devbrain serve`** (`--watch/--no-watch`): notes edited in Obsidian are re-indexed automatically.
- **Per-session Claude Code harvester:** one note per session with goal, follow-ups, outcome, files changed, and token usage; sessions that grow are re-ingested in place.

### 📊 Measured
- Hybrid hit@1 on the eval set: 0.906 to 0.969. Abstain rate on unanswerable queries: 0.000 to 1.000.
- **Automated Tests:** 66 passing.

### ⚠️ Upgrade Notes
- Re-run `devbrain init <vault>` to repair the MCP server entry, and `devbrain index` after switching an existing vault to the multilingual model.

For complete details, see [docs/changelog/v1.7.0-alpha.md](docs/changelog/v1.7.0-alpha.md).

---

## [1.6.0-alpha] - 2026-08-30

### 🚀 Added
- **Architecture Decision Records (ADR Framework):** Dedicated `30_Decisions/` directory for architectural decisions with CLI `devbrain adr [new|list]` and automatic wikilink injection into project cards (`10_Projects/`).
- **Context Assembly Engine (`context_build` & `devbrain context`):** Rapidly primes AI agents (<0.2s) by assembling 5 context tiers: User Preferences, Project State, Active ADRs, Relevant Knowledge Base Chunks, and Recent Session Work.
- **Workspace Rules & Hierarchy of Truth Generator:** Auto-generates `AGENTS.md` and `CLAUDE.md` in client repositories (`devbrain rules init`) enforcing the strict 4-level Hierarchy of Truth.
- **Embedded SQLite Machine State & Cache:** SQLite database `.brain_data/brain.db` with WAL mode for memory scope tracking (`GLOBAL`, `PROJECT`, `TASK`, `SESSION`), confidence scoring, superseded memory handling, and file hash caching.
- **Extended Skills Mesh:** Support for external skill directories (e.g. `E:/_PROJECT/_agent-skill`) via `devbrain skill link` and project-level mounting via `devbrain skill attach`.
- **FastMCP Protocol Gateway Expansion:** Added `build_task_context`, `get_user_context`, `get_decisions`, and `record_decision` tools.
- **Automated Tests:** 55 comprehensive automated tests passing 100%.

For complete release details, see [docs/changelog/v1.6.0-alpha.md](docs/changelog/v1.6.0-alpha.md).

---

## [1.5.0-alpha] - 2026-08-29

### 🚀 Added
- **Multi-Vault Federation Management:** Connect, discover, and synchronize multiple external Obsidian vaults on the local disk via `devbrain vault [link|unlink|list|sync]`.
- **Federated Hybrid Search & Memory:** Indexes notes across Central Vault and linked vaults into a single unified search index, supporting scoped searching (`scope="all"`, `scope="central"`, `scope="<alias>"`).
- **Zero-Redundancy Directory Junction Mounting:** Native `--mount` flag on `devbrain vault link` creates Windows Directory Junctions into `20_Knowledge/Linked_Vaults/<alias>/`, enabling immediate browsing in Obsidian with 0 MB duplicate disk space.
- **Automated Tests:** 46 comprehensive automated tests passing 100%.

For complete release details, see [docs/changelog/v1.5.0-alpha.md](docs/changelog/v1.5.0-alpha.md).

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
