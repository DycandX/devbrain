# Sprint 11: Fondasi — Isolasi Test, Pencarian Terukur & Harvester Claude Code

| Metadata | Nilai |
| :--- | :--- |
| **Sprint** | Sprint 11 |
| **Versi** | `v1.7.0-alpha` |
| **Status** | ✅ Done (dicatat setelah selesai) |
| **Dokumen** | [45: Roadmap](../../../brainstorming/45-roadmap-devbrain-menuju-jarvis.md) Fase 0, [changelog v1.7.0](../../../changelog/v1.7.0-alpha.md) |
| **Commit** | `7fcb96d` |

## Tujuan
Membuat inti DevBrain bisa dipercaya, dan membuat kualitas pencarian bisa diukur.

## Task

| ID | Task | Berkas | Status |
| :--- | :--- | :--- | :--- |
| S11-T01 | Isolasi test dari home directory (fixture `isolated_home`) | `tests/conftest.py` | ✅ |
| S11-T02 | Tulis config IDE secara atomik, jangan timpa config yang gagal dibaca | `core/client_config.py`, `core/fsutil.py` | ✅ |
| S11-T03 | Rapikan packaging: `mcp>=2`, versi, dependensi | `pyproject.toml` | ✅ |
| S11-T04 | Alat evaluasi retrieval (16 catatan, 38 pertanyaan) | `benchmarks/eval_retrieval.py`, `benchmarks/eval/` | ✅ |
| S11-T05 | Reciprocal Rank Fusion dan gerbang relevansi | `engine/hybrid_search.py`, `engine/bm25.py` | ✅ |
| S11-T06 | Model embedding multibahasa, indeks mencatat modelnya | `core/constants.py`, `engine/storage.py` | ✅ |
| S11-T07 | Watcher menyala bersama `devbrain serve` | `cli/commands/serve_cmd.py` | ✅ |
| S11-T08 | Harvester Claude Code: satu catatan ringkas per sesi | `harvester/claude_code.py` | ✅ |

## Hasil
- Hit@1 hybrid 0,906 → 0,969; penolakan pertanyaan tanpa jawaban 0/6 → 6/6.
- Test 55 → 66.
