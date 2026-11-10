# Sprint 18: Curator — Perawatan Tanpa LLM

| Metadata | Nilai |
| :--- | :--- |
| **Sprint** | Sprint 18 |
| **Target versi** | `v1.14.0-alpha` |
| **Status** | ⏳ Planned |
| **Dokumen** | [49](../../../brainstorming/49-siklus-belajar-hermes-dan-adopsinya-di-devbrain.md) bagian 2–3 (curator Hermes) |
| **Butuh LLM** | Tidak |
| **Syarat** | Sprint 15, 17 |

## Tujuan
Memori, catatan knowledge, dan skill yang tidak terpakai tidak menumpuk dan tidak mengotori briefing. Tidak ada yang dihapus permanen.

## Task

| ID | Task | Berkas | Status |
| :--- | :--- | :--- | :--- |
| S18-T01 | Hitung pemakaian: memori (muncul di `recall`/briefing), catatan (dibaca `read_note`), skill (dimuat) | `core/sqlite_db.py`, `memory/manager.py`, `mcp_server/server.py` | ⏳ |
| S18-T02 | Siklus status `active → stale → archived` dengan ambang hari yang bisa diatur | `curator/lifecycle.py` (baru) | ⏳ |
| S18-T03 | `pin` dan `lock`: dipin tidak diarsipkan, dikunci tidak bisa diubah agent | `curator/lifecycle.py` | ⏳ |
| S18-T04 | Arsip bisa dipulihkan; catatan perubahan per tindakan | `curator/lifecycle.py`, `core/sqlite_db.py` | ⏳ |
| S18-T05 | Perintah `devbrain curator status / run --dry-run / restore / pin / lock` | `cli/commands/curator_cmd.py` (baru) | ⏳ |
| S18-T06 | Jalankan otomatis saat `serve` menganggur, minimal tiap 7 hari | `cli/commands/serve_cmd.py` | ⏳ |
| S18-T07 | Test, changelog, rilis | `tests/`, `docs/changelog/` | ⏳ |

## Rincian

**S18-T02.** Usulan default: `stale` setelah 30 hari tidak terpakai, `archived` setelah 90 hari (sama dengan config Hermes-mu). Yang `stale` tetap bisa dicari tetapi tidak masuk briefing. Yang `archived` dipindah ke `.archive/` dan keluar dari indeks.
*Selesai bila:* `curator run --dry-run` melaporkan perubahan tanpa menulis; `restore` mengembalikan catatan utuh.

## Catatan
- Kartu projek dan ADR tidak diarsipkan otomatis.
- Konsolidasi dengan LLM (menggabungkan yang tumpang tindih) ada di Sprint 19.
