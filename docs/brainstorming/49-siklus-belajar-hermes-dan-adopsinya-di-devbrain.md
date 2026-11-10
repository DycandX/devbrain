# 49. Siklus Belajar Mandiri Hermes dan Adopsinya di DevBrain

| Metadata | Nilai |
| :--- | :--- |
| **Topik** | Cara Hermes Agent mempelajari skill dan memperbarui memorinya sendiri, fitur mana yang cocok dipindahkan ke DevBrain, dan konsep satu siklus belajar untuk banyak agent |
| **Status** | 🔬 Riset (dokumentasi resmi + instalasi lokal), belum dieksekusi |
| **Referensi** | [47](./47-hermes-agent-sebagai-badan-jarvis-jev-dan-strategi-ui.md), [48](./48-peran-llm-audit-vault-dan-arah-rag.md), [rencana sprint](../sprints/level-1/_index.md) |
| **Tanggal** | 2026-11-11 |

---

## 1. Instalasi Hermes di Mesin Ini

Hermes punya **dua lokasi** yang berbeda fungsi:

| Lokasi | Isi | Fungsi |
| :--- | :--- | :--- |
| `C:\Users\zulvikar\AppData\Local\hermes\hermes-agent` | Kode sumber Hermes (repo git) beserta `venv` | **Program.** Diperbarui lewat `hermes update` |
| `C:\Users\zulvikar\AppData\Local\hermes` | `config.yaml`, `memories/`, `skills/`, `state.db`, `sessions/`, `cron/`, `kanban.db` | **Data (Hermes home).** Ini yang dibaca dan ditulis DevBrain |
| `C:\Users\zulvikar\.hermes` | Config kecil dan skrip PowerShell dari Agustus 2026 | Sisa instalasi lama, tidak dipakai |

Versi setelah pembaruan 2026-11-11: `Hermes Agent vgit.1c8dcdb (2026.9.24) · stable`, metode instalasi git.

> **Koreksi.** Dokumen 43, 47, dan `HANDOFF.md` sebelumnya menyebut `~/.hermes` sebagai lokasi Hermes. Lokasi data yang benar adalah `%LOCALAPPDATA%\hermes`.

### Kondisi data (2026-11-11)

| Hal | Kondisi |
| :--- | :--- |
| Skill | 100 skill; 3 dibuat Hermes sendiri: `custom-mcp-servers`, `hermes-windows-host`, `linux-home-server` |
| `memories/MEMORY.md` | 2.092 / 2.200 karakter (**95% penuh**) |
| `memories/USER.md` | 1.342 / 1.375 karakter (**98% penuh**) |
| `memory.nudge_interval` | 10 giliran |
| `skills.creation_nudge_interval` | 15 giliran |
| `skills.external_dirs` | Kosong |
| `curator` | Aktif (`stale_after_days: 30`, `archive_after_days: 90`, `prune_builtins: true`) |
| `mcp_servers` | Hanya `antigravity`; DevBrain belum tersambung |

Memori Hermes hampir penuh. Fakta baru hanya bisa masuk bila fakta lama dihapus atau dipadatkan.

---

## 2. Cara Hermes Belajar

| Mekanisme | Cara kerja |
| :--- | :--- |
| **Memori inti** | `MEMORY.md` (2.200 karakter, ±800 token) dan `USER.md` (1.375 karakter, ±500 token), selalu dimuat ke system prompt. Dibekukan saat sesi dimulai agar cache prompt tetap berlaku; tulisan baru tampil di sesi berikutnya |
| **Tool `memory`** | Aksi `add`, `patch` (ganti satu potongan teks), `remove`. Bila penuh, tool menolak dan agent harus memadatkan sendiri dalam satu batch |
| **Pemeriksaan keamanan memori** | Setiap entri diperiksa dari pola prompt injection, pencurian data, backdoor SSH, dan karakter Unicode tersembunyi. Duplikat ditolak |
| **Pembuatan skill** | System prompt menyuruh agent menyimpan alur kerja yang tidak sepele, alur yang ditemukan setelah memperbaiki error, dan cara yang dikoreksi pengguna |
| **Tool `skill_manage`** | Aksi `create`, `patch`, `delete`, `write_file`, `remove_file`. Linter memberi peringatan untuk skill yang terlalu besar atau berbentuk log insiden |
| **Review latar belakang** | Setelah giliran percakapan, proses terpisah meninjau apakah ada memori atau skill yang perlu disimpan (`auxiliary.background_review`) |
| **Persetujuan** | Opsional: `memory.write_approval` dan `skills.write_approval`. Tulisan ditahan di `pending/` sampai disetujui |
| **Curator** | Berjalan saat menganggur, minimal tiap 7 hari. Tanpa LLM: skill tidak terpakai menjadi `stale` lalu diarsipkan. Dengan LLM (opsional): menggabungkan skill yang tumpang tindih. Tidak pernah menghapus; ada cadangan, catatan perubahan, `pin`, dan `lock` |
| **Pengungkapan bertahap** | Daftar skill (nama, deskripsi), lalu isi skill, lalu berkas referensi |
| **Pencarian sesi** | FTS5 (kata kunci) atas percakapan lama di `state.db` |

---

## 3. Fitur Mana yang Cocok untuk DevBrain

Perbedaan mendasarnya: **Hermes adalah agent yang melihat percakapannya sendiri. DevBrain adalah server yang hanya tahu apa yang dikirim agent kepadanya.** Yang bisa dipindahkan adalah pola dan tempat penyimpanannya, bukan pemicunya.

| Fitur Hermes | Ke DevBrain | Bentuknya di DevBrain |
| :--- | :---: | :--- |
| Memori inti kecil yang selalu dimuat | ✅ | Tingkat memori inti (dipin, dibatasi ukuran) yang selalu masuk briefing; sisanya lewat `recall` |
| Pemeriksaan keamanan memori | ✅ **Kritis** | Memori DevBrain disodorkan ke *semua* agent; satu entri jahat bisa meracuni semuanya. `remember` saat ini belum memeriksa apa pun |
| Persetujuan sebelum tersimpan | ✅ | Mode tahan-dulu untuk memori dan skill, dengan perintah setujui/tolak |
| `skill_manage` | ✅ | Tool MCP untuk menyimpan dan memperbaiki skill di vault. Saat ini DevBrain hanya membaca skill |
| Curator | ✅ | Untuk memori dan catatan knowledge: hitungan pemakaian, `stale`, arsip, catatan perubahan, tanpa LLM. Konsolidasi lewat 9router opsional |
| Pengungkapan bertahap skill | ✅ | `load_skill` saat ini hanya mendaftar nama; tambah deskripsi dan berkas referensi |
| Review latar belakang dan nudge | ⚠️ Pemicunya tidak | Pemicu ada di agent: hook Claude Code di akhir sesi, review bawaan Hermes, dan `devbrain curate` untuk sesi yang sudah dipanen |
| Pencarian sesi | Sudah ada | DevBrain mencari sesi secara semantik dan kata kunci |
| Cron, subagent, browser, terminal, suara, kanban, checkpoint | ❌ | Kemampuan runtime (*badan*). Tetap di Hermes |

---

## 4. Konsep: Satu Siklus Belajar untuk Banyak Agent

```text
  PEMICU (di agent)              USULAN            GERBANG            SIMPAN (DevBrain)       RAWAT            SAJIKAN
  Hermes: review & nudge   ─┐
  Claude Code: hook Stop   ─┼─► remember /     ─► pemeriksaan    ─► vault + SQLite      ─► curator:    ─► briefing,
  devbrain curate (9router)─┘   save_skill       keamanan +         satu untuk semua       pemakaian,      recall,
                                (tool MCP)       persetujuan        agent                  stale, arsip    skill
```

Hasilnya: apa yang dipelajari satu agent langsung tersedia untuk agent lain. Skill yang dibuat Hermes saat diajak bicara lewat Telegram bisa dimuat Claude Code keesokan harinya, dan sebaliknya.

---

## 5. Integrasi Konkret dengan Hermes

1. **Folder skill bersama.** Arahkan `skills.external_dirs` dan `skills.create_dir` di `%LOCALAPPDATA%\hermes\config.yaml` ke `00_System/Agent_Skills` di vault. Skill buatan Hermes langsung masuk vault, bisa dicari DevBrain, dan bisa dimuat Claude Code. Cukup konfigurasi.
2. **DevBrain sebagai MCP server di Hermes** (`mcp_servers`), sesuai dokumen 47. Hermes mendapat `recall` dan `search_brain` untuk pengetahuan di luar 800 token memori intinya.
3. **Harvester untuk Hermes.** Panen `state.db` serta isi `MEMORY.md`/`USER.md` ke vault, agar Claude Code tahu apa yang dipelajari Hermes.
4. **Memori inti Hermes tetap dipakai.** Hermes paling tahu apa yang perlu selalu ada di kepalanya. DevBrain menjadi luapan dan memori bersama, bukan pengganti.

Perlu dicek saat implementasi: apakah curator Hermes akan mengelola skill di `create_dir` yang menunjuk ke vault, dan apakah itu diinginkan.

---

## 6. Urutan

Semua langkah di sini datang **setelah perapian vault** (dokumen 48 langkah 1). Folder skill bersama berarti skill Hermes ikut masuk vault, jadi vault perlu rapi lebih dulu. **Gerbang tulis** didahulukan sebelum Hermes disambungkan: begitu dua agent menulis ke memori yang sama, satu entri berbahaya bisa menyebar ke semua agent.

| # | Langkah | Kode baru |
| :---: | :--- | :--- |
| 1 | Perapian vault (dokumen 48) | Ya |
| 2 | Gerbang tulis: pemeriksaan keamanan dan mode persetujuan untuk `remember` | Ya, kecil |
| 3 | Folder skill bersama dan DevBrain sebagai MCP di Hermes | Tidak, konfigurasi |
| 4 | `save_skill` / `patch_skill` dan hook akhir sesi Claude Code | Ya |
| 5 | Curator untuk memori dan catatan (tanpa LLM) | Ya |
| 6 | Harvester Hermes dan konsolidasi lewat 9router | Ya |

Pemetaan ke sprint ada di [indeks sprint Level 1](../sprints/level-1/_index.md) (Sprint 14–20).

---

## 7. Sumber

- [Memori Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory)
- [Skills Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills)
- [Curator Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/features/curator)
- [Ringkasan fitur Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/features/overview)
- [Hermes Atlas: skills](https://hermesatlas.com/dev/skills)
- [SSOJet: skill yang ditulis Hermes sendiri](https://ssojet.com/blog/hermes-agent-self-evolving-skills.md)
