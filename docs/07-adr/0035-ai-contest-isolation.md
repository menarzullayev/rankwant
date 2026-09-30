# ADR 0035 — AI contest isolation

**STATUS:** deferred
**Sana:** 2026-09-29
**Tasdiqlagan:** Saidakbar (owner)
**Manba:** Triage (C guruhi) · `system-design-phase0-decision-closure-2026-09-29.md` §3.1
**Ta'sir doirasi:** Phase 3
**Dalil:** Blueprint §12.6 (server-side policy) · Product Strategy #9 (practice AI, contest OFF) · #10 (tashqi AI to'sib bo'lmaydi)

## 1. Muammo

Practice rejimida AI yordam bo'lishi kerak, contest rejimida esa **o'chirilishi** shart. Tashqi AI vositalarini (brauzer plaginlari, boshqa qurilma) to'liq to'sib bo'lmaydi. Oqibat: contest adolati shubha ostida qoladi.

## 2. Variantlar

1. Faqat UI'da yashirish.
2. Faqat Gateway darajasida.
3. Anti-cheat flag.
4. Server-side policy: ikki joyda tekshiriladi; rad = 403 + audit.

## 3. Tanlov

**Variant 4** — server-side policy. Bu ish **Phase 3** ga tegishli (C guruhi). Yechim **to'liq emas** — bu ochiq tan olinadi.

## 4. Sabab

Server-side tekshiruv (ikki joyda) UI'da yashirishdan kuchliroq: endpoint contest rejimida rad etadi (403) va audit yozadi. Lekin **tashqi** AI vositalarini to'liq to'sib bo'lmaydi — shuning uchun yechim halol, ammo to'liq emas deb qayd etiladi.

## 5. Oqibatlar

- Contest rejimida AI endpoint o'chiriladi (observable).
- Har rad audit'ga yoziladi.
- Tashqi vositalar bo'yicha ochiq chegara saqlanadi.

## 6. Qaytarilishi

Phase 3 da bajariladi; Phase 0 ga ta'siri yo'q.

## 7. Tasdiq

- Contest rejimida AI endpoint **O'CHIRILGAN** (observable).
- Rad holati 403 + audit.
- AI DB/testdata/judge'ga tegmaydi (ADR 0036 gate).

## 8. Bog'liq hujjatlar

- Blueprint §12.6 · §21 (ADR 0035) · §24 (Phase 3)
- ADR 0033 (AI Gateway) · ADR 0036 (AI data boundary)

**STATUS:** ADR 0035 — deferred (Phase 3). C guruhi; yechim to'liq emas (ochiq).
