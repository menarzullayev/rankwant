# RankWant — agent uchun kirish nuqtasi

Loyiha hujjatlangan: `docs/` da 10 bo'lim, `docs/07-adr/` da har qaror alohida ADR.
**Bu fayl ularni takrorlamaydi** — bu yerda faqat kod yozayotganda darhol
kerak bo'ladigan buyruqlar va ilgari vaqt yegan tuzoqlar.

## Qayerga qarash kerak

| Savol | Hujjat |
| ----- | ------ |
| Entity, maydon, o'chirish qoidalari | `docs/05-domain-model/` (locked) |
| Nega shunday qilingan | `docs/07-adr/` — har qaror alohida ADR |
| Deploy, incident, backup, monitoring | `docs/10-operations/` |
| Verdikt kodlari, sahifalash, xato formati | `docs/08-technical-spec/` |
| Judge shartnomasi va bake-off | `services/bakeoff/protocol.md` |

Pul mantiqi bo'yicha bitta qoida hammasidan muhim (ADR-0002):
**balans hech qachon to'g'ridan-to'g'ri yozilmaydi, faqat ledger orqali.**
`qvant_audit` buni butun baza bo'yicha tekshiradi.

## Saidakbar aka qarorlari

Bu qarorlarni **agent o'zi bekor qilmaydi** — «yaxshilash» deb ham.
O'zgartirish kerak bo'lsa, avval Saidakbar akadan aniq tasdiq olinadi va
jadval shu PR'da yangilanadi. `tools/check_decisions.py` har PR'da qatorlarni
kodda tekshiradi. Sabab (2026-09-17): «faqat lokal zaxira» qarori qabul
qilingan kuniyoq boshqa agent R2 ga shifrsiz offsite qo'shdi (#31) va
foydalanuvchi ma'lumoti bor dump'lar tashqariga chiqdi.

| Sana | Qaror | Kodda qayerda |
|---|---|---|
| 2026-09-17 | Zaxira 30 kunda 1 marta, **faqat lokal**; offsite (R2, USB) yo'q | `tools/backup.sh` standarti `off`; vazifa `RankWant Monthly Backup` (`KEEP=95`, `OFFSITE=off`) |
| 2026-09-17 | `main` ga faqat PR orqali; soxta muallif push qilinmaydi | `.githooks/pre-push` → `tools/push_guard.py` |
| 2026-09-18 | CI, Security, Nightly — `ubuntu-latest` (public repo, $0 daqiqa, 20 parallel). Deploy va `runner-selftest` self-hosted: deploy jonli Docker stack'iga tegadi; public `pull_request` noutbukda yugurmasin | `ci.yml` / `security.yml` / `nightly.yml` → `ubuntu-latest`; `deploy.yml` self-hosted; `tools/check_decisions.py` → `ci_test_on_hosted` |
| 2026-09-17 | CI runner — Docker Desktop'dagi `rankwant-ci-runner` konteyneri (`rankwant` label; ish papkasi volume'da; `RankWant CI Runner Watchdog` qo'riqlaydi). WSL runner 2026-09-17 da butunlay olib tashlangan. `rankwant-container` label'ini faqat `runner-selftest.yml` ishlatadi | `tools/runner/` → `RUNNER_LABELS`; `tools/check_decisions.py` → `TRIAL_RUNNER` |
| 2026-09-18 | Ikkinchi runner (`rankwant-ci-runner-2`, alohida volume, compose profile `second`, 4 CPU / 4 GB). PR'da Security yo'q. Recreate bitta servisni `down` qilmaydi | `security.yml` `on:`; `docker-compose.runner.yml`; `recreate.sh --second`; `runner_watchdog.py` |
| 2026-09-20 | Og'ir stack (smoke, E2E, bake-off, language matrix) va API pytest **faqat Nightly**. CI/PR — ruff, mypy, OpenAPI, migratsiya, web check, judge unit. Deploy darvozasi shu tez CI + Security | `ci.yml`; `nightly.yml` e2e/coverage/compatibility; `tools/check_decisions.py` → `pr_skips_heavy_ci` |
| 2026-09-20 | `check_deploy.sh` inventory `LC_ALL=C sort` — Git Bash vs Alpine collate `comm` ni yolg'on «ESKIRGAN» qilgan (o'lchandi: `__init__.py` bor, yorliq HEAD) | `tools/check_deploy.sh` → `py_inventory`; `tools/check_decisions.py` → `deploy_automation_is_safe` |
| 2026-09-16 | Deploy qo'lda (`tools/deploy.sh`); 2026-09-17 dan skript `web` ni ham quradi — bitta deploy hamma servisni yangilaydi | `deploy.yml` faqat `workflow_dispatch`; `tools/deploy.sh` → `SERVICES` |
| 2026-09-17 | Agentlar production'ni **`main` CI yashil bo'lsa** so'ramasdan deploy qiladi; bir vaqtda faqat bitta deploy | `tools/deploy.sh` → `tools/check_deploy_gate.py` + qulf (`--skip-ci-gate` faqat Saidakbar aka ruxsati bilan) |
| 2026-09-17 | Repo aralash tilda, migratsiya yo'q | `CONTRIBUTING.md` § Til |
| 2026-09-17 | `cp/` faqat RankWant uchun; tadqiqot hujjatlari `docs/research/` da | `cp/README.md` (repo'dan tashqarida) |
| 2026-09-18 | Sayt qidiruv tizimlariga **ochiq**, AI kraulerlarga **yopiq**; `/users/` sinov profillari tozalanmaguncha yopiq ([ADR-0023](docs/07-adr/0023-indexing-and-ai-crawlers.md)) | `apps/web/src/lib/site.ts` → `SITE_INDEXABLE`; `apps/web/src/app/robots.ts` → `AI_CRAWLERS` |
| 2026-09-18 | Sidebar, top bar, header va footer linklari faqat **niyatda** prefetch qiladi (hover, fokus, teginish) — ko'rinishi bilan emas: tashrif boshiga ~130–150 ms server CPU edi ([profil](docs/research/2026-09-18-homepage-profile/REPORT.md)) | `apps/web/src/components/ui/IntentLink.tsx`; `tools/check_decisions.py` → `NAV_CHROME` |
| 2026-09-18 | Bosh sahifa `<main>` havolalari ham faqat **niyatda** prefetch qiladi. 1000 tashrif/s da ko'rinish-prefetch (7 RSC) origin'ni `EOF` qildi; chrome allaqachon niyatda edi | `apps/web/src/app/page.tsx`; `ButtonLink intent`; `tools/check_decisions.py` → `HOME_MAIN` |
| 2026-09-18 | Brauzerga lug'at **alohida keshlanadigan faylda** (`/i18n/<til>.js?v=<hash>`, `immutable`) boradi, sahifa ichida emas: u har HTML'ning 72 KB'i va render CPU'sining 32% i edi ([profil](docs/research/2026-09-18-homepage-profile/REPORT.md)) | `apps/web/src/app/i18n/[file]/route.ts`; `apps/web/src/app/layout.tsx` → `dictionaryUrl`; `apps/web/src/proxy.ts` matcher |
| 2026-09-18 | `User` ga Codeforces/Robocontest/KEP bilan tenglik uchun **21 maydon** (46 → 67). 13 tasi (`plan`, `postal_*`, `device_fingerprint`…) funksiyasidan **oldin** qo'shilgan — «ishlatilmaydi» deb olib tashlanmaydi ([ADR-0024](docs/07-adr/0024-user-competitor-parity-fields.md)) | `apps/api/core/models.py` → `User`; `tools/check_decisions.py` → `PARITY_USER_FIELDS` |
| 2026-09-18 → 19 | **Tor ekran (320 px) ga sig'adi** — eng tor qo'llab-quvvatlanadigan ekran. Til tanlagich **endonimni** har kenglikda ko'rsatadi (`O'zbekcha`), lekin `sm` dan pastda `max-w-[3rem]` bilan **chegaralangan**; tanlash ro'yxati tor ekranda **viewport'ga** bog'lanadi (`fixed`), keng ekranda tugmaga; kirish yorlig'i o'ralmaydi. O'lchandi ① (2026-09-18, jonli brauzer): to'liq nom bilan 320 px da **15 px** (chiqqan) / **59 px** (kirgan), 375 px da **10 px** toshardi — o'shanda tor ekranda **kod** ko'rsatish tanlangan edi. ② (2026-09-19, HITL S4, `main` = `6486cd6`): cheklovsiz endonim yana toshadi — `Qaraqalpaqsha` **149 px** (+29), `O'zbekcha` **124 px** (+7), `ky` **123 px** (+6); header'da bo'sh joy yo'q (o'ng guruh `min-w-0` bilan allaqachon siqilgan). **48 px** chegarada barcha o'nta endonim ≤ **117 px**, toshish **0**, va **7 tasi to'liq** ko'rinadi — ya'ni kod shart emas edi. O'sha o'lchov panelning ham nuqsonini topdi: `w-64` (256 px) trigger o'ng cheti **212 px** bo'lganda chapga **44 px** toshardi va **barcha 11 bayroq** `left = -32…-11` — ko'rinmasdi (360 px da `left = -4`, bayroq ko'rinadi ⇒ chegara ~**352 px**). Endi tor ekranda panel `fixed` + o'lchangan koordinata: toshish **0**, bayroqlar **11/11** ko'rinadi, nom qirqilmaydi | `apps/web/src/layout/LocaleSwitch.tsx`; `apps/web/src/layout/UserMenu.tsx`; `tools/check_decisions.py` → `mobile_header_fits_narrow_screen`; salbiy testlar 4 ta |
| 2026-09-18 | Mobil navigatsiya paneli **e'lon qilinadi, fokuslanadi va yopiladi**: trigger holatni aytadi (`aria-expanded` + `aria-controls`), panel ochiq holatda nomli dialog (`role="dialog"`, `aria-modal`, `aria-label`), fokus ichkariga kiradi va ochgan tugmaga qaytadi, `Esc` yopadi, orqa fon scroll qilmaydi. O'lchandi (jonli brauzer, 390×844×2): ilgari `aria-expanded` **ochiq holatda ham `null`**, panelda rol/nom yo'q, fokus `body` da qolardi, `body` overflow `visible`, haqiqiy `Esc` panelni yopmasdi | `apps/web/src/layout/AppHeader.tsx`; `apps/web/src/layout/AppSidebar.tsx`; `apps/web/src/context/SidebarContext.tsx`; `apps/web/src/layout/AppShell.tsx`; `tools/check_decisions.py` → `mobile_drawer_is_accessible` |
| 2026-09-18 | Bosh sahifa KPI to'ri `lg` da **4 ustun** (1024 px dan), tor ustunda raqam esa **24 px** ga tushadi (`lg:text-2xl`, `xl` da yana 30 px). O'lchandi (1024×768, jonli sahifa): 2+2 da keyingi bo'limdan faqat **38 px** ko'rinardi, 4 ustunda **216 px** va sahifa **178 px** qisqaroq. 3 ustunli pog'ona **o'lchov bilan rad etildi** — 4 karta baribir 2 qatorni egallaydi (vertikal yutuq **0 px**) va 4-karta yolg'iz qoladi. Tor ustunning narxi bor: 30 px bold raqamda har xona ~17.2 px, 4 ustunli kartada ichki kenglik **121 px** — 8 xonali sanoq toshadi, shuning uchun raqam kichrayadi | `apps/web/src/app/page.tsx`; `apps/web/src/components/ui/Card.tsx` → `valueClassName`; `tools/check_decisions.py` → `kpi_grid_steps_at_lg` |
| 2026-09-18 | Profil KPI to'ri `xl` da (1280 px) **4 ustunga** o'tadi, `lg` da **emas**, va tor ustunda raqam `xl:text-2xl` bilan **24 px** ga tushadi (`2xl` da yana 30 px). Sabab — yon panel **300 px** ni oladi, shuning uchun profil kontent ustuni 1024 px da atigi **377 px** (bosh sahifada 749). O'lchandi: 1024 da majburan 4 ustun → karta **82 px**, ichki **40 px**, raqamlar **27 px ga qirqildi**; 1280 da 4 ustun sig'adi (ichki 104 px) — lekin 6 xonali sanoq **aynan 104 px**, shuning uchun raqam pog'onasi shart. Karta ichida `about` matni bor, ya'ni tor karta **balandroq** (2 ustunda 168 → 4 ustunda 222 px); blok baribir qisqaradi (130 px). **2026-09-19 da keyingi qaror bilan o'zgardi**: panel endi `xl` gacha stekda, 4 ustun `lg` dan — shu qatordagi o'lchovlar yangi yechim asosi bo'ldi | `apps/web/src/app/users/[username]/layout.tsx`; `tools/check_decisions.py` → `profile_sidebar_stacks_below_xl` |
| 2026-09-19 | Profil sahifasi **`xl` gacha (1024–1279 px) bir ustun**: profil kartasi kontent tepasida to'liq kenglikda, ikki ustun (`300px_minmax(0,1fr)`) va sticky panel faqat 1280 dan qaytadi. Profil KPI to'ri shu sabab `lg` dan **4 ustun**, raqam `lg:text-2xl` (24 px), `2xl` dan 30 px. HITL qarori (2026-09-19, uch variant o'lchovlar bilan taqqoslandi) — appearance auditidagi so'nggi ochiq nuqta (KPI 1024–1279 da 2 ustunda qolishi) yon panel qarorisiz yopilmasdi. Geometriya bosh sahifa (#96) o'lchovi bilan bir xil: 1024 da kontent **701 px**, karta ~163 px, ichki ~121 px — 8 xonali raqam 24 px da sig'adi; 1280 da ikki ustun qaytgach ichki **104 px** (6 xonali aynan sig'adi). Rad etilgan variantlar: panelni 300→232 px toraytirish (KPI baribir 2 ustunda qolaveradi) va holatni «by design» deb qoldirish (377 px tor ustun shu oraliqda qolaverardi). Narxi: 1024–1279 da sticky panel yo'q | `apps/web/src/app/users/[username]/layout.tsx`; `tools/check_decisions.py` → `profile_sidebar_stacks_below_xl`; salbiy testlar 4 ta |
| 2026-09-19 | **Header va footer** (HITL, 3 qaror): ① sidenav **standart** rejim qoladi (topnav ixtiyoriy, D46), mobil drawer saqlanadi, 21 band / 5 guruh o'zgarmaydi; **brend header'ga ko'chadi** — `BrandMark` bitta manba (header responsive: `sm` dan wordmark, torda monogram; topnav full; sidebar'da brend yo'q — ilgari telefonlda brend faqat drawer ichida ko'rinardi). ② Mobilda drawer saqlanadi — u hozirgina to'liq WCAG darajasida. ③ Footer **uch ustun**: brend+tagline, Platforma havolalari (mavjud nav kalitlari bilan), Aloqa va jamiyat (Telegram `t.me/rankwant`, email `support@rankwant.uz`) — **2026-09-20 HITL confirm-current**: ikkala manzil rasmiy; pastda huquqiy qator: © (yil) RankWant · Terms · Privacy (ADR-0016 talabi saqlanadi; sayt indekslanadi — ADR-0023, footer havolalari SEO uchun ishlaydi) | `apps/web/src/layout/BrandMark.tsx`; `AppHeader.tsx`; `AppSidebar.tsx`; `AppTopNav.tsx`; `AppFooter.tsx`; `tools/check_decisions.py` → `brand_in_header_and_footer_columns`; salbiy testlar 4 ta |
| 2026-09-18 | Filtr rozetkasi **diapazonni bitta filtr** deb sanaydi: `difficulty__gte` + `difficulty__lte` (va eski `level=`) — bu bitta tanlov, uch xil yozuv. O'lchandi (CI smoke, 2026-09-18): bitta «Qiyin» chip'i ikkala chegarani yozadi, `activeCount` esa `PANEL_KEYS` kalitlarini sanardi → rozetkada **`Filtrlar2`**; test `"1"` kutgani uchun `main` `#90` dan beri qizil edi va shu sabab deploy darvozasi ham yopiq qolgan edi | `apps/web/src/components/ProblemFilters.tsx` → `DIFFICULTY_KEYS`; `tools/check_decisions.py` → `difficulty_range_counts_as_one_filter` |
| 2026-09-19 | **Kontent nomlari qamrovi ko'rinadi** (HITL, T3-a + T3-c). Mavzu/ko'nikma/vazifa nomlari bazada faqat `uz`/`ru`/`en` ustunlarida, ya'ni qolgan **yetti tilda o'zbekcha** matn ko'rinadi. O'lchandi (jonli stek): zaxira **8 joyda** ishlardi, belgi esa faqat **2 tasida** — qaror amalda **25%** bajarilgan edi. Ustiga `uz` sahifasining o'zida ham `uz` chipi chiqardi: `nameInfo` `uz` ni ham qaytish deb hisoblardi (unit test tutdi — `.locale` `null` edi). Endi belgi sharti **bitta joyda** — `ContentName`; sakkizta chaqiruv joyining hammasi undan o'tadi (native `<option>` ichiga JSX sig'magani uchun tarjima qilingan matn qo'shimchasi), va tanlash ro'yxati har til yonida **`nomlar uz`** belgisini ko'rsatadi — ya'ni qamrov **tanlashdan oldin** ma'lum | `apps/web/src/i18n/messages.ts` → `CONTENT_NAME_LOCALES`/`hasContentNames`; `apps/web/src/components/ui/UzFallbackBadge.tsx` → `ContentName`/`contentNameText`; `LocaleSwitch.tsx`; `ProblemFilters.tsx`; `SkillsSection.tsx`; `ArchiveSidebar.tsx`; `ActivityTabs.tsx`; `apps/web/src/app/problems/page.tsx`; `tools/check_decisions.py` → `content_coverage_visible`; salbiy testlar 7 ta |
| 2026-09-19 | Til tanlagichdan **qaytib** o'sha tilga o'tilganda lug'at yo'qolmasin: registr va yuklash va'dasi keshi **birga** tozalanadi (`keepOnly`). O'lchandi (jonli stek, haqiqiy sichqoncha va klaviatura): `ru` → `zh` → `es` → qaytib `zh` ketma-ketligida brauzer registri bo'sh qolib sahifada **38 xom kalit** chiqdi (`nav.problems`, `locale.switchLabel`, …) va F5 gacha tiklanmadi. Sabab: `evictOtherLocales` lug'atni o'chiradi, URL bo'yicha kalitlangan va'da keshi esa qolib ketadi — `<script>` qayta kiritilmaydi. `eslint`, `tsc` va bir yo'nalishli qo'lda sinov **tutmadi**. Qayta kiritish arzon: fayl `immutable`, ya'ni keshdan o'qiladi | `apps/web/src/i18n/LocaleProvider.tsx` → `keepOnly`; `tools/check_decisions.py` → `dictionary_survives_return` |
| 2026-09-19 | **Bosh sahifa 100k ochilishda qotmasin**: CDN HTML kesh faqat mehmon GET `/` (sessiya/`rw_locale`/`rw:markup` yo'q). Origin `Cache-Control: public, s-maxage=30, stale-while-revalidate=86400`; kirgan `private, no-store` SSR. Cloudflare `/` ni Worker'siz, origin header'ga rioya qilib keshlaydi (`Eligible` + `Respect origin`). Worker catch-all `rankwant.uz/*` olib tashlandi — `host/x*` qolgan yo'llarni qamraydi | `apps/web/src/lib/home-cache.ts`; `apps/web/src/proxy.ts`; `apps/web/src/instrumentation.ts`; `services/maintenance-worker/wrangler.toml`; `tools/check_decisions.py` → `homepage_guest_cdn_cache` |
| 2026-09-19 | **50k masshtab**: modular monolit + replica; bitta Postgres + indeks; Redis (`stats`/`providers`/standings); mehmon CDN `/` + `/login` + huquqiy (`rw_exp` yozilmaydi); Celery+Redis; CF + web×2/api×2 ixtiyoriy overlay; SLO `/api/v1/slo/` (Sentry yo'q); to'rt-host compose | `home-cache.ts`; `wrangler.toml`; `core/cache.py`; `core/views.py` `SloView`; `docker-compose.replicas.yml`; `compose/four-host/README.md` |
| 2026-09-19 | **Rollar (ADR-0025)**: Django staff Groups (`staff-support` / `staff-content` / `staff-ops`) + obyekt M2M (`Contest.organizers`, `Problem.authors`). `User.role` CharField yo'q. Mavjud `is_staff` seed'da uchala guruhga qo'shiladi; permission qatorlari `sync_staff_groups()` post_migrate'da. `/contests/mine/` va `/problems/mine/` | `core/groups.py`; `contests/models.py`; `problems/models.py`; `tools/check_decisions.py` → `roles_groups_and_object_authors`; salbiy testlar 4 ta |
| 2026-09-19 | **Til havolada ham keladi** (HITL, S5 = T5-b va S5b): `?lang=<kod>` — prefiks (`/en/…`) emas. Ustunlik: **havola → cookie → `Accept-Language` → `uz`**. Havolani olgan odam o'z tilini olib keladi (qurilmasida boshqa til tanlangan bo'lishi mumkin), keyin proxy qiymatni **cookie'ga ham** yozadi — shu sababli ichki havolalarni o'zgartirish **shart emas**. Qo'lda tanlov esa `?lang=` ni **tozalaydi**, aks holda parametr cookie'dan ustun bo'lib yangi tanlov keyingi render'da qaytib ketardi. ⚠️ Proxy'da **tartib** muhim: sarlavha `NextResponse.next()` dan **oldin** yoziladi — `next()` `request.headers` ni chaqiruv paytida `x-middleware-request-*` qatorlariga ko'chiradi (`next@16.3.4`, `response.js:128`), ya'ni keyin yozilgan qiymat joriy render'ga yetib bormaydi va sahifa cookie tilida chiziladi. `?lang=` self-canonical + hreflang — 2026-09-20 HITL | `apps/web/src/i18n/locale-params.ts`; `apps/web/src/i18n/resolve.ts`; `apps/web/src/i18n/server.ts`; `apps/web/src/proxy.ts`; `apps/web/src/layout/LocaleSwitch.tsx`; `tools/check_decisions.py` → `locale_travels_in_the_url`; salbiy testlar 4 ta |
| 2026-09-19 | **Deploy to'liq avtomatik** (HITL: 1 savol, 4 variant → «to'g'ridan-to'g'ri to'liq avtomatik», `required reviewer` yo'q). Mexanizm — **host watcher**, GitHub Actions **emas**: o'lchandi (2026-09-19) — runner konteyneri jonli `.env.public` ni KO'RMAYDI (u `/work` Docker volume'ida, host repo ulanmagan: `/run/desktop/mnt/host/c/` → `No such file or directory`) va unda `gh` YO'Q. Ya'ni workflow o'z env-faylini yozsa `.env.public` dagi **29 kalitdan 4 tasi** qoladi — email zanjiri (Mailjet/Brevo/Resend/MailerSend), Turnstile, Cloudflare token, Google/GitHub/Telegram OAuth va `THROTTLE_REGISTER` **jimgina yo'qoladi**; `check_deploy_gate.py` esa har doim `exit 2` berardi. Shuning uchun `deploy.yml` **qo'lda qoladi** (`deploy_manual_only` o'zgarmaydi), avtomatlashtirish esa `tools/auto_deploy.sh` + `RankWant Auto Deploy` vazifasi (5 daqiqa; naqsh `tools/monitor.ps1` dan). ⚠️ Xavfsizlik qatlami trigger'dan **oldin**: migratsiyadan oldin `pg_dump` (`backup.sh --dump-only`), disk tozalash (`tools/prune_docker_disk.sh`; SHA teg saqlanmaydi — 2026-09-20), `DEPLOY_FREEZE` kaliti, oyna tekshiruviga lokal origin zaxirasi (`exit 2` endi faqat stack butunlay yiqilganda qoladi), qayta urinish to'sig'i (30 daqiqa). Deploy **alohida worktree'dan** yuriladi (`RANKWANT_ENV_FILE` bilan), asosiy checkout'dan emas — agentning commit qilinmagan tahriri build'ga tushmasin. ⚠️ Rollback **migratsiyani qaytarmaydi** (Django'da «orqaga» migratsiya yo'q): kod — skript, sxema — faqat deploy oldidagi dump, qo'lda | `tools/auto_deploy.sh`; `tools/rollback.sh`; `tools/deploy.sh`; `tools/backup.sh` → `--dump-only`; `tools/check_deploy_window.py`; `tools/check_decisions.py` → `deploy_automation_is_safe`; salbiy testlar 5 ta |
| 2026-09-20 | **TypeScript 7 yonma-yon** (HITL): typecheck native `typescript@7` (`@typescript/native`); `require("typescript")` TS 6 JS API (`@typescript/typescript6`). `typescript@7` yagona paket qilinmaydi — eslint-config-next/typescript-eslint peer `<6.1` va `i18n-runtime-hook.mjs` `transpileModule`. `@types/node` 26 alohida qaror (2026-09-20, runtime Node 22) | `apps/web/package.json`; `tools/i18n-runtime-hook.mjs`; `tools/check_decisions.py` → `typescript_side_by_side`; salbiy testlar 2 ta |
| 2026-09-20 | **`@types/node` major = Node major** (HITL: 4 variant → Node 22 da qolish, #143 yopiladi). Dependabot `26.6.1` ni Node 22 ustiga qo'ymoqchi edi — `skipLibCheck` yolg'on yashil. Node 22 2027-04 gacha Maintenance LTS; 26 Current. Dependabot `@types/node` semver-major'ni ignore qiladi (22.x patch/minor keladi) | `.github/dependabot.yml`; `apps/web/package.json`; `apps/web/Dockerfile`; `.github/workflows/ci.yml`; `tools/check_decisions.py` → `types_node_tracks_runtime`; salbiy testlar 2 ta |
| 2026-09-20 | **Tanlangan kit muzlatilgan** (HITL: fail-toast-freeze). Clipboard rad/xatoda overlay toast `problem.copyFailed` (`CopyControl`, `CommandPalette`, `ShareButton`). Tanlangan kit sathlarini kengaytirish (confirm v2/v3/v6/v7/v8, check v10 44px `big`, copy v9 `burn`) va MiniCal/Notificationsi/countdown jilolash — alohida topshiriqsiz PR emas; kit PR faqat regressiya | `CopyControl.tsx`; `CommandPalette.tsx`; `ShareButton.tsx`; `kit.ts`; `tools/check_decisions.py` → `selected_kit_frozen`; salbiy testlar 2 ta |
| 2026-09-20 | **ESLint 10** (HITL: avval #154, keyin 10 + plugin tuzatish). `eslint-config-next@16.3.5` compiled babel parser ESLint 10 `ScopeManager.addGlobals` bermaydi (o'lchandi: `vitest.config.mts`). Parser = `typescript-eslint`. Next import/jsx-a11y/react pluginlari hali peer ^9 — npm override, lint yashil | `apps/web/eslint.config.mjs`; `apps/web/package.json`; `tools/check_decisions.py` → `eslint_ten_uses_ts_parser`; salbiy testlar 2 ta |
| 2026-09-20 | **pytest 9 + pytest-django 4.14** (HITL: ikkalasi birga). Lock allaqachon `pytest==9.1.1` / `pytest-django==4.14.0` (Nightly shu pinni o'rnatadi); floor `>=8` / `>=4.9` qolgani compile'ni 8.x ga qaytarishi mumkin. Floor va lock birga 9.x da. PR CI pytest yugurtirmaydi — `pr_skips_heavy_ci` | `apps/api/requirements-dev.txt`; `apps/api/requirements-dev.lock`; `tools/check_decisions.py` → `pytest_nine_and_django_plugin`; salbiy testlar 2 ta |
| 2026-09-20 | **react = react-dom = 19.3** (HITL: take-19-3-pair). #163/#158 ni ajratmaslik — mismatch runtime. ViewTransition/Fragment refs shu PR da ishlatilmaydi; Activity/Fast Refresh tuzatishlari keladi | `apps/web/package.json`; `eslint.config.mjs`; `tools/check_decisions.py` → `react_and_dom_stay_paired`; salbiy testlar 2 ta |
| 2026-09-20 | **`?lang=` self-canonical + hreflang** (HITL: hreflang-self). `/?lang=ru` o'ziga canonical; `uz` toza yo'l; 10 til + `x-default`. Filtr query (`contest`) kirmaydi. CDN keshi `?lang=`ni chiqarishda qoladi. Sahifa `generateMetadata` hreflang'ni yutmasin | `locale-alternates.ts`; `layout.tsx`; `proxy.ts` `LANG_PARAM_HEADER`; masala/update/roadmap sahifalari; `tools/check_decisions.py` → `lang_query_self_canonical`; salbiy testlar 2 ta |
| 2026-09-20 | **Sitemap xhtml:link tillari** (HITL: sitemap-hreflang). Har yozuv `url` = toza `uz` yo'l; 10 til + `x-default` `alternates.languages`. 10× alohida `<url>` yo'q | `sitemap.ts` `sitemapEntry`; `sitemapLanguageAlternates`; `tools/check_decisions.py` → `sitemap_locale_xhtml_alternates`; salbiy testlar 2 ta |
| 2026-09-20 | **Vary `Accept-Language` chekkada** (HITL: cf-transform). Next.js 16 in-process `Vary` ni o'chiradi. CF Transform Rule `add` (`set` emas — RSC tokenlari). Mehmon kesh yo'llari (`/`, login, huquqiy) chiqariladi — 100k fragment yo'q. Kesh doirasi kengaytirilmaydi | `tools/cf-vary-accept-language.json`; `tools/cf_vary_apply.py`; `tools/check_decisions.py` → `vary_accept_language_at_edge`; salbiy testlar 2 ta |
| 2026-09-20 | **`/problems` mehmon CDN, tilga bog'liq** (HITL: problems-al). Query'siz GET; `uz` majburiy emas. Origin `Vary: Accept-Language` (`guest-al`); CF Cache Rule `vary.normalize` (10 til) + default `passthrough` (`bypass` Next RSC tokenlarida CDN ni o'chiradi). Kirgan / `rw_locale` / `?page=` / `?lang=` chiqariladi. Worker `problems*` → `problems/*` | `home-cache.ts`; `instrumentation.ts`; `wrangler.toml`; `tools/cf-guest-cache-rule.json`; `tools/cf_guest_cache_apply.py`; `tools/check_decisions.py` → `problems_list_guest_cdn`; salbiy testlar 4 ta |
| 2026-09-20 | **`/users/` noindex** (HITL: keep-users-closed). Sayt ochiq (ADR-0023), profillar yopiq: 974k user (CF import + sinov handle); o'chirish taqiqlangan, shuning uchun «tozalangach ochiladi» emas. Allowlist — alohida HITL | `apps/web/src/app/robots.ts`; `tools/check_decisions.py` → `users_profiles_stay_noindex`; salbiy test 1 ta |
| 2026-09-20 | **Rank ranglari 7 guruh** (HITL: encode-167). 16 pog'ona, CSS da 7 token (`--rw-rank-grey` … `red`); `title.colour_group`. 16 ta `--rw-rank-N` qaytmaydi | `titles.py` `COLOUR_GROUPS`; `globals.css`; `UserName.tsx`; `tools/check_decisions.py` → `rank_colour_groups_not_sixteen_tokens`; salbiy testlar 2 ta |
| 2026-09-20 | **Bosh sahifa CSS inline** (HITL: lh-inline-css). Lighthouse Slow 4G: 2 ta render-blocking `/_next/static/chunks/*.css` (~4.5 + 23 KiB, ~150 ms). App Router da `optimizeCss`/Critters yo'q. `experimental.inlineCss: true` — `<style>`, alohida CSS so'rovi yo'q. Cloudflare `email-decode` alohida | `apps/web/next.config.ts`; `tools/check_decisions.py` → `homepage_css_is_inlined`; salbiy test 1 ta |
| 2026-09-20 | **`owned_paths` kengligi no-star-star** (HITL). `**` / repo-ildiz / bir segmentli katalog globi (`apps/**`) taqiqlanadi; katalog globida kamida ikki segment; bir nechta paketga ruxsat. `package-one` va `files-only` rad | `tools/owned_paths.py`; `docs/10-operations/parallel-agents.md`; `tools/check_decisions.py` → `aop_owned_paths_no_star_star`; salbiy testlar 2 ta |
| 2026-09-20 | **Eski worktree stale-reap** (HITL). Agent o'z `wt/<tool>/` dagi toza, ochiq PR yo'q, yangi manifestsiz daraxtni o'chiradi. `wt/deploy` / `cp/rankwant` / boshqa tool taqiqlanadi | `tools/reap_stale_worktrees.py`; `tools/check_decisions.py` → `aop_stale_worktree_reap`; salbiy testlar 2 ta |
| 2026-09-20 | **Canonical checkout restore-when-idle** (HITL). `cp/rankwant` iflos emas va manifest `workspace` emas bo'lsa, `origin/main` ga ff-only. `git reset --hard` yo'q | `tools/restore_canonical.py`; `tools/check_decisions.py` → `aop_restore_when_idle`; salbiy testlar 2 ta |
| 2026-09-20 | **Docker disk o'smasin.** SHA obraz teglari saqlanmaydi — har deploy VHDX ni to'ldirgan (o'lchandi 15–20 sen: 40→132 GB). Muvaffaqiyatli deploy'dan keyin `tools/prune_docker_disk.sh`: `rankwant/<svc>:<sha>` hammasi, dangling obraz, builder prune (`--all` emas; `volume prune` YO'Q). Compose va `tools/docker-daemon.json`: json-file `max-size: 10m` / `max-file: 3`; builder GC **5 GB** (20 GB emas). Kodni qaytarish = kerakli commitni `deploy.sh` bilan qayta qurish; sxema = `pg-deploy` dump, qo'lda | compose fayllar; `tools/runner/docker-compose.runner.yml`; `tools/prune_docker_disk.sh`; `tools/docker-daemon.json`; `tools/deploy.sh`; `tools/check_decisions.py` → `docker_disk_stays_bounded`; salbiy testlar 4 ta |
| 2026-09-19 | **Avtomatik deploy — birinchi haqiqiy yurish ikki JIM nosozlikni topdi.** Unit tekshiruvlari yashil edi (`check_decisions` 26/26, salbiy testlar 70/70, `bash -n` toza) — va shunga qaramay zanjir **umuman ishlamasdi**. Ikkalasi ham faqat BUTUN zanjir yurganda ko'rinadi, ya'ni unit darajasi ularni o'tkazib yuboradi. ① **Watcher o'zini bloklaydi**: u qulfni oladi (qo'lda deploy bilan to'qnashmasin), keyin `deploy.sh` AYNAN o'sha qulfni so'rab `mkdir` da yiqiladi — o'lchandi: `✗ boshqa deploy ishlayapti (auto-deploy pid 1303, 2026-09-19 01:38 UTC)`. Tuzatish: `RANKWANT_LOCK_HELD=1` bilan qulf **topshiriladi**; `deploy.sh` `mkdir`/`trap` ni o'tkazib yuboradi, qulfni watcher'ning `trap` i bo'shatadi. ② **Yolg'on drift**: qo'lda `check_deploy.sh` → `Hamma konteyner joriy kodda` (exit 0), vazifada → `3 konteyner eskirgan` (exit 1). Sabab Git Bash'ga xos: `sha256sum` ishga tushishda stdin fd ni sozlaydi (`_setmode`), `conhost.exe --headless` esa farzandga stdin **bermaydi** → `sha256sum: failed to set file descriptor text/binary mode: Bad file descriptor` → BO'SH xesh; `check_deploy.sh:161` dagi `2>/dev/null` xatoni yashirgani uchun `shash` bo'sh qoladi va «farq qiladi» chiqadi (api/worker/beat). Tuzatish: watcher `exec 0</dev/null` bilan boshlanadi — butun zanjir (`deploy.sh`, `backup.sh`, `docker`) yaroqli stdin oladi — va `check_deploy.sh` ning o'zi ham `sha256sum "$src" < /dev/null` beradi. ⚠️ Umumiy saboq: **stdin yopiq muhitda MSYS coreutils JIM yiqiladi**, va **qaror dalilsiz qabul qilinmasin** — watcher endi `check_deploy.sh` ning muammoli qatorlarini (`ESKIRGAN`, `MUHIT`, `TEKSHIRILMADI`, `YO'Q`) logga chiqaradi. ⚠️ Env-fayl ham worktree'dan tashqarida (`RANKWANT_AUTO_DEPLOY_ENV`), chunki `.env.public` `.gitignore` da (`.env.*`) | `tools/auto_deploy.sh`; `tools/deploy.sh` → `RANKWANT_LOCK_HELD`; `tools/check_deploy.sh`; `tools/check_decisions.py` → `deploy_automation_is_safe`; `docs/10-operations/deploy-runbook.md`; salbiy testlar 4 ta |

## Darvozalar

Pre-push hook **tor**: `push_guard`, API `ruff`/`format`, web `check_i18n`
va `check_hardcoded`. mypy, pytest, tsc, eslint, salbiy testlar — faqat
CI. 2026-09-18 o'lchov: to'liq hook Windows'da 5.8 daqiqa edi.

Qo'lda to'liq to'plam:

```bash
cd apps/api && uv run ruff check . && uv run ruff format --check . && uv run mypy . && env CELERY_EAGER=1 uv run pytest -q -n 4
```

```bash
cd apps/web && npm run lint && npm run typecheck && npm run build
```

```bash
python3 tools/check_i18n.py && python3 tools/check_contrast.py && python3 tools/check_docs.py && python3 tools/check_contract.py
```

Endpoint qo'shilsa yoki serializer o'zgarsa, sxemani yangilash **shart** —
aks holda CI yiqiladi:

```bash
cd apps/api && uv run python manage.py spectacular --file openapi/schema.yml
```

Kod yoki compose yangi muhit o'zgaruvchisini o'qisa, u `.env.example` ga
yoziladi (sir bo'lsa qiymatsiz) — aks holda `tools/check_env_example.py`
CI da yiqiladi.

`pytest -n 4` — `auto` EMAS: runner shu mashinada, jonli preview bilan
yonma-yon ishlaydi.

`CELERY_EAGER=1` CI pytest uchun **shart**. Busiz task navbatga yoziladi
va test javobni kutib qotadi; `settings.py` uni `CELERY_TASK_ALWAYS_EAGER`
ga o'giradi. O'lchangan farq: 14m54s → 1m57s.

## Preview

```bash
docker compose -p rankwant --env-file .env.public -f docker-compose.yml -f docker-compose.public.yml up -d --build --wait
```

**`-p rankwant` tushib qolmasin.** `docker-compose.yml` da `name:` kaliti
yo'q, ya'ni loyiha nomi joriy KATALOG nomidan olinadi. Worktree ichidan
bayroqsiz chaqirilsa, compose jimgina alohida stack va **alohida baza**
ko'taradi — xato bermaydi, shunchaki boshqa ma'lumot ko'rsatadi. Faqat
`docker-compose.ci.yml` o'z nomini (`rankwant-ci`) o'zi belgilaydi.

Mashina dual-boot (Linux + Windows), har tizimda preview'ning o'z bazasi bor.
Tizim almashtirishdan **oldin** `tools/handoff.sh out` (Linux) yoki
`tools\handoff.ps1 out` (Windows), yuklangandan keyin `in` — aks holda ikki
baza jimgina ajralib ketadi. Protokol: [10-operations](docs/10-operations/README.md)
§ «Ikki tizimli preview».
Linux'da `in` ni yuklanishda `rankwant-handoff.service` o'zi chaqiradi va
`tools/handoff.sh switch` bitta buyruqda `out` + Windows'ga qayta yuklashni
bajaradi. Windows'da bunday `switch` yo'q: `out`, keyin qayta yuklash —
EFI tartibi Ubuntu'ni birinchi qo'yadi. U yerda avtomatik `in` uchun logon
vazifasi bir marta ro'yxatga olinadi (hujjatda).

**Servis nomini ro'yxatlab qisqartirmang.** Django kodi API'da ham,
`worker` da ham, `beat` da ham ishlaydi; faqat `api` ni qayta qursangiz
worker eski kodda qoladi. O'lchangan oqibat: judge yangi verdikt
yubordi, eski worker uni tanimay `IE` ga aylantirdi va sabab faqat
worker logida ko'rindi.

Portlar: web `127.0.0.1:8300`, API `127.0.0.1:8301`. `ALLOWED_HOSTS`
tufayli curl'ga host sarlavhasi kerak, aks holda bo'sh 400 keladi:

```bash
curl -H 'Host: rankwant.uz' http://127.0.0.1:8301/api/v1/health/
```

## Bake-off (judge izolyatsiyasi)

Ishga tushirishdan oldin `worker` va `beat` **to'xtatilishi shart** —
`drain_results` natijalarni harness'dan oldin olib ketadi va hisobot
«XAVFSIZLIKDAN O'TMADI» deb yozadi, aslida sandbox soz:

```bash
docker compose -p rankwant --env-file .env.public -f docker-compose.yml -f docker-compose.public.yml stop worker beat
IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' rankwant-redis-1)
apps/api/.venv/bin/python services/bakeoff/harness/runner.py --worker judge-go --redis redis://$IP:6379/0
docker compose -p rankwant --env-file .env.public -f docker-compose.yml -f docker-compose.public.yml start worker beat
```

Redis host portiga chiqarilmagan — shuning uchun konteyner IP'si olinadi.
`rankwant-redis-1` nomi ham aynan `-p rankwant` bo'lgandagina topiladi:
konteyner nomini compose loyiha nomidan yasaydi. Bayroq tushsa
`docker inspect` bo'sh qaytaradi va `IP` o'zgaruvchisi jimgina bo'sh
qoladi.

## Ish uslubi

Issue ishlatilmaydi — **PR asosida**. Vazifa qo'shish
kerak bo'lsa branch va PR ochiladi, tracker'ga ticket yozilmaydi.

Til: izoh va docstring inglizcha, mavjud hujjat o'z tilida — to'liq qoida
[CONTRIBUTING § Til](CONTRIBUTING.md#til). Mavjud izohlarni tarjima qilmang.

CI, Security va Nightly `ubuntu-latest` da (public repo — standard
runner daqiqasi $0). Deploy `tools/deploy.sh` / `deploy.yml` shu
mashinada qoladi. PR'da Security yo'q. Smoke, E2E, bake-off, language
matrix va API pytest — Nightly.

**`main` ga to'g'ridan-to'g'ri push'ni hook rad etadi** (`tools/push_guard.py`).
GitHub bu tarifda branch protection bermaydi (403), ya'ni server hech narsani
to'xtatmaydi — qoidani faqat shu hook ushlab turadi. Tartib: branch → PR →
CI yashil → GitHub'da merge. `RANKWANT_ALLOW_MAIN_PUSH=1` va `--no-verify` —
agent uchun faqat Saidakbar akaning aniq ruxsati bilan.

**Commit qilishdan oldin identity'ni tekshiring:**
`git config --show-origin user.email`. 2026-09-16 da salbiy test haqiqiy
repoda ishlab `.git/config` ga `test@example.com` yozib qo'ygan va 42 commit
shu nom bilan ketgan (tarix `.mailmap` da to'g'rilangan). Hook endi soxta
muallifli commit'ni ham, ifloslangan config'ni ham rad etadi; salbiy
to'plam esa haqiqiy repo config'i o'zgarsa o'zi yiqiladi.
