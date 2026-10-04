# Qaror #1 — Deploy poll'i: 5 daqiqa → 1 daqiqa

> **Arxiv yozuvi.** Repoga 2026-10-04 da ko'chirildi; matn yozilgan kunidagi holatni aks ettiradi. Qarorning amaldagi matni `CLAUDE.md` jadvalida.

**Sana:** 2026-09-21
**PR:** [#202](https://github.com/menarzullayev/rankwant/pull/202) · **Merge:** `1eba7aa` (squash)
**Holat:** ✅ **to'liq sikl bajarildi** — commit → push → PR → CI → merge → deploy → tekshiruv

---

## 1. Savol va javob

> «30 sekund kutmasdan darhol deploy tezlik bilan qilinishi kerak.
> Menimcha buni qo'lda bajargan osonroqmi? Yoki GitHub'da qilingani
> yaxshimi avtomatik?»

| Yo'l | Kechikish | Holat |
|---|---|---|
| **Qo'lda** — `bash tools/kick_auto_deploy.sh` | **0 soniya** | ✅ bor, ishlaydi |
| **Avtomatik poll** (yangi) | ≤ **1 daqiqa** | ✅ shu qaror bilan |
| GitHub Actions orqali avtomatik | — | ❌ **mumkin emas** (quyida) |

**Javob:** ikkalasi **birga** ishlatiladi. Merge oxirida qo'lda `kick` qilinsa
kutish **nol**; poll esa zaxira tarmoq — agar `kick` qilinmasa, 1 daqiqada
o'zi boshlanadi. Ya'ni «qo'lda **yoki** GitHub» emas, «qo'lda **+** host poll».

**Nega GitHub emas:** 2026-09-19 da o'lchandi — runner konteyneri jonli
`.env.public` ni ko'rmaydi (u `/work` volume'ida, host repo ulanmagan), ya'ni
29 kalitdan faqat 4 tasi qoladi va email zanjiri, Turnstile, OAuth, Cloudflare
token **jimgina yo'qoladi**; runner'da `gh` ham yo'q, shuning uchun
`check_deploy_gate.py` doim `exit 2` beradi. GitHub — audit izi uchun yaxshi,
lekin bu mashinada **deploy manbai bo'la olmaydi** (alohida qaror).

## 2. Asosiy topilma — 30 soniya mumkin emas

Task Scheduler takrorlash oralig'ining eng kichigi — **1 daqiqa**.
`PT30S` ni XML sxemasi rad etadi (o'lchandi; unified va klassik
engine'ning **ikkalasida ham bir xil**):

```text
The task XML contains a value which is incorrectly formatted or out of
range.(31,27):Interval:PT30S
```

`UseUnifiedSchedulingEngine=false` ham yordam bermaydi — xizmat uni
`true` ga normallashtiradi. ⇒ **Eng yaxshi erishiladigan qiymat — `PT1M`.**

## 3. Nima o'zgardi

**Host (haqiqiy xatti-harakat):** `RankWant Auto Deploy` vazifasi
`Interval: PT5M → PT1M`. Qolgani **saqlandi**: `Duration=P1D`,
`StopAtDurationEnd=true`, `MultipleInstances=IgnoreNew`,
`ExecutionTimeLimit=PT1H`, action, `Enabled=true`.

**Repo (PR #202, 5 fayl):**

| Fayl | O'zgarish |
|---|---|
| `tools/auto_deploy.sh` | yangi «Poll oralig'i» bloki + 5 ta eskirgan izoh |
| `docs/10-operations/deploy-runbook.md` | interval havolalari + o'lchangan dalil + `Register-ScheduledTask` buyrug'i |
| `tools/check_decisions.py` | 2 izoh satri |
| `tools/check_negative.py` | 3 docstring |
| `CLAUDE.md` | eski qator + yangi 2026-09-21 qaror qatori |

⚠️ **Vazifa faqat host'da** — repo'da uni yaratuvchi skript **yo'q**. Shuning
uchun aniq buyruq runbook'ga yozildi; aks holda qayta o'rnatishda interval
jimgina 5 daqiqaga qaytardi. Zaxira XML'lar: `wt/deploy/.handoff/`.

## 4. Tekshiruv (o'lchandi)

| Tekshiruv | Natija |
|---|---|
| `check_decisions.py` | **51/51** ✓ |
| `check_docs.py` | 144 fayl, **0 muammo** ✓ |
| `check_negative.py --serial decisions` | **134/134** ✓ |
| `bash -n` + `py_compile` | toza ✓ |
| Pre-push hook (`push_guard`) | o'tdi ✓ |
| **PR #202 CI** | Path filter 7 s · Docs 9 s · Web 35 s · API/Judge skip — **hammasi pass** ✓ |
| **`main` CI** (run `35536414938`, `1eba7aa`) | **success** ✓ |
| Vazifa: interval / multi / limit | `PT1M` / `IgnoreNew` / `PT1H` ✓ |
| Vazifa: `LastTaskResult` / `missedRuns` | `0` / `0` ✓ |
| Deploy daraxti HEAD = `origin/main` | `1eba7aa` ✓ |
| Sayt: `rankwant.uz/` | **HTTP 200** (0.64 s) ✓ |
| Sayt: `/api/v1/health/` | `{"status":"ok","checks":{"database":"ok","redis":"ok"}}` ✓ |

## 5. Eng muhim dalil — o'zgarish ishlayapti

| Narsa | Vaqt |
|---|---|
| Merge | `20:42:36Z` |
| **Birinchi tick uni ko'rdi** | `20:43:03Z` → **27 soniya** |
| Eski 5 daqiqalik jadvalda bo'lardi | `20:45:05Z` → 149 soniya |

Ya'ni merge'dan deploy'gacha **5.5× tez**. Ustma-ust tushish yo'q
(`IgnoreNew`); tick narxi ~2.0–2.3 s (asosan `git fetch`) ⇒ ish yuki ~3.5%.

**Deploy haqida halol izoh:** `deploy_scope.py 56ede88..7516118` → **bo'sh**,
ya'ni obraz qayta qurilmadi. Bu **to'g'ri**, nosozlik emas: commit faqat
`docs/`/`tools/`/`CLAUDE.md` ga tegdi, haqiqiy ishlab chiqarish effekti
(vazifa intervali) esa host darajasida va merge'dan **oldin** qo'llangan.
Jonli konteynerlar ataylab o'zgarmadi (`web` = `f45700d`, `api` = `7584881`).

## 6. Narxi (halol)

Log o'sishi: sog'lom tick aynan **1 qator** yozadi ⇒ 5 daqiqada ~288
qator/kun, 1 daqiqada **~1 440 qator/kun**. O'lchandi: qator ~72 bayt ⇒
**~100 KB/kun (~37 MB/yil)**. `.handoff/auto-deploy.log` **aylantirilmaydi**
(hozir 2.04 MB). ⚠️ `check_decisions.py` o'sha log satrini literal qilib
qadab qo'ygan, ya'ni uni jimgina qilish ham alohida qaror.

## 7. Ochiq bandlar

1. **Log rotatsiyasi yo'q** — shu qaror kiritgan yagona narx.
2. **Interval qo'riqlanmaydi** — u host'da, CI uni ko'rmaydi (runbook'da qo'lda
   tekshiruv bor).
3. **Sub-daqiqa poll** — faqat doimiy aylanadigan wrapper bilan mumkin
   (yangi nosozlik rejimi) — alohida qaror.
4. **GitHub-orchestrated deploy** (audit izi) — 1-bo'limdagi o'lchovlarga ko'ra
   hozircha bloklangan.

## 8. Keyingi qaror nomzodlari (muhimlik tartibida)

1. **Log rotatsiyasi / jimgina tick** — eng kichigi, shu qaror kiritgan narxni
   yopadi.
2. **Sub-daqiqa deploy** (doimiy watcher) — 27 s → ~30 s barqaror.
3. **GitHub-orchestrated deploy** — bloklangan, katta ish.
