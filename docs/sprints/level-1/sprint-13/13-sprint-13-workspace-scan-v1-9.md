# Sprint 13: Pemindaian Workspace Bertingkat, Grup & Sandbox

| Metadata | Nilai |
| :--- | :--- |
| **Sprint** | Sprint 13 |
| **Versi** | `v1.9.0-alpha` |
| **Status** | ✅ Done (dicatat setelah selesai) |
| **Dokumen** | [changelog v1.9.0](../../../changelog/v1.9.0-alpha.md) |
| **Commit** | `79ab825` |

## Tujuan
Projek di dalam folder wadah (`_fxmedia`, `_TEST`) ikut tercatat, dengan asal-usul grup dan pemisahan sandbox.

## Task

| ID | Task | Berkas | Status |
| :--- | :--- | :--- | :--- |
| S13-T01 | Penanda projek, vault, dan wadah di satu modul | `harvester/markers.py` | ✅ |
| S13-T02 | Kenali Flutter, PHP/Laravel, Java, .NET, C/C++ | `harvester/manifest_parser.py` | ✅ |
| S13-T03 | Pemindaian bertingkat sampai 3 level | `harvester/service.py` | ✅ |
| S13-T04 | Grup projek di frontmatter dan tag, diatur lewat `project_groups` | `core/config.py`, `harvester/project_harvester.py` | ✅ |
| S13-T05 | Sandbox tidak masuk briefing projek lain | `context/builder.py` | ✅ |
| S13-T06 | Nama kartu unik, nama bawaan generator diganti nama folder | `harvester/service.py`, `harvester/markers.py` | ✅ |
| S13-T07 | Tautan sesi tidak hilang saat kartu dipindai ulang | `harvester/project_harvester.py` | ✅ |
| S13-T08 | Pemindaian sungguhan ke vault utama | vault | ✅ |

## Hasil
- `E:\_PROJECT`: sekitar 26 → 65 projek; 12 projek FXMedia bergrup; 8 kartu sandbox.
- Test 83 → 91.
