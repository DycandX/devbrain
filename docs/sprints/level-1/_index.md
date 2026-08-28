# 🏃‍♂️ Sprints Index - Level 1: Standalone Local

Dokumen ini memetakan seluruh Sprint dan Task yang harus diselesaikan untuk merampungkan **Level 1: Standalone Local (Zero-Friction Core)**.

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
| 📄 [Task 01](./sprint-04/task-01-integration-and-unit-tests.md) | Pytest Suite Komprehensif | `tests/test_*.py` | ⏳ Todo |
| 📄 [Task 02](./sprint-04/task-02-benchmarking-and-profiling.md) | Benchmarking Latensi (<20ms) & RAM Profiling | `benchmarks/*.py` | ⏳ Todo |
| 📄 [Task 03](./sprint-04/task-03-developer-guide-and-release-readiness.md) | Developer Quickstart & Packaging | `README.md`, `docs/changelog/` | ⏳ Todo |
