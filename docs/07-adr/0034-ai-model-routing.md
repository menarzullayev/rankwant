# ADR 0034 — AI model routing

**STATUS:** deferred
**Sana:** 2026-09-29
**Tasdiqlagan:** Saidakbar (owner)
**Manba:** Triage (C guruhi) · `system-design-phase0-decision-closure-2026-09-29.md` §3.1
**Ta'sir doirasi:** Phase 3
**Dalil:** Blueprint §21 (ADR 0034) · blueprint §26 Q6 (7B hardware feasibility **o'lchanmagan**)

## 1. Muammo

Vendor lock-in eng katta xavf sifatida belgilangan (REPORT). Local model (7B) hardware feasibility **o'lchanmagan**. Routing qarorisiz AI qatlami bitta provayderga yopishib qoladi.

## 2. Variantlar

1. Faqat lokal model.
2. Faqat bulut.
3. Gibrid.
4. Local-first (yuqori hajm) + bulut faqat explicit consent + zero-retention; Model Adapter interfeysi.

## 3. Tanlov

**Variant 4** — local-first + Model Adapter. Bu ish **Phase 3** ga tegishli (C guruhi).

## 4. Sabab

Local-first IP/privacy va xarajatni boshqaradi; bulut faqat rozilik bilan. Model Adapter provayderni almashtirish imkonini beradi. 7B feasibility o'lchovi P3 ni **bloklaydi** (Q6) — shuning uchun qaror Phase 3 da o'lchovdan keyin qotadi.

## 5. Oqibatlar

- Model Adapter interfeysi.
- 7B feasibility o'lchovi P3 ni bloklaydi.
- Cloud faqat explicit consent + zero-retention.

## 6. Qaytarilishi

Phase 3 da bajariladi; Phase 0 ga ta'siri yo'q.

## 7. Tasdiq

- FAR / HR / CPF / p95 latency **raqamlangan** va maqsadga yetgan.
- Model Adapter mavjud; provayder almashtiriladi.

## 8. Bog'liq hujjatlar

- Blueprint §21 (ADR 0034) · §24 (Phase 3) · §26 Q6
- ADR 0033 (AI Gateway)

**STATUS:** ADR 0034 — deferred (Phase 3). C guruhi; hardware feasibility o'lchovini kutadi.
