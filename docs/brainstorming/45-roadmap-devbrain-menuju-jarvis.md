# 45. Roadmap: Dari DevBrain (Mesin Memori) Menuju Jarvis (Asisten Personal)

| Metadata | Nilai |
| :--- | :--- |
| **Topik** | Posisi DevBrain terhadap Jarvis, kondisi nyata kode v1.6.0-alpha, dan urutan fase pengembangan |
| **Status** | 🗺️ Roadmap (belum dieksekusi) |
| **Referensi** | [41](./41-penjelasan-inti-arsitektur-hakikat-devbrain.md), [44](./44-rangkuman-komprehensif-evolusi-dan-spesifikasi-fitur-baru.md), [46](./46-riset-projek-serupa-efisiensi-token-dan-tech-stack.md), PRD Level 2 & 3 |
| **Tanggal** | 2026-11-10 |

---

## 1. Posisi: DevBrain Bukan Jarvis

DevBrain adalah **mesin memori dan konteks**. Jarvis adalah **asisten** yang memakai mesin itu.

| Kebutuhan Jarvis | Siapa yang mengerjakan |
| :--- | :--- |
| Mengingat (memori, konteks, keputusan, skill) | **DevBrain** |
| Berpikir (loop LLM: terima permintaan, panggil tool, jawab) | Jarvis (agent runtime) |
| Mendengar dan bicara (chat, suara) | Jarvis (kanal) |
| Bertindak (kalender, email, rumah) | Jarvis (connector MCP lain) |
| Jalan terus dan proaktif (jadwal, pengingat) | Jarvis (daemon + scheduler) |

Alasan dipisah:

1. DevBrain tetap berguna untuk agent coding (Claude Code, Antigravity) walau Jarvis belum ada.
2. Runtime agent berubah cepat. Memori harus bertahan lebih lama daripada runtime mana pun.
3. Di dalam DevBrain saat ini tidak ada satu pun pemanggilan LLM. Ini kelebihan (murah, offline, deterministik) yang layak dijaga di intinya.

```text
[ Telegram / Suara / CLI ]            [ Claude Code / Antigravity / Cursor ]
            │                                          │
   [ Jarvis: runtime + scheduler ]                     │
      │            │           │                       │
      │     [ Kalender/Email ] [ Home Assistant ]      │
      └──────────────┬─────────────────────────────────┘
                     ▼
        [ DevBrain: memori + konteks (MCP) ]
          Vault Markdown  +  SQLite (indeks, memori, ADR)
```

---

## 2. Kondisi Nyata v1.6.0-alpha (Hasil Baca Kode)

| Lapisan | Kondisi | Catatan |
| :--- | :--- | :--- |
| Penyimpanan (vault + `.brain_data/`) | ✅ | Solid |
| Retrieval (FastEmbed + BM25) | ⚠️ | Skor dense dan BM25 beda skala, model embedding khusus Inggris |
| Ingestion (harvester) | ⚠️ | Antigravity bagus. Claude Code hanya menyalin JSON mentah. Cline dibuang |
| State (SQLite) | ⚠️ | Tabel `memories` dan `file_cache` belum dipakai kode produksi |
| Context assembly | ✅ | Jalan, ukurannya terbatas, heuristiknya sederhana |
| Antarmuka (CLI + MCP stdio) | ⚠️ | Hanya lokal, watcher belum tersambung ke `serve` |
| Rules & skills | ✅ | Ada satu signature tool yang salah di template |
| Test | ⚠️ | 55 lulus, tapi satu test menimpa config MCP asli di home |

---

## 3. Prinsip

1. **Ukur dulu, klaim belakangan.** Angka hemat token dan kualitas retrieval harus berasal dari pengukuran sendiri.
2. **Markdown tetap sumber kebenaran untuk manusia.** SQLite adalah indeks yang bisa dibangun ulang kapan saja.
3. **Hemat token lewat desain tool**: jawaban kecil dulu, detail hanya kalau diminta.
4. **Satu fase selesai sebelum fase berikutnya.** Setiap fase punya kriteria selesai yang bisa dicek.
5. **Jangan membangun ulang yang sudah ada.** Pelajari atau pakai projek lain bila cocok (lihat [46](./46-riset-projek-serupa-efisiensi-token-dan-tech-stack.md)).

---

## 4. Fase

### Fase 0: Fondasi dan Alat Ukur

Tujuan: inti yang bisa dipercaya, plus cara mengukur kemajuan.

- Isolasi test dari home directory, pulihkan entri `central-brain` di config MCP.
- Penulisan config IDE secara atomik (temp lalu replace).
- Ganti fusi skor dengan Reciprocal Rank Fusion, tambah ambang relevansi.
- Sambungkan `VaultWatcher` ke `serve`.
- Perbaiki extractor Claude Code: satu catatan per sesi, isi berupa ringkasan percakapan.
- Rapikan: versi `pyproject.toml`, pin `mcp>=2`, signature `write_agent_log` di template rules.
- **Eval retrieval**: 30 sampai 50 pasangan pertanyaan dan catatan yang benar, dalam bahasa Indonesia dan Inggris.
- **Pencatat token**: baca field `usage` dari transkrip Claude Code, tampilkan lewat `devbrain stats`.

Selesai bila: test tidak menyentuh home, eval retrieval punya angka dasar, konsumsi token per sesi bisa dilihat.

### Fase 1: Memori Hidup dan Hemat Token

Tujuan: agent bisa menulis dan membaca memori, dengan biaya token yang terukur.

- Tool MCP `remember`, `recall`, `forget`, memakai tabel `memories` yang sudah ada. Setiap memori juga ditulis sebagai catatan Markdown agar terlihat di Obsidian.
- Progressive disclosure: `search_brain` mengembalikan indeks ringkas (judul, path, skor, satu baris), lalu `get_note(id)` untuk isi.
- Batas token di semua tool (`max_tokens`), termasuk `get_project_context` yang sekarang mengembalikan seluruh file.
- Distilasi sesi: transkrip diringkas menjadi keputusan, masalah, dan solusi. Butuh LLM murah atau lokal, bersifat opsional.
- Hook Claude Code: `SessionStart` memuat briefing, `Stop` menyimpan ringkasan.
- Model embedding multibahasa, dipilih berdasarkan eval Fase 0.
- Masa berlaku memori: `valid_from`, `invalid_at`, `superseded_by` benar-benar dipakai saat recall.

Selesai bila: benchmark A/B (dengan dan tanpa DevBrain) pada 10 tugas nyata menunjukkan hasilnya, apa pun arahnya.

### Fase 2: Konsolidasi Penyimpanan

Tujuan: satu file database, tulis inkremental, siap tumbuh.

- Pindahkan chunk, vektor, dan indeks kata kunci ke `brain.db` (FTS5 + vektor sebagai BLOB, sqlite-vec bila perlu).
- Hapus `index_metadata.json`, `vectors.npy`, dan dependensi `rank-bm25`.
- Tabel `edges` dari wikilink, dipakai untuk memperluas hasil pencarian ke catatan tetangga.
- Perintah `devbrain index --rebuild` membangun ulang semuanya dari Markdown.

Selesai bila: menulis satu catatan tidak lagi menulis ulang seluruh indeks, dan skor eval tidak turun.

### Fase 3: Layanan Selalu Hidup (PRD Level 2 dan 3)

Tujuan: satu DevBrain di homeserver, dipakai semua perangkat.

- `devbrain serve` dengan transport HTTP (Streamable HTTP) dan autentikasi token.
- Jalan sebagai service di homeserver Jarvis, diakses lewat Tailscale.
- Sinkronisasi vault (Syncthing atau Git) dan backup terjadwal.
- Pemisahan scope kerja dan pribadi.

Selesai bila: laptop dan homeserver memakai memori yang sama tanpa konflik indeks.

### Fase 4: Jarvis Inti (Repo Terpisah)

Tujuan: asisten yang bisa diajak bicara.

- Agent runtime (Claude Agent SDK) dengan DevBrain sebagai MCP server.
- Satu kanal chat lebih dulu: Telegram.
- Taksonomi vault untuk domain pribadi: orang, tugas, jadwal, kebiasaan.
- Izin bertingkat: baca bebas, tulis memori bebas, aksi keluar perlu konfirmasi.

Selesai bila: pertanyaan lewat Telegram dijawab memakai memori DevBrain, dan percakapannya tersimpan kembali.

### Fase 5: Tangan dan Proaktif

- Connector kalender, email, tugas.
- Scheduler: briefing pagi, pengingat, review harian ke `99_Daily/`.
- Smart home lewat Home Assistant.

### Fase 6: Suara dan Multi-Perangkat

- STT dan TTS, klien mobile.

---

## 5. Keputusan yang Masih Terbuka

| Pertanyaan | Kapan harus diputuskan |
| :--- | :--- |
| Vault mana yang jadi vault utama? | Sebelum Fase 0 |
| Distilasi pakai model lokal (Ollama) atau API murah? | Fase 1 |
| Model embedding multibahasa yang mana? | Fase 1, dari hasil eval |
| Pemahaman kode: bangun sendiri atau pakai Graphify per repo? | Setelah Fase 1 |
| Sinkronisasi: Syncthing atau Git? | Fase 3 |
| Runtime Jarvis: Claude Agent SDK atau lainnya? | Fase 4 |

---

## 6. Yang Sengaja Tidak Dikerjakan

- Pindah ke Qdrant, Postgres, atau Neo4j sebelum ada bukti SQLite tidak cukup.
- Menulis ulang ke Go atau Rust.
- Membangun runtime agent di dalam DevBrain.
- Web dashboard sebelum Fase 3. Obsidian sudah menjadi tampilannya.
