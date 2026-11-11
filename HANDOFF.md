# Handoff: devbrain (Central AI Brain Hub)

Dokumen serah terima untuk agent atau developer yang melanjutkan projek ini. Baca berkas ini lebih dulu, lalu [AGENTS.md](AGENTS.md) untuk aturan kerja.

| | |
| :--- | :--- |
| **Versi** | `1.11.0-alpha` |
| **Branch** | `main`. Commit sejak v1.7.0 belum di-push ke `origin` (cek `git status -sb`) |
| **Test** | 132 lulus, sekitar 3 menit |
| **Ditulis** | 2026-11-11 |
| **Pemilik** | DycandX (bahasa percakapan: Indonesia) |

---

## 1. Projek ini apa

`devbrain` adalah **mesin memori dan konteks** untuk AI agent. Ia menjadikan vault Obsidian (berkas Markdown) sebagai sumber kebenaran bersama untuk Claude Code, Antigravity IDE, Hermes, dan agent lain, lewat server MCP.

Ia **bukan** asisten itu sendiri. Rencana jangka panjang pemilik adalah asisten pribadi bernama **Jarvis**, dengan [Hermes Agent](https://hermes-agent.nousresearch.com/docs) sebagai badannya (runtime, kanal chat, cron) dan devbrain sebagai memorinya. Lihat [dokumen 45](docs/brainstorming/45-roadmap-devbrain-menuju-jarvis.md) dan [dokumen 47](docs/brainstorming/47-hermes-agent-sebagai-badan-jarvis-jev-dan-strategi-ui.md).

Tujuan kedua pemilik: **menghemat token** agent. Hipotesisnya belum terbukti, alat ukurnya (`devbrain usage`) sudah ada. Lihat [dokumen 46](docs/brainstorming/46-riset-projek-serupa-efisiensi-token-dan-tech-stack.md) bagian 2.

Prinsip yang dipegang:
- Inti devbrain **tidak memanggil LLM**. Lokal, offline, deterministik.
- Markdown adalah sumber kebenaran untuk manusia. Indeks dan SQLite bisa dibangun ulang dari vault.
- Ukur dulu sebelum mengklaim. Setiap perubahan retrieval diukur dengan `benchmarks/eval_retrieval.py`.

---

## 2. Lingkungan saat ini

| Komponen | Lokasi / nilai |
| :--- | :--- |
| Repo | `E:\_PROJECT\_Central AI Brain Hub` |
| Vault utama | `E:\_PROJECT\_DevBrain_Vault` (85 catatan awal + 66 kartu projek + 11 sesi Claude Code) |
| Workspace yang dipindai | `E:\_PROJECT` |
| OS | Windows 11, Python 3.14 (`C:\Python314\python.exe`) |
| Instalasi | Editable (`pip install -e .`). Perintah `devbrain` **tidak ada di PATH**, pakai `python -m devbrain.cli.main` |
| Server MCP | `central-brain`, terdaftar di `~/.claude.json` dan tiga `~/.gemini/.../mcp_config.json`, menunjuk ke vault utama |
| Model embedding | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (sekitar 220 MB, cache FastEmbed) |
| Hermes | Data di `%LOCALAPPDATA%\hermes` (program di subfolder `hermes-agent`, versi git `1c8dcdb`). `~/.hermes` hanya sisa lama. Belum disambungkan ke devbrain |

`demo_vault/` di repo adalah vault lama untuk demo, diabaikan Git. Vault yang dipakai sungguhan adalah `_DevBrain_Vault`.

---

## 3. Arsitektur

```text
src/devbrain/
├── cli/            Typer CLI. main.py mendaftarkan semua perintah
├── core/           config (.brainrc.json), konstanta taksonomi, SQLite, scaffolder,
│                   fsutil (tulis atomik), textutil (batas ukuran teks)
├── engine/         parser, chunker, embeddings (FastEmbed), bm25, storage,
│                   hybrid_search (RRF + gerbang relevansi)
├── harvester/      penemuan sesi agent, ekstraksi, sanitizer secret,
│                   pemindai projek (markers, inspector, manifest_parser, service)
├── context/        perakit briefing (build_task_context)
├── memory/         remember / recall / forget
├── mcp_server/     12 tool MCP
├── adr/, rules/    ADR dan generator AGENTS.md/CLAUDE.md untuk projek lain
└── watcher/        watchdog, re-index saat catatan berubah
```

Alur data:

```text
sesi agent + folder projek ──harvester──► vault Markdown ──engine──► indeks
                                               │                       │
                              memory (SQLite) ─┴──► context/builder ◄──┘
                                                        │
                                                 mcp_server (12 tool) ──► agent
```

Penyimpanan per vault, di `.brain_data/`:
- `index_metadata.json` + `vectors.npy`: indeks chunk dan vektor. Mencatat model pembuatnya; diganti model berarti dibangun ulang.
- `brain.db`: SQLite (memori, ADR, file cache).
- `ingested_sessions.json`: registry sesi yang sudah dipanen.

### Tool MCP

| Tool | Catatan |
| :--- | :--- |
| `search_brain` | Satu baris per catatan secara default. `detail="snippet"` untuk cuplikan |
| `read_note` | Baca catatan atau satu bagian (`heading`). Menolak path di luar vault |
| `build_task_context` | Briefing. Mengutamakan ketepatan: kosong lebih baik daripada salah |
| `get_project_context` | Kartu projek, dibatasi 6.000 karakter |
| `remember` / `recall` / `forget` | Memori jangka panjang, dengan scope projek. Setiap tulisan melewati pemeriksa isi (`memory/guard.py`); `pinned` masuk memori inti |
| `get_user_context`, `get_decisions`, `record_decision`, `write_agent_log`, `load_skill` | |

---

## 4. Cara kerja sehari-hari

```bash
pip install -e ".[dev]"
python -m pytest -q
python benchmarks/eval_retrieval.py
python -m devbrain.cli.main status --vault "E:/_PROJECT/_DevBrain_Vault"
python -m devbrain.cli.main ingest --from claude-code --vault "E:/_PROJECT/_DevBrain_Vault"
python -m devbrain.cli.main ingest projects --dry-run --vault "E:/_PROJECT/_DevBrain_Vault"
python -m devbrain.cli.main usage
```

Setelah mengubah kode server MCP, sesi agent harus dimulai ulang agar `central-brain` memuat kode baru.

---

## 5. Riwayat kerja terakhir

| Versi | Isi | Dokumen |
| :--- | :--- | :--- |
| 1.7.0 | Isolasi test dari home, tulis config atomik, RRF, model multibahasa, harvester Claude Code, watcher di `serve`, alat evaluasi | [v1.7.0](docs/changelog/v1.7.0-alpha.md) |
| 1.8.0 | `remember`/`recall`/`forget`, `read_note`, batas ukuran keluaran tool, `devbrain usage`, perbaikan kebocoran koneksi SQLite | [v1.8.0](docs/changelog/v1.8.0-alpha.md) |
| 1.8.1 | Briefing pada vault nyata: ringkasan projek, pemilihan catatan lewat kesepakatan dua pemeringkat, riwayat sesi lewat tautan Project Hub | [v1.8.1](docs/changelog/v1.8.1-alpha.md) |
| 1.9.0 | Pemindaian workspace bertingkat, grup projek, sandbox, Flutter/PHP/Java/.NET/C | [v1.9.0](docs/changelog/v1.9.0-alpha.md) |
| 1.11.0 | Sprint 15: pemeriksa isi memori, mode persetujuan, `devbrain memory`, memori inti dipin, ledger | [v1.11.0](docs/changelog/v1.11.0-alpha.md) |
| 1.10.0 | Sprint 14: `devbrain lint --fix`, aliases kartu, tautan harian, judul sesi bersih, `adr supersede`; vault utama dimigrasi | [v1.10.0](docs/changelog/v1.10.0-alpha.md) |

Setiap changelog memuat masalah, perbaikan, angka pengukuran, dan keterbatasan.

---

## 6. Angka acuan

| Ukuran | Nilai | Sumber |
| :--- | :--- | :--- |
| Retrieval hit@1 (korpus evaluasi, hybrid) | 0,969 | `benchmarks/eval_retrieval.py` |
| Penolakan pertanyaan tanpa jawaban | 6 dari 6 | sama |
| Beban tetap definisi 12 tool | sekitar 1.470 token per sesi | v1.8.0 |
| Pemakaian token Claude Code (semua waktu) | 384 juta konteks, 97% dari cache, 0 panggilan ke devbrain | `devbrain usage`, 2026-11-10 |
| Pemindaian `E:\_PROJECT` | 65 projek, sekitar 19 detik | v1.9.0 |

Korpus evaluasi kecil (16 catatan, 38 pertanyaan) dan ditulis sendiri. Angkanya menunjukkan arah, bukan kinerja di vault nyata.

---

## 7. Masalah yang diketahui

| Masalah | Dampak | Tempat |
| :--- | :--- | :--- |
| `DOCS` dan `_Laporan Magang FXMedia` di `_fxmedia` tidak tercatat | Konteks magang hilang | Aturan "mayoritas Markdown" di `inspector.py` |
| Folder berisi `skills/` dianggap skill, bukan projek | Satu projek portofolio salah kelas | `inspector.py` langkah 1 |
| Sesi yang dijalankan di folder projek tapi tidak terkait tetap muncul di riwayat projek itu | Briefing sedikit berisik | `context/builder.py` `get_project_sessions` |
| Batas relevansi (cosine 0,38, kesepakatan 0,6) dikalibrasi dari sedikit data | Bisa terlalu longgar atau ketat | `core/constants.py`, `context/builder.py` |
| `serve --no-stdio` (mode jaringan) belum diuji, tanpa autentikasi | Belum bisa dipakai di homeserver | `cli/commands/serve_cmd.py` |
| Klaim latensi dan RAM di README belum diukur ulang sejak ganti model | Dokumentasi mungkin salah | `README.md` |
| Peringatan FastEmbed soal mean pooling pada model multibahasa | Hanya peringatan | `engine/embeddings.py` |

---

## 8. Langkah berikutnya (urut prioritas)

Rencana kerja kini dipecah menjadi **Sprint 14–20** dengan task bernomor (mis. `S14-T03`), keputusan yang dibutuhkan, dan kriteria selesai. Lihat [indeks sprint Level 1](docs/sprints/level-1/_index.md). Daftar di bawah adalah ringkasannya.

1. **Hook Claude Code.** `SessionStart` memuat briefing, `Stop` menyimpan ringkasan. Agar devbrain terpakai tanpa agent harus ingat. Keputusan terbuka: dipasang global (`~/.claude/settings.json`) atau per projek.
2. **Uji A/B hemat token.** 10 tugas nyata dengan dan tanpa devbrain, dibandingkan lewat `devbrain usage`. Butuh beberapa hari pemakaian dulu.
3. **Rapikan masalah kecil di bagian 7**: teks dobel, folder dokumen non-Markdown, klasifikasi skill.
4. **Sambungkan Hermes** lewat `mcp_servers` di `%LOCALAPPDATA%\hermes\config.yaml` (lihat [dokumen 49](docs/brainstorming/49-siklus-belajar-hermes-dan-adopsinya-di-devbrain.md)).
5. **Satukan indeks ke SQLite** (FTS5 + vektor). Belum mendesak di ukuran vault sekarang.
6. **Mode homeserver**: transport HTTP dan autentikasi.

Audit vault dan rekomendasi perapian ada di [dokumen 48](docs/brainstorming/48-peran-llm-audit-vault-dan-arah-rag.md); langkah perapian vault di sana diusulkan dikerjakan sebelum hook.

Rencana lengkap ada di [dokumen 45](docs/brainstorming/45-roadmap-devbrain-menuju-jarvis.md), dengan revisi Fase 4 sampai 6 di [dokumen 47](docs/brainstorming/47-hermes-agent-sebagai-badan-jarvis-jev-dan-strategi-ui.md).

---

## 9. Keputusan yang menunggu pemilik

| Pertanyaan | Kapan |
| :--- | :--- |
| Hook dipasang global atau per projek? | Sebelum langkah 1 |
| Kapan push ke `origin`? | Kapan saja |
| Distilasi sesi pakai model lokal (Ollama) atau API murah? | Sebelum ekstraksi memori otomatis |
| Hermes berjalan di laptop atau homeserver? | Sebelum langkah 4 |
| Apakah `test-project` sungguhan sandbox? | Bisa diatur di `project_groups` vault |

---

## 10. Hal yang mudah keliru

- **Jangan jalankan test tanpa fixture `isolated_home`.** Fixture autouse di `tests/conftest.py` mencegah test menulis ke `~/.claude.json`. Test baru yang memanggil `devbrain init` atau `client_config` harus tetap lewat fixture ini.
- **Mengganti model embedding berarti mengindeks ulang** dan mengkalibrasi ulang `EMBEDDING_MODEL_MIN_SIMILARITY` dengan `benchmarks/eval_retrieval.py`.
- **`search_brain` dan `build_task_context` punya aturan berbeda.** Pencarian mengutamakan kelengkapan (agent yang menilai), briefing mengutamakan ketepatan (agent cenderung percaya).
- **Jangan ubah berkas di `00_System/Memories/` secara manual.** Sumber resminya SQLite, berkas itu ditulis ulang devbrain.
- **Server MCP yang sedang berjalan memegang kode lama** sampai sesi agent dimulai ulang. Untuk menguji perubahan tanpa memulai ulang, jalankan kode lewat skrip pada salinan vault.
- **Vault berisi data pribadi**, termasuk prompt yang menempelkan pesan obrolan dengan nama orang. Sanitizer hanya menyamarkan kredensial.
