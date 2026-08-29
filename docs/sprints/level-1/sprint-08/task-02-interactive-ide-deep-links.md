# Task 02: Interactive IDE Deep Links & File Protocol Integration

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 08 (Unified Ingestion UX & IDE Deep Links) |
| **Status** | ✅ Done |
| **Target Files** | `src/devbrain/harvester/project_harvester.py` |

---

## 1. Deskripsi Task
Menyematkan tautan protokol IDE interaktif (`vscode://file/...`) dan Windows Explorer file link (`file:///...`) pada setiap kartu projek di `10_Projects/` dan `20_Knowledge/` agar pengguna dapat meluncurkan folder koding di IDE dalam 1 klik dari Obsidian.

---

## 2. Rincian Pekerjaan
1. **URI Formatter:**
   * Mengonversi `local_path` Windows/POSIX ke forward slash yang valid untuk URL protokol.
   * Menghasilkan tautan IDE: `vscode://file/{clean_path}`.
   * Menghasilkan tautan Explorer: `file:///{clean_path}`.
2. **Card Header Enhancement:**
   * Menyisipkan baris `> 🔗 **Quick Actions:** [🚀 Open in IDE (VS Code / Antigravity)](...) | [📁 Open in File Explorer](...)` pada template `10_Projects/` dan `20_Knowledge/`.

---

## 3. Kriteria Keberhasilan (Definition of Done)
* [ ] Seluruh kartu projek baru memiliki tombol tautan 1-klik ke IDE dan Explorer.
* [ ] Tautan diformat secara valid dan dapat diklik langsung di Obsidian.
