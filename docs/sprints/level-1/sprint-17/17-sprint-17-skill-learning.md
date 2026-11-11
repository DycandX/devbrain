# Sprint 17: Skill yang Dipelajari Agent

| Metadata | Nilai |
| :--- | :--- |
| **Sprint** | Sprint 17 |
| **Target versi** | `v1.13.0-alpha` |
| **Status** | ✅ Done |
| **Dokumen** | [49](../../../brainstorming/49-siklus-belajar-hermes-dan-adopsinya-di-devbrain.md) bagian 2–4, [42](../../../brainstorming/42-sentralisasi-agent-skills-akses-eksternal-dan-manajemen-skill.md) |
| **Butuh LLM** | Tidak (agent yang menulis) |
| **Syarat** | Sprint 15 (gerbang tulis), Sprint 16 (folder bersama) |

## Tujuan
Semua agent bisa menyimpan dan memperbaiki skill di vault, dengan format yang juga dibaca Hermes dan Claude Code.

## Task

| ID | Task | Berkas | Status |
| :--- | :--- | :--- | :--- |
| S17-T01 | Tool MCP `save_skill` (buat) dan `patch_skill` (ganti potongan teks) | `skills/manager.py` (baru), `mcp_server/server.py` | ✅ |
| S17-T02 | Format `SKILL.md` sesuai standar agentskills.io (`name`, `description`, folder `references/`) | `skills/manager.py` | ✅ |
| S17-T03 | Gerbang tulis untuk skill: pemeriksa isi dan mode persetujuan (memakai Sprint 15) | `skills/manager.py`, `memory/guard.py` | ✅ |
| S17-T04 | `load_skill` bertahap: daftar dengan deskripsi, isi skill, berkas referensi | `mcp_server/server.py` | ✅ |
| S17-T05 | Panduan kapan menyimpan skill di deskripsi tool dan template rules | `mcp_server/server.py`, `rules/generator.py` | ✅ |
| S17-T06 | Catat asal skill (`created_by`: agent, sesi) dan hitungan pemakaian | `skills/manager.py` | ✅ |
| S17-T07 | Aktifkan `skills.create_dir` Hermes ke vault (keputusan D16-2) | konfigurasi | ❌ Tidak dikerjakan (lihat Hasil) |
| S17-T08 | Test, changelog, rilis | `tests/`, `docs/changelog/` | ✅ |

## Rincian

**S17-T01.** Skill hanya ditulis di `00_System/Agent_Skills/<nama>/`. Nama dibatasi huruf kecil, angka, dan tanda hubung. Skill yang di-`lock` tidak bisa diubah agent.
*Selesai bila:* skill yang disimpan Claude Code bisa dimuat Hermes, dan sebaliknya.

**S17-T05.** Agent diarahkan menyimpan skill untuk alur kerja yang tidak sepele, alur yang ditemukan setelah memperbaiki error, dan cara yang dikoreksi pengguna (pola Hermes). Bukan untuk tugas sekali jalan.

## Hasil
- Rilis [v1.13.0-alpha](../../../changelog/v1.13.0-alpha.md). Test 143 → 157.
- `skills.write_approval` diaktifkan di vault utama, mengikuti alasan D15-1.
- **S17-T07 sengaja tidak dikerjakan:** `create_dir` Hermes ke vault membuat Hermes menulis skill langsung ke folder bersama tanpa melewati pemeriksa isi dan persetujuan. Hermes tetap membaca skill vault dan bisa menyimpan lewat `save_skill`.
- Beban tetap tool naik dari ±1.470 ke ±1.790 token per sesi (14 tool).
- Agent belum bisa menambah berkas `references/` lewat MCP.

## Catatan
- Perhatikan curator Hermes: ia ikut mengelola skill di `create_dir`. Tentukan siapa yang mengarsipkan skill bersama (Sprint 18).
