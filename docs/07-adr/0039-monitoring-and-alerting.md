# ADR 0039 — Monitoring and alerting

**STATUS:** deferred
**Sana:** 2026-09-29
**Tasdiqlagan:** Saidakbar (owner)
**Manba:** Triage (C guruhi) · `system-design-phase0-decision-closure-2026-09-29.md` §3.1
**Ta'sir doirasi:** Phase 1
**Dalil:** `apps/api/notifications/tasks.py` (`send_telegram`, `TELEGRAM_BOT_TOKEN`) · `apps/api/core/views.py` (`/api/v1/slo/`) · blueprint §21 (ADR 0039, CONFLICT-4)

## 1. Muammo

Metrics store **yo'q**; faqat `/api/v1/slo/` endpoint mavjud. Xatolar kuzatilmaydi — tizim «ko'r». Product Strategy Sentry qurilishini talab qiladi (F70), lekin repo'da Sentry **ataylab yo'q** va CI bilan majburlangan (CONFLICT-4). Oqibat: incident sezilmaydi.

## 2. Variantlar

1. Sentry (tashqi).
2. GlitchTip (self-hosted, Sentry SDK).
3. Strukturali log + Telegram alert.
4. Hozirgi holat (kuzatuv yo'q).

## 3. Tanlov

**Qaror talab** — ehtiyoj qabul qilinadi, vosita Phase 1 da tanlanadi. Telegram bot **allaqachon bor** (`apps/api/notifications/tasks.py`), ya'ni ops alert kanali qo'shimcha vositasiz ishga tushirilishi mumkin. Bu ish **Phase 1** ga tegishli (C guruhi).

## 4. Sabab

Kuzatuv Phase 0 kodini bloklamaydi, lekin production uchun shart. Telegram ops kanali mavjud tokenni alohida `ops` chat_id bilan ishlatadi va Sentry CI taqiqini **buzmaydi**. GlitchTip ham Sentry SDK ishlatadi — bu CI qoidasi bilan ziddiyat ehtimoli bor, shuning uchun vosita tanlovi alohida qaror talab qiladi.

## 5. Oqibatlar

- Ops alert kanali (Telegram) qo'shiladi.
- Metrics store qo'shiladi.
- Sentry/GlitchTip qarori Product Owner tasdig'ini kutadi.

## 6. Qaytarilishi

Phase 1 da bajariladi; Phase 0 ga ta'siri yo'q.

## 7. Tasdiq

- Alert kanali ishlaydi (test alert yetib boradi).
- Incident seziladi va yoziladi.
- Sentry/GlitchTip qarori qayd etilgan.

## 8. Bog'liq hujjatlar

- Blueprint §21 (ADR 0039) · §24 (Phase 1) · §26 Q4
- `apps/api/notifications/tasks.py` · `apps/api/core/views.py`
- Product Strategy F70 (CONFLICT-4)

**STATUS:** ADR 0039 — deferred (Phase 1). C guruhi; vosita tanlovi qaror talab qiladi.
