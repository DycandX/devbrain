# Task 03: Watchdog Vault Watcher & Incremental Indexer

| Attribute | Detail |
| :--- | :--- |
| **Sprint** | Level 1 / Sprint 02 |
| **Status** | Todo |
| **Target Files** | `src/devbrain/watcher/vault_watcher.py`, `src/devbrain/watcher/debounce.py` |

---

## 1. Deskripsi Task
Membangun service pemantau sistem berkas (*file system watcher*) berbasis `watchdog` untuk mendeteksi event pembuatan, perubahan, dan penghapusan file `.md` di dalam Obsidian Vault secara real-time, lalu memperbarui indeks secara inkremental tanpa re-indexing penuh.

---

## 2. Rincian Pekerjaan
1. **Debounce Queue (`debounce.py`):**
   * Menggabungkan event edit bertubi-tubi saat pengguna sedang mengetik (debounce window: 500ms).
2. **FileSystemEventHandler (`vault_watcher.py`):**
   * Filter event: Hanya memproses file berekstensi `.md`.
   * Ignore list: Mengabaikan path `.brain_data/`, `.obsidian/`, `.git/`, dan rule `.brainignore`.
   * **Event `on_created` / `on_modified`:**
     1. Parse file `.md` baru/terubah.
     2. Hapus chunk lama file tersebut dari storage.
     3. Generate embedding chunk baru via FastEmbed.
     4. Masukkan ke local storage & rebuild BM25 corpus secara inkremental.
   * **Event `on_deleted`:**
     1. Hapus semua chunk milik file tersebut dari storage & BM25.
3. **Lifecycle Watcher:**
   * Fungsi `start_watcher(vault_path: Path, on_change_callback)`, `stop_watcher()`.

---

## 3. Kriteria Selesai (Acceptance Criteria)
* Saat file `.md` baru dibuat di folder vault, dalam <1 detik file tersebut otomatis terindeks dan bisa langsung dicari.
* Saat file dihapus, hasil pencarian tidak lagi memunculkan file tersebut.
