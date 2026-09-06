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
