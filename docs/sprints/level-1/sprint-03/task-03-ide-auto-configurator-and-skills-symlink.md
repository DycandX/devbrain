# Task 03: IDE Auto-Configurator & Agent Skill Manager

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 03 |
| **Status** | ✅ Done |
| **Target Files** | `src/devbrain/core/client_config.py`, `src/devbrain/cli/commands/skill_cmd.py` |

---

## 1. Deskripsi Task
Membangun modul yang secara otomatis mendaftarkan konfigurasi FastMCP Stdio ke aplikasi IDE AI (Antigravity IDE & Claude Code) tanpa perlu pengguna mengedit JSON secara manual, serta menyediakan command CLI `devbrain skill` untuk mengelola skills.

---

## 2. Rincian Pekerjaan
1. **Auto-Configurator Modul (`client_config.py`):**
   * **Antigravity IDE (`~/.gemini/antigravity/mcp_config.json`):**
     * Membaca file JSON jika ada (atau membuat baru jika belum ada).
     * Menambahkan blok konfigurasi:
       ```json
       "mcpServers": {
         "central-brain": {
           "command": "devbrain",
           "args": ["serve", "--stdio", "--vault", "<VAULT_PATH>"]
         }
       }
       ```
   * **Claude Code (`~/.claude.json`):**
     * Menambahkan entri server MCP serupa.
2. **Command CLI `devbrain skill` (`skill_cmd.py`):**
   * `devbrain skill list`: Memindai dan menampilkan daftar seluruh skill di `00_System/Agent_Skills/`.
   * `devbrain skill add <name>`: Membuat folder baru `00_System/Agent_Skills/<name>/SKILL.md` dengan template frontmatter standar.
   * `devbrain skill symlink`: Mengotomatiskan pembuatan symlink / hardlink dari folder skills vault ke folder skill global Antigravity (`~/.gemini/config/skills/`).

---

## 3. Kriteria Selesai (Acceptance Criteria)
* Menjalankan `devbrain init` atau auto-config berhasil menambahkan entri `central-brain` ke file konfigurasi Antigravity tanpa merusak config MCP lain yang sudah ada.
* Perintah `devbrain skill add test-skill` berhasil membuat folder dan file template `SKILL.md`.
