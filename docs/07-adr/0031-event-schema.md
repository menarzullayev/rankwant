# ADR 0031 — Event schema / envelope

**STATUS:** deferred
**Sana:** 2026-09-29
**Tasdiqlagan:** Saidakbar (owner)
**Manba:** Triage (C guruhi) · `system-design-phase0-decision-closure-2026-09-29.md` §3.1
**Ta'sir doirasi:** Phase 2
**Dalil:** `apps/api/core/models.py` (`AnalyticsEvent`) · `props` erkin JSON · 9 call site

## 1. Muammo

`AnalyticsEvent.props` erkin JSON. Kanonik maydonlar — `event_id`, `schema_version`, `subject`, `origin` — yo'q. 9 ta call site turli shaklda yozadi. Oqibat: funnel qurib bo'lmaydi; qarorlar ko'r qabul qilinadi. Event `origin` (ADR 0030) bilan bog'lanmagani uchun real va demo trafik aralashadi.

## 2. Variantlar

1. Mavjud modelni saqlash.
2. Tashqi analytics (PostHog va h.k.).
3. Kafka.
4. Kanonik envelope (blueprint §13.2) + event katalogi (§13.3).

## 3. Tanlov

**Variant 4** — kanonik envelope + event katalogi. Bu ish **Phase 2** ga tegishli (triage C guruhi).

## 4. Sabab

Envelope maydonlari (`event_id`, `schema_version`, `subject`, `origin`) server va mijoz event'larini bir shaklga keltiradi va ADR 0030 origin'iga tayanadi. Tashqi analytics chegara (PII) xavfini keltiradi; Kafka — ortiqcha murakkablik. Shuning uchun C guruhida, Phase 2 da, origin backfill (0030) dan keyin bajariladi.

## 5. Oqibatlar

- Instrumentatsiya majburiy qadamga aylanadi.
- Eski yozuvlar `schema_version=0` oladi; server-side event'lar qo'shiladi.
- Event hajmi o'sadi (trigger: partition).

## 6. Qaytarilishi

Phase 2 da bajariladi; Phase 0 ga ta'siri yo'q. M4 migratsiya forward-only.

## 7. Tasdiq

- Envelope maydonlari mavjud.
- Funnel dashboard ishlaydi.
- Metrikalar `origin='real'` filtri bilan (ADR 0030).

## 8. Bog'liq hujjatlar

- Blueprint §13 (instrumentation) · §21 (ADR 0031) · §24 (Phase 2)
- ADR 0030 (data origin)
- Triage C guruhi — `system-design-phase0-decision-closure-2026-09-29.md`

**STATUS:** ADR 0031 — deferred (Phase 2). C guruhi; Phase 0 scope'idan tashqarida.
