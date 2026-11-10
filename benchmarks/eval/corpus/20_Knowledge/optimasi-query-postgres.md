---
title: "Optimasi Query PostgreSQL"
tags: ["database", "performa"]
---

# Optimasi Query PostgreSQL

## Gejala
Halaman daftar pesanan butuh empat detik untuk dimuat. Penyebabnya masalah N+1: setiap baris pesanan memicu satu kueri tambahan untuk mengambil data pelanggan.

## Solusi
Gabungkan dengan JOIN lalu tambahkan indeks gabungan pada kolom `customer_id` dan `created_at`. Selalu periksa rencana eksekusi dengan `EXPLAIN ANALYZE` sebelum dan sesudah perubahan. Waktu muat turun menjadi 120 milidetik.
