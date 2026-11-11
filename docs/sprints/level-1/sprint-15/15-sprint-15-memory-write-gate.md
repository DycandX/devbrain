# Sprint 15: Gerbang Tulis & Memori Inti

| Metadata | Nilai |
| :--- | :--- |
| **Sprint** | Sprint 15 |
| **Target versi** | `v1.11.0-alpha` |
| **Status** | ✅ Done |
| **Dokumen** | [49](../../../brainstorming/49-siklus-belajar-hermes-dan-adopsinya-di-devbrain.md) bagian 3 |
| **Butuh LLM** | Tidak |
| **Syarat** | Sprint 14 selesai |

## Tujuan
Memori aman ditulis oleh lebih dari satu agent. Ini wajib sebelum Hermes disambungkan (Sprint 16): memori DevBrain disodorkan ke semua agent, jadi satu entri jahat bisa meracuni semuanya.

## Task

| ID | Task | Berkas | Status |
| :--- | :--- | :--- | :--- |
| S15-T01 | Pemeriksa isi memori: pola prompt injection, pencurian data, perintah berbahaya, Unicode tersembunyi | `memory/guard.py` (baru) | ✅ |
| S15-T02 | Mode persetujuan: `remember` menahan tulisan di status `pending` bila diaktifkan | `memory/manager.py`, `core/config.py` | ✅ |
| S15-T03 | Perintah `devbrain memory pending / approve / reject / list` | `cli/commands/memory_cmd.py` (baru) | ✅ |
| S15-T04 | Tingkat memori inti: memori yang dipin selalu masuk briefing, dengan batas karakter | `memory/manager.py`, `context/builder.py` | ✅ |
| S15-T05 | Aksi `patch` untuk memori (ganti potongan teks) selain `supersedes` | `memory/manager.py`, `cli/commands/memory_cmd.py` | ✅ (tanpa tool MCP, lihat Hasil) |
| S15-T06 | Catatan perubahan (ledger) untuk setiap tulis, ganti, dan lupa | `core/sqlite_db.py` | ✅ |
| S15-T07 | Test, changelog, rilis | `tests/`, `docs/changelog/` | ✅ |

## Rincian

**S15-T01.** Tolak isi yang mengandung instruksi untuk agent ("ignore previous instructions", "you must now ..."), perintah unduh-lalu-jalankan, kunci SSH, URL pengiriman data, dan karakter Unicode tak terlihat. Kembalikan alasan penolakan ke agent.
*Selesai bila:* kumpulan contoh jahat ditolak semua dan kumpulan contoh wajar diterima semua (diuji).

**S15-T02.** Config `memory.write_approval` (default `false`). Bila `true`, memori baru berstatus `pending`, tidak muncul di `recall` maupun briefing.
*Selesai bila:* memori pending tidak pernah tampil ke agent sebelum disetujui.

**S15-T04.** Memori dengan `pinned: true` selalu masuk briefing, maksimal `memory.core_char_limit` karakter (usulan 2.000). Melebihi batas ditolak, seperti Hermes, bukan dipotong diam-diam.
*Selesai bila:* briefing memuat semua memori inti; `remember(pinned=True)` gagal dengan pesan jelas saat penuh.

## Hasil
- Rilis [v1.11.0-alpha](../../../changelog/v1.11.0-alpha.md). Test 100 → 132.
- Pemeriksa isi: 16 contoh jahat ditolak, 8 fakta yang mirip diterima.
- **Penyimpangan S15-T05:** `patch` tersedia di manager dan CLI (`devbrain memory edit`), tidak sebagai tool MCP. Satu tool tambahan memakan ±100 token per sesi untuk semua agent, sedangkan memori berisi satu fakta per entri sehingga `remember(..., supersedes=...)` sudah cukup bagi agent.
- `write_approval` dibiarkan mati di vault utama; keputusan D15-1 di bawah.

## Catatan
- Skill akan memakai gerbang yang sama di Sprint 17.
