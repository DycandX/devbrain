# Sprint 16: Integrasi Agent — Hook Claude Code & Hermes

| Metadata | Nilai |
| :--- | :--- |
| **Sprint** | Sprint 16 |
| **Target versi** | `v1.12.0-alpha` |
| **Status** | ⏳ Planned |
| **Dokumen** | [47](../../../brainstorming/47-hermes-agent-sebagai-badan-jarvis-jev-dan-strategi-ui.md), [48](../../../brainstorming/48-peran-llm-audit-vault-dan-arah-rag.md) langkah 2, [49](../../../brainstorming/49-siklus-belajar-hermes-dan-adopsinya-di-devbrain.md) bagian 5 |
| **Butuh LLM** | Tidak (agent yang menyuling) |
| **Syarat** | Sprint 15 selesai |

## Tujuan
DevBrain terpakai tanpa agent harus ingat memanggilnya, dan Hermes berbagi memori serta skill dengan agent lain.

## Keputusan sebelum mulai

| ID | Pertanyaan | Usulan |
| :--- | :--- | :--- |
| D16-1 | Hook Claude Code dipasang global (`~/.claude/settings.json`) atau per projek? | Per projek lewat `devbrain hooks install`, global opsional |
| D16-2 | Skill buatan Hermes langsung ditulis ke vault (`skills.create_dir`) atau hanya dibaca (`skills.external_dirs`)? | Dibaca dulu; tulis langsung setelah Sprint 17 |

## Task

| ID | Task | Berkas | Status |
| :--- | :--- | :--- | :--- |
| S16-T01 | Hook `SessionStart`: muat briefing projek dari folder kerja | `hooks/claude_code.py` (baru) | ⏳ |
| S16-T02 | Hook `Stop`/`SessionEnd`: minta agent meringkas dan memanggil `remember`; panen sesi | `hooks/claude_code.py` | ⏳ |
| S16-T03 | Perintah `devbrain hooks install / uninstall` | `cli/commands/hooks_cmd.py` (baru) | ⏳ |
| S16-T04 | Daftarkan DevBrain sebagai MCP di Hermes (`mcp_servers`) | `core/client_config.py` | ⏳ |
| S16-T05 | Folder skill bersama: `skills.external_dirs` Hermes → `00_System/Agent_Skills` | `core/client_config.py` | ⏳ |
| S16-T06 | Harvester Hermes: sesi dari `state.db`, isi `MEMORY.md`/`USER.md` | `harvester/hermes.py` (baru), `harvester/discovery.py` | ⏳ |
| S16-T07 | Lokasi Hermes dari `%LOCALAPPDATA%\hermes` (bukan `~/.hermes`), bisa ditimpa `HERMES_HOME` | `harvester/discovery.py` | ⏳ |
| S16-T08 | Test, uji langsung dengan Hermes dan Claude Code, changelog, rilis | `tests/`, `docs/changelog/` | ⏳ |

## Rincian

**S16-T01.** Hook membaca `cwd`, mencari kartu projek yang `local_path`-nya cocok, lalu mengeluarkan briefing ringkas sebagai konteks tambahan. Tanpa kartu yang cocok, hook diam.
*Selesai bila:* sesi baru Claude Code di folder projek langsung memuat briefing tanpa diminta.

**S16-T04/T05.** Tulis ke `%LOCALAPPDATA%\hermes\config.yaml` dengan cadangan dan penulisan atomik, seperti config IDE lain. Jangan menyentuh kunci lain.
*Selesai bila:* `hermes` di sesi baru bisa memanggil `recall` dan melihat skill dari vault.

**S16-T06.** Baca `state.db` dalam mode hanya-baca. Satu catatan per sesi, format seperti harvester Claude Code. Memori inti Hermes dicatat sebagai satu catatan yang diperbarui, bukan dipindahkan.
*Selesai bila:* `devbrain ingest --from hermes` memanen sesi Hermes; sesi yang bertambah diperbarui di catatan yang sama.

## Catatan
- Jalankan hook dan integrasi Hermes pada salinan config lebih dulu.
- Setelah sprint ini, `devbrain usage` mulai punya data panggilan ke DevBrain untuk uji A/B (Sprint 20).
