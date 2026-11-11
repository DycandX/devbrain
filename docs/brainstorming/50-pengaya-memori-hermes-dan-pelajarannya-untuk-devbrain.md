# 50. Enam Pengaya Memori Hermes dan Pelajarannya untuk DevBrain

| Metadata | Nilai |
| :--- | :--- |
| **Topik** | Pemeriksaan enam "pengaya memori gratis" untuk Hermes Agent yang dipromosikan carousel Instagram julian.goldie_: sumber asli, ketepatan klaim, kematangan, cara kerja, serta pola yang layak dan tidak layak diadopsi DevBrain |
| **Status** | 🔬 Riset (repo, API GitHub, marketplace Hermes), belum dieksekusi |
| **Referensi** | [47](./47-hermes-agent-sebagai-badan-jarvis-jev-dan-strategi-ui.md), [48](./48-peran-llm-audit-vault-dan-arah-rag.md), [49](./49-siklus-belajar-hermes-dan-adopsinya-di-devbrain.md), [rencana sprint](../sprints/level-1/_index.md) |
| **Tanggal** | 2026-11-11 |

> Carousel aslinya tidak bisa diambil. Klaim yang diuji di sini berasal dari screenshot yang dikirim pemilik, lalu dicocokkan dengan repo dan listing marketplace per 2026-11-11.

---

## 1. Ringkasan

- Keenam pengaya itu benar ada, dan semuanya terdaftar di ekosistem resmi Hermes. Teks carousel hampir sama kata per kata dengan README masing-masing, jadi kemungkinan besar disusun dari teks promosi, bukan dari pengujian.
- Hanya dua yang cukup matang: **hermes-dreaming** dan **ZeroMem**. Empat lainnya berumur 4–5 hari saat dipromosikan, dengan 0–2 bintang.
- Ada tiga klaim yang menyesatkan:
  - "Signed change log" milik mindhall tidak memakai kriptografi.
  - "Zero model calls" milik ZeroMem tetap menjalankan model embedding.
  - Munin tidak terbukti gratis.
- Bagi DevBrain, nilai keenam proyek ini ada pada **pola rancangannya**, bukan untuk dipasang. Empat di antaranya menjauhkan LLM dari jalur simpan dan cari, prinsip yang sama dengan DevBrain.

---

## 2. Sumber dan Klaim

| Pengaya | Sumber | Klaim carousel | Kenyataan | Penilaian |
| :--- | :--- | :--- | :--- | :--- |
| hermes-dreaming | [itpartypattaya/hermes-dreaming](https://github.com/itpartypattaya/hermes-dreaming) | Konsolidasi tiap malam; hanya menyimpan fakta yang didukung ucapan orang | Skrip Python deterministik. Sebuah fakta dihitung bila **manusia** menyebutnya pada **hari yang berbeda** di chat tepercaya. Maksimal 6 perubahan per malam. Judge LLM opsional hanya bisa memveto | Akurat. "Didukung" berarti heuristik frekuensi, bukan pencocokan dengan kutipan |
| mindhall | [jai-srinivas/mindhall](https://github.com/jai-srinivas/mindhall) | Satu memori untuk semua AI, dengan change log bertanda tangan | SQLite dengan tabel `changes`. Kolom `by` berisi teks bebas dari `clientInfo.name` yang dideklarasikan klien sendiri. Tidak ada HMAC, kunci, atau rantai hash | **Menyesatkan** |
| ZeroMem | [ptaranat/zeromem](https://github.com/ptaranat/zeromem) | Setiap pesan disimpan verbatim dalam satu berkas; nol panggilan model | Satu SQLite, tanpa LLM. Namun secara default setiap giliran di-embed dengan bge-small-en-v1.5 (±130 MB) | Sebagian menyesatkan: yang nol adalah LLM, bukan inferensi |
| Recall | [memeshee/hermes-recall](https://github.com/memeshee/hermes-recall) | Index lokal untuk PDF, Word, Excel, dan slide; tanpa internet | FTS5 + BM25 dengan bonus path dan kebaruan. Parser PDF/Office buatan sendiri berbasis regex, tanpa OCR | Akurat, tetapi parsernya rapuh |
| Munin | [Munin-Labs-AI/munin-hermes-plug-in](https://github.com/Munin-Labs-AI/munin-hermes-plug-in) | Keputusan rapat dicek terhadap transkrip sampai ke menit; gratis | Konektor MIT ke server MCP SaaS (`app.muninlabs.ai/mcp`, OAuth). Transkripsi oleh ElevenLabs, data di Supabase Tokyo, tanpa E2E, hanya bisa dipakai dengan undangan. Pengecekan dilakukan LLM dengan mengikuti instruksi skill | **"Gratis" tidak terbukti.** Pengecekannya probabilistik |
| Hermes Roam | [vcruz305/hermes-roam](https://github.com/vcruz305/hermes-roam) | Sinkronisasi terenkripsi AES-256 ke penyimpanan milik sendiri | AES-256-GCM + AAD, HEAD ditandatangani HMAC-SHA256 dengan kunci turunan HKDF, compare-and-swap, rollback floor. Backend S3/R2, git, atau lokal | Akurat. Belum diaudit; tidak bisa menggabungkan isi file |

## 3. Kematangan (per 2026-11-11)

| Pengaya | Dibuat | Bintang/fork | Commit | Versi | Lisensi | Test | Tingkat |
| :--- | :--- | :---: | :---: | :--- | :--- | :--- | :--- |
| hermes-dreaming | 2026-08-16 | 23/3 | 154 | v3.8.6 | MIT | unittest + CI ruff | Kecil tetapi terawat |
| ZeroMem | 2026-08-05 | 20/6 | 32 | PyPI 0.4.1 | MIT | test Rust | Muda tetapi kredibel; port pihak ketiga dari arXiv:2607.29377 |
| Hermes Roam | 2026-11-07 | 2/1 | 17 | v0.5.6 | Apache-2.0 | klaim 586–613 (belum diverifikasi) | Alpha; sudah ditinjau maintainer Hermes |
| Recall | 2026-11-06 | 0/0 | 6 | v0.2.1 | MIT | 30 selftest | Sangat mentah |
| mindhall | 2026-11-07 | 0/0 | ±27 | v0.3.2 | MIT | pytest | Sangat mentah; klaimnya berlebihan |
| Munin | 2026-11-07 | 0/0 | 4 | v0.1.0 | MIT (konektor saja) | tidak ada | Pembungkus tipis untuk SaaS |

---

## 4. Posisi DevBrain (v1.11.0-alpha)

| Kemampuan | DevBrain | Keterangan |
| :--- | :---: | :--- |
| Konsolidasi berkala (dreaming) | 📋 Rencana | Curator tanpa LLM di Sprint 18; proposal LLM opsional di Sprint 19 |
| Memori bersama + change log (mindhall) | ⚠️ Sebagian | Sudah ada `memory_ledger` append-only, tetapi tanpa rantai hash. `remember` menulis `source="mcp"` secara hardcode, jadi agen penulisnya tidak bisa dibedakan |
| Simpan dan cari tanpa LLM (ZeroMem) | ✅ | Sesi disimpan sebagai ringkasan, bukan verbatim |
| Index dokumen non-Markdown (Recall) | ❌ | Hanya `*.md` yang diindeks. Folder `DOCS` terlewat |
| Memori rapat (Munin) | ❌ | Yang terdekat: `record_decision` dan ADR |
| Sinkronisasi terenkripsi (Roam) | ❌ | Arah roadmap: satu instance homeserver (Fase 3) |

Guard memori DevBrain sudah lebih ketat daripada sebagian besar pengaya ini. Masalah terbesarnya bukan fitur, melainkan adopsi: Claude Code tercatat **0 kali memanggil DevBrain** ([HANDOFF.md](../../HANDOFF.md)).

---

## 5. Pola yang Layak Diadopsi

| # | Ide | Asal | Sprint | Bentuk di DevBrain |
| :---: | :--- | :--- | :--- | :--- |
| 1 | Identitas agen di `source` ledger, diambil dari `clientInfo.name` MCP | mindhall | 16 | Perubahan kecil di `remember` dan `record_decision`. Diberi label *atribusi yang dideklarasikan klien*, bukan autentikasi |
| 2 | Hint ambien: dipicu kata isyarat, dibatasi jumlah karakter, path tidak diulang dalam satu sesi, isinya hanya petunjuk | Recall | 16, diukur di 20 | Batas lewat `core/textutil.py`, ambang skor dari gate RRF, dan agen tetap memanggil `read_note` untuk membaca isinya. Kandidat terkuat untuk memecah angka 0 panggilan |
| 3 | Ledger berantai hash (`prev_hash` + `sha256`), dengan HMAC opsional | Roam; memperbaiki klaim mindhall | 16 atau 18 | Cukup `hashlib`/`hmac` dari stdlib. Ditambah `devbrain memory ledger --verify` |
| 4 | Undo berbasis snapshot sebelum/sesudah, ditolak bila baris sudah diubah lagi | mindhall | 18 | Untuk `curator restore`; snapshot disimpan di `detail` ledger |
| 5 | Gerbang korroborasi: bukti dari ≥2 sesi atau hari berbeda, bukan dari agen itu sendiri | hermes-dreaming | 18–19 | Menaikkan prioritas proposal |
| 6 | Batas perubahan per run, gerbang bangun, daftar tolak dengan cooldown, loss guard | hermes-dreaming | 18–19 | Batas pengaman untuk curator |
| 7 | LLM hanya boleh memveto, tidak menambah; dengan batas biaya per run | hermes-dreaming | 19 | Sejalan dengan doc 48 |
| 8 | Index dokumen non-Markdown sebagai ekstra opsional | Recall | Backlog | `devbrain[docs]` dengan parser sungguhan (`pypdf`), bukan regex. Tetap menolak path di luar root |
| 9 | Teks sumber sebagai kebenaran, index sebagai turunan yang bisa dibangun ulang | ZeroMem | Backlog FTS5 | Sudah sejalan. `state.db` Hermes dibaca read-only, tidak diduplikasi |
| 10 | CAS, rollback floor, daftar "jangan pernah disinkronkan" | Roam | Fase 3 | Relevan bila nanti ada ekspor terenkripsi |

Butir 1–3 tidak melanggar aturan [AGENTS.md](../../AGENTS.md): tanpa LLM, tanpa dependensi baru, dan semua tulis tetap lewat `memory/guard.py`.

## 6. Yang Harus Dihindari

- **Munin.** Audio dan transkrip dikirim ke cloud tanpa E2E. Satu-satunya yang layak dipinjam adalah format sitasi `id · waktu · baris`, misalnya untuk ADR hasil Sprint 19 yang merujuk ke sesi dan nomor giliran.
- **Autentikasi dengan URL rahasia** ala mindhall untuk `serve --no-stdio`. Mode homeserver butuh token sungguhan.
- **Penyimpanan verbatim tanpa batas** ala ZeroMem: tanpa pruning, tanpa batas panjang recall yang disuntikkan. ZeroMem juga memakai satu-satunya slot `memory.provider` di Hermes, sehingga memasangnya memecah "satu memori" menjadi dua (lihat [47](./47-hermes-agent-sebagai-badan-jarvis-jev-dan-strategi-ui.md)).
- **hermes-dreaming bersama holographic** sebelum Sprint 16, karena holographic membuka jalur tulis yang tidak dicakup `memory.write_approval` (bertentangan dengan D15-1).
- **Membaca path bebas** ala `recall_open`. `read_note` DevBrain sudah benar dengan menolak path di luar vault.
- **Mengarahkan Roam ke `.brain_data/`.** Roam tidak bisa menggabungkan isi file, sedangkan memori DevBrain ada di `brain.db`.

---

## 7. Keterbatasan

- Tidak ada ulasan independen atau laporan pengguna untuk proyek mana pun. Angka benchmark dan akurasi adalah klaim penulis masing-masing.
- Kode berikut belum dibaca: bobot di `dream.py`, logika fusi ZeroMem, dan indexer Recall.
- Harga dan kebijakan retensi Munin tidak dipublikasikan.

## 8. Sumber

- Laporan riset lengkap beserta tautan per klaim: `reports/Pengaya memori Hermes Agent.md` (lokal, tidak di-commit)
- [Marketplace Hermes](https://hermes-agent.nousresearch.com/marketplace/hermes-roam), [docs hermes-dreaming](https://hermes-agent.nousresearch.com/docs/plugins/hermes-dreaming)
- [PR katalog Roam #150563](https://github.com/NousResearch/hermes-agent/pull/150563), [PR katalog Munin #150768](https://github.com/NousResearch/hermes-agent/pull/150768)
- [Paper Zero-Mem, arXiv:2607.29377](https://arxiv.org/abs/2607.29377)
