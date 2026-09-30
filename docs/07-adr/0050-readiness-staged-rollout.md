# ADR 0050 — Readiness darvozalari bosqichma-bosqich joriy etiladi

**STATUS:** accepted
**Sana:** 2026-09-30
**Tasdiqlagan:** Saidakbar (owner)
**Manba:** ADR 0049 §6a (joriy etish sharti) · ADR-0037 (content integrity gate)
**Ta'sir doirasi:** `apps/api/config/settings.py`, `problems/readiness.py`, `problems/models.py`, `contests/staff_serializers.py`, `contests/staff_views.py`, `docker-compose.public.yml`, `.env.example`
**Dalil:** o'lchov 2026-09-30 — ishlab turgan baza: 1 225 `legacy_unverified`, 867 `draft`, 4 `needs_review`, **0 `validated`**

## 1. Muammo

ADR 0049 readiness darvozalarini majburladi. Ular **to'g'ri**, lekin joriy etilsa
production buziladi: `GRADED_READY` ga mos masala **bitta ham yo'q**, ya'ni
contest'ga masala qo'shish **har doim** `400` qaytaradi.

Kod `main` da. Har qanday keyingi deploy uni production'ga olib chiqadi.

## 2. Variantlar

1. **Bosqichma-bosqich** — darvoza kodda qoladi, lekin bayroq o'chirilganda rad
   etmaydi, faqat WARNING yozadi.
2. **Kontentni oldin `validated` ga ko'chirish** — keyin deploy.
3. **Grandfather + ratchet** — mavjud masalalar istisno, yangilari darvozadan o'tadi.
4. **#315 ni orqaga qaytarish.**

## 3. Tanlov

**Variant 1** — bosqichma-bosqich: standart holat **majburlash**, production
vaqtincha `READINESS_ENFORCE=0` bilan yuradi.

## 4. Sabab

- **Spec saqlanadi**: standart qiymat `True`, ya'ni qoidalar va qabul testlari
  o'zgarmaydi; chekinish faqat deploy konfiguratsiyasida va ochiq yozilgan.
- **Production darhol ishlamaydi degan xavf yo'qoladi** — `0` bilan har bir
  rad etilishi WARNING bo'lib logga tushadi, ya'ni kontent qanchalik
  yetishmayotgani **ko'rinadi**.
- **Variant 2 bloklangan**: 1 222 / 1 226 masalada yashirin test yo'q, ya'ni ular
  S1 dan o'tmaydi va `validated` ga chiqa olmaydi. Bu alohida, katta kontent ishi.
- **Variant 3 spec'ga zid**: D8-F aynan "legacy graded contest'ga kira olmaydi"
  deydi. Uni chetlab o'tish yangi qaror talab qilardi va muammoni yashirardi.
- **Variant 4 qaytarib qo'yadi**: guruh yana dormant bo'lardi va 5 ta qabul testi
  yiqilardi.

## 5. Oqibatlar

- Yangi sozlama: `READINESS_ENFORCE` (`env_bool`, standart `True`).
- `problems/readiness.py` da ikki yordamchi: `enforcing()` va `gate(message)`.
  `assert_transition` endi `gate` orqali ishlaydi.
- `Problem.clean()`: `requirement_error` natijasi `gate(error)` orqali.
- `staff_serializers.py` va `staff_views.py`: bayroq o'chirilganda `continue` +
  WARNING; mutatsiya isboti uchun shart matni **o'zgarmadi**
  (`row["problem"].readiness != GRADED_READY`).
- `docker-compose.public.yml`: `READINESS_ENFORCE: ${READINESS_ENFORCE:-1}` —
  api xizmatiga uzatiladi.
- `.env.example`: o'zgaruvchi hujjatlashtirildi (darvoza talab qiladi).
- `.env.public` (gitignored): `READINESS_ENFORCE=0` — vaqtinchalik chekinish.
- **Har bir chetlab o'tish logga yoziladi** — jimgina yashil bo'lib qolmaydi.

### Qachon olib tashlanadi

Kontent `validated` ga ko'chirilgach: `.env.public` dagi qator o'chiriladi,
`READINESS_ENFORCE` standart `True` ga qaytadi. O'shanda darvoza yana to'liq
majburlaydi va bu ADR bilan 0049 birga o'qiladi.

## 6. Qaytarilishi

Bayroqni `1` ga qo'yish yoki `.env.public` dagi qatorni o'chirish — darvoza
darhol majburlaydi. Kod o'zgarishi talab qilinmaydi.

## 7. Tasdiq

- `apps/api/tests/test_problem_readiness.py` (11 test) — standart bilan yashil,
  ya'ni majburlash yoqilganda qoidalar ishlaydi.
- `check_negative.py --group neg_refsolution_gate` — 2/2 mutatsiya isboti.
- Bayroq o'chirilganda: `draft` masala contest'ga qo'shiladi (`200`) va WARNING
  logga tushadi — alohida test bilan o'lchandi.
