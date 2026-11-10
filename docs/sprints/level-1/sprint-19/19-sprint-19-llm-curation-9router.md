# Sprint 19: Penyulingan dengan LLM lewat 9router & Lapisan Knowledge

| Metadata | Nilai |
| :--- | :--- |
| **Sprint** | Sprint 19 |
| **Target versi** | `v1.15.0-alpha` |
| **Status** | ⏳ Planned |
| **Dokumen** | [48](../../../brainstorming/48-peran-llm-audit-vault-dan-arah-rag.md) bagian 1 dan 4, [46](../../../brainstorming/46-riset-projek-serupa-efisiensi-token-dan-tech-stack.md) (pola LLM Wiki) |
| **Butuh LLM** | Ya, opsional |
| **Syarat** | Sprint 14, 15, 18 |

## Tujuan
Log sesi mentah diolah menjadi memori dan catatan `20_Knowledge` yang rapi. LLM tidak pernah masuk ke jalur pencarian, dan hasilnya selalu berupa usulan.

## Keputusan sebelum mulai

| ID | Pertanyaan | Usulan |
| :--- | :--- | :--- |
| D19-1 | Kebijakan privasi per grup | `_fxmedia`: hanya model lokal (Ollama) atau tidak diolah; lainnya lewat 9router |
| D19-2 | Model untuk penyulingan | Combo 9router yang murah; model lokal sebagai cadangan |

## Task

| ID | Task | Berkas | Status |
| :--- | :--- | :--- | :--- |
| S19-T01 | Config `llm` format OpenAI (`base_url`, `model`, `api_key_env`), tanpa kunci di berkas | `core/config.py`, `llm/client.py` (baru) | ⏳ |
| S19-T02 | Kebijakan privasi per grup dan sanitasi sebelum dikirim | `llm/policy.py` (baru), `harvester/sanitizer.py` | ⏳ |
| S19-T03 | `devbrain curate sessions`: sesi menjadi usulan memori dan catatan knowledge | `curator/distill.py` (baru), `cli/commands/curate_cmd.py` (baru) | ⏳ |
| S19-T04 | Usulan ditaruh di `90_Agent_Inbox/manual_review/` dengan tautan ke sumber; perintah setujui/tolak | `curator/proposals.py` (baru) | ⏳ |
| S19-T05 | Konsolidasi knowledge: gabungkan log tentang topik yang sama menjadi satu catatan `20_Knowledge` | `curator/distill.py` | ⏳ |
| S19-T06 | Pemeriksaan berkala: kontradiksi, duplikat, memori usang (usulan, bukan perubahan) | `curator/lint.py` (baru) | ⏳ |
| S19-T07 | Batas biaya: jumlah token per jalan, berhenti saat router gagal | `llm/client.py` | ⏳ |
| S19-T08 | Test (LLM tiruan), evaluasi retrieval sesudah lapisan knowledge, changelog, rilis | `tests/`, `docs/changelog/` | ⏳ |

## Rincian

**S19-T03.** Keluaran terstruktur (JSON) per sesi: keputusan, masalah dan solusi, fakta yang layak diingat, skill kandidat. Setiap butir mencatat sesi sumbernya.
*Selesai bila:* satu sesi nyata menghasilkan usulan yang bisa disetujui; tidak ada yang tersimpan sebelum disetujui.

**S19-T05.** Pola LLM Wiki: `90_Agent_Inbox` adalah sumber mentah yang tidak diubah, `20_Knowledge` adalah wiki hasil olahan.
*Selesai bila:* hit@1 evaluasi pada pertanyaan nyata naik dibanding mencari di log mentah.

## Catatan
- Tanpa config `llm`, DevBrain tetap berfungsi penuh.
- Hasil LLM melewati gerbang tulis Sprint 15.
