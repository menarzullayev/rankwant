# ADR 0051 — Test guruhlari semantik toifa sifatida

**STATUS:** accepted
**Sana:** 2026-09-30
**Tasdiqlagan:** Saidakbar (owner)
**Manba:** PROMPT_0 §3 (Test Data Groups) · ADR-0037 · ADR 0049 · ADR 0050
**Ta'sir doirasi:** `problems/models.py` (`TestCase`), `problems/testgroups.py`, `problems/staff_serializers.py`, `problems/staff_views.py`, `judging/services.py`
**Dalil:** o'lchov 2026-09-30 — `TestCase` da faqat `is_sample` va `origin` bor edi; guruh tushunchasi **yo'q** edi

## 1. Muammo

Test ma'lumotlari tasniflanmagan edi. `TestCase` da faqat ikki o'q bor edi:

- `is_sample` — namuna yoki yashirin
- `origin` — muallif yoki hack

Bu **manba** va **ko'rinish** haqida gapiradi, lekin test NIMANI
tekshirishini aytmaydi. Oqibat: "bu masalada chegara testi bormi?" degan
savolga kod javob bera olmasdi, ya'ni release checklist'ning «edge case,
boundary va maksimal testlar mavjud» bandi **tekshirilmas** edi.

## 2. Variantlar

1. **TextChoices enum** (`TestCase.Group`) + siyosat moduli.
2. **`TestGroup` modeli** (jadval) + `TestCase.group` FK.
3. `is_sample` ni kengaytirish (bayroqlar to'plami).

## 3. Tanlov

**Variant 1** — `TestCase.Group` TextChoices + `problems/testgroups.py`.

## 4. Sabab

- **Repo an'anasi**: `Problem.Readiness` (9 holat) va `Problem.Checker`
  (5 tur) ham TextChoices — taksonomiya kichik, qat'iy va kod bilan
  birga versiyalanadi.
- **Variant 2 ortiqcha abstraksiya**: 8 ta qat'iy guruh uchun alohida
  jadval, FK va join qo'shardi; guruhlar foydalanuvchi tomonidan
  yaratilmaydi.
- **Variant 3 yetarli emas**: bayroqlar bir nechta guruhga tegishli testni
  ifodalay olmaydi va "aniq bitta toifa" qoidasini buzadi.
- **Siyosat alohida modulda**: ko'rinish, nashr talabi va judge istisnosi
  serializer, view, nashr darvozasi va judge payload'ining hammasiga
  kerak. Ularni har biriga ko'chirib yozish ajralib ketardi.

## 5. Oqibatlar

- `TestCase.group` — 8 guruh + `unclassified` (faqat ko'chirish holati).
- `testgroups.py` — yagona siyosat manbai: `PUBLIC_GROUPS`,
  `REQUIRED_GROUPS`, `NON_JUDGED_GROUPS`, `GROUP_META`.
- **Uchta haqiqiy oqim** guruhga tayanadi:
  1. **Ko'rinish** — `SAMPLE` yagona ommaviy guruh.
  2. **Nashr talabi** — `BOUNDARY` va `MAXIMUM` bo'lmasa
     `TEST_GROUP_MISSING` (`READINESS_ENFORCE` ortida, ADR 0050).
  3. **Judge siyosati** — `STRESS` testlari baholashga **kirmaydi**
     (`build_standalone_job`). Ular kalibrlash dalili: baholansa har bir
     oddiy yechim TLE bo'lardi.
- `is_sample` va `group=SAMPLE` **mosligi majburlanadi** (serializer):
  `is_sample=True` guruhni o'zi `sample` qiladi; `group=sample` ni
  `is_sample=False` bilan qo'yish rad etiladi. Ikki manba ikki xil
  gapirmasin.
- **Backfill** (0027) faqat statik shartlar bilan: `hack` → `adversarial`
  (**birinchi** tekshiriladi — hack testi hech qachon `sample` bo'lmasin),
  `is_sample` → `sample`, qolgani → `unclassified`. Tasodifiy deb yozish
  yolg'on bo'lardi.
- `UNCLASSIFIED` majburiy guruhni **qoplamaydi**: ko'chirish holati
  darvozani jimgina ochib qo'ymasin.

### Yon topilma: yuklash chegarasi

Yuklash maydonlari cheklovsiz `CharField` edi. O'lchandi: Django'ning
`DATA_UPLOAD_MAX_MEMORY_SIZE` standarti (2.5 MB) `storage.MAX_TEST_BYTES`
dan **past**, ya'ni haqiqiy chegara shu edi va katta qonuniy test umuman
yuklanmasdi (`RequestDataTooBig`). Endi Django 16 MiB (orqa qo'riqchi),
biznes chegara esa `MAX_TEST_BYTES` = 8 MiB — foydalanuvchi sababni aniq
ko'radi.

## 6. Qaytarilishi

`group` maydoni qo'shimcha (default `unclassified`); uni ishlatmaydigan
kod o'zgarmaydi. Migratsiya `0026` + `0027`, ikkisi ham additive.

## 7. Tasdiq

- `apps/api/tests/test_test_groups.py` — 17 test (siyosat, yuklash,
  judge tanlovi, nashr darvozasi).
- Backfill haqiqiy ma'lumotda o'lchandi: 0026 da to'xtatib, 4 xil test
  yaratib, 0027 qo'llandi → `adversarial=2 sample=1 unclassified=1`,
  kutilganidek.
