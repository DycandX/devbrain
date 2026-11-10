# AGENTS.md

Aturan kerja untuk AI agent di repo ini. Konteks projek, kondisi terkini, dan langkah berikutnya ada di [HANDOFF.md](HANDOFF.md). Baca itu lebih dulu.

## Komunikasi
- Bicara dengan pemilik dalam bahasa Indonesia. Kode, nama, komentar kode, dan pesan commit dalam bahasa Inggris.
- Untuk perubahan besar, jelaskan rencana dan tunggu persetujuan. Jangan push tanpa diminta.
- Laporkan dengan jujur apa yang sudah diuji, apa yang belum, dan apa yang gagal.

## Perintah
```bash
pip install -e ".[dev]"
python -m pytest -q
python benchmarks/eval_retrieval.py
python -m devbrain.cli.main --help
```
`devbrain` tidak ada di PATH mesin pemilik; pakai `python -m devbrain.cli.main`.

## Aturan kode
- Ikuti gaya berkas yang diubah: type hints, docstring singkat, modul kecil.
- Tulis berkas lewat `core/fsutil.py` (`atomic_write_text`, `atomic_write_json`), bukan `open(..., "w")`.
- Batasi ukuran keluaran tool MCP lewat `core/textutil.py`. Setiap token yang dikembalikan tool dibayar agent.
- Buat engine pencarian dengan `HybridEngine.from_config(vault)`, bukan konstruktor langsung, agar model dan pola ignore mengikuti config vault.
- Penanda projek, vault, dan sandbox ada di `harvester/markers.py`. Jangan menyalin daftar manifest ke tempat lain.
- Inti devbrain tidak memanggil LLM. Fitur yang butuh LLM harus opsional.

## Test
- Setiap perubahan perilaku disertai test. Perbaikan bug disertai test yang menangkap bug itu.
- Fixture autouse `isolated_home` di `tests/conftest.py` mencegah test menyentuh config IDE asli. Jangan dilewati.
- Perubahan pada pencarian atau briefing: jalankan `benchmarks/eval_retrieval.py` sebelum dan sesudah, dan coba pada salinan vault nyata. Test memakai vault buatan yang terlalu rapi.

## Dokumentasi
- Setiap versi dicatat di `CHANGELOG.md` (ringkas, bahasa Inggris) dan `docs/changelog/vX.Y.Z-alpha.md` (rinci, bahasa Indonesia: masalah, perbaikan, pengukuran, keterbatasan), lalu ditambahkan ke `docs/changelog/_index.md`.
- Naikkan versi di `pyproject.toml` dan `src/devbrain/__init__.py` bersamaan.
- Dokumen rancangan di `docs/brainstorming/` bernomor urut dan didaftarkan di `_index.md`-nya.
- Perbarui [HANDOFF.md](HANDOFF.md) bila kondisi projek berubah: versi, masalah yang diketahui, langkah berikutnya.

## Git
- Conventional Commits dengan scope: `feat(memory):`, `fix(context):`, `docs(brainstorming):`.
- Satu perubahan logis per commit.

## Jangan
- Jangan menulis ke vault utama (`E:\_PROJECT\_DevBrain_Vault`) atau config IDE di home tanpa izin pemilik. Uji pada salinan vault atau folder sementara.
- Jangan commit `.brain_data/`, vault, `.env`, atau kredensial.
- Jangan mengganti library inti, model embedding, atau penyimpanan tanpa mencatat keputusan dan mengukurnya lebih dulu.
