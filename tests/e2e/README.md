# tests/e2e — Playwright

test-strategy.md § 4. Ishlayotgan stack talab qiladi.

```bash
npm install && npm run install-browsers

# Stack ko'tarilgan bo'lishi kerak
E2E_BASE_URL=http://localhost:3000 \
E2E_API_BASE=http://localhost:8000/api/v1 \
npm test
```

## Nima qamrab olingan

| Spec | Oqim |
| ---- | ---- |
| `browse.spec.ts` | Ochiq sahifalar, SSR mazmuni, reyting formulalari ochiqligi |
| `submit-flow.spec.ts` | Ro'yxat → login → submit; PAT scope; IDOR |
| `contest.spec.ts` | Contest sahifasi va standings |
| `settings-info.spec.ts` | Sozlamalar: telefon, sinf, futbolka o'lchami, ism-familiya saqlanadi (ADR-0024); sayt va API bitta originda bo'lsagina |
| `visual/visual.spec.ts` | **Vizual regressiya** — piksel solishtirish (RW-ARCH-016) |

## Proyektlar

`testDir` — `./`, ya'ni ikkala papka bir config ostida, lekin
**proyektlar bilan ajratilgan**:

| Proyekt | Nima yuritadi | Brauzerlar |
| ------- | ------------- | ---------- |
| `e2e`, `firefox`, `webkit`, `mobile` | `specs/` — funksional testlar | 4 ta |
| `visual` | `visual/` — skrinshot solishtirish | faqat chromium |

```bash
npx playwright test                      # hammasi
npx playwright test --project=e2e        # faqat funksional (chromium)
npx playwright test --project=visual     # faqat vizual
```

## Vizual regressiya

⚠️ **Baseline'lar CI muhitida (Linux konteyneri) olinadi — CI yagona
haqiqat.** Sabab o'lchandi (2026-09-24): Linux konteynerida 6/6 sahifa
**3–4%** farq berdi (bizning chegaramiz — 1%). Diff rasmda butun matn
qizil, ya'ni sabab shrink **antialiasing/hinting**, layout emas.
Konteynerda faqat 50 ta shrift bor (`FreeSans`, `DejaVu`…); web esa
`Inter`/sistema shriftlarini ishlatadi va ular Linux'da yo'q.

Shu sababdan lokal **Windows'da vizual suite qizil beradi — bu normal**.
Windows'da baseline YARATILMAYDI va yangilanmaydi.

Baseline'larni yangilash (CI muhitida):

```bash
MSYS_NO_PATHCONV=1 docker run --rm --network rankwant_default \
  -v "<repo>/tests/e2e:/e2e" -w /e2e \
  -e E2E_BASE_URL=http://host.docker.internal:3400 -e CI=1 \
  mcr.microsoft.com/playwright:v1.63.0-noble \
  npx playwright test --project=visual --update-snapshots
# keyin yangi PNG'larni PR ga qo'shing
```

⚠️ Yuqoridagi buyruqda `E2E_BASE_URL` **majburiy**. Usiz har sahifa
`ERR_CONNECTION_REFUSED` bo'ladi, Playwright yangi skrinshot olmaydi va
`--update-snapshots` hech narsa yozmaydi — ya'ni "o'zgarmadi" degan
**yolg'on** natija chiqadi.

### ⚠️ O'lik darvoza (o'lchandi 2026-09-24) — `check-baseline-drift.sh`

`tests/e2e/scripts/check-baseline-drift.sh` baseline'lar shu image'da
olinganini tekshiradi (xesh oldin/keyin). Uning **birinchi versiyasi
o'lik edi**: `E2E_BASE_URL`siz yurgizilardi, sahifalar yuklanmasdi,
xesh o'zgarmasdi va skript «Baseline'lar shu image bilan mos ✓» deb
**yashil** berardi — holbuki haqiqiy suite 3/7 qizil edi.

Endi ikki qulf bor, ikkisi ham salbiy test bilan tasdiqlangan:

1. **Stek javob berishi shart.** `curl` `$E2E_BASE_URL` ga yetmasa —
   `exit 2` (o'lchanmadi), `0` emas.
2. **Update yurishi qizil bo'lmasligi shart.** Xesh o'zgarmagan bo'lsa ham,
   logda `N failed` bo'lsa — `exit 2`.

Chiqish kodlari: `0` mos · `1` drift (boshqa OS'da olingan) · `2` o'lchab
bo'lmadi. **`2` hech qachon yashil hisoblanmaydi.**

⚠️ CI imagei o'zgarsa (`tools/ci_playwright.sh` dagi
`PLAYWRIGHT_SOURCE`), baseline'lar o'sha image'da QAYTA olinishi shart.

Baseline'lar `visual/visual.spec.ts-snapshots/*.png` da **commit qilinadi** —
shu sababli ular git'da turadi, `test-results/` esa yo'q.

| Nima | Nega |
| ---- | ---- |
| Faqat chromium | Brauzerlar shrift/soyani boshqacha chizadi — bitta baseline ularga yaramaydi |
| `maxDiffPixelRatio: 0.01` | 0 qilinsa har antialiasing shovqin beradi; ko'tarilsa (masalan 5%) haqiqiy regressiya yutib yuboriladi |
| `animations: "disabled"` | Yarim holatdagi animatsiya skrinshotni beqaror qiladi |
| `snapshotPathTemplate` (platformasiz nom) | Sukut `-win32`/`-linux` qo'shadi — bu ko'p-muhitli yurishni jimgina buzadi |
| Username **bosh sahifadan** olinadi | Ilgari `/users/ustoz` qattiq yozilgan edi (`seed_demo`); jonli bazada u yo'q → 404 baseline bo'lib qoldi. Endi bosh sahifadagi reyting blokidagi birinchi `/users/<name>` havolasi olinadi va 404 bo'lsa test **yiqiladi** |

⚠️ **API'ga murojaat qilinmaydi.** Ilgari username `E2E_API_BASE` dan
so'ralardi va CI'da ikki marta jimgina SKIP bo'ldi: (1) web `baseURL`
bilan 404 (`next.config` da `rewrites` yo'q), (2) konteynerdan
`http://rankwant-api-1:8000` → **400** (`ALLOWED_HOSTS` konteyner nomini
bilmaydi). Endi manba — sahifaning o'zi.

⚠️ **`/rating` sahifasi yaramaydi** — u klient tomonda renderlanadi,
SSR HTML'da `/users/` havolasi yo'q (o'lchandi: 0 ta).

⚠️ **Darvoza o'lik emasligi isbotlangan bo'lishi kerak.** "Piksel
solishtirish o'tdi" faqat mutatsiya KO'RINADIGAN bo'lsa dalil: `--rw-rank-grey`
bilan suite yashil qoldi (token sahifalarda ko'rinmasdi). Isbot
`check_negative.py --group visual` da (`--rw-ground` mutanti).

⚠️ Yangi sahifa qo'shilsa, birinchi yurish baseline yozadi va **yiqiladi**.
Bu ataylab: hech kim ko'rib chiqmagan skrinshot jimgina "haqiqat" bo'lib
qolmasligi kerak.

## Nega PR da ishlamaydi

Judge konteyneri `--privileged` talab qiladi va uni har PR da ko'tarish
qimmat. Bu testlar **staging deploy'dan keyin** ishlaydi
([10-operations § CI/CD](../../docs/10-operations/README.md)) — vizual
regressiya ham Nightly'da, `tools/ci_playwright.sh` orqali.

Bundle byudjeti (`tools/check_bundle_budget.py`) esa **har PR da** yuritiladi,
chunki u build'ni talab qiladi va asosiy CI'da build allaqachon bor.
