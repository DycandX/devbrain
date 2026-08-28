# 🧠 Central AI Brain Hub - Brainstorming Documents

Folder ini berisi catatan eksplorasi arsitektur, strategi integrasi sistem, dan detail teknis hasil percakapan brainstorming untuk proyek **Central AI Brain Hub**.

| Document | Topic | Key Focus |
| :--- | :--- | :--- |
| 📄 [01: Arsitektur Dasar Central Brain](./01-arsitektur-dasar-central-brain.md) | Arsitektur Sistem & Komponen | Network Mesh (Tailscale), Storage & Vector Layer, FastMCP Gateway, Single Source of Truth (SSOT) |
| 📄 [02: Integrasi Obsidian Core KB](./02-integrasi-obsidian-core-knowledge-base.md) | Human-Agent UI & Obsidian Integration | Central Obsidian Vault, Ingestion Pipeline Watcher, Human-Agent Separation Protocol, Direct MCP vs REST |
| 📄 [03: Penyimpanan Memory Antigravity](./03-penyimpanan-memory-antigravity-ide-cli.md) | Antigravity IDE & agy CLI Storage Map | Struktur `~/.gemini/antigravity/brain/`, artifacts (`task.md`, `walkthrough.md`), dan `transcript.jsonl` |
| 📄 [04: Peta Penyimpanan Multi-Agent](./04-peta-penyimpanan-multi-agent-cli.md) | Multi-Agent Ecosystem Storage | Peta penyimpanan Claude Code, Hermes, Aider, OpenCode, Cline; Passive Capture vs Active MCP Context |
| 📄 [05: Komparasi Repo Open Source](./05-komparasi-repo-open-source.md) | Open-Source Landscape & Tools | Evaluasi Mem0, Khoj, Letta (MemGPT), AnythingLLM, dan MCP Obsidian Servers |
| 📄 [06: Siklus Hidup Data & Sync Multi-Device](./06-siklus-hidup-data-dan-sync-multi-device.md) | Data Lifecycle & Conflict Resolution | Mencegah race condition/file lock saat multi-agent aktif, Append-Only UUID Partitioning, Syncthing over Tailscale |
| 📄 [07: Taksonomi Vault & Standar Metadata](./07-taksonomi-vault-dan-standar-metadata.md) | Obsidian Ontology & Schema | Struktur folder (Hybrid PARA + Inbox), skema YAML Frontmatter, konvensi `[[Wikilinks]]`, Dataview Dashboard |
| 📄 [08: Server Stack Jarvis & FastMCP](./08-server-stack-jarvis-dan-fastmcp.md) | Homeserver Stack & MCP Gateway | Docker Compose lengkap (Qdrant Vector DB, Ollama `bge-m3` local embedding, FastMCP SSE Server, Watcher) |
| 📄 [09: Client Adapters & Distillation](./09-client-adapters-dan-distillation-pipeline.md) | Client Connectivity & Ingestion | Konfigurasi MCP client (Antigravity, Claude Code, Hermes), Python Local Session Harvester & LLM Distiller |
| 📄 [10: Security, Privacy & Boundary Protocol](./10-security-privacy-dan-boundary-protocol.md) | Security & Work vs Personal Boundary | Isolasi konteks kerja (office) vs personal, Regex Secret Redactor/Sanitizer, Tailscale ACL & Disaster Recovery |
| 📄 [11: Sentralisasi Agent Skills & Efisiensi Token](./11-sentralisasi-agent-skills-dan-efisiensi-token.md) | Skills Mesh & Token Economics | Sentralisasi folder `Agent_Skills` (Symlink & FastMCP), analisis efisiensi konsumsi token (hemat 60-85% via JIT retrieval) |
| 📄 [12: Opsi Deployment & Konsep Embedding](./12-opsi-deployment-dan-konsep-embedding.md) | Deployment Profiles & Embeddings | Penjelasan konsep Semantic Search/Vector, opsi Embedding (Cloud API vs CPU FastEmbed vs Ollama), 3 Profil Deployment (Standalone 1 Laptop, P2P Sync, Homeserver) |
| 📄 [13: Korelasi Projek FXMedia & Hybrid Graph-RAG](./13-korelasi-projek-fxmedia-dan-hybrid-graph-rag.md) | Synergies & Hybrid Graph-RAG | Hubungan riset `_fxmedia` (Qdrant, BM25, LangChain/LangGraph, Neo4j) dengan Central Brain Hub, arsitektur Hybrid Dense+Sparse Search & Graph RAG |
| 📄 [14: Panduan Implementasi Praktis & Koneksi Obsidian](./14-panduan-implementasi-praktis-dan-koneksi-obsidian.md) | Practical Guide & Obsidian Connect | Penjelasan inti konsep, 3 modul program yang dibuat (`mcp_brain_server`, `vault_indexer`, `session_harvester`), cara koneksi file-system, persiapan, dan setup server headless tanpa app Obsidian |
| 📄 [15: Multi-Vault & Strategi Adopsi Existing Vault](./15-multi-vault-dan-strategi-adopsi-existing-vault.md) | Multi-Vault & Vault Adoption | Konsep Multi-Vault (Work vs Personal vs Server), metadata scoping, Auto-Scaffolding vs Non-destructive Existing Vault attachment, & `.brainignore` |
