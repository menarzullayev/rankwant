# ADR 0033 — AI Gateway

**STATUS:** proposed
**Sana:** 2026-09-29
**Tasdiqlagan:** Saidakbar (owner)
**Manba:** D6 (ADR 0036 AI boundary — joylashuv) · `owner-decision-closure-matrix-2026-09-29.md`
**Ta'sir doirasi:** Phase 3 (joylashuv Phase 0)
**Dalil:** `apps/api/ai/` (monolit modul skeleti mavjud) · `apps/api/ai/README.md` · `apps/api/ai/__init__.py`

## 1. Muammo

AI hozircha yo'q (0 endpoint). Savol: AI Gateway **qayerda** joylashadi — alohida servismi yoki modulmi? Joylashuv keyinchalik ajratish imkonini belgilaydi. Agar AI qatlami bugun DB sxemasiga yopishsa, keyin alohida xizmatga ajratish imkonsiz bo'ladi.

## 2. Variantlar

1. To'g'ridan-to'g'ri SDK chaqiruv (joylashuvsiz).
2. Tashqi platforma (masalan LangChain).
3. Alohida servis.
4. Monolit Python modul (`apps/api/ai/`).

## 3. Tanlov

**Variant 4** — **monolit modul** `apps/api/ai/` (D6). Bu modul **Django app emas**: `models.py`, `migrations/`, `apps.py` yo'q va `INSTALLED_APPS` ga qo'shilmaydi.

**Runtime** (policy · limit · context · prompt registry · kesh · audit · cost) **Phase 3** ga tegishli va hozir **yo'q**.

## 4. Sabab

D6 ataylab monolit modulni tanladi: u AI qatlamini keyinchalik alohida xizmatga ajratishni mumkin qiladi. To'g'ridan-to'g'ri SDK chaqiruv chegara qoldirmaydi; tashqi platforma vendor lock-in keltiradi. Modulning chegara kontrakti ADR 0036 (`check_ai_boundary.py`) bilan majburlanadi.

## 5. Oqibatlar

- `apps/api/ai/` — AI qatlamining yagona uyi (skelet Phase 0).
- AI Gateway runtime Phase 3 da qo'shiladi.
- Modul DB modelni import qilmaydi, `DATABASE_URL` ni bilmaydi, testdata'ga tegmaydi.
- `check_ai_boundary.py` statik chegara; `neg_ai_boundary` salbiy test.

## 6. Qaytarilishi

Oson (modul). Ajratish Phase 3 da mumkin — chegara shu imkoniyatni saqlaydi.

## 7. Tasdiq

- AI Gateway **monolit modul** (`apps/api/ai/`).
- Modul `INSTALLED_APPS` da yo'q, `models.py`/`migrations/` yo'q.
- `check_ai_boundary.py` bugungi repo'da yashil (ADR 0036).

## 8. Bog'liq hujjatlar

- D6 — `owner-decision-closure-matrix-2026-09-29.md`
- Blueprint §12 (AI feedback) · §21 (ADR 0033)
- `apps/api/ai/README.md`
- ADR 0036 (AI data boundary) · ADR 0034 (model routing) · ADR 0035 (contest isolation)

**STATUS:** ADR 0033 — proposed. Joylashuv Phase 0 (monolit modul); runtime Phase 3.
