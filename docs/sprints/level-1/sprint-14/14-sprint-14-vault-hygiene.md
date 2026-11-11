# Sprint 14: Perapian Vault

| Metadata | Nilai |
| :--- | :--- |
| **Sprint** | Sprint 14 |
| **Target versi** | `v1.10.0-alpha` |
| **Status** | ✅ Done |
| **Dokumen** | [48](../../../brainstorming/48-peran-llm-audit-vault-dan-arah-rag.md) bagian 2, 3, 5 |
| **Butuh LLM** | Tidak |

## Tujuan
Vault yang bersih sebelum ada agent atau LLM lain yang menulis ke dalamnya. Semua perbaikan bersifat deterministik dan bisa diulang.

## Keputusan sebelum mulai

| ID | Pertanyaan | Usulan |
| :--- | :--- | :--- |
| D14-1 | Kartu projek: ganti nama berkas atau cukup `aliases`? | `aliases` + `title`. Ganti nama memutus tautan lama |
| D14-2 | Tautan harian putus: buat catatan harian otomatis atau hapus tautannya? | Hapus tautannya, berhenti membuatnya |

## Task

| ID | Task | Berkas | Status |
| :--- | :--- | :--- | :--- |
| S14-T01 | Kartu projek punya `aliases` (nama projek) agar tidak tampil sebagai "README" | `harvester/project_harvester.py`, migrasi vault | ✅ |
| S14-T02 | Berhenti membuat tautan `99_Daily/<tanggal>`, bersihkan 30 tautan putus | `harvester/entity_linker.py`, migrasi vault | ✅ |
| S14-T03 | Judul sesi bersih dari teks harness (Antigravity) dan judul lama diperbaiki | `harvester/extractor.py`, migrasi vault | ✅ |
| S14-T04 | Blok `dataview` dan kode khusus Obsidian tidak ikut diindeks | `engine/chunker.py` atau `engine/parser.py` | ✅ |
| S14-T05 | Skema frontmatter bersama dan perintah `devbrain lint` | `core/schema.py` (baru), `cli/commands/lint_cmd.py` (baru) | ✅ |
| S14-T06 | Perbaiki 3 frontmatter rusak dan 1 yang tidak ada | migrasi vault (lewat `lint --fix`) | ✅ |
| S14-T07 | ADR bisa digantikan: ADR baru untuk model multibahasa, ADR-001 `superseded`; briefing hanya menampilkan yang aktif | `adr/manager.py`, `cli/commands/adr_cmd.py` | ✅ |
| S14-T08 | Hapus teks ganda `(Live Dataview):` di baris tautan sesi | `harvester/project_harvester.py`, `harvester/entity_linker.py` | ✅ |
| S14-T09 | Test, evaluasi retrieval sebelum/sesudah, changelog, rilis | `tests/`, `docs/changelog/` | ✅ |

## Rincian

**S14-T01.** Tambahkan `aliases: [<nama projek>]` ke frontmatter kartu baru dan kartu lama. Nama berkas tetap `README.md`.
*Selesai bila:* quick switcher Obsidian menemukan kartu dengan nama projeknya; tidak ada tautan lama yang putus.

**S14-T02.** `generate_graph_links_block` tidak lagi menulis tautan Timeline. Migrasi menghapus baris `- **Timeline:** [[99_Daily/...]]` dari catatan sesi.
*Selesai bila:* tidak ada tautan ke `99_Daily/` yang menunjuk ke berkas yang tidak ada.

**S14-T03.** Terapkan pembersihan yang sama dengan harvester Claude Code ke extractor Antigravity (buang `The user changed setting ...`, blok tag harness). Migrasi menulis ulang `title` sesi lama dari isinya.
*Selesai bila:* tidak ada judul sesi yang memuat teks harness; judul lama terbaca sebagai tugas.

**S14-T04.** Lewati blok kode berbahasa `dataview`, `dataviewjs`, dan `query` saat membuat chunk.
*Selesai bila:* jumlah chunk turun, dan hit@1 di `eval_retrieval.py` tidak turun.

**S14-T05.** Kunci wajib: `type`, `title`, `created`, `tags`. Kunci opsional: `updated`, `project`, `status`, `aliases`. `devbrain lint` melaporkan pelanggaran per catatan; `--fix` memperbaiki yang aman (mis. `date` → `created`).
*Selesai bila:* `devbrain lint` pada vault utama melaporkan 0 pelanggaran wajib setelah `--fix`.

**S14-T07.** `devbrain adr supersede <lama> <baru>` mengubah status dan menautkan keduanya. `get_decisions` dan briefing hanya menampilkan `accepted`.
*Selesai bila:* briefing devbrain tidak lagi menampilkan ADR-001 setelah digantikan.

## Hasil
- Rilis [v1.10.0-alpha](../../../changelog/v1.10.0-alpha.md). Keputusan: D14-1 `aliases`, D14-2 hapus tautan.
- Vault utama dimigrasi: 142 catatan diperbaiki, `devbrain lint` bersih, ADR-002 menggantikan ADR-001.
- Tambahan di luar rencana: aturan `noisy-link-label` untuk label tautan sesi di kartu projek.
- Test 91 → 100.

## Catatan
- Semua migrasi vault harus punya `--dry-run` dan dijalankan pada salinan vault lebih dulu.
- Cadangkan vault sebelum migrasi sungguhan.
