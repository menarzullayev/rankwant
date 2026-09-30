# ADR 0043 — Backup / PITR / DR

**STATUS:** deferred
**Sana:** 2026-09-29
**Tasdiqlagan:** Saidakbar (owner)
**Manba:** Triage (C guruhi) · `system-design-phase0-decision-closure-2026-09-29.md` §3.1
**Ta'sir doirasi:** Phase 1
**Dalil:** `tools/backup.sh` (offsite nusxa **standart O'CHIQ**) · `tools/backup.sh` (2026-09-17 PII hodisasi — shifrlanmagan dump R2 ga ketgan) · `tools/backup.sh` (avtomatik `restore_test()`)

## 1. Muammo

Backup **oylik**; off-site **OFF**; PITR **yo'q**; RPO ≤30 kun. Oqibat: ma'lumot yo'qotish oynasi katta. Off-site ataylab o'chirilgan — sabab bor: 2026-09-17 da **shifrlanmagan** PII dump R2 ga ketgan.

## 2. Variantlar

1. Hozirgi holat (oylik, off-site OFF).
2. Managed Postgres.
3. Faqat ko'proq `pg_dump`.
4. Kunlik + off-site ON + shifrlash + WAL→R2 (PITR); RPO ≤24 soat; DR mashqi.

## 3. Tanlov

**Variant 4** — kunlik + off-site + shifrlash + WAL→R2 (PITR). Bu ish **Phase 1** ga tegishli (C guruhi).

**Tartib qat'iy:** off-site'ni yoqishdan **OLDIN** shifrlash. Aks holda 2026-09-17 PII hodisasi takrorlanadi.

## 4. Sabab

RPO ≤30 kun production uchun qabul qilib bo'lmaydi. Managed Postgres narx/vendor keltiradi; faqat ko'proq `pg_dump` PITR bermaydi. Shuning uchun kunlik + off-site + shifrlash + WAL→R2. `tools/backup.sh` da avtomatik `restore_test()` allaqachon bor — kuchli tomon.

## 5. Oqibatlar

- Kunlik backup + off-site (shifrlangan) + PITR.
- RPO ≤24 soat; DR mashqi majburiy.
- Disk/xarajat ortadi.

## 6. Qaytarilishi

Phase 1 da bajariladi; Phase 0 ga ta'siri yo'q. **Deploy-oldi dump** (D11A) Phase 0 da allaqachon majburiy.

## 7. Tasdiq

- Kunlik backup ishlaydi; off-site **shifrlangan** holda yoqilgan.
- RPO/RTO **raqamlashtirilgan**.
- PITR (WAL→R2) ishlaydi.
- DR mashqi o'tkazilgan; `restore_test()` yashil.

## 8. Bog'liq hujjatlar

- Blueprint §21 (ADR 0043) · §22.2 (M7) · §24 (Phase 1)
- `tools/backup.sh` · `tools/check_decisions.py` (offsite default gate)
- ADR 0044 (secrets management)

**STATUS:** ADR 0043 — deferred (Phase 1). C guruhi; shifrlash off-site'dan OLDIN.
