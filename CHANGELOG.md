# Changelog

All notable changes to the `devbrain` project are documented here and in [`docs/changelog/`](docs/changelog/_index.md).

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- **4 Core AI Memory Tools:**
  - `search_brain`: Semantic + keyword hybrid query across notes.
  - `get_project_context`: Direct retrieval of active project architecture & roadmap notes from `10_Projects/`.
  - `write_agent_log`: Append-only session notes in `90_Agent_Inbox/` with immutable UUID partition tags.
  - `load_skill`: Just-in-time loading of agent workflows from `00_System/Agent_Skills/`.
- **AI Client Auto-Configurator:** Zero-friction registration for Antigravity IDE (`mcp_config.json`) and Claude Code (`~/.claude.json`).
- **Agent Skill Commands:** Added `devbrain skill list`, `devbrain skill add <name>`, and `devbrain skill symlink`.
- **Clean Uninstallation:** Added `devbrain uninstall [--purge]` to safely remove MCP registrations without affecting Markdown notes.

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
