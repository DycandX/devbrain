# 47. Hermes Agent sebagai Badan Jarvis, Jev, dan Strategi UI

| Metadata | Nilai |
| :--- | :--- |
| **Topik** | Apakah Hermes Agent sudah bisa menjadi Jarvis, di mana DevBrain masuk, apa itu Jev, dan cara membuat tampilan Jarvis tanpa mem-fork Hermes |
| **Status** | 🔬 Riset (web + cek instalasi lokal), belum ada yang dieksekusi |
| **Referensi** | [43](./43-katalog-lengkap-ekosistem-ai-tools-agent-dan-peta-storage.md), [45](./45-roadmap-devbrain-menuju-jarvis.md), [46](./46-riset-projek-serupa-efisiensi-token-dan-tech-stack.md) |
| **Tanggal** | 2026-11-10 |

> **Catatan keandalan.** Detail konfigurasi Hermes di bawah berasal dari dokumentasi resmi dan mirror pihak ketiga. Cek ke dokumentasi versi yang terpasang sebelum dipakai. Informasi tentang Jev seluruhnya dari hasil pencarian.

> **Koreksi (2026-11-11):** lokasi data Hermes yang benar adalah `%LOCALAPPDATA%\hermes` (`C:\Users\zulvikar\AppData\Local\hermes`). Programnya ada di subfolder `hermes-agent`. `~/.hermes` hanyalah sisa instalasi lama. Lihat [dokumen 49](./49-siklus-belajar-hermes-dan-adopsinya-di-devbrain.md).

> **Dampak ke roadmap.** Dokumen ini merevisi Fase 4 sampai 6 di [dokumen 45](./45-roadmap-devbrain-menuju-jarvis.md). Fase 0 sampai 3 tidak berubah.

---

## 1. Hermes Agent: Sudah Bisa Jadi Jarvis?

Hermes Agent (Nous Research, lisensi MIT) sudah memenuhi empat dari lima kebutuhan Jarvis.

| Kebutuhan Jarvis | Hermes | Keterangan |
| :--- | :--- | :--- |
| Berpikir (loop agent) | ✅ | Runtime agent lengkap |
| Mendengar dan bicara | ✅ | Gateway ke Telegram, Discord, Slack, WhatsApp, Signal, CLI, termasuk pesan suara |
| Proaktif | ✅ | Cron bawaan, hasil bisa dikirim ke kanal mana pun |
| Bertindak | ✅ | Tool bawaan, plugin, dan MCP server |
| Mengingat | ⚠️ | Ada, tetapi terbatas (lihat bagian 2) |

Kesimpulan: runtime, kanal chat, scheduler, dan suara tidak perlu dibangun dari nol. Hermes bisa menjadi **badan** Jarvis.

---

## 2. Di Mana DevBrain Masuk

### 2.1 Batas memori Hermes

- **Memori inti kecil.** `MEMORY.md` dan `USER.md` dibatasi sekitar 1.300 token total menurut satu ulasan, tanpa mekanisme luapan.
- **Pencarian sesi hanya kata kunci** (SQLite FTS5), bukan semantik. Agent harus berinisiatif memanggilnya.
- **Memori hanya milik Hermes.** Claude Code dan Antigravity tidak bisa membacanya.
- **Tidak ada ADR, kartu projek, atau vault** yang bisa dibaca manusia di Obsidian.

### 2.2 Cara menyambungkan

| Jalur | Cara | Kapan |
| :--- | :--- | :--- |
| **MCP** | Daftarkan DevBrain di `mcp_servers` pada `%LOCALAPPDATA%\hermes\config.yaml` | Pilihan pertama, tanpa mengubah Hermes |
| Memory provider | DevBrain sebagai provider eksternal (slot yang sama dengan Honcho, Mem0). Hanya satu provider aktif dalam satu waktu | Nanti, bila integrasi lebih dalam diperlukan |
| Plugin + hook | Hook `on_session_start` memuat briefing, `on_session_end` menyimpan ringkasan | Pelengkap jalur MCP |

Hasilnya: satu memori dipakai bersama oleh Hermes, Claude Code, dan Antigravity.

### 2.3 Pembagian peran

| Lapisan | Pemilik | Isi |
| :--- | :--- | :--- |
| Memori inti (selalu dimuat) | Hermes | `USER.md`, `MEMORY.md`, `SOUL.md`. Kecil dan padat |
| Memori panjang (dicari saat perlu) | **DevBrain** | Vault, ADR, kartu projek, sesi semua agent |
| Skill | Keduanya | Hermes menjalankan, DevBrain bisa menjadi sumber terpusat |

---

## 3. Yang Bisa Dipelajari dari Hermes

1. **Memori inti yang dibatasi ketat.** Fakta terpenting selalu dimuat dan ukurannya dijaga kecil. Pola hemat token yang DevBrain belum punya.
2. **Skill sebagai memori prosedural.** Agent menulis skill sendiri setelah menyelesaikan masalah sulit, lalu memuatnya untuk tugas serupa.
3. **Nudge berkala** yang mengingatkan agent menyimpan memori, sehingga tidak bergantung pada inisiatif agent.
4. **Pemisahan `USER.md`, `MEMORY.md`, `SOUL.md`**: siapa penggunanya, apa yang dipelajari, dan persona agent.
5. **Satu proses gateway** untuk semua kanal, sesi, dan cron.

---

## 4. Temuan di Mesin Ini

- Hermes **sudah terpasang** di `%LOCALAPPDATA%\hermes` (100 skill, memori inti hampir penuh, `mcp_servers` hanya berisi `antigravity`). Belum terhubung ke DevBrain. Catatan ini semula menyebut `~/.hermes`, yang ternyata sisa instalasi lama; rincian ada di dokumen 49.
- `gateway.pid` bertanggal 25 Agustus 2026. Belum dicek apakah prosesnya masih berjalan.
- **Koreksi untuk [dokumen 43](./43-katalog-lengkap-ekosistem-ai-tools-agent-dan-peta-storage.md):** bagian Hermes menyebut `cot_trace.jsonl` dan `long_term_memory.json`. Dokumentasi Hermes memakai `MEMORY.md`, `USER.md`, dan database sesi SQLite. Harvester Hermes harus mengikuti struktur yang asli.

---

## 5. Jev

Jev **bukan agent dan bukan asisten**. Jev adalah model AI proprietary dari TypeSafe AI, rilis akses terbatas 15 September 2026.

- Tidak menghasilkan teks. Menjawab pertanyaan bertipe (ya/tidak, pilihan, skor) dengan probabilitas, untuk dikonsumsi software.
- Klaim pembuatnya: respons 70 sampai 500 ms, 40 sampai 200x lebih cepat dan 40 sampai 400x lebih murah dari LLM besar. Angka dari pengujian mereka sendiri.
- Tidak open source, tidak bisa dijalankan sendiri.

Kemungkinan peran di Jarvis: pengambil keputusan cepat di samping LLM utama, misalnya "perlu ambil memori atau tidak" dan "tool mana yang dipakai". Searah dengan tujuan hemat token, tetapi opsional dan baru relevan setelah fondasi selesai.

---

## 6. Kustomisasi Hermes

Lisensi MIT mengizinkan modifikasi apa pun. Rekomendasinya tetap: **jangan mengedit kode inti**. Hermes dirilis cepat, dan fork yang diubah dalam-dalam akan bentrok di setiap update.

| Yang mau diubah | Caranya | Perlu fork? |
| :--- | :--- | :--- |
| Kepribadian dan gaya bicara | `%LOCALAPPDATA%\hermes\SOUL.md`, preset `/personality` | Tidak |
| Kemampuan baru | Skill di `%LOCALAPPDATA%\hermes\skills\` | Tidak |
| Tool baru dan hook | Plugin di `%LOCALAPPDATA%\hermes\plugins\` (`pre_tool_call`, `post_tool_call`, `on_session_start`, `on_session_end`, dan lainnya). Plugin harus diaktifkan di config | Tidak |
| Memori | DevBrain lewat `mcp_servers` | Tidak |
| Aksi ke luar | MCP server lain (kalender, email, rumah) | Tidak |
| Tampilan | Frontend sendiri di atas API server | Tidak |

---

## 7. Strategi UI

Hermes punya **API server berformat OpenAI** (default `http://localhost:8642/v1`, diaktifkan dengan `API_SERVER_ENABLED=true`). UI terpisah total dari mesin.

| Jalur | Isi | Kapan |
| :--- | :--- | :--- |
| **1. UI jadi** | Open WebUI, LobeChat, atau LibreChat diarahkan ke endpoint Hermes | Sekarang, untuk mencoba |
| **2. UI Jarvis sendiri** | Aplikasi web yang berbicara ke API Hermes: tampilan sendiri, mode suara, panel memori dari DevBrain, linimasa aktivitas, konfirmasi aksi | Setelah tahu apa yang kurang |
| **3. Chat di HP** | Telegram atau WhatsApp lewat gateway | Pemakaian harian |

Ketiganya bisa berjalan bersamaan sebagai klien dari Hermes yang sama.

```text
[ UI Jarvis buatan sendiri ]  [ Telegram ]  [ Open WebUI ]
              └────────────────┬────────────────┘
                   API server Hermes (:8642)
                   [ Hermes Agent, tanpa diubah ]
                     │ plugin / skill      │ MCP
              [ kemampuan khusus ]     [ DevBrain ]
                                          ▲
                        [ Claude Code / Antigravity ] (MCP)
```

---

## 8. Revisi Fase 4 sampai 6

| Fase | Sebelumnya (dokumen 45) | Sekarang |
| :--- | :--- | :--- |
| 4 | Bangun runtime Jarvis dengan Claude Agent SDK + Telegram | **Coba Hermes apa adanya** (Open WebUI + Telegram), lalu sambungkan DevBrain lewat MCP |
| 5 | Bangun connector dan scheduler | Pasang MCP server dan cron Hermes. Tulis skill dan plugin khusus |
| 6 | Suara dan multi-perangkat | **UI Jarvis sendiri** di atas API server, termasuk mode suara |

Yang menjadi milik sendiri hanya tiga hal: **DevBrain** (memori), **UI** (pengalaman pakai), dan **skill/plugin** (kemampuan khusus). Mesin agent dirawat oleh Nous Research.

Langkah yang bisa dilakukan lebih awal tanpa menunggu Fase 0: mencoba Hermes dengan Open WebUI dan Telegram selama satu sampai dua minggu, lalu mencatat apa yang kurang.

---

## 9. Keputusan yang Masih Terbuka

| Pertanyaan | Kapan |
| :--- | :--- |
| Hermes berjalan di laptop atau di homeserver? | Sebelum mencoba |
| Model LLM apa yang dipakai Hermes (lokal atau API)? | Sebelum mencoba |
| DevBrain sebagai MCP saja, atau juga memory provider? | Setelah Fase 1 |
| Stack UI sendiri (misalnya Next.js)? | Setelah masa coba |
| Perlu Jev atau model keputusan lain? | Paling akhir |

---

## 10. Sumber

- Hermes Agent: [dokumentasi](https://hermes-agent.nousresearch.com/docs), [memori](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory), [MCP](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp), [plugin](https://hermes-agent.nousresearch.com/docs/user-guide/features/plugins), [personality](https://hermes-agent.nousresearch.com/docs/user-guide/features/personality), [API server](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server), [Open WebUI](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/open-webui)
- Ulasan memori Hermes: [Vectorize: cara kerja](https://vectorize.io/articles/hermes-agent-memory-explained), [Vectorize: provider](https://vectorize.io/articles/hermes-agent-memory-providers-compared), [Mem0](https://mem0.ai/blog/how-memory-works-in-hermes-agent-%28and-how-to-improve-it%29)
- Open WebUI: [panduan Hermes](https://docs.openwebui.com/getting-started/quick-start/connect-an-agent/hermes-agent)
- Jev: [Wikipedia](https://en.wikipedia.org/wiki/Jev_(AI_model)), [jev-eval-agent](https://github.com/vinilana/jev-eval-agent)
