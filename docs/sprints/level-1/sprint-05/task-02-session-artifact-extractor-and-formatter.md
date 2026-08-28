# Task 02: Session Artifact Extractor & Obsidian Markdown Formatter

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 05 (Ingestion & Vault Seeding) |
| **Status** | ⏳ Todo |
| **Target Files** | `src/devbrain/harvester/extractor.py`, `src/devbrain/harvester/formatter.py` |

---

## 1. Deskripsi Task
Membangun modul ekstraktor artefak kognitif untuk memproses file `walkthrough.md`, `task.md`, dan `transcript.jsonl` dari sesi internal AI Agent menjadi catatan Markdown bersih yang siap dimasukkan ke `90_Agent_Inbox/<agent_name>/` dengan format standar YAML Frontmatter.

---

## 2. Rincian Pekerjaan
1. **Antigravity Artifact Extractor:**
   * Membaca folder `~/.gemini/antigravity/brain/<session_id>/`.
   * Memprioritaskan pembacaan `walkthrough.md` atau `implementation_plan.md`.
   * Jika tidak ada walkthrough, mengekstrak prompt awal dan kesimpulan akhir dari `transcript.jsonl`.
2. **Claude Code Session Extractor:**
   * Membaca log sesi JSONL dari `~/.claude/projects/`.
   * Mengekstrak user goal, ringkasan tool execution, dan respon akhir.
3. **Obsidian Formatter & Frontmatter Enricher:**
   * Menyusun metadata YAML standar:
     ```yaml
     ---
     id: "INGEST-YYYYMMDD-HHMMSS-UUID"
     title: "Session Title / Goal"
     type: "agent-session-log"
     source: "antigravity" # atau "claude-code"
     device: "hostname"
     created: "2026-08-29T12:00:00Z"
     tags: ["agent-inbox", "antigravity", "walkthrough", "topic-tag"]
     ---
     ```
   * Memformat body catatan dengan struktur Markdown yang jelas: `# Title`, `## Overview`, `## Changes Made`, `## Verification`.

---

## 3. Kriteria Selesai (Acceptance Criteria)
* Ekstraktor berhasil mengekstrak sesi tanpa error decoding/JSON parsing.
* Format catatan yang dihasilkan 100% valid YAML frontmatter dan siap dibaca oleh Obsidian Dataview & Indexer.
