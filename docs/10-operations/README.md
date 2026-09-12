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

## Ochiq risk: arxivda yashirin test yo'q

**Holat:** bilib turib qoldirilgan — testlar keyinroq o'zimiz generatsiya
qilinadi.

**1 226 ta ommaviy masaladan 1 222 tasida yashirin test yo'q** — har bir
`TestCase` da `is_sample=True`. Sababi importda: KEP'ning ochiq API'si
faqat namuna testlarni beradi va `import_kep.apply_samples` hammasini
namuna deb yozadi.

Oqibati: kutilgan javob masala sahifasida (`/api/v1/problems/<slug>/`
javobidagi `samples`) ochiq turadi, ya'ni uni bosib chiqargan dastur
`AC` oladi. O'lchandi (2026-09-10, preview) — `#437 · 3 ta son` ga
kirishni umuman o'qimaydigan `print('3 2 1')` yuborildi, verdikt `AC`.

Bu 870 ta testsiz masaladan **og'irroq**: ular `WRONG_TEST` qaytarardi —
ko'rinadigan nosozlik. Bular `AC` qaytaradi va skills reytingi shu
`AC` lar ustiga quriladi.

Yashirin testi bor 4 ta masala: `a-plus-b`, `juft-toq`, `eng-katta`,
`fibonacci` (seed).

**Hozircha qilingan ish — faqat to'siq:** yangi masala yashirin testsiz
e'lon qilinmaydi. Tekshiruv ikki joyda va faqat E'LON QILISH paytida
ishlaydi (arxivdagi 1 222 masala hali tahrirlanishi kerak):

- `problems/staff_serializers.py` — qoralamadan ommaviyga o'tkazishda
- `publish_problems` — standart filtr `tests__is_sample=False`

**Yopilmagan qism:** mavjud 1 222 masala. Rejalashtirilgan yo'l — har
masalaga etalon yechim yozib, undan yashirin test generatsiya qilish.

Yana ikkita kichikroq nuqson o'sha o'lchovda ko'rindi:

| Nuqson | Soni | Izoh |
| ------ | ---- | ---- |
| Statement butunlay bo'sh | 5 | `#730`, `#1447`, `#1733`, `#2043`, `#1734` |
| Statement < 100 belgi | 164 | ko'pi haqiqatan qisqa, lekin tekshirilmagan |
| Matnda «istalgan javob» iborasi bor, checker `standard` | 200 | ko'p javobli masala aniq moslik bilan tekshirilyapti — to'g'ri yechim WA olishi mumkin |

## Ommaviy preview (rankwant.uz)

**Bu production EMAS** — yuqoridagi to'rt-hostli topologiya o'rniga bitta
mashinada ishlaydigan ko'rsatuv nusxasi.

```bash
docker compose --env-file .env.public \
  -f docker-compose.yml -f docker-compose.public.yml up -d --build --wait
```

| Nima | Qanday |
| ---- | ------ |
| Tashqi kirish | Cloudflare Tunnel (`/etc/cloudflared/config.yml`), ochiq port yo'q |
| Tunnel o'chiq bo'lsa | [`services/maintenance-worker`](../../services/maintenance-worker/README.md) — Cloudflare Worker xom `Error 1033` o'rniga `503` va "texnik ishlar" sahifasini beradi, `/api/*` ga loyiha xato formatida |
| Domen | `rankwant.uz` (Eskiz'da ro'yxatdan o'tgan, NS — Cloudflare). Eski `rankwant.bugvector.uz` o'chirilmagan: sahifalar yangi domenga 301 bo'ladi (`apps/web/src/proxy.ts`), `/api/*` esa javob beraveradi — eski avatar manzillari uchun |
| Kiruvchi pochta | `admin@rankwant.uz` — Zoho Mail Forever Free (5 foydalanuvchi × 5 GB, faqat web va mobil ilova, IMAP yo'q). Apex'da MX `mx/mx2/mx3.zoho.com`, SPF `include:zohomail.com`, DKIM `zmail._domainkey`. Sayt xatlarini yuboruvchi zanjir (`mail1-4.rankwant.bugvector.uz`) bunga bog'liq emas |
| Domen almashsa | `PUBLIC_ORIGIN` → to'liq deploy → `manage.py rehost_avatars <eski origin>`. Tashqarida: Google klientiga yangi origin va redirect URI, GitHub OAuth App'ga yangi callback (bir nechtasini qabul qiladi — eskisi qoladi), BotFather `/setdomain` (bitta domen). Cookie domenga bog'liq — hamma qaytadan kiradi |
| Marshrutlash | `/api/*` → API, qolgani → Next.js — **bitta origin**, ya'ni CORS/CSRF cross-origin muammosi yo'q |
| Sirlar | `.env.public` (gitignore): `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS` |
| `DJANGO_DEBUG` | `0` — aks holda xato sahifasi sozlamalarni oshkor qiladi |
| Django admin | tunnel'dan **chiqarilmagan**; faqat `127.0.0.1:8301/admin/`. Kundalik boshqaruv esa saytning o'z admin UI'sida: `/admin` (faqat `is_staff`) |
| Standings keshi | **Ochiq**: origin `Cache-Control: public, s-maxage=10` beradi, Cloudflare esa `cf-cache-status: DYNAMIC` qaytaradi — ya'ni keshlamaydi (standart qoidalar fayl kengaytmasiga qaraydi, `/api/v1/...` unga tushmaydi). Cache Rule kerak: `/api/v1/contests/*/standings/` va `/api/v1/arena/*/standings/` → *Eligible for cache*, *Respect origin TTL*. Nega muhimligi pastda |
| `robots.txt` | Bizniki beriladi — `rankwant.uz` zonasida Cloudflare'ning managed robots.txt'i o'chiq, ya'ni `Sitemap: https://rankwant.uz/sitemap.xml` kraulerga yetadi. Search Console (domen resursi) va Yandex Webmaster'da DNS TXT orqali tasdiqlangan, sitemap ikkalasiga yuborilgan (2026-09-11) — apex'dagi `google-site-verification` va `yandex-verification` TXT'larini o'chirmang |

### Standings sig'imi (o'lchangan, 2026-09-10)

Jadval hamma uchun bir xil, ya'ni uni CDN keshlashi KERAK — bu
optimizatsiya emas, loyihaning o'zi:

| | O'lchangan |
| --- | --- |
| Javob (500 qator) | 45 KB |
| Origin kechikishi | 25 ms |
| Origin o'tkazuvchanligi | ~130 so'rov/s |
| 110 000 tomoshabin, 15 s polling | **7 300 so'rov/s**, **330 MB/s** |

Kesh ishlaganda origin 10 soniyada bitta so'rov ko'radi. Ishlamasa — ~56
barobar sig'im yetishmaydi. Shuning uchun jadval 500 qator bilan
cheklangan va foydalanuvchining o'z qatori ALOHIDA endpointda
(`standings/me/`): uni umumiy javobga qo'shish javobni har kimga
boshqacha qilib, keshni yo'q qilardi.

Alohida SSE xizmati bu muammoni YECHMAYDI: 110 000 ochiq ulanishni
ushlab turish, hamma bir xil hujjatni kutayotgan joyda, chekka keshi
tekinga beradigan narsani qimmat qiladi.

### Ochiq risklar

| Risk | Holat |
| ---- | ----- |
| Judge ommaviy koddan bajaradi | Sandbox 14/14 izolyatsiya sinovidan o'tgan, lekin konteyner `--privileged`. To'xtatish: `docker compose ... stop judge` |
| Demo hisoblar (`ustoz`, `oquvchi1..3`) zaif parolli | Ko'rsatuv uchun ataylab qoldirilgan; ommaviy e'lon oldidan o'chirilsin |
| Ro'yxatdan o'tish ochiq | Cheklov yo'q — abuse qatlami ([test-strategy § 12](test-strategy.md)) hali qurilmagan |
| 10 tilning tarjimasi ona tilida so'zlashuvchi tomonidan ko'rilmagan | Kalitlar to'liq va `check_i18n.py` buni qo'riqlaydi, lekin matn sifati tekshirilmagan — ayniqsa qoraqalpoq, tojik va qirg'iz. Qaror (2026-09-10): shikoyat kelganda tuzatiladi |

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

Preview (bitta mashina) uchun: `tools/backup.sh` — Postgres dump va MinIO
nusxasi, 30 kun saqlanadi. Cron:

```
0 4 * * * /path/to/rankwant/tools/backup.sh >> ~/backups/rankwant/backup.log 2>&1
```

Har yurishda dump butunligi tekshiriladi; choraklik to'liq sinov —
`tools/backup.sh --restore-test` (alohida bazaga tiklaydi va qator
sonlarini asl baza bilan solishtiradi).

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

### Runner

Joblar **self-hosted runner** da ishlaydi (`runs-on: [self-hosted, rankwant]`):
`nsn-pc` dagi `actions.runner.menarzullayev-rankwant.nsn-pc-rankwant`
systemd xizmati. Sababi — repo private, GitHub'ning bulut runnerlari esa
oyiga 2000 daqiqa bilan cheklangan va u kvota hisobdagi boshqa
repolar bilan bo'lishiladi. O'z mashinasida Actions bepul va cheksiz.

Buning evaziga muhit mustaqilligi yo'qoladi: CI ishlab chiqish mashinasida
ishlaydi, ya'ni «menda ishlayapti» sinfidagi muammolarni toza bulut
runneri kabi tutmaydi.

**Muhim:** CI stack'i `docker-compose.ci.yml` dagi `name: rankwant-ci`
bilan alohida compose loyihasida turadi. Loyiha nomi katalogdan olinsa
runner'ning ish katalogi (`_work/rankwant/rankwant`) jonli preview
stack'i bilan bir loyihaga tushar va CI tozalashdagi `down -v` uning
bazasini o'chirib yuborardi. Shu sababli test tarmog'i ham
`rankwant-ci_default`.

### Push'dan oldingi darvoza

`.githooks/pre-push` (repo bilan versiyalanadi, `core.hooksPath` orqali
yoqiladi) o'zgargan qismlarga qarab lint, tip va testlarni push'dan
oldin ishlatadi. Runner o'sha mashinada bo'lgani uchun buzuq commit
GitHub vaqtini emas, kompyuter vaqtini yeydi — darvoza uni oldinroq
to'xtatadi. Chetlab o'tish: `git push --no-verify`.

Yangi klonda yoqish:

```bash
git config core.hooksPath .githooks
```

## Keyinroq to'ldiriladi

- [ ] Hosting provayderi va narx modeli
- [ ] On-call rotatsiyasi va eskalatsiya
- [ ] Aniq runbook qadamlari (real incident tajribasidan keyin)
- [ ] SLO/error budget raqamlari (real trafikdan keyin)
