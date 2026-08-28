# 🧠 devbrain — Central AI Second Brain Hub

> **Single Source of Truth (SSOT) for Multi-Agent Coding & Obsidian.**

`devbrain` connects your AI coding assistants (**Antigravity IDE**, **Claude Code**, **Hermes**, **OpenCode**) directly to a local **Obsidian Vault** using the Model Context Protocol (MCP) and Hybrid Semantic Search.

---

## 🚀 Quickstart (Zero-Friction Standalone Mode)

### 1. Installation
```bash
pip install -e .
```

### 2. Initialize Vault
```bash
devbrain init E:/MyDevBrainVault
```

### 3. Check Status
```bash
devbrain status
```

---

## 🛠️ Tech Stack
- **Language:** Python 3.10+
- **CLI Framework:** Typer + Rich
- **Protocol:** FastMCP (Stdio & SSE)
- **Hybrid Search:** FastEmbed (Local CPU ONNX `bge-small-en-v1.5`) + Rank-BM25
- **Vault Watcher:** Watchdog File System Event Listener
- **Vault Storage:** Markdown (.md) + YAML Frontmatter + `[[Wikilinks]]`

---

## 📚 Documentation
- [Documentation Index](docs/_index.md)
- [Master Blueprint (docs/_summary/00.md)](docs/_summary/00.md)
- [PRD Level 1 (docs/prd/01-prd-level-1-standalone-local.md)](docs/prd/01-prd-level-1-standalone-local.md)
- [Implementation Plan (docs/implementation-plan/01-implementation-plan-level-1-standalone.md)](docs/implementation-plan/01-implementation-plan-level-1-standalone.md)
- [Sprint Tasks (docs/sprints/level-1/)](docs/sprints/level-1/)
