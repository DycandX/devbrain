---
title: "Cara Backup Database Otomatis"
tags: ["backup", "database"]
---

# Cara Backup Database Otomatis

## Jadwal
Setiap malam pukul dua, cron menjalankan `pg_dump` dan mengompres hasilnya.

## Penyimpanan
Berkas cadangan dienkripsi lalu diunggah ke penyimpanan awan dengan rclone. Cadangan yang lebih tua dari tiga puluh hari dihapus. Uji pemulihan dilakukan sebulan sekali.
