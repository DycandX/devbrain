# Task 02: Implementasi 4 Core MCP Tools

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 03 |
| **Status** | Todo |
| **Target Files** | `src/devbrain/mcp_server/tools/search_brain.py`, `src/devbrain/mcp_server/tools/project_context.py`, `src/devbrain/mcp_server/tools/agent_logger.py`, `src/devbrain/mcp_server/tools/skill_loader.py` |

---

## 1. Deskripsi Task
Mengimplementasikan 4 tools standar MCP yang akan dipanggil oleh AI Agent (**Antigravity IDE**, **Claude Code**, **Hermes**, **OpenCode**) untuk mencari memori, mengambil konteks proyek, menulis catatan log, dan memuat skill.

---

## 2. Rincian Pekerjaan
1. **Tool 1: `@mcp.tool() search_brain(query: str, limit: int = 5, scope: str = "all")`:**
   * Menjalankan Hybrid Search (FastEmbed + BM25) pada vault.
   * Mengembalikan daftar dokumen/chunk relevan beserta cuplikan teks dan path file.
2. **Tool 2: `@mcp.tool() get_project_context(project_name: str)`:**
   * Mencari file `10_Projects/{project_name}.md` atau file yang memiliki tag `#project/{project_name}`.
   * Mengembalikan seluruh isi ringkasan proyek, arsitektur, dan todo list aktif.
3. **Tool 3: `@mcp.tool() write_agent_log(summary: str, details: str, tags: list[str])`:**
   * Menerapkan prinsip **Append-Only UUID Partitioning**:
     * Nama file: `90_Agent_Inbox/{timestamp}_{device_name}_{uuid}.md`
     * Menyusun YAML Frontmatter standar (`author`, `type: session_log`, `tags`).
     * Menyimpan file ke disk dan memicu event indexer.
4. **Tool 4: `@mcp.tool() load_skill(skill_name: str)`:**
   * Membaca file `00_System/Agent_Skills/{skill_name}/SKILL.md`.
   * Mengembalikan instruksi lengkap secara *Just-In-Time* (menghemat token context window).

---

## 3. Kriteria Selesai (Acceptance Criteria)
* Keempat tool terdaftar di skema FastMCP.
* Tool `write_agent_log` berhasil membuat file markdown baru di `90_Agent_Inbox/` dengan format frontmatter yang valid.
* Tool `load_skill` berhasil mengembalikan isi file `SKILL.md`.
