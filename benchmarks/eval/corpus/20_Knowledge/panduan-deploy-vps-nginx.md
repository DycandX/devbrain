---
title: "Panduan Deploy ke VPS dengan Nginx"
tags: ["deploy", "server"]
---

# Panduan Deploy ke VPS dengan Nginx

## Langkah
Pasang aplikasi di belakang Nginx sebagai reverse proxy. Aplikasi berjalan di port 3000 dan dikelola oleh systemd agar otomatis menyala setelah server dinyalakan ulang.

## Sertifikat
Gunakan Certbot untuk memasang sertifikat SSL gratis dari Let's Encrypt. Perpanjangan dijadwalkan otomatis. Jangan lupa membuka port 80 dan 443 di firewall.
