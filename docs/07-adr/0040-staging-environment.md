# ADR 0040 — Staging environment

**STATUS:** deferred
**Sana:** 2026-09-29
**Tasdiqlagan:** Saidakbar (owner)
**Manba:** Triage (C guruhi) · `system-design-phase0-decision-closure-2026-09-29.md` §3.1
**Ta'sir doirasi:** Phase 1
**Dalil:** `.github/workflows/deploy.yml` (faqat input, infra yo'q) · `docs/06-architecture/README.md` (staging ziddiyati — CONFLICT-3)

## 1. Muammo

Staging muhiti **yo'q**. `deploy.yml` da faqat input bor, infra yo'q. Hujjat «staging deploy» deb yozadi (CONFLICT-3). Oqibat: pre-prod tekshiruv yo'q — har o'zgarish to'g'ridan-to'g'ri production'ga boradi.

## 2. Variantlar

1. Staging yo'q (ci-local yetarli).
2. Ephemeral preview.
3. To'liq staging host (production bilan bir xil kichik topologiya).

## 3. Tanlov

**Variant 3** — alohida staging host, production bilan bir xil (kichik) topologiya. Bu ish **Phase 1** ga tegishli (C guruhi).

## 4. Sabab

ci-local konteyner chegarasini tekshiradi, lekin host darajasidagi farqlarni (tarmoq, volume, TLS, cgroup) ko'rsatmaydi. To'liq staging four-host rejasiga mos va M6 (topologiya) sinov maydoni bo'ladi. Ephemeral preview murakkab; staging'siz xavf katta.

## 5. Oqibatlar

- Alohida staging host qo'shiladi.
- CI → staging → prod zanjiri.
- `docs/10-operations/README.md` dagi staging da'vosi (CONFLICT-3) haqiqatga aylanadi.

## 6. Qaytarilishi

Phase 1 da bajariladi; Phase 0 ga ta'siri yo'q.

## 7. Tasdiq

- Staging'da deploy bo'lgan (observable).
- Staging topologiyasi production bilan mos (kichik).
- CI → staging → prod zanjiri ishlaydi.

## 8. Bog'liq hujjatlar

- Blueprint §21 (ADR 0040) · §24 (Phase 1) · §26 Q5
- `compose/four-host/README.md` · `.github/workflows/deploy.yml`
- ADR 0047 (judge host separation)

**STATUS:** ADR 0040 — deferred (Phase 1). C guruhi; CONFLICT-3 ni yopadi.
