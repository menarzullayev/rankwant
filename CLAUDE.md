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
| 2026-09-17 | CI faqat self-hosted runner — GitHub bepul daqiqalari tugagan, hosted runner taklif qilinmaydi | har `runs-on: [self-hosted, rankwant]` |
| 2026-09-17 | CI runner — Docker Desktop'dagi `rankwant-ci-runner` konteyneri (`rankwant` label; ish papkasi volume'da; `RankWant CI Runner Watchdog` qo'riqlaydi). WSL runner 2026-09-17 da butunlay olib tashlangan. `rankwant-container` label'ini faqat `runner-selftest.yml` ishlatadi | `tools/runner/` → `RUNNER_LABELS`; `tools/check_decisions.py` → `TRIAL_RUNNER` |
| 2026-09-18 | Ikkinchi runner (`rankwant-ci-runner-2`, alohida volume, compose profile `second`, 4 CPU / 4 GB). PR'da Security va smoke yo'q — main push + cron / `workflow_dispatch` / deploy chaqiruvi to'liq. Recreate bitta servisni `down` qilmaydi | `security.yml` `on:`; `ci.yml` smoke `if:`; `docker-compose.runner.yml`; `recreate.sh --second`; `runner_watchdog.py` |
| 2026-09-16 | Deploy qo'lda (`tools/deploy.sh`); 2026-09-17 dan skript `web` ni ham quradi — bitta deploy hamma servisni yangilaydi | `deploy.yml` faqat `workflow_dispatch`; `tools/deploy.sh` → `SERVICES` |
| 2026-09-17 | Agentlar production'ni **`main` CI yashil bo'lsa** so'ramasdan deploy qiladi; bir vaqtda faqat bitta deploy | `tools/deploy.sh` → `tools/check_deploy_gate.py` + qulf (`--skip-ci-gate` faqat Saidakbar aka ruxsati bilan) |
| 2026-09-17 | Repo aralash tilda, migratsiya yo'q | `CONTRIBUTING.md` § Til |
| 2026-09-17 | `cp/` faqat RankWant uchun; tadqiqot hujjatlari `docs/research/` da | `cp/README.md` (repo'dan tashqarida) |
| 2026-09-18 | Sayt qidiruv tizimlariga **ochiq**, AI kraulerlarga **yopiq**; `/users/` sinov profillari tozalanmaguncha yopiq ([ADR-0023](docs/07-adr/0023-indexing-and-ai-crawlers.md)) | `apps/web/src/lib/site.ts` → `SITE_INDEXABLE`; `apps/web/src/app/robots.ts` → `AI_CRAWLERS` |
| 2026-09-18 | Sidebar, top bar, header va footer linklari faqat **niyatda** prefetch qiladi (hover, fokus, teginish) — ko'rinishi bilan emas: tashrif boshiga ~130–150 ms server CPU edi ([profil](docs/research/2026-09-18-homepage-profile/REPORT.md)) | `apps/web/src/components/ui/IntentLink.tsx`; `tools/check_decisions.py` → `NAV_CHROME` |
| 2026-09-18 | Bosh sahifa `<main>` havolalari ham faqat **niyatda** prefetch qiladi. 1000 tashrif/s da ko'rinish-prefetch (7 RSC) origin'ni `EOF` qildi; chrome allaqachon niyatda edi | `apps/web/src/app/page.tsx`; `ButtonLink intent`; `tools/check_decisions.py` → `HOME_MAIN` |
| 2026-09-18 | Brauzerga lug'at **alohida keshlanadigan faylda** (`/i18n/<til>.js?v=<hash>`, `immutable`) boradi, sahifa ichida emas: u har HTML'ning 72 KB'i va render CPU'sining 32% i edi ([profil](docs/research/2026-09-18-homepage-profile/REPORT.md)) | `apps/web/src/app/i18n/[file]/route.ts`; `apps/web/src/app/layout.tsx` → `dictionaryUrl`; `apps/web/src/proxy.ts` matcher |
| 2026-09-18 | `User` ga Codeforces/Robocontest/KEP bilan tenglik uchun **21 maydon** (46 → 67). 13 tasi (`plan`, `postal_*`, `device_fingerprint`…) funksiyasidan **oldin** qo'shilgan — «ishlatilmaydi» deb olib tashlanmaydi ([ADR-0024](docs/07-adr/0024-user-competitor-parity-fields.md)) | `apps/api/core/models.py` → `User`; `tools/check_decisions.py` → `PARITY_USER_FIELDS` |
| 2026-09-18 | Header **320 px** ga sig'adi — eng tor qo'llab-quvvatlanadigan ekran. Til tanlagich `sm` dan pastda to'liq nom o'rniga **kod** ko'rsatadi (`kaa`, kichik harf), kirish yorlig'i esa o'ralmaydi. O'lchandi (jonli brauzer): to'liq nom bilan 320 px da **15 px** (chiqqan) va **59 px** (kirgan), 375 px da kirgan holatda **10 px** toshardi; kod bilan hammasi **0 px** | `apps/web/src/layout/LocaleSwitch.tsx`; `apps/web/src/layout/UserMenu.tsx`; `tools/check_decisions.py` → `mobile_header_fits_narrow_screen` |
| 2026-09-18 | Mobil navigatsiya paneli **e'lon qilinadi, fokuslanadi va yopiladi**: trigger holatni aytadi (`aria-expanded` + `aria-controls`), panel ochiq holatda nomli dialog (`role="dialog"`, `aria-modal`, `aria-label`), fokus ichkariga kiradi va ochgan tugmaga qaytadi, `Esc` yopadi, orqa fon scroll qilmaydi. O'lchandi (jonli brauzer, 390×844×2): ilgari `aria-expanded` **ochiq holatda ham `null`**, panelda rol/nom yo'q, fokus `body` da qolardi, `body` overflow `visible`, haqiqiy `Esc` panelni yopmasdi | `apps/web/src/layout/AppHeader.tsx`; `apps/web/src/layout/AppSidebar.tsx`; `apps/web/src/context/SidebarContext.tsx`; `apps/web/src/layout/AppShell.tsx`; `tools/check_decisions.py` → `mobile_drawer_is_accessible` |
| 2026-09-18 | Bosh sahifa KPI to'ri `lg` da **4 ustun** (1024 px dan), tor ustunda raqam esa **24 px** ga tushadi (`lg:text-2xl`, `xl` da yana 30 px). O'lchandi (1024×768, jonli sahifa): 2+2 da keyingi bo'limdan faqat **38 px** ko'rinardi, 4 ustunda **216 px** va sahifa **178 px** qisqaroq. 3 ustunli pog'ona **o'lchov bilan rad etildi** — 4 karta baribir 2 qatorni egallaydi (vertikal yutuq **0 px**) va 4-karta yolg'iz qoladi. Tor ustunning narxi bor: 30 px bold raqamda har xona ~17.2 px, 4 ustunli kartada ichki kenglik **121 px** — 8 xonali sanoq toshadi, shuning uchun raqam kichrayadi | `apps/web/src/app/page.tsx`; `apps/web/src/components/ui/Card.tsx` → `valueClassName`; `tools/check_decisions.py` → `kpi_grid_steps_at_lg` |

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

CI self-hosted runner'da (GitHub'ning bepul daqiqalari tugagan — hosted
taklif qilinmaydi). 2026-09-18 dan ikkita konteyner bir xil `rankwant`
label'ida; PR'da Security va smoke yo'q. Ikkinchi runner hali register
qilinmagan bo'lsa, navbat yana ketma-ket.

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
