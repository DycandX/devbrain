# Task 01: Multi-Agent Storage Discovery & Secret Redaction Filter

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 05 (Ingestion & Vault Seeding) |
| **Status** | ⏳ Todo |
| **Target Files** | `src/devbrain/harvester/discovery.py`, `src/devbrain/harvester/sanitizer.py` |

---

## 1. Deskripsi Task
Membangun modul **Dynamic Agent Storage Discovery** untuk mendeteksi lokasi folder riwayat percakapan dari berbagai AI tools (Google Antigravity IDE, `agy` CLI, Claude Code, Cline/Roo Code, Aider) serta modul **Secret Redaction Regex Filter** untuk membersihkan kredensial sensitif (API key, token JWT, password) sebelum disimpan ke Obsidian Vault.

---

## 2. Rincian Pekerjaan
1. **Dynamic Storage Path Discovery (`discovery.py`):**
   * Memindai direktori user secara otomatis lintas OS (Windows `%USERPROFILE%` & `%APPDATA%`, macOS/Linux `~`):
     * Antigravity IDE: `~/.gemini/antigravity-ide/brain/` & `~/.gemini/antigravity/brain/`
     * Antigravity CLI: `~/.gemini/antigravity-cli/`
     * Claude Code: `~/.claude/projects/`
     * Cline / Roo Code: `%APPDATA%/Code/User/globalStorage/saoudrizwan.claude-dev/tasks/`
   * Mengembalikan daftar direktori sesi yang aktif dan dapat dipanen (*harvestable*).
2. **Secret Redaction Filter (`sanitizer.py`):**
   * Menerapkan aturan regex untuk mendeteksi dan mengganti secret dengan `[REDACTED_SECRET]`:
     * OpenAI (`sk-[a-zA-Z0-9]{20,}` / `sk-proj-...`)
     * Anthropic (`sk-ant-[a-zA-Z0-9_-]{20,}`)
     * Google AI Studio (`AIzaSy[a-zA-Z0-9_-]{33}`)
     * GitHub Personal Access Tokens (`ghp_[a-zA-Z0-9]{36}`, `github_pat_...`)
     * Bearer Tokens (`Bearer\s+[a-zA-Z0-9_\-\.]{20,}`)
     * Password / Secret Key patterns (`password\s*=\s*['"][^'"]+['"]`)

---

## 3. Kriteria Selesai (Acceptance Criteria)
* Modul discovery mendeteksi minimal folder Google Antigravity dan Claude Code yang terpasang di sistem.
* Seluruh test case regex sanitizer berhasil membersihkan token rahasia tanpa merusak format teks Markdown atau kode.
