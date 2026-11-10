# Sprint 12: Memori Jangka Panjang, Hemat Token & Briefing

| Metadata | Nilai |
| :--- | :--- |
| **Sprint** | Sprint 12 |
| **Versi** | `v1.8.0-alpha`, `v1.8.1-alpha` |
| **Status** | ✅ Done (dicatat setelah selesai) |
| **Dokumen** | [45](../../../brainstorming/45-roadmap-devbrain-menuju-jarvis.md) Fase 1, [46](../../../brainstorming/46-riset-projek-serupa-efisiensi-token-dan-tech-stack.md) bagian 2, [v1.8.0](../../../changelog/v1.8.0-alpha.md), [v1.8.1](../../../changelog/v1.8.1-alpha.md) |
| **Commit** | `f43619e`, `2f099c8` |

## Tujuan
Agent bisa mengingat antar sesi, keluaran tool kecil dan terukur, dan briefing tepat sasaran di vault nyata.

## Task

| ID | Task | Berkas | Status |
| :--- | :--- | :--- | :--- |
| S12-T01 | Tool `remember` / `recall` / `forget` dengan cermin Markdown | `memory/manager.py`, `mcp_server/server.py` | ✅ |
| S12-T02 | `search_brain` satu baris per catatan, tool `read_note` per bagian | `mcp_server/server.py`, `core/textutil.py` | ✅ |
| S12-T03 | Batas ukuran `get_project_context` dan preferensi | `mcp_server/server.py`, `context/builder.py` | ✅ |
| S12-T04 | `devbrain usage` dari transkrip Claude Code | `harvester/usage_stats.py`, `cli/commands/usage_cmd.py` | ✅ |
| S12-T05 | Perbaiki kebocoran koneksi SQLite | `core/sqlite_db.py` | ✅ |
| S12-T06 | Ringkasan projek tanpa frontmatter mentah | `context/builder.py` | ✅ |
| S12-T07 | Riwayat sesi lewat tautan Project Hub | `context/builder.py` | ✅ |
| S12-T08 | Catatan briefing dipilih lewat kesepakatan dua pemeringkat | `context/builder.py` | ✅ |

## Hasil
- Definisi 12 tool ±1.470 token per sesi; mode indeks pencarian 37% lebih kecil dari mode cuplikan.
- Test 66 → 83.
