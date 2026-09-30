# ADR 0047 — Judge host separation

**STATUS:** deferred
**Sana:** 2026-09-29
**Tasdiqlagan:** Saidakbar (owner)
**Manba:** D4 (triage: 0029 → B guruhi) · `owner-decision-closure-matrix-2026-09-29.md`
**Ta'sir doirasi:** Phase 1
**Dalil:** `compose/four-host/README.md` (maqsad topologiya) · `docker-compose.yml` (judge data servislari bilan bir hostda)

## 1. Muammo

Preview topologiyasida judge Postgres/Redis/MinIO bilan **bir hostda** turadi. ADR 0004 ning birinchi sharti (judge ajratilgan host) bajarilmagan. Judge izolyatsiyasi buzilsa — escape nafaqat host root, balki butun testdata va bazaga ham yetadi.

## 2. Variantlar

1. Bir host qoldirish.
2. Faqat tarmoqni ajratish (alohida tarmoq + alohida volume).
3. To'liq 4-host topologiya (judge alohida host, faqat data Redis/S3 ga ulanadi).

## 3. Tanlov

**Variant 3** — judge alohida host. Bu ish **Phase 1** ga tegishli (D4: 0029 B guruhi).

## 4. Sabab

0029 — topologiya ishi, kod blokeri **emas** (D4). Phase 0 kodini uni kutmasdan yozib bo'ladi. Blueprint §21 uni Phase 0 ga qo'ygan edi — bu reconciliation jadvalining 2-qatorida yopilgan (faza nomuvofiqligi). Owner qarori 0029 ni B guruhiga (Phase 1) o'tkazdi.

## 5. Oqibatlar

- `compose/four-host` rejasi amalga oshiriladi.
- Ops yuki ortadi; deploy murakkablashadi.
- Phase 0 da **o'zgarmaydi** — hozirgi bir host holati saqlanadi.

## 6. Qaytarilishi

Oson (topologiya o'zgarishi), lekin Phase 1 da bajariladi. Phase 0 ga ta'siri yo'q.

## 7. Tasdiq

- Judge alohida host(lar)da ishlaydi.
- Faqat judge → data Redis/S3; judge boshqa servislarga to'g'ridan-to'g'ri bog'lanmaydi.
- Phase 1 done-condition ④ bilan birga tekshiriladi.

## 8. Bog'liq hujjatlar

- D4 — `owner-decision-closure-matrix-2026-09-29.md`
- Blueprint §21 (ADR 0047) · §24 (Phase 1)
- `compose/four-host/README.md`
- ADR 0004 (judge engine) · ADR 0046 (judge privilege model)

**STATUS:** ADR 0047 — deferred (Phase 1). B guruhi; Phase 0 scope'idan tashqarida.
