# Implementation Plan - Level 1: Standalone Local (Zero-Friction Core)

| Attribute | Detail |
| :--- | :--- |
| **Project** | `devbrain` (Central AI Brain Hub) |
| **Tier** | **Level 1: Standalone Local** |
| **Derived From** | [PRD Level 1: Standalone Local](../prd/01-prd-level-1-standalone-local.md) |
| **Tech Stack** | Python 3.10+ (Typer, Rich, FastMCP, FastEmbed, Rank-BM25, Watchdog, Pydantic) |
| **Status** | Ready for Execution |

---

## 1. Arsitektur Komponen Teknis Level 1

```
devbrain/ (Python Package)
├── cli/
│   ├── main.py                  # Entry point CLI (Typer app)
│   ├── commands/
│   │   ├── init_cmd.py          # Wizard interaktif setup vault & embedding
│   │   ├── status_cmd.py        # Status & health check vault
│   │   ├── search_cmd.py        # Terminal search runner
│   │   ├── index_cmd.py         # Manual indexing command
│   │   ├── skill_cmd.py         # Skill registry & symlink manager
│   │   └── uninstall_cmd.py     # Clean teardown & un-register MCP
│   └── ui/
│       └── console.py           # Rich console formatting & spinners
├── core/
│   ├── config.py                # Pydantic schema .brainrc.json
│   ├── scaffolder.py            # Vault folder tree & templates generator
│   └── client_config.py         # Auto-config Antigravity IDE & Claude JSON
├── engine/
│   ├── parser.py                # Markdown YAML frontmatter & content parser
│   ├── chunker.py               # Header-aware markdown chunker
│   ├── embeddings.py            # FastEmbed (CPU ONNX) provider
│   ├── bm25.py                  # Rank-BM25 sparse keyword indexer
│   ├── hybrid_search.py         # Hybrid search fusion (Dense + Sparse)
│   └── storage.py               # Embedded vector cache & document store
├── watcher/
│   └── vault_watcher.py         # Watchdog file system event listener
└── mcp_server/
    ├── server.py                # FastMCP Stdio server instance
    └── tools/
        ├── search_brain.py      # MCP Tool: search_brain
        ├── project_context.py   # MCP Tool: get_project_context
        ├── agent_logger.py      # MCP Tool: write_agent_log (Append-only UUID)
        └── skill_loader.py      # MCP Tool: load_skill (JIT loader)
```

---

## 2. Rencana Sprint & Pembagian Task

Level 1 dibagi menjadi **4 Sprint Berurutan**:

```text
┌────────────────────────────────────────────────────────────────────────┐
│ [ SPRINT 01: Project Setup, CLI Scaffolding & Configuration ]          │
│ Task 01: pyproject.toml, package structure, dependencies               │
│ Task 02: Config schema (.brainrc.json) & Vault Scaffolder              │
│ Task 03: CLI `devbrain init` wizard & `devbrain status`                │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ [ SPRINT 02: Hybrid Indexer & Real-time Vault Watcher ]                │
│ Task 01: Markdown parser & Header-aware chunker                        │
│ Task 02: FastEmbed + Rank-BM25 Hybrid Search Engine                    │
│ Task 03: Watchdog incremental vault watcher                            │
│ Task 04: CLI `devbrain search` & `devbrain index`                      │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ [ SPRINT 03: FastMCP Gateway & AI Client Auto-Config ]                 │
│ Task 01: FastMCP Stdio server setup                                    │
│ Task 02: 4 Core Tools (search_brain, context, write_log, load_skill)   │
│ Task 03: Auto-config Antigravity/Claude JSON & `devbrain skill`        │
│ Task 04: CLI `devbrain uninstall` clean teardown                       │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ [ SPRINT 04: Integration Testing, Benchmarking & Packaging ]           │
│ Task 01: Pytest suite (CLI, Indexer, MCP Tools, Config)                │
│ Task 02: Benchmark & RAM profiling on 1,000 documents                  │
│ Task 03: Developer Quickstart & `pip install -e .` validation          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Rincian Task Per Sprint

### Sprint 01: Project Setup, CLI Scaffolding & Configuration
* 📄 [Task 01: Setup Proyek & Struktur Package](../sprints/level-1/sprint-01/task-01-pyproject-and-package-structure.md)
* 📄 [Task 02: Config Schema & Vault Scaffolder](../sprints/level-1/sprint-01/task-02-config-and-vault-scaffolder.md)
* 📄 [Task 03: Perintah CLI Init & Status](../sprints/level-1/sprint-01/task-03-cli-init-and-status-commands.md)

### Sprint 02: Hybrid Indexer & Real-time Vault Watcher
* 📄 [Task 01: Markdown Parser & Chunker](../sprints/level-1/sprint-02/task-01-markdown-parser-and-chunker.md)
* 📄 [Task 02: FastEmbed & BM25 Hybrid Engine](../sprints/level-1/sprint-02/task-02-fastembed-and-bm25-hybrid-engine.md)
* 📄 [Task 03: Vault Watcher & Incremental Indexer](../sprints/level-1/sprint-02/task-03-vault-watcher-and-incremental-indexer.md)
* 📄 [Task 04: CLI Search & Index Commands](../sprints/level-1/sprint-02/task-04-cli-search-and-index-commands.md)

### Sprint 03: FastMCP Gateway & AI Client Auto-Config
* 📄 [Task 01: FastMCP Stdio Server Setup](../sprints/level-1/sprint-03/task-01-fastmcp-stdio-server.md)
* 📄 [Task 02: Implementasi 4 Core MCP Tools](../sprints/level-1/sprint-03/task-02-mcp-tools-implementation.md)
* 📄 [Task 03: Auto-Configurator IDE & Skill Manager](../sprints/level-1/sprint-03/task-03-ide-auto-configurator-and-skills-symlink.md)
* 📄 [Task 04: CLI Uninstall & Clean Teardown](../sprints/level-1/sprint-03/task-04-cli-uninstall-and-clean-teardown.md)

### Sprint 04: Integration Testing, Benchmarking & Packaging
* 📄 [Task 01: Integration & Unit Tests](../sprints/level-1/sprint-04/task-01-integration-and-unit-tests.md)
* 📄 [Task 02: Benchmarking & RAM Profiling](../sprints/level-1/sprint-04/task-02-benchmarking-and-profiling.md)
* 📄 [Task 03: Quickstart & Release Packaging](../sprints/level-1/sprint-04/task-03-developer-guide-and-release-readiness.md)

### Sprint 05: Automated Session Ingestion & Initial Vault Seeding
* 📄 [Task 01: Multi-Agent Storage Discovery & Secret Sanitizer](../sprints/level-1/sprint-05/task-01-agent-storage-discovery-and-secret-sanitizer.md)
* 📄 [Task 02: Session Artifact Extractor & Formatter](../sprints/level-1/sprint-05/task-02-session-artifact-extractor-and-formatter.md)
* 📄 [Task 03: CLI Ingest Command & Continuous Watcher](../sprints/level-1/sprint-05/task-03-cli-ingest-command-and-continuous-watcher.md)
* 📄 [Task 04: Automated Tests & Documentation](../sprints/level-1/sprint-05/task-04-integration-testing-and-benchmarking.md)

---

## 4. Standar Kualitas & Definisi Selesai (*Definition of Done*)

Setiap task dinyatakan **SELESAI (DONE)** jika:
1. Kode telah diimplementasikan dengan type hints lengkap (`typing`) dan docstrings standar.
2. Tidak menimbulkan error linter (`ruff` / `flake8`).
3. Memiliki unit test yang lulus uji.
4. Diuji langsung menggunakan perintah CLI `devbrain`.
5. Perubahan di-commit ke Git dengan format *Conventional Commits*.
