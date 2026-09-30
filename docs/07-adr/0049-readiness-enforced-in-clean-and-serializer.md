# ADR 0049 — Readiness darvozalari `clean()` va serializer/view qatlamida

**STATUS:** accepted
**Sana:** 2026-09-30
**Tasdiqlagan:** Saidakbar (owner)
**Manba:** ADR-0037 (content integrity gate) · ADR 0048 (readiness guruhi Nightly'da)
**Ta'sir doirasi:** `apps/api/problems/models.py`, `apps/api/contests/staff_serializers.py`, `apps/api/contests/staff_views.py`
**Dalil:** `apps/api/problems/readiness.py` (359 qator, hech bir production yo'li chaqirmaydi) · o'lchov 2026-09-30

## 1. Muammo

`apps/api/problems/readiness.py` **to'liq yozilgan**: S1 (`has_hidden_test`), S2 (`checker_ready`), S3/S4 (`evaluate_readiness`), R10 (`assert_transition`), D8-F (`graded_gate_error`), `GRADED_READY`.

Lekin uni **hech bir production yo'li chaqirmaydi** — faqat ikkita management command import qiladi (`backfill_readiness`, `verify_readiness`). Natijada:

- `Problem.clean()` faqat `difficulty` ni tekshiradi — o'tish qo'riqchisi yo'q.
- `contests/staff_serializers.py` va `contests/staff_views.py` da `readiness` so'zi umuman yo'q — graded darvoza yo'q.

**Dalil:** `legacy_unverified` masalani graded contest'ga qo'shish `400` o'rniga **`200`** qaytardi; `draft -> validated` sakrashi `full_clean()` da rad etilmadi.

Ya'ni `readiness.py` — **o'lik kutubxona**: qoidalar yozilgan, majburlanmagan.

## 2. Variantlar

1. **`clean()` + serializer/view** — `Problem.clean()` da S1/S2 va o'tish qo'riqchilari; graded sharti ikki qavatda (serializer + view).
2. **`save()` da majburlash** — har qanday yozuv ushlanadi.
3. **DB cheklovi/trigger** — holat mashinasi SQL darajasida.
4. **Yagona xizmat qatlami** — barcha holat o'zgarishlari `readiness.py` orqali.

## 3. Tanlov

**Variant 1.**

## 4. Sabab

- **Testlar shuni talab qiladi**: qabul testlari `draft.full_clean()` ni chaqirib `ValidationError` kutadi (S1, S2, R10) — ya'ni `clean()` qatlami majburiy, tanlov emas.
- **Django-an'anaviy**: model validatsiyasi `clean()` da, biznes qoidalari serializer/view da.
- **Variant 2 rad etildi**: `backfill_readiness` va `verify_readiness` holatni **qonuniy** yozadi; `save()` darvozasi ularni bloklashi mumkin. Ustiga-ustak `bulk_create`/`queryset.update()` `save()` ni baribir chetlab o'tadi — himoya to'liq bo'lmaydi, lekin murakkablik to'liq qo'shiladi.
- **Variant 3 rad etildi**: S3/S4 judge harness'ini talab qiladi — SQL'da ifodalab bo'lmaydi.
- **Variant 4 rad etildi**: mavjud chaqiruvchilarni ko'chirish va yangi konventsiya talab qiladi; hozirgi hajm uchun ortiqcha abstraksiya.
- **Ikki qavat graded sharti** — ataylab: `check_negative.py` ning mutatsiya isboti ikkala qavatni ham olib tashlashi shart, aks holda bitta qavat o'lik ekanini ko'rsatib bo'lmaydi (o'lchandi).

## 5. Oqibatlar

- `Problem.clean()`: avval `assert_transition(oldingi, yangi)`, keyin `requirement_error(...)`. **Tartib muhim** — aks holda `draft -> validated` sakrashi "S3" xatosini berardi, test esa "is not allowed" kutadi.
- Oldingi holat **DB'dan** o'qiladi: `full_clean()` xotiradagi nishonni ko'radi, qator qayerdaligini emas.
- `StaffContestProblemListSerializer.validate_problems()` va `staff_views.py` ning `problems` amali — ikkalasi ham `row["problem"].readiness != GRADED_READY` shartini yozadi.
- View'dagi tekshiruv **`transaction.atomic()` dan OLDIN** turadi: aks holda rad etilganda eski qatorlar allaqachon o'chirilgan bo'lardi.
- **Chetlab o'tish yo'li qoladi**: `save()`, `bulk_create`, `queryset.update()` `clean()` ni chaqirmaydi. Bu qabul qilindi — hozir `full_clean()` ni faqat testlar chaqiradi, ya'ni amaldagi sirt tor. Sirt kengaysa, alohida qaror bilan kuchaytiriladi.
- `test_validated_problem_is_accepted` `save()` bilan to'g'ridan-to'g'ri `validated` ga o'tadi va ishlaydi — ya'ni bu yo'l ataylab ochiq qoladi.
- **Mavjud testlar yangilandi.** `tests/test_staff_contests.py` ning 200 kutadigan ikki testi (`test_put_toliq_almashtiradi`, `test_post_va_obyekt_korinish`) endi `_gradable()` bilan masalani `validated` qiladi. Sabab: umumiy fixture'lar ataylab boshqa holatlarda (`problem` — `legacy_unverified`, `hard_problem` — `draft`), ya'ni ularni contest'ga qo'shish yangi qoida bo'yicha **to'g'ri rad etiladi**. 400 kutadigan testlar (`test_takror_harf_rad`, `test_takror_masala_rad`) tegilmadi — ularning sharti darvozadan oldin ishlaydi.

### Tekshirilmagan qism

`tests/test_staff_contests.py` ni **mahalliy yakka yurgizib bo'lmadi**: umumiy fixture'lardagi `code` (`max(code)+1`) bilan `ProblemCodeSequence` poyga qiladi va 4 urinishdan keyin `IntegrityError` beradi. Bu **avvaldan mavjud** nuqson — o'zgarishlar `git stash` bilan olib tashlanganda ham aynan yiqiladi, va to'liq to'plamda ham uchraydi (`test_problems`, `test_judging`, `test_profile_stats`, `test_staff_duels` ham). CI'da 1558 test o'tadi, ya'ni u yerda bu holat yuzaga kelmaydi.

Shu sababli darvozaning **xatti-harakati** alohida probe bilan o'lchandi (4/4): `draft` → 400, `legacy_unverified` → 400, `validated` → 200, va rad etish eski qatorlarni saqlaydi. Yakuniy tasdiq — Nightly'ning `API coverage` job'i.

## 6. Qaytarilishi

Uch fayldagi o'zgarish bir commit'da qaytariladi. Sxema o'zgarmaydi, migratsiya yo'q.

## 6a. ⚠️ Joriy etishdan OLDIN o'qilishi shart

**Bu o'zgarish production'da hozircha ishlatilmasligi kerak.** Sabab — o'lchandi
2026-09-30, ishlab turgan baza:

| readiness | masalalar |
| --- | --- |
| `legacy_unverified` | 1 225 |
| `draft` | 867 |
| `needs_review` | 4 |
| **`validated`** | **0** |

Ya'ni `GRADED_READY` ga mos keladigan masala **bitta ham yo'q**, demak darvoza
**har qanday** contest'ga masala qo'shishni rad etadi (`400`). Kod `main` da,
lekin **deploy qilinmagan** — va kontent `validated` ga ko'chirilmaguncha
deploy qilinmasligi kerak.

`validated` ga chiqish yo'li bor: `manage.py verify_readiness` (S3/S4 judge
harness'i bilan) va `manage.py backfill_readiness` (audit). Lekin 2 096 masalani
`validated` ga ko'chirish — **alohida ish**, va u kontent tayyorligi bilan
bog'liq (yashirin testlar, checker turlari, etalon yechimlar). Tartib:

1. Kontentni `validated` ga ko'chirish (yoki darvozani bosqichma-bosqich
   joriy etish: avval faqat ogohlantirish, keyin rad etish).
2. Shundan keyingina deploy.

Shu sababli bu ADR **hujjat sifatida** yozildi: kod tayyor, joriy etish sharti
bajarilmagan.

## 7. Tasdiq

- `apps/api/tests/test_problem_readiness.py` to'liq yashil (11 test).
- `tools/check_negative.py --group neg_refsolution_gate` yashil — mutatsiya isboti ikkala qavatni ham ushlaydi.
- `tools/check_architecture.py`, `check_decisions.py`, `check_docs.py` — o'zgarishsiz.
