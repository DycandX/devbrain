# devbrain profile vs. six Hermes Agent memory add-ons

Sources are local files in `E:/_PROJECT/_Central AI Brain Hub` (paths given relative to repo root). No web sources used. Vault `E:\_PROJECT\_DevBrain_Vault` was not touched; vault numbers below come from docs that audited it.

## Q1. What version is devbrain at, and what does it do today?

### Takeaway
devbrain is at `1.11.0-alpha` (Sprint 15 done, 132 tests passing, commits since v1.7.0 not pushed). It is a local, LLM-free memory and context engine that exposes an Obsidian Markdown vault to several AI agents (Claude Code, Antigravity, later Hermes) through a 12-tool MCP server (`central-brain`), with hybrid search, a session/project harvester, guarded long-term memory with a ledger, pinned core memory, vault lint, and task briefings.

### Cited Findings
- Version `1.11.0-alpha`, branch `main`, 132 tests passing, written 2026-11-11; `pyproject.toml` version `1.11.0a0` — [HANDOFF.md](HANDOFF.md) section header table; [pyproject.toml](pyproject.toml)
- Self-definition: devbrain is "mesin memori dan konteks" for AI agents, making an Obsidian vault the shared source of truth for Claude Code, Antigravity IDE, Hermes and others via an MCP server; it is not the assistant itself. Long-term plan: personal assistant "Jarvis" with Hermes Agent as the body (runtime, chat channels, cron) and devbrain as memory — [HANDOFF.md](HANDOFF.md) section 1; [docs/brainstorming/47-hermes-agent-sebagai-badan-jarvis-jev-dan-strategi-ui.md](docs/brainstorming/47-hermes-agent-sebagai-badan-jarvis-jev-dan-strategi-ui.md) section 8
- Second goal: save agent tokens; hypothesis unproven, measuring tool `devbrain usage` exists. Measured: 384M context tokens in Claude Code, 97% cached, 0 calls to devbrain (2026-11-10) — [HANDOFF.md](HANDOFF.md) sections 1 and 6
- Dependencies are only typer, rich, pydantic, watchdog, fastembed, rank-bm25, mcp, pyyaml, numpy (no PDF/Office parsers, no crypto libs, no LLM SDK) — [pyproject.toml](pyproject.toml)
- Architecture modules: `cli/`, `core/` (config `.brainrc.json`, SQLite, fsutil atomic writes, textutil size limits, schema), `engine/` (parser, chunker, FastEmbed embeddings, BM25, storage, `hybrid_search` with RRF + relevance gate), `harvester/` (agent session discovery, extraction, secret sanitizer, project scanner), `context/` (briefing builder), `memory/` (remember/recall/forget, guard), `mcp_server/` (12 tools), `adr/`, `rules/`, `watcher/` (watchdog re-index), `maintenance/lint.py` — [HANDOFF.md](HANDOFF.md) section 3; file listing of `src/devbrain/`
- MCP tools: `search_brain` (one line per note by default, `detail="snippet"`), `read_note` (refuses paths outside vault), `build_task_context` (briefing, precision over recall), `get_project_context` (capped 6,000 chars), `remember`/`recall`/`forget` (project scope; every write goes through `memory/guard.py`; `pinned` → core memory), `get_user_context`, `get_decisions`, `record_decision`, `write_agent_log`, `load_skill` — [HANDOFF.md](HANDOFF.md) section 3; [src/devbrain/mcp_server/server.py](src/devbrain/mcp_server/server.py)
- Fixed overhead of 12 tool definitions ≈1,470 tokens per session — [HANDOFF.md](HANDOFF.md) section 6
- Hybrid search: FastEmbed embeddings (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, ~220 MB) + rank-bm25, fused with Reciprocal Rank Fusion plus a relevance gate; hit@1 0.969 on a small self-written eval corpus (16 notes, 38 questions), 6/6 unanswerable questions rejected — [HANDOFF.md](HANDOFF.md) sections 2 and 6
- Storage per vault in `.brain_data/`: `index_metadata.json` + `vectors.npy` (chunk index and vectors), `brain.db` (SQLite: memories, ADR, file cache), `ingested_sessions.json` — [HANDOFF.md](HANDOFF.md) section 3
- SQLite tables: `memories` (id, type, content, scope, project, confidence, source, status, superseded_by, metadata_json, timestamps, plus `pinned` column), `decisions`, `memory_ledger` (id, memory_id, action, source, detail, at), `file_cache` (file_path, mtime, sha256_hash, chunk_count) — [src/devbrain/core/sqlite_db.py](src/devbrain/core/sqlite_db.py) lines ~46–110
- v1.11.0 (Sprint 15) added: memory content guard (refuses text that reads as instructions to an agent, runs code / sends data elsewhere, contains credentials, or hides Unicode); `memory.write_approval` (new memories wait as `pending`, invisible until approved); `devbrain memory list/pending/approve/reject/pin/unpin/edit/forget/ledger`; core memory (pinned memories in every briefing within a char budget per project and global); append-only memory ledger of every write, approval, edit, pin and blocked attempt. Guard measured: 16 malicious samples refused, 8 look-alike facts accepted — [CHANGELOG.md](CHANGELOG.md) 1.11.0-alpha
- v1.10.0 (Sprint 14) added `devbrain lint` (shared frontmatter schema, `--fix`), `adr supersede`; main vault migrated (142 of 143 notes repaired) — [CHANGELOG.md](CHANGELOG.md) 1.10.0-alpha
- v1.9.0 nested workspace scan, project groups, sandboxes, more project types; 65 projects found in ~19 s — [CHANGELOG.md](CHANGELOG.md) 1.9.0-alpha
- Harvested agent sources today: Antigravity IDE, Antigravity CLI, Claude Code (`~/.claude/projects/*.jsonl`), Cline (VS Code globalStorage); Hermes not yet — [src/devbrain/harvester/discovery.py](src/devbrain/harvester/discovery.py) `get_default_agent_roots`; [docs/sprints/level-1/sprint-16/16-sprint-16-agent-integration-hooks-hermes.md](docs/sprints/level-1/sprint-16/16-sprint-16-agent-integration-hooks-hermes.md) S16-T06
- Main vault: `E:\_PROJECT\_DevBrain_Vault` (85 initial notes + 66 project cards + 11 Claude Code sessions); audit in doc 48 found 61 raw session logs in `90_Agent_Inbox` (369 KB) but only 5 notes in `20_Knowledge` — [HANDOFF.md](HANDOFF.md) section 2; [docs/brainstorming/48-peran-llm-audit-vault-dan-arah-rag.md](docs/brainstorming/48-peran-llm-audit-vault-dan-arah-rag.md) section 1.1

### Inferences
- devbrain is already, in effect, "one shared memory for many AIs" at the local-machine level, but agents mostly do not call it yet (0 calls measured), so adoption hooks (Sprint 16) matter more than new storage features.

### Gaps
- No current measurement of latency/RAM after the embedding model change (HANDOFF lists README claims as unverified).

## Q2. Mapping to the six capability areas

### Takeaway
None of the six is fully present. devbrain partially covers (2) shared multi-agent memory with an audit log (but unsigned, and agent identity is not recorded), partially covers (3) zero-model-call save/search (but over distilled notes, not a verbatim message log), and has (1) consolidation planned in Sprints 18–19. (4) office-document indexing, (5) meeting transcripts, and (6) encrypted cross-machine sync are absent from code; (6) is discussed only as external Syncthing/Git/restic in old brainstorming docs.

### Cited Findings

**(1) Nightly consolidation keeping only evidence-backed facts ("hermes-dreaming") — PLANNED (Sprints 18, 19), not present**
- No consolidation/decay job exists in `src/devbrain/`; grep for consolidat/decay returns nothing relevant — [src/devbrain/](src/devbrain/) (grep)
- Sprint 18 "Curator tanpa LLM" (v1.14.0, planned): usage counting for memories/notes/skills; lifecycle `active → stale → archived` (defaults 30/90 days, mirroring Hermes curator config); `pin` and `lock`; restorable archive and per-action change log; `devbrain curator status / run --dry-run / restore / pin / lock`; auto-run when `serve` is idle, at least every 7 days. Nothing deleted permanently; project cards and ADRs not auto-archived — [docs/sprints/level-1/sprint-18/18-sprint-18-curator.md](docs/sprints/level-1/sprint-18/18-sprint-18-curator.md)
- Sprint 19 "Penyulingan LLM lewat 9router" (v1.15.0, planned, LLM optional): `devbrain curate sessions` produces structured JSON per session (decisions, problem/solution, facts, candidate skills), **every item records its source session**; proposals go to `90_Agent_Inbox/manual_review/` with source links and need approve/reject; knowledge consolidation into `20_Knowledge` (LLM Wiki pattern); periodic check for contradictions, duplicates, stale memories (proposals, not changes); per-run token cost cap; LLM output still passes the Sprint 15 write gate — [docs/sprints/level-1/sprint-19/19-sprint-19-llm-curation-9router.md](docs/sprints/level-1/sprint-19/19-sprint-19-llm-curation-9router.md)
- Doc 48: LLM is not needed for search but is needed for maintenance (distilling sessions, merging logs into knowledge, weekly contradiction/duplicate/stale checks); principle "LLM tidak boleh masuk ke jalur pencarian"; proposals are never automatically truth; each result records its source — [docs/brainstorming/48-peran-llm-audit-vault-dan-arah-rag.md](docs/brainstorming/48-peran-llm-audit-vault-dan-arah-rag.md) sections 1.2–1.3
- Doc 49 maps Hermes curator to devbrain as "✅" (usage counts, stale, archive, change log, no LLM; consolidation via 9router optional) — [docs/brainstorming/49-siklus-belajar-hermes-dan-adopsinya-di-devbrain.md](docs/brainstorming/49-siklus-belajar-hermes-dan-adopsinya-di-devbrain.md) section 3
- Existing building blocks: memory `supersedes`/`superseded_by`, `forget` keeps row with status `forgotten`, duplicate detection (`find_active_memory` on identical content), `confidence` column — [src/devbrain/memory/manager.py](src/devbrain/memory/manager.py); [src/devbrain/core/sqlite_db.py](src/devbrain/core/sqlite_db.py)
- Doc 45 Fase 1 planned memory validity (`valid_from`, `invalid_at`, `superseded_by` used at recall) — [docs/brainstorming/45-roadmap-devbrain-menuju-jarvis.md](docs/brainstorming/45-roadmap-devbrain-menuju-jarvis.md) section 4

**(2) One shared memory for many AIs with a signed change log ("mindhall") — PARTIAL**
- Shared memory across agents is the core purpose; MCP server registered in `~/.claude.json` and three Antigravity `mcp_config.json` files pointing to the main vault — [HANDOFF.md](HANDOFF.md) sections 1–2
- Append-only `memory_ledger` table records created/approved/edited/pinned/blocked events with `source` and timestamp — [CHANGELOG.md](CHANGELOG.md) 1.11.0; [src/devbrain/core/sqlite_db.py](src/devbrain/core/sqlite_db.py) `memory_ledger`
- **No cryptographic signing or hash chaining** of ledger rows (schema is plain columns: id, memory_id, action, source, detail, at); grep for sign/hmac/crypt finds none — [src/devbrain/core/sqlite_db.py](src/devbrain/core/sqlite_db.py)
- **Agent identity not captured**: the MCP `remember` tool hardcodes `source="mcp"`, so the ledger cannot tell Claude Code from Antigravity or Hermes — [src/devbrain/mcp_server/server.py](src/devbrain/mcp_server/server.py) `remember` (~line 398–414)
- Guard rationale explicitly multi-agent: "one poisoned entry written by one agent can steer all of them" — [src/devbrain/memory/guard.py](src/devbrain/memory/guard.py) module docstring
- Hermes integration (devbrain as Hermes MCP server, shared skill folder, Hermes harvester) planned in Sprint 16; network mode `serve --no-stdio` untested and without authentication — [docs/sprints/level-1/sprint-16/16-sprint-16-agent-integration-hooks-hermes.md](docs/sprints/level-1/sprint-16/16-sprint-16-agent-integration-hooks-hermes.md); [HANDOFF.md](HANDOFF.md) section 7
- Doc 49 concept "Satu siklus belajar untuk banyak agent": triggers in agents → `remember`/`save_skill` → safety gate + approval → vault + SQLite → curator → briefing/recall/skills — [docs/brainstorming/49-siklus-belajar-hermes-dan-adopsinya-di-devbrain.md](docs/brainstorming/49-siklus-belajar-hermes-dan-adopsinya-di-devbrain.md) section 4
- Doc 06 (older design) proposed append-only, UUID-partitioned writes for multi-agent/multi-device conflict avoidance — [docs/brainstorming/06-siklus-hidup-data-dan-sync-multi-device.md](docs/brainstorming/06-siklus-hidup-data-dan-sync-multi-device.md) section 3

**(3) Verbatim message log in one local file, zero-model-call save/search ("ZeroMem") — PARTIAL / different shape**
- Save and search make zero LLM calls (core principle); search uses a local embedding model (FastEmbed) plus BM25, so "zero model call" holds for generative LLMs but not for embedding inference — [HANDOFF.md](HANDOFF.md) sections 1 and 3
- Sessions are harvested as **summaries**, not verbatim logs: Claude Code transcripts are summarized into goal, outcome, files and stats, one note per session; Antigravity uses walkthrough artifacts with transcript.jsonl fallback; secrets sanitized — [src/devbrain/harvester/extractor.py](src/devbrain/harvester/extractor.py) (~lines 111–198); [src/devbrain/harvester/claude_code.py](src/devbrain/harvester/claude_code.py)
- Storage is many Markdown files + `.brain_data/` (JSON, .npy, SQLite), not one file; unifying the index into SQLite (FTS5 + vectors) is backlog / Fase 2 — [HANDOFF.md](HANDOFF.md) section 8 item 5; [docs/brainstorming/45-roadmap-devbrain-menuju-jarvis.md](docs/brainstorming/45-roadmap-devbrain-menuju-jarvis.md) Fase 2
- Doc 06 envisioned an append-only event log for agent-generated streams (sessions, transcripts, tool outputs) — [docs/brainstorming/06-siklus-hidup-data-dan-sync-multi-device.md](docs/brainstorming/06-siklus-hidup-data-dan-sync-multi-device.md) section 2
- Hermes itself already has FTS5 keyword search over past conversations in `state.db` — [docs/brainstorming/49-siklus-belajar-hermes-dan-adopsinya-di-devbrain.md](docs/brainstorming/49-siklus-belajar-hermes-dan-adopsinya-di-devbrain.md) section 2

**(4) Private local index of PDFs/Word/Excel/slides with auto-injection of candidate files ("Recall") — NOT PRESENT (only Markdown); partial auto-injection**
- Indexer only walks `*.md` (`vault_path.rglob("*.md")`, also for linked vaults) — [src/devbrain/engine/hybrid_search.py](src/devbrain/engine/hybrid_search.py) lines ~135–144
- No PDF/DOCX/XLSX/PPTX parsing anywhere; no such dependencies — [pyproject.toml](pyproject.toml); grep over `src/devbrain/`
- Known problem: `DOCS` and `_Laporan Magang FXMedia` folders are not recorded because they are not majority Markdown; workaround is `devbrain vault link`; "Folder dokumen non-Markdown" is in the unscheduled backlog — [docs/changelog/v1.9.0-alpha.md](docs/changelog/v1.9.0-alpha.md) line ~100; [HANDOFF.md](HANDOFF.md) section 7; [docs/sprints/level-1/_index.md](docs/sprints/level-1/_index.md) Backlog
- Doc 46 notes that a comparable project parses code locally with tree-sitter but routes documents, PDFs and images through an LLM semantic stage — [docs/brainstorming/46-riset-projek-serupa-efisiensi-token-dan-tech-stack.md](docs/brainstorming/46-riset-projek-serupa-efisiensi-token-dan-tech-stack.md) line ~35
- Auto-injection analog: `build_task_context` briefing and planned Sprint 16 `SessionStart` hook that loads a project briefing by matching `cwd` to a project card — [docs/sprints/level-1/sprint-16/16-sprint-16-agent-integration-hooks-hermes.md](docs/sprints/level-1/sprint-16/16-sprint-16-agent-integration-hooks-hermes.md) S16-T01

**(5) Meeting transcripts with decisions cited to timestamps ("Munin") — NOT PRESENT; adjacent ADR feature exists**
- No meeting/audio transcript ingestion; "transcript" in code refers only to agent session JSONL — grep over [src/devbrain/](src/devbrain/)
- Decisions exist as ADRs: `record_decision`, `get_decisions`, `adr supersede`; `decisions` table with status/superseded_by; briefings show only accepted decisions — [CHANGELOG.md](CHANGELOG.md) 1.10.0; [src/devbrain/core/sqlite_db.py](src/devbrain/core/sqlite_db.py)
- Planned Sprint 19 distillation extracts decisions from agent sessions and records source session per item (session-level, not timestamp-level citation) — [docs/sprints/level-1/sprint-19/19-sprint-19-llm-curation-9router.md](docs/sprints/level-1/sprint-19/19-sprint-19-llm-curation-9router.md) S19-T03
- STT/voice is Fase 6 and moved to Hermes/Jarvis UI, not devbrain — [docs/brainstorming/45-roadmap-devbrain-menuju-jarvis.md](docs/brainstorming/45-roadmap-devbrain-menuju-jarvis.md) Fase 6; [docs/brainstorming/47-hermes-agent-sebagai-badan-jarvis-jev-dan-strategi-ui.md](docs/brainstorming/47-hermes-agent-sebagai-badan-jarvis-jev-dan-strategi-ui.md) section 8

**(6) Encrypted sync of memories/skills/settings across machines ("Hermes Roam") — NOT PRESENT in code; external tools discussed**
- No sync or encryption code; `sha256_hash` exists only in `file_cache` for change detection — [src/devbrain/core/sqlite_db.py](src/devbrain/core/sqlite_db.py)
- Recommended approach in docs: Syncthing over Tailscale as primary sync (TLS-encrypted P2P), Git auto-commit as backup — [docs/brainstorming/21-metode-sync-obsidian-dan-prosedur-uninstall-bersih.md](docs/brainstorming/21-metode-sync-obsidian-dan-prosedur-uninstall-bersih.md); [docs/brainstorming/22-panduan-detail-syncthing-dan-git-auto-sync.md](docs/brainstorming/22-panduan-detail-syncthing-dan-git-auto-sync.md)
- Doc 40: `.brain_data/` (machine binary layer) need not be synced to phone; only Markdown — [docs/brainstorming/40-panduan-praktis-sinkronisasi-obsidian-windows-dan-mobile.md](docs/brainstorming/40-panduan-praktis-sinkronisasi-obsidian-windows-dan-mobile.md)
- Doc 10: encrypted offsite backup via Rclone or Restic weekly; git snapshot every 6 h on Jarvis server — [docs/brainstorming/10-security-privacy-dan-boundary-protocol.md](docs/brainstorming/10-security-privacy-dan-boundary-protocol.md)
- Roadmap Fase 3 "Layanan Selalu Hidup": HTTP transport with token auth, homeserver over Tailscale, vault sync (Syncthing or Git), scheduled backup; decision Syncthing vs Git still open — [docs/brainstorming/45-roadmap-devbrain-menuju-jarvis.md](docs/brainstorming/45-roadmap-devbrain-menuju-jarvis.md) Fase 3, section 5
- Important caveat: memories' source of truth is SQLite (`brain.db`), and `00_System/Memories/` Markdown is rewritten by devbrain ("Jangan ubah ... manual") — so syncing Markdown alone does not sync memories/ledger — [HANDOFF.md](HANDOFF.md) section 10

### Inferences
- Closest existing fit: (2) and (3). Cheapest wins: record real agent identity in `source` (MCP client name) and hash-chain the ledger, which would move (2) toward "signed change log" without an LLM.
- (1) "evidence-backed only" aligns well with Sprint 19's design (source session per item, approval gate), but devbrain's chosen pattern is propose-then-human-approve, not automatic nightly pruning.
- (4) would require new optional parsers (PDF/Office) and conflicts with "majority Markdown" scanner rules; it is backlog only.
- (6) Because SQLite holds memory truth while Markdown is a mirror, file-level Syncthing of the vault risks SQLite conflicts across machines; the roadmap instead favors one homeserver instance (Fase 3).

### Gaps
- Whether the Hermes add-ons can coexist with devbrain as Hermes memory provider (doc 47 notes only one memory provider active at a time) is not analyzed in local docs beyond that note.
- No local doc analyzes the six named add-ons specifically.

## Q3. Design principles and constraints that affect adoption

### Takeaway
Core rules: no LLM in core (LLM features optional, never in the search path), local/offline/deterministic, Markdown as human source of truth with rebuildable indexes, all agent memory writes through `memory/guard.py` and recorded in the ledger, atomic writes via `core/fsutil.py`, MCP output size caps, measure before claiming, and no writes to the main vault or IDE configs without owner permission.

### Cited Findings
- "Inti devbrain tidak memanggil LLM. Fitur yang butuh LLM harus opsional." — [AGENTS.md](AGENTS.md) Aturan kode
- "Semua jalur yang menulis memori (atau nanti skill) dari agent harus melewati `memory/guard.py` dan tercatat di ledger. Jangan menulis langsung ke tabel `memories`." — [AGENTS.md](AGENTS.md)
- Writes via `atomic_write_text`/`atomic_write_json`; MCP output bounded via `core/textutil.py` because every returned token is paid by the agent; search engine built via `HybridEngine.from_config(vault)` — [AGENTS.md](AGENTS.md)
- Don't replace core library, embedding model, or storage without recording and measuring the decision first; don't write to `E:\_PROJECT\_DevBrain_Vault` or home IDE configs without owner permission — [AGENTS.md](AGENTS.md) Jangan
- Principles: local, offline, deterministic core; Markdown is human source of truth; index and SQLite rebuildable from vault; measure before claiming — [HANDOFF.md](HANDOFF.md) section 1; [docs/brainstorming/45-roadmap-devbrain-menuju-jarvis.md](docs/brainstorming/45-roadmap-devbrain-menuju-jarvis.md) section 3
- Deliberately not doing: moving to Qdrant/Postgres/Neo4j without evidence, rewrite in Go/Rust, building an agent runtime inside devbrain, web dashboard before Fase 3 — [docs/brainstorming/45-roadmap-devbrain-menuju-jarvis.md](docs/brainstorming/45-roadmap-devbrain-menuju-jarvis.md) section 6
- Division of roles: Hermes owns small always-loaded core memory (`USER.md`, `MEMORY.md`, `SOUL.md`); devbrain owns long memory (vault, ADR, project cards, sessions of all agents); skills shared — [docs/brainstorming/47-hermes-agent-sebagai-badan-jarvis-jev-dan-strategi-ui.md](docs/brainstorming/47-hermes-agent-sebagai-badan-jarvis-jev-dan-strategi-ui.md) section 2.3
- Hermes can have only one external memory provider active at a time (slot shared with Honcho, Mem0); MCP is the first-choice connection — [docs/brainstorming/47-hermes-agent-sebagai-badan-jarvis-jev-dan-strategi-ui.md](docs/brainstorming/47-hermes-agent-sebagai-badan-jarvis-jev-dan-strategi-ui.md) section 2.2
- Privacy: vault contains personal data incl. pasted chats with people's names; sanitizer only masks credentials. Pending decision D19-1: per-group LLM privacy (e.g. `_fxmedia` local model only) — [HANDOFF.md](HANDOFF.md) section 10; [docs/sprints/level-1/_index.md](docs/sprints/level-1/_index.md)
- "Hermes adalah agent yang melihat percakapannya sendiri. DevBrain adalah server yang hanya tahu apa yang dikirim agent kepadanya." — patterns transfer, triggers don't — [docs/brainstorming/49-siklus-belajar-hermes-dan-adopsinya-di-devbrain.md](docs/brainstorming/49-siklus-belajar-hermes-dan-adopsinya-di-devbrain.md) section 3

### Inferences
- Add-ons that call an LLM for every save (if any of the six do) can only be adopted as optional layers outside the core; any add-on that writes memories directly into Hermes or a separate store bypasses devbrain's guard + ledger and fragments the "one memory" goal.
- Since devbrain is a server and cannot see conversations, add-ons that rely on the agent's own conversation stream (verbatim logs, nightly dreaming over chats) are naturally Hermes-side; devbrain would consume their output via harvester (Sprint 16 S16-T06).

### Gaps
- None noted within local sources.

## Q4. Roadmap (Sprints 14–20), HANDOFF next steps, and existing Hermes analysis

### Takeaway
Sprints 14 and 15 are done; 16–20 are planned in dependency order: hooks + Hermes integration (16), agent-learned skills (17), LLM-free curator (18), optional LLM distillation via 9router + knowledge layer (19), token A/B test (20). Hermes has been analyzed in docs 47 and 49 (local install at `%LOCALAPPDATA%\hermes`, memory 95–98% full, curator active, devbrain not yet connected).

### Cited Findings
- Sprint table: 14 Perapian vault v1.10.0 ✅; 15 Gerbang tulis & memori inti v1.11.0 ✅; 16 Hook Claude Code & integrasi Hermes v1.12.0 ⏳; 17 Skill yang dipelajari agent v1.13.0 ⏳; 18 Curator tanpa LLM v1.14.0 ⏳; 19 Penyulingan LLM lewat 9router & lapisan knowledge v1.15.0 ⏳ (LLM: Ya); 20 Uji A/B hemat token ⏳ — [docs/sprints/level-1/_index.md](docs/sprints/level-1/_index.md)
- Backlog (unscheduled): unify index into SQLite (FTS5 + vector); homeserver mode HTTP + auth; Jarvis UI on Hermes API server; non-Markdown document folders and `skills/` classification — [docs/sprints/level-1/_index.md](docs/sprints/level-1/_index.md)
- Pending decisions: D15-1 enable `memory.write_approval` on main vault before connecting Hermes; D16-1 hooks global vs per project; D16-2 Hermes skills written to vault or read only; D19-1 per-group LLM privacy; D19-2 distillation model — [docs/sprints/level-1/_index.md](docs/sprints/level-1/_index.md)
- HANDOFF next steps by priority: (1) Claude Code hooks (SessionStart briefing, Stop summary); (2) A/B token test on 10 real tasks; (3) small fixes (non-Markdown docs folder, skill classification); (4) connect Hermes via `mcp_servers` in `%LOCALAPPDATA%\hermes\config.yaml`; (5) unify index into SQLite; (6) homeserver mode — [HANDOFF.md](HANDOFF.md) section 8
- Sprint 16 tasks: S16-T01/T02 hooks; S16-T03 `devbrain hooks install/uninstall`; S16-T04 register devbrain in Hermes `mcp_servers`; S16-T05 shared skill folder (`skills.external_dirs` → `00_System/Agent_Skills`); S16-T06 Hermes harvester (`state.db` read-only, `MEMORY.md`/`USER.md` as one updated note); S16-T07 Hermes path `%LOCALAPPDATA%\hermes` overridable by `HERMES_HOME` — [docs/sprints/level-1/sprint-16/16-sprint-16-agent-integration-hooks-hermes.md](docs/sprints/level-1/sprint-16/16-sprint-16-agent-integration-hooks-hermes.md)
- Doc 49 Hermes facts on this machine: program at `%LOCALAPPDATA%\hermes\hermes-agent` (git `1c8dcdb`, 2026.9.24 stable); data at `%LOCALAPPDATA%\hermes` (`config.yaml`, `memories/`, `skills/`, `state.db`, `sessions/`, `cron/`, `kanban.db`); `~/.hermes` is a leftover. 100 skills (3 self-created); `MEMORY.md` 2,092/2,200 chars (95%), `USER.md` 1,342/1,375 (98%); curator active (stale 30 d, archive 90 d); `mcp_servers` only `antigravity` — [docs/brainstorming/49-siklus-belajar-hermes-dan-adopsinya-di-devbrain.md](docs/brainstorming/49-siklus-belajar-hermes-dan-adopsinya-di-devbrain.md) section 1
- Doc 49 Hermes learning mechanisms: small always-loaded core memory frozen per session; `memory` tool add/patch/remove; security scan of memory entries (injection, exfiltration, SSH backdoor, hidden Unicode, duplicates); `skill_manage`; background review; optional write approval with `pending/`; curator (LLM-free stale/archive, optional LLM merge, never deletes); FTS5 session search — [docs/brainstorming/49-siklus-belajar-hermes-dan-adopsinya-di-devbrain.md](docs/brainstorming/49-siklus-belajar-hermes-dan-adopsinya-di-devbrain.md) section 2
- Doc 49 ordering: vault cleanup → write gate → shared skill folder + MCP in Hermes → `save_skill`/`patch_skill` + end-of-session hook → curator (no LLM) → Hermes harvester + 9router consolidation — [docs/brainstorming/49-siklus-belajar-hermes-dan-adopsinya-di-devbrain.md](docs/brainstorming/49-siklus-belajar-hermes-dan-adopsinya-di-devbrain.md) section 6
- Doc 47: Hermes limits — small core memory with no overflow, keyword-only session search, memory private to Hermes, no human-readable vault; devbrain fills those gaps — [docs/brainstorming/47-hermes-agent-sebagai-badan-jarvis-jev-dan-strategi-ui.md](docs/brainstorming/47-hermes-agent-sebagai-badan-jarvis-jev-dan-strategi-ui.md) section 2.1

### Inferences
- Several add-on ideas overlap with planned sprints: hermes-dreaming ↔ Sprints 18–19; mindhall ↔ Sprint 15 ledger + Sprint 16 Hermes connection; Recall ↔ backlog item "non-Markdown documents". These would be inputs to sprint design rather than replacements.

### Gaps
- Sprint 17 file was not read in detail (skill learning: `save_skill`/`patch_skill`, progressive disclosure per doc 49); not central to the six areas.

## Q5. File types indexed, sync/encryption, consolidation/decay jobs (direct answers)

### Takeaway
Indexed today: Markdown only (`*.md`) in the vault and linked vaults, plus harvested agent session JSONL/artifacts and project manifests turned into Markdown notes. No PDF/DOCX/XLSX/PPTX. No sync or encryption features in code. No consolidation/decay job yet (curator planned Sprint 18).

### Cited Findings
- `rglob("*.md")` in the engine — [src/devbrain/engine/hybrid_search.py](src/devbrain/engine/hybrid_search.py)
- Harvester inputs: agent session stores (Antigravity, Claude Code JSONL, Cline) and project folders (manifests like `package.json`, `pubspec.yaml`, `composer.json`, `pom.xml`, `*.csproj`, `CMakeLists.txt`), output as Markdown cards/logs — [src/devbrain/harvester/discovery.py](src/devbrain/harvester/discovery.py); [CHANGELOG.md](CHANGELOG.md) 1.9.0
- Dataview/Tasks/Bases/query blocks excluded from indexing since v1.10.0 — [CHANGELOG.md](CHANGELOG.md) 1.10.0
- Watcher re-indexes on note changes (watchdog, connected to `serve`) — [HANDOFF.md](HANDOFF.md) sections 3 and 5
- No sync/encryption/consolidation code (grep for encrypt, crypt, hmac, syncthing, consolidat, decay over `src/devbrain/` found no implementation) — [src/devbrain/](src/devbrain/)

### Inferences
- devbrain has nothing that auto-expires memories today; only manual `forget`, `supersedes`, and owner approval.

### Gaps
- Did not verify whether the watcher or `ingest` service can be scheduled nightly (no cron feature found; Hermes cron is the planned scheduler per doc 47).
