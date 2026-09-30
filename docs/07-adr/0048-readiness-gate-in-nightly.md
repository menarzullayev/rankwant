# ADR 0048 — Readiness darvozasi Nightly'da yurgiziladi

**STATUS:** accepted
**Sana:** 2026-09-30
**Tasdiqlagan:** Saidakbar (owner)
**Manba:** Sessiya auditi (`tools/check_negative.py` api guruhi) · ADR-0037
**Ta'sir doirasi:** CI (`.github/workflows/nightly.yml`, `tools/check_negative.py`)
**Dalil:** `tools/check_negative.py` (8846–8862) · `.github/workflows/ci.yml` (web job `timeout-minutes: 3`) · `.github/workflows/nightly.yml` (`load`/`latency` `timeout-minutes: 15`) · `tools/ci.Dockerfile` · o'lchov 2026-09-30

## 1. Muammo

`tools/check_negative.py` ning **api guruhi** (WP1 · D8 · D8-F · ADR-0037 — S1/S2 o'tish qo'riqchilari va graded-contest darvozasi) per-PR CI'da **hech qachon yurgizilmaydi**.

Sabab — guruh pytest'ni `rankwant-api-dev:audit` image'i ICHIDA yuritadi:

- `ci.yml` dagi `web` job byudjeti **3 daqiqa**; unda `docker build` yo'q.
- Hech bir CI workflow image qurmaydi. `tools/ci-local.sh` uni `rankwant-api-dev:<lock-hash>` tegi bilan quradi, guruh esa `:audit` tegini kutadi.
- Guruhning case fayllari repo'ga commit qilinishi bilan precondition skip'dan **qattiq qizilga** o'tadi — ya'ni fayllar kira olmaydi.

Natija: "yashil CI" shu guruh haqida **hech narsa demaydi**, guruh esa amalda dekorativ.

## 2. Variantlar

1. **Nightly'da** — Nightly allaqachon api image'ini quradi va 15–20 daqiqa byudjetli.
2. **Per-PR job + GHCR prebuilt image** — image lock/base o'zgarganda registry'ga chiqadi, PR job uni tortadi.
3. **Per-PR job, har safar qurish** — Django image har PR'da quriladi.
4. **CI'dan chiqarish** — faqat egasi qo'lda yurgizadi.

## 3. Tanlov

**Variant 1** — guruh Nightly'da, alohida `readiness` job'ida yurgiziladi.

## 4. Sabab

- Nightly'da image **allaqachon quriladi**, byudjet 15–20 daqiqa — ya'ni qo'shimcha infratuzilma kerak emas.
- Repo falsafasi o'lchangan: per-PR tez (2–3 daqiqa), og'ir ish Nightly'da. Variant 3 shu falsafaga zid.
- GHCR bugungacha **ishlatilmagan** (`packages: write` bor, lekin image registry yo'q) — Variant 2 yangi boshqaruv yukini kiritadi.
- Tayyor naqsh bor: `visual` va `csp_nonce` guruhlari **aynan shunday** ishlaydi — to'liq to'plamda ochiq skip, `--group` bilan alohida yuritiladi.
- O'z job'i ataylab, `latency` bilan bir mantiq: boshqa guruhga bog'langan darvoza aloqasiz sababdan qizil bo'lardi.

## 5. Oqibatlar

- `.github/workflows/nightly.yml` da yangi `readiness` job: api image → dev image → `--group neg_refsolution_gate`.
- `tools/check_negative.py` da **uch joy**:
  1. **Parallel yo'l** (CI, `NEGATIVE_JOBS=4`): guruh fan-out ro'yxatidan chiqariladi — `visual` va `csp_nonce` bilan bir qatorda, ochiq skip xabari bilan.
  2. **Serial yo'l**: `--group neg_refsolution_gate` berilmasa — ochiq skip; berilsa — old shart tekshiriladi va bajarilmasa **ochiq qizil**.
  3. **CASES tsikli**: skip bo'lganda guruhning case'lari ham yuritilmaydi. Bu shart: aks holda skip xabari chiqib, case'lar baribir yurib, o'lik yashil yoki soxta qizil berardi (lokal o'lchandi 2026-09-30).
- Case fayllari commit qilinmagan bo'lsa — ochiq skip, qizil emas (mavjud `_UNCOMMITTED_GROUP_FILES` mantig'i saqlanadi).
- **Guruh hozircha dormant**: case fayllari repo'da yo'q va 5 test **implementatsiya qilinmagan** darvozalarni tavsiflaydi (quyida).
- Per-PR web job'ning xatti-harakati **o'zgarmaydi** — u baribir guruhni yurgizmasdi.

### O'lchangan holat (2026-09-30)

`apps/api/tests/test_problem_readiness.py` image ichida yurgizilganda **5 ta test yiqiladi**:

```
FAILED TestStateMachine::test_hidden_test_required_for_the_step      (S1)
FAILED TestStateMachine::test_checker_type_required                  (S2)
FAILED TestStateMachine::test_draft_to_validated_jump_rejected       (S3)
FAILED TestGradedGate::test_graded_requires_validated                (R8)
FAILED TestGradedGate::test_legacy_unverified_public_but_not_in_contest (R9 · D8-F)
```

`Problem.Readiness` holat mashinasi (9 holat) **mavjud** (`apps/api/problems/models.py:214`), lekin **o'tish qo'riqchilari va graded-contest darvozasi yo'q**. Dalil: `legacy_unverified` masalani graded contest'ga qo'shish `400` o'rniga **`200`** qaytardi.

Ya'ni bu job darvozani *yurgizadigan joy*; darvozaning *o'zi* hali yozilmagan. Bu ADR faqat joyni hal qiladi — R1–R10 joriy etilishi alohida qaror.

## 6. Qaytarilishi

Job va skip o'zgarishi bitta commit'da qaytariladi. Runtime kodga ta'sir yo'q — o'zgarish faqat CI va tekshiruv skriptida.

## 7. Tasdiq

- `tools/check_negative.py --group neg_refsolution_gate` image bilan yurgizildi (mahalliy, 2026-09-30).
- To'liq to'plamda api guruhi **skip** bo'ladi va boshqa guruhlar o'zgarmaydi.
- `python tools/check_decisions.py` va `python tools/check_docs.py` yashil qoladi.
