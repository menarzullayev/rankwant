# ADR 0036 — AI data boundary

**STATUS:** accepted
**Sana:** 2026-09-29
**Tasdiqlagan:** Saidakbar (owner)
**Manba:** D6 (ADR 0036 AI boundary) · `owner-decision-closure-matrix-2026-09-29.md`
**Ta'sir doirasi:** Phase 0
**Dalil:** `services/judge-go/main.go` (`DATABASE_URL` rad etish) · `apps/api/ai/` (monolit modul) · `tools/check_ai_boundary.py` (statik chegara) · `apps/api/tests/test_ai_boundary.py` (runtime chegara)

## 1. Muammo

AI qatlami nima o'qiy oladi — chegara ta'riflanmagan. Chegara bo'lmasa `check_ai_boundary.py` darvozasi **vakuumli yashil** o'tadi (o'lchanadigan kod yo'q). Xavf: AI qatlami DB modelini import qilib yoki testdata'ni o'qib, ajratish imkonini va ma'lumot yaxlitligini buzadi.

## 2. Variantlar

1. To'liq DB kirish.
2. Faqat read replica.
3. Context whitelist + DB credential yo'q + tool ruxsat ro'yxati + chiqish validatsiyasi.
4. MCP (qo'shimcha qatlam).

## 3. Tanlov

**Variant 3** (D6) — AI qatlami:
- context whitelist;
- AI'ga **`DATABASE_URL` berilmaydi**;
- **judge va testdata'ga tegilmaydi**;
- tool ruxsat ro'yxati; chiqish validatsiyasi.

Chegara `tools/check_ai_boundary.py` bilan majburlanadi.

## 4. Sabab

Judge `DATABASE_URL` ni allaqachon **rad etadi** (`services/judge-go/main.go`, bo'lsa `exit 1`) — bu takrorlanadigan naqsh, endi Python tomonida takrorlanadi. To'liq DB kirish yaxlitlikni buzadi; read replica testdata xavfini qoldiradi. Shuning uchun context whitelist + credential yo'q + tool allowlist.

## 5. Oqibatlar

- `apps/api/ai/` DB modelni import qilmaydi, `django.db`/`django.contrib.*` ni import qilmaydi, `DATABASE_URL` ni bilmaydi, testdata'ni o'qimaydi.
- Statik darvoza (`check_ai_boundary.py`) + runtime darvoza (`test_ai_boundary.py`): `ai` paketini import qilganda `sys.modules` ga birorta `*.models` moduli tushmaydi.
- Salbiy test (`neg_ai_boundary`) majburiy — aks holda darvoza o'lik.

## 6. Qaytarilishi

Oson (statik qoida). Chegara Phase 0 da o'rnatiladi; runtime Phase 3 da qo'shiladi.

## 7. Tasdiq

- `tools/check_ai_boundary.py` bugungi repo'da **yashil** (exit 0).
- DB-model import yoki testdata o'qish mutatsiyasi → **qizil** (exit 1).
- AI qatlamida **`DATABASE_URL` yo'q**.
- AI Gateway **monolit modul** (`apps/api/ai/`).
- O'qib bo'lmasa `exit 2` — hech qachon "toza" deb o'qilmaydi.

## 8. Bog'liq hujjatlar

- D6 — `owner-decision-closure-matrix-2026-09-29.md`
- `acceptance-criteria-lock-2026-09-29.md` — WP5 bloki
- Blueprint §21 (ADR 0036) · §24 (Phase 0 done-condition ⑤)
- `phase0-reconciliation-table-2026-09-29.md` — 4-qator (faza nomuvofiqligi)
- ADR 0033 (AI Gateway) · ADR 0046 (judge privilege model)

**STATUS:** ADR 0036 — accepted. Phase 0; context whitelist + DB credential yo'q + testdata yo'q; `check_ai_boundary.py` majburlaydi.
