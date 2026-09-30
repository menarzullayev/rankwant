# ADR 0045 — Audit and object-level authorization

**STATUS:** deferred
**Sana:** 2026-09-29
**Tasdiqlagan:** Saidakbar (owner)
**Manba:** Triage (C guruhi) · `system-design-phase0-decision-closure-2026-09-29.md` §3.1
**Ta'sir doirasi:** Phase 4
**Dalil:** `apps/api/core/permissions.py` (`require_staff_group` — imperativ) · `apps/api/classroom/views.py` (imperativ tekshiruv) · blueprint §21 (ADR 0045)

## 1. Muammo

Umumiy audit **qisman**. DRF `has_object_permission` override **topilmadi** — avtorizatsiya faqat imperativ (`core/permissions.py`, `classroom/views.py`). Oqibat: B2B multi-tenant xavfi — bir obyekt boshqa obyekt ma'lumotiga yetishi mumkin.

## 2. Variantlar

1. Hozirgi holat.
2. Middleware.
3. Faqat staff uchun.
4. `AuditLog` + har staff/obyekt amali uchun **majburiy** object-level tekshiruv.

## 3. Tanlov

**Variant 4** — `AuditLog` + majburiy object-level tekshiruv. Bu ish **Phase 4** ga tegishli (C guruhi); B2B oldidan **majburiy**.

## 4. Sabab

Imperativ tekshiruv yangi view qo'shilganda o'tkazib yuborilishi mumkin — umumiy `has_object_permission` buni tizimli yopadi. Middleware (variant 2) sekin; faqat staff (variant 3) yetarli emas. Shuning uchun `AuditLog` + majburiy object-level tekshiruv B2B oldidan.

## 5. Oqibatlar

- `AuditLog` modeli qo'shiladi.
- Har staff/obyekt amali object-level tekshiruvdan o'tadi.
- B2B multi-tenant ochilishi bloklanmaydi.

## 6. Qaytarilishi

Phase 4 da bajariladi; Phase 0 ga ta'siri yo'q.

## 7. Tasdiq

- Object-level authz **majburiy** va testlangan.
- `AuditLog` har staff/obyekt amalini yozadi.
- B2B pilot 5+ maktab bilan ishlaydi.

## 8. Bog'liq hujjatlar

- Blueprint §17 (B2B) · §21 (ADR 0045) · §24 (Phase 4)
- `apps/api/core/permissions.py` · `apps/api/classroom/views.py`
- ADR 0041 (billing boundary)

**STATUS:** ADR 0045 — deferred (Phase 4). C guruhi; B2B oldidan majburiy.
