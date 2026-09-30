# ADR 0032 — NAT throttle

**STATUS:** proposed
**Sana:** 2026-09-29
**Tasdiqlagan:** Saidakbar (owner)
**Manba:** D4 (triage: 0032 ≠ A) · `owner-decision-closure-matrix-2026-09-29.md`
**Ta'sir doirasi:** Phase 4 (Phase 0 da **faqat o'lchov**)
**Dalil:** `apps/api/core/throttling.py` (`TrustedClientIdent`, `CacheOutageTolerant`) · `apps/api/config/settings.py` (throttle scope) · `docs/10-operations/README.md` (CONFLICT-1: `60/min` vs `1500/hour`)

## 1. Muammo

Throttle IP-based. Maktab sinfi bitta NAT IP ortidan kelganda 429 oladi. Hujjat va kod raqami ziddiyatli (CONFLICT-1: `60/min` yoki `1500/hour`). Oqibat: B2B (maktab) ochilishi bloklanadi **yoki** abuse himoyasi zaiflashadi.

## 2. Variantlar

1. Anonim limitni ko'tarish.
2. Katalogni throttle'dan chiqarish.
3. IP allowlist.
4. Identity-first: `user:` → `org:` → `ip:`; o'qish/yozish ajratish; `NetworkAllowlist`.

## 3. Tanlov

**Variant 4** — identity-first. Bu ish **Phase 4** ga tegishli. **Phase 0 da faqat o'lchov (M5)** — kod **yozilmaydi**.

## 4. Sabab

D4 triage: 0032 **A emas** (kod blokeri emas). Blueprint §21 uni Phase 0 (Trust) ga qo'ygan edi — reconciliation jadvalining 3-qatorida yopilgan (guruh + scope nomuvofiqligi). Phase 0 da faqat joriy konfiguratsiyani qayta o'lchash (20+ user, 1 IP) kerak; qaror Phase 4 da qabul qilinadi.

## 5. Oqibatlar

- Phase 0: faqat o'lchov natijasi (raqam), kod o'zgarmaydi.
- Phase 4: B2B ochiladi; abuse himoyasi saqlanadi.
- `NetworkAllowlist` va o'qish/yozish ajratish Phase 4 da qo'shiladi.

## 6. Qaytarilishi

Phase 4 da bajariladi; Phase 0 ga ta'siri yo'q (o'lchov qaytarilmaydi).

## 7. Tasdiq

- Phase 0: o'lchov natijasi qayd etilgan (raqam).
- Phase 4: bitta NAT IP'da 20+ user **429 OLMAYDI** (o'lchangan).

## 8. Bog'liq hujjatlar

- D4 — `owner-decision-closure-matrix-2026-09-29.md`
- Blueprint §21 (ADR 0032) · §22.2 (M5) · §24 (Phase 0/4)
- `phase0-reconciliation-table-2026-09-29.md` — 3-qator · 9-qator
- `docs/10-operations/README.md` — CONFLICT-1

**STATUS:** ADR 0032 — proposed. Phase 0 da faqat o'lchov (M5); qarori Phase 4.
