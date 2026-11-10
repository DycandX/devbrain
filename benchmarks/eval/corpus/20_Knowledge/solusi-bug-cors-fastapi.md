---
title: "Solusi Bug CORS di FastAPI"
tags: ["bug", "fastapi"]
---

# Solusi Bug CORS di FastAPI

## Masalah
Permintaan dari frontend ditolak browser dengan pesan bahwa asal tidak diizinkan. Permintaan lewat Postman berhasil.

## Penyebab dan Perbaikan
Middleware CORS didaftarkan setelah router sehingga tidak berlaku untuk respons galat. Pindahkan pendaftarannya ke paling awal dan tulis daftar asal secara eksplisit, jangan memakai tanda bintang bila kredensial dikirim.
