# 15. Konsep Multi-Vault, Isolasi Device & Strategi Adopsi Existing Vault

Dokumen ini membahas dua skenario fleksibilitas tingkat lanjut:
1. **Konsep Multi-Vault (Pemisahan vault per device, per domain kerja vs personal).**
2. **Strategi Adopsi Vault (Inisialisasi vault baru otomatis vs Menyambungkan (*Attach*) ke Vault Obsidian lama milik user).**

---

## 1. Konsep Multi-Vault: Pemisahan Vault per Device / Domain

Dalam praktiknya, pengguna mungkin tidak ingin menggabungkan semua hal ke dalam satu folder vault tunggal. Misalnya:
* **Laptop Kantor:** Hanya berisi catatan kerja & proyek kantor (`Work-Vault`).
* **Laptop Pribadi:** Berisi riset AI, proyek sampingan, dan catatan harian (`Personal-Vault`).
* **Homeserver Jarvis:** Menyimpan data otomasi server dan memory jangka panjang (`Server-Vault`).

### Bagaimana Central Brain Menangani Multi-Vault?

Central Brain Hub dirancang mendukung **Multi-Vault Multi-Tenancy**:

```
┌────────────────────────────────────────────────────────────────────────┐
│                          MULTI-VAULT TOPOLOGY                          │
│                                                                        │
│   [ Laptop Kerja ]          [ Laptop Pribadi ]       [ Server Jarvis ] │
│    📁 Work-Vault            📁 Personal-Vault         📁 Server-Vault  │
│          │                         │                         │         │
│     (Metadata:                 (Metadata:                (Metadata:    │
│    vault="work")             vault="personal")         vault="server") │
│          │                         │                         │         │
│          └─────────────────────────┼─────────────────────────┘         │
│                                    │                                   │
│                                    ▼                                   │
│                 ┌──────────────────────────────────────┐               │
│                 │   CENTRAL QDRANT & BM25 VECTOR DB    │               │
│                 │ (Payload Filter: vault="work" dll.)  │               │
│                 └──────────────────────────────────────┘               │
└────────────────────────────────────────────────────────────────────────┘
```

### Mekanisme Isolasi Konteks:
1. **Metadata Tagging Otomatis:** Saat mengindeks file, sistem otomatis menyematkan metadata nama vault dan device ID ke setiap chunk dokumen.
2. **Scoping Query AI Agent:**
   * AI Agent di laptop kerja dikonfigurasi dengan flag `--scope work` $\rightarrow$ Agent hanya bisa membaca dan mencari context dari `Work-Vault`.
   * AI Agent di laptop pribadi bisa diberi akses `--scope personal` atau `--scope all`.
3. **Partitioned Ingestion:** AI Agent di Laptop A akan menulis log ke `90_Agent_Inbox/` di vault lokal Laptop A, sehingga tidak ada file lock antar device.

---

## 2. Inisialisasi Vault: Vault Baru (Default) vs Existing Vault (Vault Lama)

Bagaimana jika user baru pertama kali pakai (belum punya vault), atau sebaliknya, **user sudah punya Obsidian Vault lama yang sudah berisi ribuan catatan**?

Sistem menangani kedua skenario tersebut dengan sangat mulus:

---

### Skenario A: User Baru (Fresh Install / Auto-Scaffolding)
Jika user mengarahkan Central Brain ke folder baru atau folder kosong:
```bash
python mcp_brain_server.py --vault "E:/MyNewVault" --init
```
* **Perilaku Sistem:**
  1. Otomatis membuat struktur folder standar:
     * `00_System/Agent_Skills/`
     * `10_Projects/`
     * `20_Knowledge/`
     * `30_Decisions/`
     * `90_Agent_Inbox/`
  2. Mengisi file template awal seperti `00_System/global_context.md`, panduan penggunaan, dan template ADR.
  3. Siap langsung dibuka di aplikasi Obsidian!

---

### Skenario B: User Sudah Punya Vault Sendiri (Existing Vault Adoption)
Jika user sudah memiliki Obsidian Vault lama dengan struktur folder sendiri (misal: `Catatan_Kuliah/`, `Daily_Journal/`, `Programming/`):
```bash
python mcp_brain_server.py --vault "C:/Users/zulvikar/Documents/MyExistingVault"
```

* **Prinsip Utama: NON-DESTRUCTIVE (100% Aman & Tanpa Merusak):**
  1. **TIDAK MENGUBAH / MENGAWURKAN Struktur Folder Lama:** Central Brain tidak akan memindahkan atau menghapus folder lama milik Anda.
  2. **Read-Only Indexing ke Catatan Lama:** Semua file `.md` lama Anda otomatis dibaca dan diindeks ke Qdrant/BM25 sehingga AI Agent langsung pintar dan mengerti catatan lama Anda!
  3. **Hanya Menambahkan Folder Agent Khusus:**
     Central Brain hanya membuat 1 folder baru untuk zona kerja agent:
     * `90_Agent_Inbox/` (tempat AI menaruh hasil riset/log).
     * `.brain_data/` (folder hidden untuk database cache lokal).
  4. **Fitur `.brainignore` (Privasi Catatan Pribadi):**
     User bisa membuat file `.brainignore` di root vault untuk melarang AI membaca folder tertentu:
     ```text
     # .brainignore
     Pribadi/
     Diary/
     Finance/
     .obsidian/
     .trash/
     ```

---

## 3. Matriks Perbandingan Skenario

| Parameter | Skenario Fresh Vault | Skenario Existing Vault | Skenario Multi-Vault |
| :--- | :--- | :--- | :--- |
| **Folder Struktur** | Dibuat otomatis (*Template Standar*). | Mempertahankan folder asli milik user. | Terpisah per vault (masing-masing punya folder sendiri). |
| **Dampak ke Catatan Lama** | Tidak ada (folder baru). | **100% Aman** (hanya dibaca / read-only index). | Terisolasi per folder. |
| **Zona Tulis AI Agent** | `90_Agent_Inbox/` | `90_Agent_Inbox/` (dibuat di dalam vault lama). | `90_Agent_Inbox/` masing-masing vault. |
| **Filter Privasi** | Sesuai default. | Didukung via `.brainignore`. | Didukung via filter `--scope`. |

---

## 4. Kesimpulan Desain

Central AI Brain Hub **sangat fleksibel dan adaptif**:
1. **Tidak memaksa satu struktur kaku:** Jika Anda sudah punya vault sendiri, Anda cukup arahkan path-nya dan sistem langsung mengindeksnya tanpa merusak apapun.
2. **Mendukung isolasi multi-device:** Anda bebas memisahkan vault kerja dan vault pribadi, namun AI tetap bisa diberi akses pencarian yang terkoordinasi dan aman.
