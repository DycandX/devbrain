# 48. Peran LLM, Audit Vault, dan Arah RAG DevBrain

| Metadata | Nilai |
| :--- | :--- |
| **Topik** | Apakah DevBrain butuh LLM (dan konsepnya dengan 9router), audit struktur dan isi vault utama, posisi RAG, dan urutan langkah berikutnya |
| **Status** | 🔬 Analisa + audit vault (belum dieksekusi) |
| **Referensi** | [45](./45-roadmap-devbrain-menuju-jarvis.md), [46](./46-riset-projek-serupa-efisiensi-token-dan-tech-stack.md), [47](./47-hermes-agent-sebagai-badan-jarvis-jev-dan-strategi-ui.md), [HANDOFF.md](../../HANDOFF.md) |
| **Tanggal** | 2026-11-11 |

> Semua angka di dokumen ini berasal dari audit vault utama `E:\_PROJECT\_DevBrain_Vault` (143 catatan) pada tanggal di atas, setelah pemindaian workspace v1.9.0.

---

## 1. Apakah DevBrain Butuh LLM?

**Untuk mencari: tidak. Untuk merawat: ya.**

### 1.1 Bukti dari vault

| Folder | Catatan | Ukuran |
| :--- | ---: | ---: |
| `90_Agent_Inbox` (log sesi mentah) | 61 | 369 KB |
| `10_Projects` (kartu projek) | 67 | 274 KB |
| `20_Knowledge` (pengetahuan hasil olahan) | 5 | 12 KB |
| `30_Decisions` | 2 | 2 KB |
| `00_System` | 7 | 17 KB |
| `99_Daily` | 1 | 1 KB |

Sesi terus masuk, tetapi tidak pernah diolah menjadi pengetahuan. Subfolder `Bug_Solutions`, `Frameworks_Tools`, dan `Security_Checklists` kosong. Memori hanya terisi bila agent ingat memanggil `remember`. Mengubah transkrip menjadi pelajaran yang bisa dipakai ulang butuh pemahaman bahasa.

### 1.2 Pembagian kerja

| Pekerjaan | Butuh LLM | Kapan |
| :--- | :---: | :--- |
| Mencari, briefing, recall | Tidak | Saat agent bertanya; harus cepat, murah, dan tidak bisa gagal karena router |
| Menyuling sesi menjadi keputusan, masalah/solusi, dan fakta | Ya | Setelah sesi selesai, di latar belakang |
| Menggabungkan log menjadi catatan `20_Knowledge` | Ya | Berkala |
| Memeriksa kontradiksi, duplikat, memori usang | Ya | Mingguan |

**Prinsip:** LLM tidak boleh masuk ke jalur pencarian. Inti DevBrain tetap tanpa LLM; lapisan perawatan bersifat opsional.

### 1.3 Konsep dengan 9router

9router di homeserver Jarvis sudah menyediakan endpoint format OpenAI dengan combo `hermes-9router-jarvis-v1` (model berkredit dengan cadangan model gratis). DevBrain cukup diberi pengaturan:

```json
"llm": {
  "base_url": "http://jarvis:20128/v1",
  "model": "hermes-9router-jarvis-v1",
  "api_key_env": "NINEROUTER_API_KEY"
}
```

Perintah baru `devbrain curate`:
1. Membaca sesi yang belum diolah.
2. Meminta LLM menghasilkan **usulan**: memori, catatan knowledge, perbaikan.
3. Menaruh usulan di `90_Agent_Inbox/manual_review/` untuk disetujui pemilik. Usulan tidak otomatis menjadi kebenaran.
4. Setiap hasil mencatat sumbernya (tautan ke sesi asal).

Port dan nama variabel lingkungan di atas adalah contoh; sesuaikan dengan instalasi 9router.

### 1.4 Dua keputusan sebelum dibangun

**Privasi.** Combo tersebut memakai model gratis dari OpenRouter dan penyedia lain. Layanan gratis sering memakai data masukan untuk pelatihan. Vault berisi prompt pribadi dan pekerjaan magang FXMedia. Usulan: kebijakan per grup, misalnya `_fxmedia` hanya boleh diolah model lokal (Ollama) atau tidak diolah sama sekali. Teks juga disanitasi sebelum dikirim.

**Alternatif tanpa infrastruktur baru.** Yang menyuling adalah agent itu sendiri: lewat hook di akhir sesi, Claude Code diminta menulis ringkasan dan memanggil `remember`. Agent sudah LLM dan konteks sesinya masih utuh, sehingga lebih murah dan lebih akurat untuk sesi Claude Code. 9router diperlukan untuk sesi agent lain dan perawatan berkala.

**Rekomendasi:** hook lebih dulu, 9router menyusul.

---

## 2. Audit Struktur Vault

### 2.1 Yang sudah baik
- Pemisahan sistem, projek, pengetahuan, keputusan, inbox, dan harian dengan awalan angka.
- Data mesin terpisah di `.brain_data/` dan tidak tercampur dengan catatan.
- Kartu projek sudah memuat `group` dan tag `group/...` sejak v1.9.0.

### 2.2 Yang perlu dibenahi

| Temuan | Dampak | Usulan |
| :--- | :--- | :--- |
| **65 kartu projek bernama `README.md`** | Di graph view dan quick switcher Obsidian semuanya tampil sebagai "README" | Nama berkas mengikuti nama projek, atau minimal `aliases` di frontmatter |
| **30 tautan ke `99_Daily/<tanggal>` putus** | Folder harian hanya berisi indeks; graph penuh simpul hantu | Buat catatan harian otomatis, atau hapus tautannya |
| Inbox penuh, knowledge kosong | Lapisan paling berharga tidak ada | Lihat bagian 1 dan 4 |
| ADR-001 masih menyebut `bge-small-en-v1.5` | Keputusan usang tanpa tanda digantikan, tetap disodorkan di briefing | ADR baru untuk model multibahasa, ADR-001 berstatus `superseded` |
| 66 kartu rata di `10_Projects`, campur sandbox dan 15 bot Discord | Masih wajar dengan `group` dan tag | Tampilan per grup (Dataview/Bases), bukan subfolder |
| Indeks manual (`_X_Index.md`, 5 berkas) | Cepat usang | Dibuat otomatis atau diganti tampilan Dataview |

---

## 3. Audit Isi Berkas Markdown

### 3.1 Yang sudah baik
- Frontmatter ada di 142 dari 143 catatan.
- `type` konsisten untuk jenis utama: `project` (65), `agent-session-log` (59), `index-hub` (5).
- Tautan wikilink dari sesi ke kartu projek (Project Hub).

### 3.2 Yang perlu dibenahi

| Temuan | Contoh / angka | Dampak |
| :--- | :--- | :--- |
| **Judul sesi kotor** | `Task: intiall ini untuk projek iin uipro init --ai antigravity # Antigravity The user changed settin...` | Teks harness ikut masuk; merusak pencarian, briefing, dan graph |
| **Blok `dataview` ikut terindeks** | 66 catatan | Hanya berguna di Obsidian; bagi agent adalah teks sampah yang dibayar token |
| Emoji di judul bagian | 138 catatan | Menambah token dan mengotori kata kunci |
| Kunci tanggal tidak seragam | `created`, `date`, `updated`, `last_scanned` | Sulit diurutkan dan disaring |
| Frontmatter rusak atau tidak ada | 3 rusak, 1 tidak ada | Metadata tidak terbaca |
| Log sesi tanpa kolom terstruktur | Tidak ada `project`, `outcome`, `status` | Penyulingan dan penyaringan harus menebak dari teks |

### 3.3 Skema frontmatter bersama (usulan)

| Kunci | Wajib | Keterangan |
| :--- | :---: | :--- |
| `type` | Ya | `project`, `session`, `knowledge`, `decision`, `memory`, `daily`, `system` |
| `title` | Ya | Bersih, tanpa teks harness |
| `created` | Ya | ISO 8601 |
| `updated` | Tidak | ISO 8601 |
| `project` | Tidak | Nama kartu projek terkait |
| `status` | Tidak | Mis. `active`, `superseded`, `draft` |
| `tags` | Ya | Termasuk `group/...` bila ada |
| `aliases` | Tidak | Nama lain untuk Obsidian |

Aturan tambahan: blok kode untuk Obsidian (`dataview`) tidak ikut diindeks; judul bagian di catatan buatan DevBrain tanpa emoji.

---

## 4. Apakah DevBrain Butuh RAG?

**DevBrain sudah RAG.** Pencarian hybrid ditambah tool MCP yang dipanggil agent sesuai kebutuhan adalah bentuk RAG agentik yang paling umum. Bagian *generation* dilakukan agent, bukan DevBrain.

Yang lebih penting dari menambah teknik RAG adalah **memperbaiki bahan yang diambil**. Mencari di 61 log mentah akan selalu kalah dari mencari di 20 catatan knowledge yang rapi (pola *LLM Wiki*, dokumen 46). Urutan peningkatan:

1. Lapisan knowledge hasil sulingan.
2. Perluasan lewat wikilink: ikut ambil catatan yang tertaut ke hasil teratas.
3. Reranker, hanya bila `benchmarks/eval_retrieval.py` menunjukkan perlu.

Tidak diperlukan: GraphRAG berat atau database vektor terpisah pada ukuran vault ini.

---

## 5. Urutan Langkah Berikutnya

| # | Langkah | LLM | Alasan |
| :---: | :--- | :---: | :--- |
| 1 | **Rapikan vault**: nama kartu, tautan harian putus, judul sesi, dataview tidak diindeks, skema frontmatter, ADR usang | Tidak | Murah dan pasti; memperbaiki kualitas semua langkah berikutnya |
| 2 | **Hook Claude Code**: briefing di awal sesi, ringkasan dan `remember` di akhir | Tidak (agent yang menyuling) | DevBrain terpakai tanpa diminta |
| 3 | **`devbrain curate` lewat 9router**, usulan harus disetujui | Ya | Menyuling sesi agent lain dan merawat vault |
| 4 | **Lapisan knowledge**: inbox digabung menjadi catatan `20_Knowledge` | Ya | Bahan pencarian paling berharga |
| 5 | Uji A/B hemat token | Tidak | Butuh data dari langkah 1–4 |
| 6 | Sambungkan Hermes | Tidak | Langkah menuju Jarvis |

Langkah 1 didahulukan karena LLM yang bekerja di atas judul kotor dan tautan putus akan menghasilkan sulingan yang ikut kotor, dan memperbaikinya belakangan lebih mahal.

---

## 6. Keputusan yang Menunggu Pemilik

| Pertanyaan | Kapan |
| :--- | :--- |
| Kebijakan privasi per grup untuk pengolahan LLM (mis. `_fxmedia` hanya model lokal) | Sebelum langkah 3 |
| Kartu projek: ganti nama berkas atau cukup `aliases`? | Langkah 1 (ganti nama memutus tautan lama bila tidak dimigrasikan) |
| Catatan harian: dibuat otomatis atau tautannya dihapus? | Langkah 1 |
| Hook dipasang global atau per projek? | Langkah 2 |
