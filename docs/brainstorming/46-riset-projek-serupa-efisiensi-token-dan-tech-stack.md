# 46. Riset: Projek Serupa, Konsep Hemat Token, dan Evaluasi Tech Stack

| Metadata | Nilai |
| :--- | :--- |
| **Topik** | Peta projek yang mirip DevBrain, penjelasan kapan memori terpusat menghemat token, dan perbandingan tech stack sekarang dengan alternatifnya |
| **Status** | 🔬 Riset (web + baca kode), belum ada yang dieksekusi |
| **Referensi** | [05](./05-komparasi-repo-open-source.md), [11](./11-sentralisasi-agent-skills-dan-efisiensi-token.md), [19](./19-analisis-komprehensif-pemilihan-tech-stack.md), [45](./45-roadmap-devbrain-menuju-jarvis.md) |
| **Tanggal** | 2026-11-10 |

> **Catatan keandalan.** Hampir semua angka benchmark di bawah berasal dari pembuat projeknya sendiri. Jumlah bintang GitHub berbeda antar sumber. Perlakukan sebagai petunjuk arah, bukan fakta terukur.

---

## 1. Projek Serupa

### 1.1 Peta kategori

| Kategori | Projek | Inti idenya |
| :--- | :--- | :--- |
| **A. Memori Markdown + MCP** (paling mirip) | Basic Memory, pola LLM Wiki (Karpathy), memori OpenClaw, Khoj | File Markdown sebagai sumber kebenaran, indeks lokal di sampingnya |
| **B. Perekam sesi agent coding** | claude-mem, MemPalace | Menangkap sesi otomatis lewat hook, lalu menyajikannya kembali |
| **C. Lapisan memori berbasis fakta** | Mem0, Zep/Graphiti, Letta, Cognee | LLM mengekstrak fakta dari percakapan, disimpan di vektor atau graf |
| **D. Graf pengetahuan kode** | Graphify | Struktur kode jadi graf, agent menelusuri graf alih-alih membaca file |
| **E. Bawaan platform** | Memory tool + context editing Anthropic, `CLAUDE.md` | Memori berbasis file yang dikelola model sendiri |

### 1.2 Yang paling layak dipelajari

**Basic Memory** (`basicmachines-co/basic-memory`, AGPL-3.0). Kembaran terdekat DevBrain.
- Markdown adalah sumber kebenaran, SQLite adalah indeks.
- File diurai menjadi *entity*, *observation*, dan *relation*, lalu wikilink menjadi graf yang bisa ditelusuri.
- Tool MCP untuk baca, tulis, cari, dan navigasi. Bisa membuat file Obsidian Canvas.
- **Pelajaran:** format observasi dan relasi di dalam Markdown, serta jalur tulis memori yang DevBrain belum punya.

**Graphify** (`safishamsi/graphify`). Ini yang dimaksud "grapify".
- Kode diurai dengan tree-sitter secara lokal dan deterministik, tanpa LLM. Dokumen, PDF, dan gambar lewat tahap semantik yang memakai LLM.
- Setiap sisi graf diberi label `EXTRACTED` (tertulis di sumber) atau `INFERRED` (hasil penalaran).
- Komunitas dideteksi dengan algoritma Leiden. Hasilnya `graph.json`, `GRAPH_REPORT.md` (node pusat, hubungan tak terduga, saran pertanyaan), dan `graph.html`.
- Hook mengarahkan agent untuk bertanya ke graf sebelum melakukan grep.
- Klaim hemat token: 71,5x menurut README pada satu benchmark. Sumber lain melaporkan 40 sampai 70%.
- **Pelajaran:** Graphify menjawab "bagaimana struktur kode ini", DevBrain menjawab "apa yang sudah diputuskan dan dikerjakan". Keduanya saling melengkapi. Lebih masuk akal memakai Graphify per repo dan menyimpan `GRAPH_REPORT.md` ke vault daripada membangun ulang.

**claude-mem** (`thedotmack/claude-mem`).
- Hook menangkap aktivitas sesi, LLM memampatkannya, lalu disuntikkan di sesi berikutnya.
- Pengambilan tiga lapis: indeks ringkas, lalu linimasa, lalu detail untuk ID yang dipilih. Diklaim hemat sekitar 10x.
- **Pelajaran:** pola *progressive disclosure* dan penangkapan lewat hook. DevBrain menangkap sesi setelah selesai (harvester), claude-mem menangkap saat berjalan.

**Pola LLM Wiki (Andrej Karpathy, April 2026).** Berupa gagasan, bukan produk.
- Agent tidak mengambil dari dokumen mentah setiap kali bertanya. Agent membangun dan merawat wiki Markdown yang saling terhubung.
- Folder sumber mentah tidak diubah. Wiki ditulis LLM di atasnya. Ada langkah *lint* berkala untuk memeriksa kontradiksi.
- **Pelajaran:** `90_Agent_Inbox/` adalah sumber mentah, `20_Knowledge/` seharusnya wiki hasil sulingan. Langkah penyulingan itu yang belum ada di DevBrain.

**Memori OpenClaw.** Asisten personal, jadi relevan untuk Jarvis.
- `MEMORY.md` untuk fakta jangka panjang, file harian untuk log.
- Chunk sekitar 400 token dengan tumpang tindih 80 token, disimpan di SQLite. Vektor lewat sqlite-vec, kata kunci lewat FTS5, bobot 70/30.
- **Pelajaran:** arsitekturnya hampir sama dengan DevBrain, tetapi seluruh indeks ada di satu file SQLite.

**Zep / Graphiti.**
- Setiap fakta punya rentang berlaku (`valid_at`, `invalid_at`). Fakta yang usang tidak dihapus, hanya ditutup masa berlakunya.
- **Pelajaran:** kolom `superseded_by` di tabel `memories` DevBrain sudah searah. Tinggal dipakai saat recall.

**Mem0, Letta, Cognee.** Mem0 cocok sebagai lapisan memori untuk agent yang sudah ada. Letta adalah runtime agent lengkap. Cognee untuk graf pengetahuan bersama. Ketiganya bergantung pada LLM untuk setiap penulisan memori.

### 1.3 Posisi DevBrain

| Yang DevBrain punya dan jarang ada di tempat lain | Yang projek lain punya dan DevBrain belum |
| :--- | :--- |
| Panen sesi lintas agent (Antigravity + Claude Code) ke satu vault | Jalur tulis memori (`remember`) |
| Kerangka ADR dan generator `AGENTS.md` / `CLAUDE.md` | Penyulingan sesi dengan LLM |
| Federasi multi-vault | Progressive disclosure |
| Pemindai projek dan kartu projek otomatis | Pencarian yang memakai graf wikilink |
| Inti tanpa LLM, sepenuhnya offline | Masa berlaku fakta, graf kode, hook |

---

## 2. Apakah Memori Terpusat Menghemat Token?

Jawaban singkat: **bisa, dengan syarat**. Hipotesisnya masuk akal, tetapi tidak otomatis benar.

### 2.1 Ke mana token habis dalam satu sesi agent

1. **Orientasi.** Agent membaca file, grep, dan menelusuri folder untuk memahami projek. Biasanya porsi terbesar di awal sesi.
2. **Penjelasan ulang.** Pengguna mengetik lagi konteks, preferensi, dan keputusan lama.
3. **Coba-salah.** Agent mengulang kesalahan yang dulu sudah pernah diselesaikan.
4. **Beban tetap.** System prompt, definisi tool, dan `CLAUDE.md` dikirim di setiap sesi.
5. **Akumulasi riwayat.** Setiap giliran mengirim ulang seluruh percakapan. Prompt caching membuat bagian ini murah, tetapi tetap memakan jendela konteks.

### 2.2 Di mana memori menghemat

Memori mengganti butir 1, 2, dan 3 dengan satu pengambilan kecil yang tepat sasaran. Contoh: kartu briefing 500 token menggantikan pembacaan sepuluh file sebesar 20.000 token.

### 2.3 Di mana memori justru menambah biaya

- **Definisi tool** ikut dimuat di setiap sesi, dipakai atau tidak.
- **Konteks yang disuntikkan tetapi tidak relevan** tetap dibayar, dan bisa menurunkan kualitas jawaban. Riset "context rot" dari Chroma menunjukkan keandalan model turun saat konteks memanjang, terutama bila ada isi yang mirip tetapi tidak menjawab.
- **Memori usang** mengarahkan agent ke jalan yang salah, dan biaya perbaikannya lebih besar daripada penghematannya.
- **Agent tetap harus membaca kode yang akan diubah.** *Hierarchy of Truth* di DevBrain sendiri menempatkan kode di atas catatan. Memori memangkas orientasi, bukan pekerjaan intinya.

### 2.4 Rumusnya

```text
Hemat bersih = (orientasi + penjelasan ulang + coba-salah yang terhindar)
             − (beban tool + konteks yang disuntikkan + biaya akibat memori salah)
```

Hasilnya positif bila pengambilan **kecil, relevan, dan masih berlaku**.

### 2.5 Angka dari luar, dan cara membacanya

| Sumber | Klaim | Catatan |
| :--- | :--- | :--- |
| Mem0 (paper arXiv 2504.19413) | Hemat lebih dari 90% token dibanding memuat seluruh riwayat | Benchmark percakapan, bukan coding. Satu ulasan menyebut pemakaian nyata sekitar 40% |
| Graphify | 71,5x | Kasus terbaik untuk pertanyaan tentang kode. Sumber lain: 40 sampai 70% |
| claude-mem | Sekitar 10x | Klaim projek sendiri |
| Anthropic (context editing + memory tool) | 84% pada evaluasi 100 giliran | Evaluasi internal |
| Dokumen 11 projek ini | 60 sampai 85%, contoh 95,8% | **Skenario ilustrasi, belum pernah diukur** |

Untuk pekerjaan coding, perkiraan yang jujur: penghematan besar pada sesi yang banyak orientasinya, dan kecil pada tugas yang memang harus membaca dan mengubah banyak kode.

Dua hal yang sering terlewat:
- **Token tidak sama dengan biaya.** Token yang terbaca dari cache jauh lebih murah. Menghemat token yang sudah di-cache hampir tidak menghemat uang.
- **Manfaat terbesar sering bukan token.** Konteks yang lebih bersih membuat agent lebih jarang salah dan lebih konsisten antar sesi.

### 2.6 Kondisi DevBrain sekarang dari sisi token

| Tool | Ukuran keluaran | Penilaian |
| :--- | :--- | :--- |
| `search_brain` | 5 hasil × 300 karakter | ✅ Terbatas |
| `build_task_context` | Ringkasan 500 karakter + 3 potongan 160 karakter | ✅ Terbatas, kecuali `User_Preferences.md` yang dimuat utuh |
| `get_project_context` | Seluruh file | ⚠️ Tanpa batas. Di vault demo masih sekitar 3 KB |
| `load_skill` | Seluruh `SKILL.md` | ✅ Wajar, dimuat saat diminta |
| Catatan sesi Claude Code | JSON mentah | ❌ Boros dan hampir tidak berguna saat terambil |
| 8 definisi tool | Belum diukur | Beban tetap per sesi |

### 2.7 Prinsip desain hemat token

1. **Progressive disclosure.** Indeks ringkas dulu, isi hanya untuk yang dipilih.
2. **Anggaran token di setiap tool**, dengan potongan yang rapi bila terlampaui.
3. **Kembalikan penunjuk, bukan isi**: path dan baris, biarkan agent memutuskan.
4. **Suling sebelum simpan.** Ringkasan keputusan lebih berguna daripada transkrip.
5. **Jumlah tool sedikit, deskripsinya pendek.**
6. **Ambang relevansi.** Lebih baik "tidak ditemukan" daripada lima hasil lemah.
7. **Tandai yang usang.** Memori lama yang bertentangan harus ditutup.

### 2.8 Cara membuktikannya

- Ambil 10 tugas nyata dari riwayat projek.
- Jalankan dua kali dari sesi baru: tanpa DevBrain dan dengan DevBrain.
- Catat token masuk, token cache, token keluar, jumlah panggilan tool, dan apakah tugasnya berhasil.
- Datanya sudah tersedia: setiap baris transkrip Claude Code di `~/.claude/projects/*/*.jsonl` punya field `usage` (`input_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens`, `output_tokens`). Harvester tinggal membacanya.

---

## 3. Evaluasi Tech Stack

### 3.1 Perbandingan per komponen

| Komponen | Sekarang | Masalah | Rekomendasi |
| :--- | :--- | :--- | :--- |
| Bahasa | Python 3.10+ | Tidak ada | **Tetap** |
| CLI | Typer + Rich | Tidak ada | **Tetap** |
| Protokol | `mcp` 2.x (`MCPServer`), stdio | `pyproject.toml` menulis `mcp>=1.0.0`, padahal kodenya butuh API 2.x | **Tetap**, pin `mcp>=2`. Untuk Level 3 pakai Streamable HTTP |
| Metadata chunk | `index_metadata.json` | Ditulis ulang seluruhnya setiap ada perubahan. Vault demo: 680 chunk = 766 KB | **Pindah ke SQLite** |
| Vektor | `vectors.npy` + cosine brute-force NumPy | Ditulis ulang seluruhnya. Pencariannya sendiri masih cukup cepat sampai puluhan ribu chunk | **Simpan di SQLite** (BLOB), sqlite-vec bila perlu |
| Kata kunci | `rank-bm25` di memori | Dibangun ulang setiap proses mulai dan setiap indeks berubah | **SQLite FTS5** (bawaan, persisten, inkremental) |
| Fusi skor | `0.6 × dense + 0.4 × bm25` | Dua skor beda skala, ambang tidak berfungsi | **Reciprocal Rank Fusion** |
| Embedding | `BAAI/bge-small-en-v1.5` | **Model khusus Inggris**, sedangkan catatan dan pertanyaan banyak berbahasa Indonesia | **Model multibahasa**, dipilih lewat eval |
| Reranker | Tidak ada | Belum tentu perlu | Tunda sampai eval menunjukkan perlu |
| Graf | Wikilink hanya di teks | Tidak dipakai saat mencari | Tabel `edges` di SQLite |
| State | SQLite WAL | Tidak ada | **Tetap** |
| Watcher | watchdog | Belum tersambung ke `serve` | **Tetap**, sambungkan |
| LLM | Tidak ada | Tidak bisa menyuling sesi | Opsional: model murah atau lokal (Ollama) |
| Parser kode | Tidak ada | Tidak paham struktur kode | Pakai Graphify, atau tree-sitter nanti |

### 3.2 Soal "ganti database yang lebih proper"

Arah yang tepat bukan pindah ke database yang lebih besar, tetapi **menyatukan tiga penyimpanan menjadi satu SQLite**.

| Pilihan | Kapan cocok | Untuk DevBrain |
| :--- | :--- | :--- |
| **SQLite + FTS5 + vektor BLOB / sqlite-vec** | Satu pengguna, lokal, sampai sekitar 100 ribu vektor | ✅ Pilihan utama. `brain.db` sudah ada, tanpa server |
| LanceDB | Data jutaan baris, multimodal, tetap embedded | Cadangan bila SQLite tidak cukup |
| Qdrant | Server bersama banyak klien, filter rumit | Baru relevan di Level 3, dan belum tentu perlu |
| Postgres + pgvector | Aplikasi multi-pengguna | Berlebihan untuk vault pribadi |
| Neo4j / graph DB | Graf sangat besar dengan query rumit | Tidak perlu. Tabel `edges` cukup |

Alasannya:
- Vault pribadi berisi ribuan sampai puluhan ribu chunk. Pada ukuran ini pencarian brute-force selesai dalam hitungan milidetik.
- Masalah yang ada sekarang adalah **cara menulis** (seluruh indeks ditulis ulang), bukan kecepatan mencari.
- Satu file database lebih mudah dicadangkan dan dibangun ulang, sesuai filosofi *zero-friction* di dokumen 23.
- OpenClaw dan Basic Memory sampai pada desain yang sama.

Urutan aman: FTS5 dan vektor BLOB dulu (tanpa dependensi baru). sqlite-vec menyusul bila jumlah vektor menuntut. Yang perlu dicek: sqlite-vec masih pra-1.0 dan butuh Python yang mengizinkan pemuatan ekstensi SQLite.

### 3.3 Model embedding

Tersedia langsung di FastEmbed 0.8.0 yang terpasang:

| Model | Dimensi | Ukuran | Catatan |
| :--- | :--- | :--- | :--- |
| `BAAI/bge-small-en-v1.5` (sekarang) | 384 | kecil | Khusus Inggris |
| `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | 384 | 0,22 GB | Sekitar 50 bahasa, dimensi sama |
| `intfloat/multilingual-e5-large` | 1024 | 2,24 GB | Sekitar 100 bahasa, berat di CPU |

Di luar daftar itu: EmbeddingGemma (308M parameter, peringkat teratas di kelas bawah 500M pada MTEB multibahasa) dan BGE-M3. Keduanya perlu jalur lain, misalnya Ollama. Field `embedding_provider` di config sudah menyediakan pilihan `ollama`, tetapi belum diimplementasikan.

Tidak ditemukan benchmark khusus bahasa Indonesia. Keputusan harus dari eval sendiri (Fase 0 di [45](./45-roadmap-devbrain-menuju-jarvis.md)). Mengganti model berarti mengindeks ulang seluruh vault.

### 3.4 Kesimpulan tech stack

Pilihan besarnya sudah benar: Python, MCP, Markdown, SQLite, embedding lokal. Yang perlu diubah ada empat, urut menurut dampak:

1. Model embedding multibahasa.
2. Fusi skor dengan RRF.
3. Indeks disatukan ke SQLite (FTS5 + vektor).
4. Lapisan LLM opsional untuk penyulingan.

---

## 4. Sumber

- Graphify: [repo](https://github.com/safishamsi/graphify), [InfoQ](https://www.infoq.com/news/2026/09/graphify-codebase-exploration/), [AWS Builder Center](https://builder.aws.com/content/3Bs2aqRyKTc4YuAH0EzViNmKcZs/reduce-ai-coding-agent-token-usage-by-40-70percent-with-graphify-knowledge-graphs-in-kiro), [ulasan CodeConductor](https://codeconductor.ai/blog/graphify-review/)
- Basic Memory: [dokumentasi](https://docs.basicmemory.com/llms-full.txt), [cara kerja](https://www.mintlify.com/basicmachines-co/basic-memory/concepts/how-it-works)
- claude-mem: [dokumentasi](https://docs.claude-mem.ai/introduction), [Augment Code](https://www.augmentcode.com/learn/claude-mem-74k-stars-agent-memory)
- LLM Wiki: [gist Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), [MindStudio](https://www.mindstudio.ai/blog/andrej-karpathy-llm-wiki-obsidian-ai-second-brain)
- OpenClaw: [dokumentasi memori](https://openclaw.im/docs/concepts/memory), [penjelasan Mem0](https://mem0.ai/blog/openclaw-memory-system-how-it-works-and-how-to-set-it-up)
- Perbandingan lapisan memori: [mcp.directory](https://mcp.directory/blog/mem0-vs-letta-vs-zep-vs-cognee-2026), [Cognee](https://www.cognee.ai/blog/guides/best-ai-memory-layers-for-ai-agents-in-2026-comparison), [Rick Hightower](https://rickhigh.substack.com/p/eight-agent-memory-systems-none-of)
- Mem0: [paper arXiv 2504.19413](https://arxiv.org/abs/2504.19413), [ulasan biaya](https://dev.to/crabtalk/mem0-what-three-memory-scopes-actually-cost-1kpc)
- Graphiti: [repo](https://github.com/getzep/graphiti), [blog Zep](https://blog.getzep.com/beyond-static-knowledge-graphs/)
- Anthropic: [context management](https://www.anthropic.com/news/context-management)
- Context rot: [Chroma Research](https://research.trychroma.com/context-rot)
- SQLite hybrid search: [Simon Willison](https://simonwillison.net/2024/Oct/4/hybrid-full-text-search-and-vector-search-with-sqlite/), [contoh FTS5 + sqlite-vec + RRF](https://dev.to/soytuber/building-a-hybrid-rag-in-200-lines-sqlite-fts5-sqlite-vec-rrf-38h1)
- Database vektor embedded: [Actian](https://www.actian.com/blog/developer/comparing-embedded-vector-databases/), [Encore](https://encore.dev/articles/best-vector-databases)
- Embedding: [paper EmbeddingGemma](https://arxiv.org/abs/2509.20354)
- MemPalace, Khoj, Letta: [DEV: perbandingan](https://dev.to/rohit_raj_8c7902b7d37cf21/ai-agent-memory-in-2026-mem0-vs-zep-vs-letta-vs-mempalace-open-source-benchmarked-4jpl), [Vectorize](https://vectorize.io/articles/mempalace-alternatives)
