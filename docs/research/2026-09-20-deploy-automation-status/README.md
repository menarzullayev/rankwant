# Deploy avtomatikasi — holat hisoboti

> **Arxiv yozuvi.** Repoga 2026-10-04 da ko'chirildi; matn yozilgan kunidagi holatni aks ettiradi. Keyin o'zgargan: deploy poll'i 1 daqiqa, Security run o'chirilgan.

**Sana:** 2026-09-20 · **Repo:** `rankwant` · **Holat:** ishlayapti va o'lchandi

---

## 1. Qisqa javob

**Avtomatlashtirish allaqachon qurilgan edi va ishlayapti** — uni qaytadan
qurish kerak emas. Mexanizm: `tools/auto_deploy.sh` + Windows vazifasi
`RankWant Auto Deploy` (har 5 daqiqada), deploy `<deploy worktree>`
worktree'sidan yuriladi.

Bu sessiyada:

1. **PR #191 merge qilindi** → `ea47cc4`.
2. Watcher uni **qo'lda aralashuvsiz** deploy qildi va **tasdiqlandi**.
3. Bitta **haqiqiy nuqson** topildi va tuzatildi (**PR #193** → `5d29bd3`).

---

## 2. Vaqt chizig'i (haqiqiy o'lchov, UTC)

| Vaqt | Voqea |
|---|---|
| 18:03:57 | PR #191 squash-merge → `main` = `ea47cc4` |
| 18:04:00 | CI + Security avtomatik boshlandi |
| 18:04:40 | Security ✅ |
| 18:05:11 | CI ✅ |
| 18:05:12 | Watcher tick: `jonli 3518bbd ≠ main ea47cc4` → deploy boshlandi |
| 18:06:23 | **Deploy tugadi** — `api`/`worker`/`beat` = `ea47cc4` |
| 18:09:36 | Parallel agent PR #192 merge → `main` = `50eec1f` |
| 18:10:06 | Tick → darvoza yopiq (CI yugurmoqda) → **`deploy YIQILDI` + 1800 s to'siq** ← nuqson |
| 18:20:13 | (tuzatishdan keyin) tick → deploy `5d29bd3` |
| 18:22:05 | **Deploy tugadi**, to'siq yo'q |
| 18:25:04 | Tick: `obrazga tushmaydi — bake yo'q` (ish yo'q, jim) |

**Merge → jonli sayt: 2 daqiqa 26 soniya, qo'lda tegmasdan.**

Tasdiq (taxmin emas, o'lchov):

| Tekshiruv | Natija |
|---|---|
| `api` / `worker` / `beat` SHA | `ea47cc4` ✅ |
| `web` SHA | `5d29bd3` ✅ (PR #192 ning o'zgarishi) |
| `judge` SHA | `3518bbd` — ataylab qayta qurilmadi (manbasi o'zgarmagan) |
| Yangi buyruq konteynerda | `seed_contest_scale.py` **PRESENT** + `manage.py` ro'yxatida |
| `bash tools/check_deploy.sh` | «Hamma konteyner joriy kodda» |
| `https://rankwant.uz/` | `200` (0.30 s) |

---

## 3. Trigger shartlari — qachon deploy boshlanadi

Hammasi **bir vaqtda** bajarilishi shart; biri bajarilmasa deploy boshlanmaydi.

| # | Shart | Qayerda tekshiriladi |
|---|---|---|
| 1 | qulf bo'sh (boshqa deploy ketmayapti) | `<git common dir>/rankwant-deploy.lock` |
| 2 | `DEPLOY_FREEZE` bo'sh yoki `0` | env |
| 3 | `origin/main` olindi — tarmoq ishlaydi | `git fetch origin main` |
| 4 | deploy worktree toza (commit qilinmagan tahrir yo'q) | `git status --untracked-files=no` |
| 5 | **bake kerak** — `deploy_scope.py --from-live` bo'sh emas | docs/tools commit'i obraz talab qilmaydi |
| 6 | **jonli kod `main` dan orqada** | `all_up` + `check_deploy.sh` |
| 7 | shu SHA uchun yaqinda urinilmagan (1800 s) | `~/.rankwant-auto-deploy-state` |
| 8 | **darvoza ochiq** — `main` CI + Security yashil | `tools/check_deploy_gate.py` |

⚠️ 6-shart **jonli holatdan** aniqlanadi, worktree `HEAD` dan emas: merge bo'lib
deploy yiqilgan bo'lsa `HEAD` allaqachon `main` da bo'ladi va drift abadiy
qolardi (2026-09-19 da sayt `main` dan 4 commit orqada edi).

---

## 4. Xato bo'lganda — o'lchangan xatti-harakat

| Holat | Xatti | Qayta urinish to'sig'i |
|---|---|---|
| `git fetch` yiqildi (tarmoq) | log + `exit 0` | yo'q — keyingi yurish |
| qulf band | JIM `exit 0` | yo'q |
| `DEPLOY_FREEZE` qo'yilgan | log + `exit 0` | yo'q |
| bake kerak emas (docs/tools) | log + `exit 0` | yo'q |
| jonli = `main` (ish yo'q) | JIM `exit 0` | yo'q |
| **darvoza yopiq** (CI yugurmoqda / qizil / o'lchanmadi) | log (sababi bilan) + `exit 0` | **yo'q** |
| worktree iflos · env-fayl yo'q · `ff-only` yiqildi | `die` (exit 1) | yo'q — har 5 daqiqada takrorlanadi |
| `deploy.sh` yiqildi | `deploy YIQILDI` | **1800 s (30 daqiqa)** |

Boshqarish:

```bash
bash tools/auto_deploy.sh --status   # holat: HEAD, main, jonli SHA, env-fayl
bash tools/auto_deploy.sh --dry-run  # qarorni ko'rsatadi, hech narsa qilmaydi
bash tools/kick_auto_deploy.sh       # merge'dan keyin 5 daqiqa kutmaslik
rm -f ~/.rankwant-auto-deploy-state  # to'siqni darhol olib tashlash
DEPLOY_FREEZE=1 bash tools/deploy.sh --yes   # favqulodda «to'xta»
```

---

## 5. Topilgan nuqson va tuzatish (PR #193)

**Nuqson:** yopiq darvoza **nosozlik** deb hisoblanardi. Watcher urinishni
`deploy.sh` dan **oldin** yozadi, ya'ni `main` CI hali yugurib turganda kelgan
yurish SHAni 30 daqiqalik to'siqqa qo'yardi va bo'lmagan nosozlikni logga
yozardi. CI `main` da ~70 s yuradi, yurish har 5 daqiqada ⇒ **har to'rtinchi
merge** shu yo'lga tushardi.

**O'lchandi** (haqiqiy ishlab chiqarishda, 18:10:06Z va 18:15:13Z):

```
[2026-09-20T18:10:06Z] deploy YIQILDI (target 50eec1f) — 1800s to'siq qo'yildi
[2026-09-20T18:15:13Z] shu SHA uchun yaqinda urinilgan (5 daqiqa oldin) — to'siq 1800s
```

**Tuzatish:** watcher darvozani urinishdan **oldin** tekshiradi; yopiq bo'lsa
sababini logga yozib `exit 0` qiladi (nosozlik emas ⇒ to'siq ham yo'q).
`tools/deploy.sh` o'z darvozasini **baribir** yurgizadi — u yagona haqiqat
manbai; watcher'niki faqat «hozir urinishga arziydimi?» savoli.

**A/B tasdiqi** — bir xil kirish (yopiq darvoza), faqat versiya farq qildi:

| | yangi `5d29bd3` | eski `50eec1f` |
|---|---|---|
| exit kodi | **0** | **1** |
| log | `darvoza yopiq (exit 2) — to'siq YO'Q` | `deploy YIQILDI — 1800s to'siq` |
| to'siq fayli | **yozilmadi** ✅ | **yozildi** ❌ (30 daqiqa blok) |

Qo'shimcha: `check_negative.py --serial decisions` → **128/128 ✓**; yangi test
neytrallanganda **aynan bitta** test yiqildi (ya'ni test bo'sh emas).

---

## 6. Ochiq qaror

**Deploy bosqichi — to'liq avtomatik.** **Merge bosqichi — hamon qo'lda:**
PR'ni agent yoki ega merge qiladi, keyin watcher o'zi jonli chiqaradi.
GitHub'da `allow_auto_merge` **yoqilmagan**, `main` **himoyalanmagan**
(`push_guard.py` faqat lokal qulf).

To'liq avtomatik merge uchun bitta qaror kerak edi (o'sha kuni ochiq qolgan).
