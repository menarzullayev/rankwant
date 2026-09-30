# ADR 0038 — Judge queue semantics

**STATUS:** deferred
**Sana:** 2026-09-29
**Tasdiqlagan:** Saidakbar (owner)
**Manba:** Triage (C guruhi) · `system-design-phase0-decision-closure-2026-09-29.md` §3.1
**Ta'sir doirasi:** Phase 1
**Dalil:** `services/judge-go/main.go` (`BRPOP` — job'ni navbatdan olib tashlaydi) · blueprint §21 (ADR 0038)

## 1. Muammo

Judge `BRPOP` bilan job'ni navbatdan **olib tashlaydi** (at-most-once): worker crash bo'lsa job **yo'qoladi**. `RUNNING` holat yo'q, DLQ (dead-letter queue) yo'q, visibility timeout yo'q — bitta navbat. Oqibat: yuborish «osilib» qoladi yoki jimgina yo'qoladi.

## 2. Variantlar

1. Hozirgi holat (`BRPOP`, at-most-once).
2. Redis Streams (consumer group + ack).
3. Kafka.
4. `BRPOPLPUSH` + processing list + heartbeat + DLQ + prioritetli navbat.

## 3. Tanlov

**Variant 4** — at-least-once + idempotentlik. Bu ish **Phase 1** ga tegishli (C guruhi).

## 4. Sabab

Job yo'qolishi contest adolatiga bevosita ta'sir qiladi, lekin Phase 0 kodini bloklamaydi. `BRPOPLPUSH` + processing list Redis'ning mavjud imkoniyati — Kafka ortiqcha. `judging/services.py` da `apply_result` allaqachon idempotent, ya'ni at-least-once'ga o'tish qayta ishlovni buzmaydi.

## 5. Oqibatlar

- At-least-once + idempotent natija qayta ishlash.
- DLQ va `RUNNING` holat qo'shiladi.
- Redis rol ajratish (TD23) trigger bilan bog'liq.

## 6. Qaytarilishi

Phase 1 da bajariladi; Phase 0 ga ta'siri yo'q.

## 7. Tasdiq

- Worker crash bo'lsa job **yo'qolmaydi** (processing list'dan qayta olinadi).
- DLQ mavjud; osilgan job `reap_stuck` bilan tiklanadi.
- `apply_result` idempotentligi saqlanadi.

## 8. Bog'liq hujjatlar

- Blueprint §21 (ADR 0038) · §24 (Phase 1)
- `services/judge-go/main.go` · `apps/api/judging/services.py`
- ADR 0046 (judge privilege model)

**STATUS:** ADR 0038 — deferred (Phase 1). C guruhi; at-most-once → at-least-once.
