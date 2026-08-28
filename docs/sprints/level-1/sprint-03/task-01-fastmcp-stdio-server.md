# Task 01: FastMCP Stdio Server Setup

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 03 |
| **Status** | ✅ Done |
| **Target Files** | `src/devbrain/mcp_server/server.py`, `src/devbrain/cli/commands/serve_cmd.py` |

---

## 1. Deskripsi Task
Menyiapkan instance server Model Context Protocol (MCP) menggunakan FastMCP / SDK resmi Python dengan transport standard input/output (Stdio) yang dapat diluncurkan secara on-demand oleh IDE AI.

---

## 2. Rincian Pekerjaan
1. **FastMCP Server Initialization (`server.py`):**
   * Menginisialisasi `mcp = FastMCP("central-brain")`.
   * Setup lifecycle event: Saat server Stdio dimulai, otomatis memuat `.brainrc.json` dan memicu inisialisasi hybrid indexer + inisialisasi background watcher.
   * Graceful shutdown handler saat stream Stdio ditutup oleh IDE.
2. **Command CLI `devbrain start / serve` (`serve_cmd.py`):**
   * Mode default: Menjalankan transport Stdio untuk integrasi IDE langsung:
     ```bash
     devbrain serve --stdio
     ```
   * Logging: Seluruh logging internal diarahkan ke `stderr` (bukan `stdout`) agar tidak merusak format pesan JSON-RPC pada protokol Stdio MCP.

---

## 3. Kriteria Selesai (Acceptance Criteria)
* Server MCP dapat merespons `tools/list` dan JSON-RPC handshake dari MCP Inspector / Antigravity IDE via Stdio.
