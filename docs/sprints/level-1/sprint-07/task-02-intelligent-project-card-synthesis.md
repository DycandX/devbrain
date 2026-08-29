# Task 02: Intelligent Project Card Synthesis

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 07 (Smart Codebase Synthesizer & README-less Project Harvester) |
| **Status** | ✅ Done |
| **Target Files** | `src/devbrain/harvester/project_harvester.py` |

---

## 1. Deskripsi Task
Meng-upgrade `project_harvester.py` agar mampu mensintesis deskripsi arsitektur projek secara otomatis ketika `README.md` tidak tersedia.

---

## 2. Rincian Pekerjaan
1. **Auto-Synthesized Overview Generator:**
   * Jika tidak ada `README.md` dan tidak ada `description` di manifest:
     * Menyusun kalimat ringkasan berdasarkan stack & entrypoint yang terdeteksi. Contoh:
       *"A Node.js/Express application detected with active services (`server.js`, `docker-compose.yml`)."*
2. **Rich Project Card Layout Integration:**
   * Menambahkan blok **`## ⚡ Runnable Scripts`** (menampilkan `npm run dev`, `python main.py`, dll.).
   * Menambahkan blok **`## 🌳 Project Structure`** (menampilkan ASCII Tree).
   * Menambahkan blok **`## 📋 Project Notes`** sebagai placeholder interaksi developer & AI Agent.
3. **Penyisipan Dataview Live Query:**
   * Tetap menyertakan blok Dataview untuk riwayat sesi AI terkini.

---

## 3. Kriteria Keberhasilan (Definition of Done)
* [ ] Projek tanpa `README.md` tidak lagi menghasilkan "No description provided", melainkan kartu kaya informasi berisi overview sintesis, daftar script, dan pohon direktori.
* [ ] Frontmatter YAML tetap valid dan bersih.
