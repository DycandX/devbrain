# 🏃‍♂️ Sprints Index - Level 1: Standalone Local

Dokumen ini memetakan seluruh Sprint dan Task yang harus diselesaikan untuk merampungkan **Level 1: Standalone Local (Zero-Friction Core & Extensions)**.

---

## 📋 Daftar Sprint & Task Level 1

### 🚀 [Sprint 01: Project Setup, CLI Scaffolding & Configuration](./sprint-01/)
| Task | Deskripsi | Target File | Status |
| :--- | :--- | :--- | :--- |
| 📄 [Task 01](./sprint-01/task-01-pyproject-and-package-structure.md) | Setup `pyproject.toml` & Struktur Package | `pyproject.toml`, `src/devbrain/cli/main.py` | ✅ Done |
| 📄 [Task 02](./sprint-01/task-02-config-and-vault-scaffolder.md) | Config Schema (`.brainrc.json`) & Vault Scaffolder | `src/devbrain/core/config.py`, `scaffolder.py` | ✅ Done |
| 📄 [Task 03](./sprint-01/task-03-cli-init-and-status-commands.md) | CLI Init Wizard & Status Command | `src/devbrain/cli/commands/init_cmd.py` | ✅ Done |

---

### 🔍 [Sprint 02: Hybrid Indexer & Real-time Vault Watcher](./sprint-02/)
| Task | Deskripsi | Target File | Status |
| :--- | :--- | :--- | :--- |
| 📄 [Task 01](./sprint-02/task-01-markdown-parser-and-chunker.md) | Markdown Parser & Header-Aware Chunker | `src/devbrain/engine/parser.py`, `chunker.py` | ✅ Done |
| 📄 [Task 02](./sprint-02/task-02-fastembed-and-bm25-hybrid-engine.md) | FastEmbed & Rank-BM25 Hybrid Search Engine | `src/devbrain/engine/hybrid_search.py` | ✅ Done |
| 📄 [Task 03](./sprint-02/task-03-vault-watcher-and-incremental-indexer.md) | Watchdog Vault Watcher & Incremental Indexer | `src/devbrain/watcher/vault_watcher.py` | ✅ Done |
| 📄 [Task 04](./sprint-02/task-04-cli-search-and-index-commands.md) | CLI Search & Index Commands | `src/devbrain/cli/commands/search_cmd.py` | ✅ Done |

---

### ⚡ [Sprint 03: FastMCP Protocol Gateway & AI Client Auto-Config](./sprint-03/)
| Task | Deskripsi | Target File | Status |
| :--- | :--- | :--- | :--- |
| 📄 [Task 01](./sprint-03/task-01-fastmcp-stdio-server.md) | FastMCP Stdio Server Setup | `src/devbrain/mcp_server/server.py` | ✅ Done |
| 📄 [Task 02](./sprint-03/task-02-mcp-tools-implementation.md) | Implementasi 4 Core MCP Tools | `src/devbrain/mcp_server/server.py` | ✅ Done |
| 📄 [Task 03](./sprint-03/task-03-ide-auto-configurator-and-skills-symlink.md) | IDE Auto-Configurator & Agent Skill Manager | `src/devbrain/core/client_config.py` | ✅ Done |
| 📄 [Task 04](./sprint-03/task-04-cli-uninstall-and-clean-teardown.md) | CLI Uninstall & Clean Teardown Command | `src/devbrain/cli/commands/uninstall_cmd.py` | ✅ Done |

---

### 🧪 [Sprint 04: Integration Testing, Benchmarking & Packaging](./sprint-04/)
| Task | Deskripsi | Target File | Status |
| :--- | :--- | :--- | :--- |
| 📄 [Task 01](./sprint-04/task-01-integration-and-unit-tests.md) | Pytest Suite Komprehensif (23 Tests) | `tests/test_*.py` | ✅ Done |
| 📄 [Task 02](./sprint-04/task-02-benchmarking-and-profiling.md) | Benchmarking Latensi (<20ms) & RAM Profiling | `benchmarks/*.py` | ✅ Done |
| 📄 [Task 03](./sprint-04/task-03-developer-guide-and-release-readiness.md) | Developer Quickstart & Packaging | `README.md`, `docs/changelog/` | ✅ Done |

---

### 🚜 [Sprint 05: Automated Session Ingestion & Initial Vault Seeding](./sprint-05/)
| Task | Deskripsi | Target File | Status |
| :--- | :--- | :--- | :--- |
| 📄 [Task 01](./sprint-05/task-01-agent-storage-discovery-and-secret-sanitizer.md) | Multi-Agent Storage Discovery & Secret Sanitizer | `src/devbrain/harvester/discovery.py`, `sanitizer.py` | ✅ Done |
| 📄 [Task 02](./sprint-05/task-02-session-artifact-extractor-and-formatter.md) | Session Artifact Extractor & Markdown Formatter | `src/devbrain/harvester/extractor.py`, `formatter.py` | ✅ Done |
| 📄 [Task 03](./sprint-05/task-03-cli-ingest-command-and-continuous-watcher.md) | CLI `devbrain ingest` & Continuous Service | `src/devbrain/cli/commands/ingest_cmd.py`, `service.py` | ✅ Done |
| 📄 [Task 04](./sprint-05/task-04-integration-testing-and-benchmarking.md) | Automated Tests & Documentation | `tests/test_ingestion.py`, `docs/changelog/` | ✅ Done |

---

### 🕸️ [Sprint 06: Graph Mesh, Workspace Harvester & Targeted Ingestion](./sprint-06/)
| Task | Deskripsi | Target File | Status |
| :--- | :--- | :--- | :--- |
| 📄 [Task 01](./sprint-06/task-01-auto-inspector-repo-scanner-and-manifest-parser.md) | Auto-Inspector, Repo Scanner & Manifest Parser | `src/devbrain/harvester/inspector.py`, `manifest_parser.py` | ✅ Done |
| 📄 [Task 02](./sprint-06/task-02-auto-seeding-multi-type-cards.md) | Auto-Seeding Multi-Type Cards (Projects, Knowledge, Skills) | `src/devbrain/harvester/project_harvester.py` | ✅ Done |
| 📄 [Task 03](./sprint-06/task-03-auto-entity-linker-and-backlink-injector.md) | Auto-Entity Linker & Backlink Injector | `src/devbrain/harvester/entity_linker.py` | ✅ Done |
| 📄 [Task 04](./sprint-06/task-04-cli-targeted-single-and-batch-ingestion.md) | CLI Targeted Single & Batch Ingestion (`project`, `projects`, `all`) | `src/devbrain/cli/commands/ingest_cmd.py` | ✅ Done |
| 📄 [Task 05](./sprint-06/task-05-automated-test-suite-and-release-v1-2-0.md) | Automated Test Suite & Release `v1.2.0-alpha` | `tests/test_project_ingestion.py`, `CHANGELOG.md` | ✅ Done |

---

### 🧠 [Sprint 07: Smart Codebase Synthesizer & README-less Harvester Upgrade](./sprint-07/)
| Task | Deskripsi | Target File | Status |
| :--- | :--- | :--- | :--- |
| 📄 [Task 01](./sprint-07/task-01-codebase-tree-and-entrypoint-analyzer.md) | Codebase Tree Generator & Entrypoint Analyzer | `src/devbrain/harvester/tree_analyzer.py` | ✅ Done |
| 📄 [Task 02](./sprint-07/task-02-intelligent-project-card-synthesis.md) | Intelligent Project Card Synthesis for README-less Projects | `src/devbrain/harvester/project_harvester.py` | ✅ Done |
| 📄 [Task 03](./sprint-07/task-03-parent-workspace-folder-auto-delegation.md) | Workspace Container / Multi-Project Folder Auto-Delegation | `src/devbrain/harvester/inspector.py`, `service.py` | ✅ Done |
| 📄 [Task 04](./sprint-07/task-04-automated-test-suite-and-release-v1-3-0.md) | Automated Test Suite & Release `v1.3.0-alpha` | `tests/test_codebase_synthesizer.py`, `CHANGELOG.md` | ✅ Done |

---

### ⚡ [Sprint 08: Unified Ingestion UX & 4-Layer IDE Deep Links](./sprint-08/)
| Task | Deskripsi | Target File | Status |
| :--- | :--- | :--- | :--- |
| 📄 [Task 01](./sprint-08/task-01-unified-dwim-ingest-router.md) | Unified Dynamic DWIM Ingest CLI Router | `src/devbrain/cli/commands/ingest_cmd.py` | ✅ Done |
| 📄 [Task 02](./sprint-08/task-02-interactive-ide-deep-links.md) | Interactive IDE Deep Links & File Protocol Integration | `src/devbrain/harvester/project_harvester.py` | ✅ Done |
| 📄 [Task 03](./sprint-08/task-03-self-ingestion-guard.md) | Self-Ingestion Guard in IngestionService | `src/devbrain/harvester/service.py` | ✅ Done |
| 📄 [Task 04](./sprint-08/task-04-automated-test-suite-and-release-v1-4-0.md) | Automated Test Suite & Release `v1.4.0-alpha` | `tests/test_unified_ingest.py`, `CHANGELOG.md` | ✅ Done |
