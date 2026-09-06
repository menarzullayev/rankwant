# 10. Quality & Operations

**STATUS:** draft (2026-09-06) — siyosatlar yozilgan, **runbook'lar production tajribasidan keyin**

Nima **hozir** bilinadi: deploy topologiyasi, siyosatlar va incident turlari — ular arxitektura va ADR'lardan kelib chiqadi.
Nima **hali bilinmaydi**: hosting provayderi, real narxlar, aniq runbook qadamlari.

## Deploy topologiyasi

Bu taqsimot **xavfsizlik chegarasidan** kelib chiqadi ([06](../06-architecture/README.md) 🔒), qulaylikdan emas:

| Host              | Nima ishlaydi                    | Tarmoq                                       |
| ----------------- | -------------------------------- | -------------------------------------------- |
| **app**           | Django API + Celery worker       | ↔ Postgres, Redis, S3 · public HTTPS         |
| **web**           | Next.js SSR                      | → API · public HTTPS                         |
| **judge** ×N      | judge worker + sandbox           | → Redis, S3 **faqat**; kiruvchi port **yo'q** |
| **data**          | Postgres, Redis                  | faqat ichki tarmoq                           |

Judge hostlar **gorizontal** miqyoslanadi — navbat uzunligi oshsa worker qo'shiladi.

## Judge sig'imi (o'lchangan, 2026-09-06)

[ADR-0004](../07-adr/0004-judge-engine.md) bake-off o'lchovi:

| Worker | O'tkazuvchanlik | p95 |
| ------ | --------------- | --- |
| 1 | 2.4 submit/s | 857 ms |
| 4 | 5.4 submit/s | 952 ms |
| 8 | 8.0 submit/s | 1360 ms |

### API o'qish sig'imi (o'lchangan, 2026-09-07)

`tests/load/main.js` `ci` ssenariysi, compose stack (gunicorn 4 worker):

| O'lchov | Qiymat | NFR |
| ------- | ------ | --- |
| So'rov  | 57 req/s (20 VU) | — |
| `/problems/` p95 | 23 ms | < 1000 ms ✅ |
| Standings p95 | 38 ms | < 300 ms ✅ |
| Xato ulushi | 0% | < 1% ✅ |

Bu **o'qish** yo'li; judge sig'imi yuqoridagi jadvalda va u alohida
chegara.

**Miqyoslash chiziqli emas** — `total_ms` ning ~830 ms i kompilyatsiya, u
CPU-bound. Bitta host'da yadrolar tugagach worker qo'shish kam foyda beradi.

PRD NFR contest spike: **500 submit / 10 s = 50 submit/s**. Bunga yetish uchun:

1. **Ko'p judge host** — worker qo'shish emas, HOST qo'shish (bitta hostda
   ~8 worker to'yinadi). Taxminan 6–8 host kerak.
2. **Kompilyatsiya keshi** — manba hash'i bo'yicha; rejudge va takrorlanuvchi
   yechimlar kompilyatsiyani butunlay o'tkazib yuboradi. Eng katta yutuq.

Contest oldidan judge hostlarni **oldindan ko'paytirish** kerak — autoscale
spike'ga ulgurmaydi (contest boshlanishi 10 soniyalik hodisa).

## Ochiq risk: NAT ortidagi maktablar va anon rate limit

**Holat:** hal qilinmagan — mahsulot qarori kerak.

Anon throttle IP bo'yicha ishlaydi: `60/min`. Yuklama sinovi buni
ko'rsatdi — bitta manbadan kelgan 20 ta parallel foydalanuvchining
94% so'rovi `429` oldi.

Nega bu O'zbekiston uchun muhim: maktab kompyuter sinfi, kollej va
internet-kafe odatda **bitta ommaviy IP** ortida bo'ladi. Bitta sahifa
ko'rinishi bir nechta API so'rovi qiladi, ya'ni 60/min butun sinfga
yetmaydi. Aynan o'qituvchi sinfi ([P2-2](../09-development-plan/README.md))
mo'ljallangan auditoriya shu holatda.

Variantlar (tanlanmagan):

| # | Variant | Suiiste'moldan himoya | Sinf uchun |
| - | ------- | --------------------- | ---------- |
| 1 | Anon limitni ko'tarish | ⚠️ zaiflashadi | ✅ |
| 2 | Katalog (o'qish) endpointlarini throttle'dan chiqarish, yozishni qattiqroq cheklash | ✅ | ✅ |
| 3 | Sinf IP larini oq ro'yxatga olish | ✅ | ⚠️ qo'lda ish |

Limitlar endi `THROTTLE_ANON` / `THROTTLE_USER` / `THROTTLE_SUBMIT`
orqali sozlanadi, ya'ni qaror qabul qilinganda kod o'zgarishi shart emas.

## Ommaviy preview (rankwant.bugvector.uz)

**Bu production EMAS** — yuqoridagi to'rt-hostli topologiya o'rniga bitta
mashinada ishlaydigan ko'rsatuv nusxasi.

```bash
docker compose --env-file .env.public \
  -f docker-compose.yml -f docker-compose.public.yml up -d --build --wait
```

| Nima | Qanday |
| ---- | ------ |
| Tashqi kirish | Cloudflare Tunnel (`/etc/cloudflared/config.yml`), ochiq port yo'q |
| Marshrutlash | `/api/*` → API, qolgani → Next.js — **bitta origin**, ya'ni CORS/CSRF cross-origin muammosi yo'q |
| Sirlar | `.env.public` (gitignore): `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS` |
| `DJANGO_DEBUG` | `0` — aks holda xato sahifasi sozlamalarni oshkor qiladi |
| Django admin | tunnel'dan **chiqarilmagan**; faqat `127.0.0.1:8301/admin/` |

### Ochiq risklar

| Risk | Holat |
| ---- | ----- |
| Judge ommaviy koddan bajaradi | Sandbox 14/14 izolyatsiya sinovidan o'tgan, lekin konteyner `--privileged`. To'xtatish: `docker compose ... stop judge` |
| Demo hisoblar (`ustoz`, `oquvchi1..3`) zaif parolli | Ko'rsatuv uchun ataylab qoldirilgan; ommaviy e'lon oldidan o'chirilsin |
| Ro'yxatdan o'tish ochiq | Cheklov yo'q — abuse qatlami ([test-strategy § 12](test-strategy.md)) hali qurilmagan |

## Muhitlar

| Muhit    | Manzil                  | Izoh                                       |
| -------- | ----------------------- | ------------------------------------------ |
| Local    | docker-compose          | api + postgres + redis + 1 judge worker    |
| Staging  | `staging.rankwant.uz`   | production bilan bir xil topologiya, kichik |
| Prod     | `rankwant.uz`           | judge alohida hostlarda                    |

Staging'da ham judge **alohida** konteynerda — izolyatsiyani local'da sinash uchun.

## Deploy qoidalari

1. **Live contest paytida deploy YO'Q.** Bu qattiq qoida — contest davomida verdict yoki standings o'zgarishi natijani buzadi. Deploy oynasi contest jadvalidan tekshiriladi.
2. Migration'lar oldinga mos: `add column → backfill → switch → drop`, alohida deploylarda ([08](../08-technical-spec/README.md) 🔒)
3. Judge worker'lar **navbatni bo'shatib** to'xtaydi (graceful drain) — ishlayotgan submit yo'qolmaydi
4. Rollback: oldingi image tegi; migration rollback **rejalashtirilgan** bo'lishi shart

## Backup

| Nima                | Chastota           | Saqlash | Tiklash sinovi |
| ------------------- | ------------------ | ------- | -------------- |
| Postgres            | kunlik full + WAL  | 30 kun  | **choraklik**  |
| S3/R2 test data     | versiyalash yoqilgan | doimiy | choraklik      |
| Qvant ledger        | Postgres ichida    | —       | audit so'rovi bilan |

Tiklash sinovi o'tkazilmasa, backup **yo'q deb hisoblanadi**.

## Monitoring va alert

| Metrika                    | Alert sharti           | Sabab                             |
| -------------------------- | ---------------------- | --------------------------------- |
| Judge latency p95          | > 15s                  | NFR buzilishi ([04-prd](../04-prd/README.md)) |
| Judge navbat uzunligi      | > 5 min kutish         | worker yetishmaydi                |
| `SECURITY_VIOLATION`       | **har bitta hodisa**   | potensial sandbox escape          |
| `IE` / `DENIAL_OF_JUDGEMENT` | ko'tarilish          | infra nosozligi                   |
| 5xx darajasi               | > 1%                   | API muammosi                      |
| Qvant emissiyasi           | kunlik limitdan oshish | anti-farm buzilishi ([ADR-0002](../07-adr/0002-qvant-economy.md)) |

## Incident turlari

### 1. Sandbox escape shubhasi — **eng yuqori daraja**

1. Judge worker'larni darhol to'xtatish (submit navbatda qoladi, yo'qolmaydi)
2. Ta'sirlangan hostni **izolyatsiya qilish**, snapshot olish
3. Judge hostda DB credential yo'q — ma'lumot sizishi chegaralangan; baribir tekshiriladi
4. Sandbox versiyasini yangilash, host qayta quriladi (patch emas)
5. Post-mortem majburiy

### 2. Judge navbat to'lib qolishi

Worker qo'shish → yetmasa contest submit'lariga **prioritet** (arxiv submitlari kutadi) → foydalanuvchiga navbat holati ko'rsatiladi.

### 3. Noto'g'ri verdict / rejudge

Rejudge **partiyada** va e'lon bilan. Contest natijasiga ta'sir qilsa: standings qayta hisoblanadi va **Contests reytingi ham qayta hisoblanadi** ([ADR-0006](../07-adr/0006-rating-model.md)); `RatingHistory` ga sabab yoziladi.

### 4. Masala qayta baholash

[ADR-0007](../07-adr/0007-skills-uses-current-difficulty.md) siyosati: yakka-yakka emas, **partiyada va oldindan e'lon bilan**; ta'sirlangan foydalanuvchilarga bildirishnoma; har o'zgarish `RatingHistory` da.

## Repo boshqaruvi

Repo: `menarzullayev/rankwant` — **private** ([ADR-0003](../07-adr/0003-stack-django-next.md) yopiq/tijorat qaroriga ko'ra).

| Mexanizm | Holat | Izoh |
| -------- | ----- | ---- |
| CI (har PR va push) | ✅ | lint, mypy, test, OpenAPI diff, hujjat yaxlitligi |
| Dependabot | ✅ | 5 ekotizim, haftalik |
| gitleaks | ✅ | push va PR da; secret scanning o'rnini bosadi |
| Squash-only merge, branch avto-o'chirish | ✅ | |
| **Branch protection / rulesets** | ❌ | private repo + free plan → GitHub Pro yoki org Team talab qiladi |
| **Secret scanning + push protection** | ❌ | shu sabab; gitleaks qoplaydi |

**2026-09-06 qarori:** hozircha shunday qoldiriladi — pul sarflanmaydi, CI baribir qizil ko'rsatadi.
Narxi: `main` ga to'g'ridan-to'g'ri push va qizil CI bilan merge **texnik jihatdan mumkin**; DoD intizomga tayanadi.

**Qayta ko'rib chiqiladi:** ikkinchi odam jamoaga qo'shilishidan **oldin**. Yolg'iz ishlashda qabul qilsa bo'ladigan xavf, jamoada emas.

## Test strategiyasi

To'liq hujjat: **[test-strategy.md](test-strategy.md)** — 15 qatlam (functional, unit, integration, E2E, smoke, regression, load, stress, spike, soak, security, abuse, recovery, chaos, compatibility), CI/CD pipeline va vositalar.

Qisqacha, majburiy qamrov: judge pipeline · 4 reyting formulasi · Qvant ledger · auth/PAT scope.
Judge izolyatsiya sinovlari (fork bomb, fayl, tarmoq, `/proc`, symlink) — **CI da doimiy**, bir martalik emas.

## CI/CD

GitHub Actions: lint → `mypy` strict → test → OpenAPI diff → build → staging deploy.
Prod deploy **qo'lda tasdiqlash** bilan (contest oynasi tekshiruvi tufayli).

## Keyinroq to'ldiriladi

- [ ] Hosting provayderi va narx modeli
- [ ] On-call rotatsiyasi va eskalatsiya
- [ ] Aniq runbook qadamlari (real incident tajribasidan keyin)
- [ ] SLO/error budget raqamlari (real trafikdan keyin)
