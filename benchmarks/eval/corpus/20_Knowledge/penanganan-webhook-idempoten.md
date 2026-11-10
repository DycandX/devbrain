---
title: "Penanganan Webhook yang Idempoten"
tags: ["webhook", "pembayaran"]
---

# Penanganan Webhook yang Idempoten

## Masalah
Penyedia pembayaran mengirim notifikasi yang sama dua kali sehingga stok berkurang ganda.

## Solusi
Simpan pengenal kejadian di tabel dengan batasan unik. Bila pengenal sudah ada, balas sukses tanpa memproses ulang. Proses berat dipindahkan ke antrean agar balasan tetap cepat.
