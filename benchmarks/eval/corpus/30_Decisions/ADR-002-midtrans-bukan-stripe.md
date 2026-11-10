---
title: "ADR-002: Memakai Midtrans, bukan Stripe"
tags: ["adr", "pembayaran"]
---

# ADR-002: Memakai Midtrans, bukan Stripe

## Konteks
Toko online menyasar pembeli di Indonesia yang terbiasa membayar lewat transfer bank, QRIS, dan dompet digital.

## Keputusan
Gerbang pembayaran yang dipakai adalah Midtrans Snap. Stripe belum mendukung metode pembayaran lokal tersebut.

## Konsekuensi
Notifikasi pembayaran diterima lewat webhook dan harus diverifikasi tanda tangannya.
