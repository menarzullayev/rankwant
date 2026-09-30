# ADR 0041 — Billing boundary

**STATUS:** deferred
**Sana:** 2026-09-29
**Tasdiqlagan:** Saidakbar (owner)
**Manba:** Triage (C guruhi) · `system-design-phase0-decision-closure-2026-09-29.md` §3.1
**Ta'sir doirasi:** Phase 4
**Dalil:** `apps/api/qvant/ledger.py` (Qvant ledger — yagona yozuv yo'li) · ADR 0002 (Qvant iqtisodiyoti) · blueprint §21 (ADR 0041)

## 1. Muammo

Qvant (platforma coini) va Billing (haqiqiy pul) aralashib ketish xavfi bor. Pricing ADR **bloklangan**. Agar Qvant billing vazifasini olsa, ADR 0002 (yopiq loop iqtisodiyot) buziladi.

## 2. Variantlar

1. Qvant'ni billing qilish.
2. To'lov provayderida hammasi.
3. Manual invoicing.
4. `billing` alohida app; `Entitlement` = kirish nazorati; Qvant bilan **FK yo'q**.

## 3. Tanlov

**Variant 4** — chegara hozir qo'yiladi, kod keyin. Bu ish **Phase 4** ga tegishli (C guruhi).

## 4. Sabab

Qvant — o'yin ichidagi iqtisodiyot (ADR 0002); Billing — haqiqiy pul va kirish huquqi. Ularni aralashtirish ADR 0002 ni buzadi va moliyaviy izchillikni yo'qotadi. Shuning uchun `billing` alohida app va `Entitlement` modeli; Qvant ↔ Billing FK **yo'q**.

## 5. Oqibatlar

- `billing` app va `Entitlement` modeli Phase 4 da qo'shiladi.
- Qvant ↔ Billing kod yo'li **yo'q** (gate tekshiradi).
- Pricing ADR Phase 4 da qabul qilinadi.

## 6. Qaytarilishi

Phase 4 da bajariladi; Phase 0 ga ta'siri yo'q.

## 7. Tasdiq

- `Entitlement` orqali kirish nazorati ishlaydi.
- **Qvant ↔ Billing kod yo'li yo'q** (gate).
- Pricing ADR qabul qilingan.

## 8. Bog'liq hujjatlar

- Blueprint §18 (billing boundary) · §21 (ADR 0041) · §24 (Phase 4)
- ADR 0002 (Qvant iqtisodiyoti) · ADR 0045 (audit + object-level authz)

**STATUS:** ADR 0041 — deferred (Phase 4). C guruhi; chegara hozir, kod keyin.
