# Sprint 20: Uji A/B Hemat Token

| Metadata | Nilai |
| :--- | :--- |
| **Sprint** | Sprint 20 |
| **Target versi** | Laporan (tanpa rilis kode, kecuali alat ukur) |
| **Status** | ⏳ Planned |
| **Dokumen** | [46](../../../brainstorming/46-riset-projek-serupa-efisiensi-token-dan-tech-stack.md) bagian 2.8 |
| **Butuh LLM** | Tidak |
| **Syarat** | Sprint 16 selesai dan beberapa minggu pemakaian nyata |

## Tujuan
Menjawab hipotesis pemilik dengan angka: apakah memori terpusat membuat agent lebih hemat token dan lebih berhasil.

## Task

| ID | Task | Berkas | Status |
| :--- | :--- | :--- | :--- |
| S20-T01 | Pilih 10 tugas nyata dari riwayat projek, dengan kriteria berhasil yang jelas | `benchmarks/ab/tasks.md` (baru) | ⏳ |
| S20-T02 | Prosedur: sesi baru, sekali tanpa DevBrain dan sekali dengan DevBrain | `benchmarks/ab/README.md` (baru) | ⏳ |
| S20-T03 | `devbrain usage --session <id>` untuk membandingkan dua sesi | `cli/commands/usage_cmd.py` | ⏳ |
| S20-T04 | Jalankan dan catat: token masuk, cache, keluar, panggilan tool, berhasil/gagal | `benchmarks/ab/results.md` (baru) | ⏳ |
| S20-T05 | Laporan dan keputusan lanjutan | `docs/brainstorming/` | ⏳ |

## Catatan
- Bandingkan juga biaya, bukan hanya token: token dari cache jauh lebih murah.
- Hasil negatif tetap dilaporkan apa adanya.
