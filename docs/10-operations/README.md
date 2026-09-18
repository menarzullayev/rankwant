# 10. Quality & Operations

**STATUS:** draft (2026-09-06) — siyosatlar yozilgan.
✅ **Runbook yozildi (2026-09-16):** [deploy-runbook.md](deploy-runbook.md) —
migration tartibi, env kalitlari, ma'lum xatolar, reboot va zaxira.

Nima **hozir** bilinadi: deploy topologiyasi, siyosatlar va incident turlari — ular arxitektura va ADR'lardan kelib chiqadi.
Nima **hali bilinmaydi**: hosting provayderi, real narxlar.
(Runbook qadamlari endi bor — [deploy-runbook.md](deploy-runbook.md).)

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
| `robots.txt` | Bizniki beriladi — `rankwant.uz` zonasida Cloudflare'ning managed robots.txt'i o'chiq. **2026-09-18 dan qidiruvga ochiq, AI kraulerlarga yopiq** ([ADR-0023](../07-adr/0023-indexing-and-ai-crawlers.md)): `apps/web/src/lib/site.ts` da `SITE_INDEXABLE = true`, `robots.txt` `*` ga ruxsat beradi va `Sitemap: https://rankwant.uz/sitemap.xml` qatorini qaytaradi; `AI_CRAWLERS` ro'yxatidagilar (`apps/web/src/app/robots.ts`) `Disallow: /` oladi; `/users/` 10 001 ta `neytron_*` sinov profili tozalanmaguncha yopiq. 2026-09-15 dagi yopiqlik sababi: kraulerlar 14 soatda 246 ming so'rov yubordi (82% GPTBot, 16% Google) va Workers'ning kunlik 100 ming limiti tugardi. Search Console (domen resursi) va Yandex Webmaster'da DNS TXT orqali tasdiqlangan (2026-09-11) — apex'dagi `google-site-verification` va `yandex-verification` TXT'larini o'chirmang; deploy'dan keyin sitemap ikkalasiga qayta yuboriladi |
| Cloudflare WAF qoidasi | AI kraulerlarni chekkada to'sadi (ADR-0023). Dashboard: **Security → WAF → Custom rules → Create rule**, nom `Block AI crawlers`, amal **Block**. Ifoda: `lower(http.user_agent) contains "gptbot"` va shu uslubda `chatgpt-user`, `oai-searchbot`, `claudebot`, `claude-user`, `claude-searchbot`, `anthropic-ai`, `ccbot`, `google-extended`, `perplexitybot`, `perplexity-user`, `bytespider`, `amazonbot`, `applebot-extended`, `meta-externalagent`, `facebookbot`, `diffbot`, `imagesiftbot`, `timpibot`, `youbot`, `cohere-ai` — hammasi `or` bilan. ⚠️ `google-extended` va `applebot-extended` — o'quv agentlari, Googlebot va Applebot'ning o'zi bunga tushmaydi. AI Crawl Control'ning o'z Block amali pullik tarifda; bepulda shu custom rule o'sha ishni bajaradi (5 tagacha qoida bepul). Qoida zonada, repo'da emas — zona qayta tuzilsa qayta yaratiladi |

### Ikki tizimli preview (dual-boot)

Preview mashinasi dual-boot: bitta diskda Linux va Windows. Sayt qaysi tizim
yoniq bo'lsa, o'shandan ishlaydi, lekin har tizimning **o'z** bazasi va
MinIO'si bor. Ma'lumot tizimdan tizimga Cloudflare R2 dagi eksport orqali
ko'chadi; R2 dagi `state.json` hozir qaysi tizim live ekanini saqlaydi.
Ikkala tomon bitta tunnelning ikki ulagichi, ya'ni DNS o'zgarmaydi.

| Qachon | Linux | Windows |
| ------ | ----- | ------- |
| Boshqa tizimga o'tishdan **oldin** | `tools/handoff.sh out` | `tools\handoff.ps1 out` |
| Tizim yuklangandan keyin | `tools/handoff.sh in` | `tools\handoff.ps1 in` |
| Holatni ko'rish | `tools/handoff.sh status` | `tools\handoff.ps1 status` |

- `out` tunnelni to'xtatadi (sayt `services/maintenance-worker` sahifasiga
  o'tadi), yozuvchi servislarni to'xtatadi, Postgres dump va MinIO arxivini
  R2 ga yuklaydi, hajmini solishtiradi va `state.json` ga «hech kim live
  emas» deb yozadi. U faqat live tizimda ishlaydi — eskirgan tomon yangi
  eksport ustiga yoza olmaydi.
- `in` R2 dagi eksport lokal bazadan yangi bo'lsa uni import qiladi (baza
  bo'shdan tiklanadi: `--clean` bu tomondagi ortiqcha jadvallarni
  tashlamasdi), stekni `--build` bilan ko'taradi, `/api/v1/health/` ni kutadi
  va faqat shundan keyin tunnelni yoqadi.

**Asosiy qoida:** boshqa tizim live bo'lib qolgan bo'lsa (masalan `out`
unutilgan), `in` rad etadi. Aks holda ikkala tomonda yangi hisob va
urinishlar paydo bo'lib, ikki baza jimgina ajralib ketadi — ularni
birlashtiradigan vosita yo'q. To'g'ri yo'l — o'sha tizimga qaytib `out`
qilish. Qaytishning iloji bo'lmasa, `in --force` (`-Force`): o'sha tomonning
oxirgi eksportdan keyingi ma'lumoti yo'qoladi.

R2 da oxirgi ikkita eksport saqlanadi (bepul tarif 10 GB), lokal nusxadan
faqat joriysi.

Bir martalik sozlash:

1. R2 da `rankwant-handoff` bucket va faqat shu bucket uchun *Object Read &
   Write* API token. Qiymatlar `.env.handoff.example` bo'yicha `.env.handoff`
   ga — ikkala tizimda bir xil.
2. Sirlar R2 orqali **ko'chirilmaydi** — bir marta qo'lda (masalan USB
   orqali) Windows'ga: `.env.public` repo ildiziga; `/etc/cloudflared/config.yml`
   va tunnel kaliti (`<tunnel-id>.json`) `%USERPROFILE%\.cloudflared\` ga.
   `config.yml` dagi `credentials-file:` Windows yo'liga almashtiriladi.
3. Windows: `winget install --id Cloudflare.cloudflared`. U yerda tunnel xizmat
   emas, `handoff.ps1` boshqaradigan oddiy jarayon — Docker Desktop baribir
   foydalanuvchi tizimga kirgandagina ishlaydi.
4. Linux: `sudo systemctl disable cloudflared` — tunnel yuklanishda o'zi
   yoqilmasin, faqat `in` tekshiruvidan keyin. Stek `restart: unless-stopped`
   bilan o'zi ko'tariladi, lekin tunnelsiz tashqariga chiqmaydi.
5. Hozir live bo'lgan tizimda bir marta: `init`.

#### Avtomatik ko'tarilish

`in` ni qo'lda yozish shart emas: har tizimda uni yuklanish jarayoni
chaqiradi. Bu xavfsiz, chunki egalik boshqa tizimda bo'lsa `in` rad etadi
— sayt texnik ishlar sahifasida qoladi.

Linux (bir marta o'rnatiladi):

```bash
sed -e "s#__REPO__#$PWD#g" -e "s#__USER__#$USER#g" \
  tools/systemd/rankwant-handoff.service |
  sudo tee /etc/systemd/system/rankwant-handoff.service >/dev/null
sudo systemctl enable rankwant-handoff.service
```

Windows (PowerShell'da bir marta):

```powershell
$repo = (git rev-parse --show-toplevel) -replace '/', '\'   # repo ichidan chaqiring
$action = New-ScheduledTaskAction -Execute 'powershell.exe' `
  -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$repo\tools\handoff.ps1`" in" `
  -WorkingDirectory $repo
$trigger = New-ScheduledTaskTrigger -AtLogOn
$trigger.Delay = 'PT2M'   # Docker Desktop kirgandan keyin ko'tariladi
Register-ScheduledTask rankwant-handoff-in -Action $action -Trigger $trigger -RunLevel Highest
```

`in` faqat **tizim yuklanganda** ishlaydi. Ish paytida tunnel yiqilsa (masalan
jarayon o'chirilsa yoki ulanish uzilsa) sayt texnik ishlar sahifasida qolib
ketadi — 2026-09-13 da aynan shunday bo'ldi. Buning uchun alohida monitor bor:

```powershell
$repo = (git rev-parse --show-toplevel) -replace '/', '\'   # repo ichidan chaqiring
$action = New-ScheduledTaskAction -Execute 'powershell.exe' `
  -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$repo\tools\monitor.ps1`"" `
  -WorkingDirectory $repo
$trigger = New-ScheduledTaskTrigger -Daily -At '00:00'
$trigger.Repetition = (New-ScheduledTaskTrigger -Once -At '00:00' `
  -RepetitionInterval (New-TimeSpan -Minutes 5) `
  -RepetitionDuration (New-TimeSpan -Hours 24)).Repetition
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries `
  -DontStopIfGoingOnBatteries -StartWhenAvailable `
  -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 4)
Register-ScheduledTask 'RankWant Tunnel Monitor' -Action $action `
  -Trigger $trigger -Settings $settings -Force
```

Monitor har 5 daqiqada **ikkita** ommaviy manzilni tekshiradi —
`https://rankwant.uz/` va `https://rankwant.uz/api/v1/health/`.

⚠️ **Ikkinchisi 2026-09-15 dagi avariyadan keyin qo'shildi.** O'sha kuni sayt
ildizi `200` qaytarardi, API esa `503`: sahifalar ochilardi, lekin brauzerdagi
har bir API chaqiruvi yiqilardi — kirish, yuborish, jadval. Monitor faqat
ildizni tekshirgani uchun **YASHIL qolgan** va avariya o'z-o'zidan tuzalmagan.

Ikkalasi ham `200` bo'lsa boshqa hech narsa o'lchanmaydi (docker ham, R2 ham).
Biror manzil yiqilsa monitor avval egalikni, keyin qatlamni aniqlaydi:

| Qatlam | Nimadan bilinadi | Nima qiladi |
| ------ | ---------------- | ----------- |
| `OK` | ikkala manzil ham `200` | jurnalga bitta qator |
| `NOT LIVE` | R2 `owner` boshqa tizimda | **hech narsa** — yiqilish kutilgan (handoff `out` konteynerlarni to'xtatgan) |
| `UNMEASURED` | R2 yoki docker o'qilmadi | **hech narsa** — qatlamni ajratib bo'lmaydi, sayt holati haqida xulosa yo'q |
| `CONTAINER DOWN` | konteyner ishlamayapti yoki yo'q | ogohlantiradi |
| `DEAD BRIDGE` | konteyner **ichida** `/health` `200`, host portida `000` | **faqat o'sha konteynerni** `docker restart` qiladi |
| `CONTAINER UNHEALTHY` | docker healthcheck `unhealthy`, ichkarida ham `200` yo'q | ogohlantiradi — restart davo emas |
| `APP DOWN` | konteyner ishlayapti, ichkarida javob yo'q | ogohlantiradi — ilova xatosi |
| `TUNNEL DOWN` | origin `200`, tunnel jarayoni yo'q | tunnelni qayta ko'taradi |
| `EDGE` | origin `200`, tunnel bor, ommaviy URL yiqiq | ogohlantiradi — ayb Cloudflare / Worker / DNS da |

`DEAD BRIDGE` — o'sha avariyaning haqiqiy sababi. Konteyner darajasidagi
**hamma** signal yashil edi (docker `healthy`, ichkarida `/health` `200`), host
porti esa TCP ulanishni qabul qilib HTTP `000` qaytarardi. Ya'ni "port band
emasmi" degan tekshiruv ham yashil bo'lardi; yagona ishonchli farq —
**ichkarida `200`, tashqarida `000`**. Shuning uchun qaror TCP ga emas, ichki
probe'ga tayanadi.

⚠️ `docker restart` obrazni **qayta qurmaydi**, shuning uchun «`api`, `worker`
va `beat` ni birga qayta quring» qoidasi bu yerga tegishli emas — u faqat
`--build` ga taalluqli. Bu joyni `compose up --build` ga aylantirmang: u butun
stekni to'xtatadi va avariyani uzaytiradi.

Origin manzillariga `Host: rankwant.uz` sarlavhasi yuboriladi — usiz
`ALLOWED_HOSTS` bo'sh `400` qaytaradi va monitor buni «origin yiqilgan» deb
o'qirdi.

Egalik tekshiruvi `handoff.ps1` bilan bir xil R2 `state.json` dan o'qiladi. R2
javob bermasa `unknown` deb qaraladi va **hech narsa tiklanmaydi** (xavfsiz
tomon). Holat `.handoff/monitor.log` ga, muammo esa
`.handoff/monitor-alert.txt` ga yoziladi.

Chiqish kodi `check_workers.sh` va `check_ci.sh` bilan bir xil shartnomada:
`0` — sog'lom yoki live emas, `1` — muammo, `2` — o'lchab bo'lmadi. **`2` ni
yashil deb o'qib bo'lmaydi.**

`OK` holati ham jurnalga yoziladi (ilgari yozilmasdi). Sabab: `api` konteyneri
HTTP so'rovlarni umuman jurnalga yozmaydi (o'lchandi — har qanday oynada 0
qator), ya'ni uzilish qancha davom etganini boshqa hech qayerdan aniqlab
bo'lmaydi. Kuniga ~288 qator, ~26 KB.

Monitor mantig'i `tools/check_negative.py` dagi `monitor` guruhi bilan
qo'riqlanadi: u `monitor.ps1` ni stub muhit o'zgaruvchilari orqali haydaydi,
ya'ni tarmoqqa ham, docker'ga ham chiqmaydi va hech narsani qayta ishga
tushirmaydi.

Linux tomonda bu kerak emas: u yerda tunnel `cloudflared` systemd xizmati
(`Restart=always`) va `handoff.sh` uni `systemctl` bilan boshqaradi.

Boshqa tizimga o'tish bitta buyruq: `tools/handoff.sh switch` — `out` ni
bajaradi, GRUB'ning bir martalik tanlovini Windows'ga qo'yadi va qayta
yuklaydi. Doimiy yuklanish tartibi o'zgarmaydi, ya'ni keyin yana Linux
birinchi bo'lib turadi.

Windows tomonida `switch` yo'q va kerak emas: `out` dan keyin oddiy qayta
yuklash EFI tartibi bo'yicha yana Ubuntu'ni (GRUB) beradi, Linux esa o'zini
unit bilan ko'taradi. Ishni har ikki tizimda `status` bilan boshlash qulay —
u egalik kimda va oxirgi eksport qaysi ekanini bir qatorda ko'rsatadi.

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

👉 **Qadam-ma-qadam buyruqlar: [deploy-runbook.md](deploy-runbook.md).**
Quyidagilar — qoidalar, buyruqlar emas.

1. **Live contest paytida deploy YO'Q.** Bu qattiq qoida — contest davomida verdict yoki standings o'zgarishi natijani buzadi. Deploy oynasi contest jadvalidan tekshiriladi.
2. Migration'lar oldinga mos: `add column → backfill → switch → drop`, alohida deploylarda ([08](../08-technical-spec/README.md) 🔒)
3. Judge worker'lar **navbatni bo'shatib** to'xtaydi (graceful drain) — ishlayotgan submit yo'qolmaydi
4. Rollback: oldingi image tegi; migration rollback **rejalashtirilgan** bo'lishi shart
5. **Kod o'zgargach deploy qilinadi — CI yashilligi deploy qilinganini bildirmaydi.** Pastdagi bo'limga qarang.

### Eskirgan konteyner — CI ko'rmaydigan nosozlik sinfi

`tools/ci-local.sh` **manba kodni** vaqtinchalik konteynerda sinaydi
(`rankwant-api-dev:<hash>`), lekin **ishlab turgan** `rankwant-web` /
`rankwant-api` image'larini umuman tekshirmaydi. Ya'ni CI to'liq yashil
bo'lib turib, sayt eski kodni ko'rsatishi mumkin.

Bu **2026-09-13 da uch marta** sodir bo'ldi — bitta kunda:

| Alomat | Sabab |
| ------ | ----- |
| `/kirish` → 404 | web image D18/D20 kodidan oldin qurilgan |
| Admin parol to'g'ri, lekin kirilmaydi | api image'i `username` shartnomasida qolgan |
| Fon vazifalari jimgina ishlamasligi | worker/beat ham eski image'da edi |

Shuning uchun har deploy'dan keyin:

```
bash tools/check_deploy.sh
```

Skript solishtirishni **sanaga emas, kontentga** qarab qiladi:

| Konteyner | Tekshiruv |
| --------- | --------- |
| `api`, `worker`, `beat` | `core/serializers.py` sha256 — manba va konteyner ichidagi fayl bir xilmi |
| `web` | image yorlig'i `org.rankwant.git-sha` ↔ `git rev-parse HEAD` |
| `judge` | kompilyatsiya qilingan binary — hash manbada yo'q, faqat holat ko'rsatiladi |

Sana bo'yicha solishtirish **yaroqsiz**: fayl tahrirlanmasa ham `touch`
uni «yangi» qiladi (test tiklash, `git checkout`, muharrir saqlashi) va
ishlab turgan kod aynan bir xil bo'lsa ham «eskirgan» degan yolg'on javob
chiqadi. Shu sababli label'lar `apps/*/Dockerfile` da build vaqtida
yoziladi.

```bash
SHA=$(git rev-parse HEAD)
docker compose -p rankwant --env-file .env.public \
  -f docker-compose.yml -f docker-compose.public.yml build web api worker beat \
  --build-arg GIT_SHA="$SHA" --build-arg BUILT_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
docker compose -p rankwant --env-file .env.public \
  -f docker-compose.yml -f docker-compose.public.yml up -d --no-deps web api worker beat
```

Chiqish kodi `0` — hamma konteyner joriy kodda; `1` — kamida bittasi
eskirgan (tuzatish buyruqlari chop etiladi).

### Eskirgan konteyner EMAS: web↔api maydon shartnomasi (2026-09-13)

Yuqoridagi tekshiruv «konteyner manbadan eskimi» degan savolga javob
beradi. Lekin **ikkala tomon ham joriy kodda bo'lib, shartnoma baribir
buzilgan** holat bor — va u eng xavflisi, chunki hech qanday asbob
qichqirmaydi.

**Nima bo'ldi.** Ro'yxatdan o'tish (3-qaror) 1-qadamda faqat to'rt
maydon yuboradi: `email`, `password`, `terms_accepted` (+ ixtiyoriy
`marketing_opt_in`). `username`, `display_name`, `country`, `region`
2-qadamga (`/qoshimcha-malumot`) ko'chirilgan. `extra_kwargs` da
`display_name`, `country`, `region` uchun `required: False` yozilgan —
**`username` uchun yozilmagan**. U yerda faqat `validators: []` turardi.

Nima uchun bu yetarli emas: `username` model maydonida `unique=True`
bor, ya'ni DRF `ModelSerializer` uni `required=True, allow_blank=False`
qilib yasaydi. `validators: []` faqat validatorlar ro'yxatini
tozalaydi, `required`/`allow_blank` ga tegmaydi. Natija — har bir
ro'yxatdan o'tish urinishi:

```
POST /api/v1/auth/register/   {"email": "...", "password": "...", "terms_accepted": true}
→ 400 {"error": {"details": {"username": ["Ushbu maydon to'ldirilishi shart."]}}}
```

Ya'ni **sayt orqali hech kim ro'yxatdan o'ta olmasdi**. O'lchandi
(konteyner ichida, `R().fields`):

```
username         required=True  allow_blank=False   ← buzilgan
display_name     required=False allow_blank=True
country          required=False allow_blank=True
region           required=False allow_blank=True
```

**Nega sezilmadi.** Uch qavat himoya bir sababdan ko'r bo'lgan:

| Qavat | Nega tutmadi |
| ----- | ------------ |
| `pytest` | mavjud testlar faqat `errors["email"]` ni tekshirardi; `username` xatosi o'sha javobda jimgina yonma-yon turardi |
| Qo'lda sinov | API'ni to'g'ridan-to'g'ri chaqirgan skript `username` yuborardi — ya'ni ishlayverardi |
| `check_deploy.sh` | konteyner manbadan eski emas edi — nomuvofiqlik manbaning O'ZIDA |

**Tuzatish** — bitta qator (`apps/api/core/serializers.py`):

```python
"username": {"required": False, "allow_blank": True, "validators": []},
```

**Qo'shilgan to'siqlar** — bu sinf qaytmasligi uchun uch joyda:

| Joy | Nima qiladi |
| --- | ----------- |
| `tools/check_contract.py` → `check_register_contract()` | web 1-qadamda yuboradigan maydonlarni o'qib, API ularni ixtiyoriy deb bilishini talab qiladi |
| `apps/api/tests/test_auth.py` | `test_username_siz_royxatdan_otish_ishlaydi`, `test_username_bolsh_qiymat_bilan_ham_ishlaydi`, `test_username_berilsa_saqlanadi` |
| shu hujjat | nosozlik sinfining tavsifi |

⚠️ Tekshiruv **`required: False` va `allow_blank: True` ikkalasini**
talab qiladi. Faqat bittasi yetmaydi: `required: False` bo'lsa ham
`allow_blank: False` qolsa, eski mijozning bo'sh satri
(«This field may not be blank») rad etiladi.

⚠️ `check_register_contract()` ichida `extra_kwargs` **qavslar sanog'i**
bilan o'qiladi (`_brace_block`), regex bilan emas: ichma-ich lug'at
(`"email": {"required": True}`) bor, ya'ni non-greedy `.*?` birinchi
ichki `}` da to'xtab tanani chala o'qiydi va tekshiruv jimgina bo'sh
qolardi.

## Backup

| Nima                | Chastota           | Saqlash | Tiklash sinovi |
| ------------------- | ------------------ | ------- | -------------- |
| Postgres            | **oylik** `pg_dump` | 95 kun (vazifa) | **har yurishda (avtomatik)** |
| Offsite (R2)        | **o'chiq** — faqat lokal (qaror 2026-09-17) | — | — |

| S3/R2 test data     | versiyalash yoqilgan | doimiy | choraklik      |
| Qvant ledger        | Postgres ichida    | —       | audit so'rovi bilan |

Tiklash sinovi o'tkazilmasa, backup **yo'q deb hisoblanadi**.

✅ **O'tkazildi: 2026-09-17** (`bash tools/backup.sh --restore-test`) —
17 MB dump **9 soniyada** alohida `restore_test` bazasiga tiklandi:
`core_user` 10 033 · `judging_attempt` 384 530 · `problems_problem` 2 096 ·
`qvant_qvanttransaction` 13 314 · `problems_testcase` 2 486 qator,
havolalar butun. Jonli bazaga tegilmadi (`restore_test` tashlandi).

✅ **2026-09-17 dan sinov HAR yurishda AVTOMATIK** o'tkaziladi: doktrina uni
«choraklik majburiy» derdi, lekin u butunlay qo'lda edi va bir marta ham
o'tkazilmagan. 9 soniya arzon, shuning uchun zaxira **yaratilgan paytda**
tekshiriladi. Log qatorida `restore=ok|skip|YIQILDI`; sinov yiqilsa skript
ham yiqiladi — tiklanmaydigan zaxira zaxira emas.

### Har yurishda nima tekshiriladi (uch qatlam)

| Qatlam | Nima ushlanadi | Qanday |
|---|---|---|
| Dump butunligi | arxiv kesilgan; dump o'rtada uzilgan | `gzip -t` + `PostgreSQL database dump complete` qatori |
| **MinIO to'liqligi** | arxiv bo'sh yoki chala | obyekt soni arxivdan **oldin** o'lchanadi, keyin `arxiv >= oldingi` |
| Tiklash | dump haqiqatan tiklanadimi | alohida `restore_test` bazasi, 5 jadval + havolalar |

⚠️ **MinIO tekshiruvi 2026-09-17 da qo'shildi.** Ilgari faqat
`tar tzf >/dev/null` bor edi — ya'ni «o'qiladigan tar», xolos: bo'sh yoki
chala arxiv ham o'qiladi. Loyiha tarixida aynan shunday holat bo'lgan
(mount yo'qligi sababli «muvaffaqiyatli, ichi bo'sh» zaxira).

⚠️ **Tenglik emas, `>=`:** tirik tizimda arxiv olinayotganda yangi obyekt
paydo bo'lishi normal. Tenglik talab qilinsa tekshiruv muntazam yolg'on
yiqilardi — bu loyihada tiklash sinovida bir marta aynan shunday bo'lgan.

⚠️ `tar` chaqiruvida **`--force-local` SHART**: GNU tar `C:/...` ni
«host:yo'l» deb o'qiydi va `Cannot connect to C: resolve failed` beradi
(o'lchandi 2026-09-17).

**Mexanizm — oddiy `pg_dump`, WAL arxivlash YO'Q.** Repoda `archive_mode`,
`wal_level`, `archive_command`, `pgbackrest`, `wal-g`, `barman`, `PITR`
so'zlarining birortasi ham uchramaydi, `docker-compose.yml` esa standart
`postgres:16` ni hech qanday sozlama ustiga yozmasdan ko'taradi. Mavjud
narsa — **30 kunda bir marta** olinadigan **mantiqiy dump** (`tools/backup.sh`).

**Qaror (2026-09-17, Saidakbar aka):** kunlik zaxira kerak emas — 30 kunda bir
marta, faqat lokal; mashinadan tashqariga (R2, USB) nusxa olinmaydi.

**Saqlash va chastota.** Skriptning standarti `RANKWANT_BACKUP_KEEP=30` kun —
oylik jadvalda bu bitta nusxa qoldirardi, kechikkan yoki yiqilgan yurishda esa
nolta. Shuning uchun `RankWant Monthly Backup` vazifasi **`RANKWANT_BACKUP_KEEP=95`**
beradi (~3 avlod; vazifa argumentlarida o'lchandi 2026-09-17). Skriptni qo'lda
standart bilan yurgizganda shu farqni hisobga oling.

**Narxi:** nuqtadan tiklash (point-in-time recovery) **yo'q**. Avariya
oxirgi dumpdan keyin yuz bersa, o'sha oradagi yozuvlar butunlay yo'qoladi —
eng yomon holatda **~30 kunlik** ma'lumot. Disk ham bitta (NVMe, Linux ham
shu diskda), ya'ni disk o'lsa lokal zaxira ham ketadi.

**Offsite — o'chiq (qaror).** `tools/backup.sh` R2 ga yuklay oladi
(`--offsite`), lekin standart `off`: egasi faqat lokal zaxirani tanlagan
(2026-09-17). O'sha kuni 02:14–02:21 da offsite sinovi paytida R2 `backups/`
ga 3 ta pg dump va 3 ta MinIO arxivi **shifrsiz** (foydalanuvchi ma'lumoti
bilan) yuklangan edi — ular o'chirildi, lokal nusxalari hajmi bilan
tekshirilgan. Yoqish faqat Saidakbar aka tasdig'i bilan; yoqilsa shifrlash
shart. Qolgan cheklov — WAL arxivlash va PITR yo'qligi; u **qabul
qilingan**, yashirilgan emas.

Preview (bitta mashina) uchun: `tools/backup.sh` — Postgres dump va MinIO
nusxasi. Saqlash `RANKWANT_BACKUP_KEEP` kun (skriptda standart 30; Windows
vazifasi 95 beradi — oylik jadvalda 30 kunlik saqlash kechikkan yurishda
yagona nusxani qoldirardi). Bitta yurish ~24.5 MB (o'lchandi 2026-09-17:
pg 17 MB + MinIO 7.4 MB), ya'ni ~3 ta oylik nusxa ~75 MB.

`--offsite` bilan yurgizilganda ikkalasi **Cloudflare R2** ga yuklanadi
(`backups/` prefiksi, 180 kun) va hajm solishtiriladi: «rclone exit 0» dalil
emas, yarim yozilgan obyekt ham 0 qaytaradi. Standart yurishda (vazifa ham
`RANKWANT_BACKUP_OFFSITE=off` beradi) R2 ga hech narsa ketmaydi, logda `r2=skip`.

Volume, WAL yoki VHDX'ga tegadigan amal oldidan rejali nusxaga suyanmang —
u 30 kungacha eski bo'lishi mumkin. Avval qo'lda oling:
`Start-ScheduledTask 'RankWant Monthly Backup'` va `backup.log` da
`dump butun` qatorini ko'ring.

⚠️ C: — yagona qattiq disk, va undagi bo'sh joy TEZ o'zgaradi: 2026-09-15
kuni bir necha soat ichida 5.8 GB dan 31.5 GB gacha ko'tarildi (yolg'iz
Docker build cache 14.7 GB, asosan qaytarib olinadigan). Shuning uchun bu
yerga «hozir shuncha bo'sh» degan raqam YOZILMAYDI — u ertasiga yolg'on
bo'ladi. Barqaror raqam — zaxiraning o'z narxi: ~75 MB. Skript esa har
yurishda katalogning JAMI hajmini va o'chirilgan eski fayllar sonini
jurnalga yozadi, chunki zaxira joyining tugashi backup'ni jimgina
o'ldiradi.

Linux, cron:

```
0 4 1 * * RANKWANT_BACKUP_KEEP=95 "$HOME"/rankwant/tools/backup.sh >> "$HOME"/backups/rankwant/backup.log 2>&1
```

Windows — `RankWant Monthly Backup` vazifasi, **har 30 kunda bir marta
13:00** da (`DaysInterval = 30`; keyingi yurish 2026-10-16).

⚠️ **2026-09-17 da o'lchandi:** hujjat ilgari «kunlik» deb yozardi, haqiqiy
vazifa esa **oylik** edi. Qaror: jadval oylik qoladi (foydalanuvchi
qarori), hujjat haqiqatga moslashtirildi. Ya'ni **RPO 30 kun**, 24 soat
emas — bu ataylab qabul qilingan cheklov, yashirilgan emas.
Soat ataylab tunda EMAS: butun stack Docker Desktop ustida turadi, u esa
faqat foydalanuvchi tizimga kirganda ishlaydi, ya'ni 04:00 dagi trigger
«rejalashtirilgan» bo'lib ko'rinib, amalda hech qachon zaxira bermasdi.
`StartWhenAvailable` mashina o'chiq bo'lgan kunni keyingi imkoniyatda
qoplaydi — oylik jadvalda bu SHART: usiz o'tkazib yuborilgan kun butun bir
oyga cho'ziladi (mashina dual-boot, Windows kunlab ko'tarilmasligi mumkin).

```powershell
$repo = 'C:\Users\nsn\project\cp\rankwant'
$bash = 'C:\Program Files\Git\bin\bash.exe'
$dest = '/c/Users/nsn/backups/rankwant'
$inner = "RANKWANT_BACKUP_DIR=$dest RANKWANT_BACKUP_KEEP=95 '/c/Users/nsn/project/cp/rankwant/tools/backup.sh' >> $dest/backup.log 2>&1"
$action = New-ScheduledTaskAction -Execute 'C:\WINDOWS\System32\conhost.exe' `
  -Argument ('--headless "' + $bash + '" -lc "' + $inner + '"') -WorkingDirectory $repo
# Har 30 kunda: `-Daily -DaysInterval 30` — «-Monthly» EMAS, u kun
# raqamini talab qiladi va oy uzunligiga bog'lanib qoladi.
$trigger = New-ScheduledTaskTrigger -Daily -DaysInterval 30 -At '13:00'
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries `
  -DontStopIfGoingOnBatteries -StartWhenAvailable `
  -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 30)
Register-ScheduledTask 'RankWant Monthly Backup' -Action $action `
  -Trigger $trigger -Settings $settings -Force
# 2026-09-17 gacha kunlik vazifa bo'lgan — qolgan bo'lsa olib tashlang:
Unregister-ScheduledTask 'RankWant Daily Backup' -Confirm:$false -ErrorAction SilentlyContinue
```

⚠️ Yalang'och `bash` ISHLATILMAYDI: Windows'da u WSL relay'iga tushadi va
skript umuman ishga tushmaydi. Git Bash'ning to'liq yo'li beriladi.

Har yurishda dump butunligi tekshiriladi — `gzip -t` va `pg_dump` ning
yakuniy qatori (ikkinchisi shart: gzip butun bo'lib, dump o'rtada uzilgan
bo'lishi mumkin). Choraklik to'liq sinov — `tools/backup.sh --restore-test`:
dump ALOHIDA `restore_test` bazasiga tiklanadi, jadvallar bo'sh emasligi va
havolalar butunligi tekshiriladi, keyin o'sha baza tashlanadi. Jonli
`rankwant` bazasiga **tegilmaydi**.

⚠️ Sinov jonli baza bilan qator sonlarini **SOLISHTIRMAYDI**. Ilgari shunday
edi va muntazam yolg'on yiqilardi: zaxira — vaqt kesimi, jonli baza esa
o'shandan beri o'zgargan bo'ladi. Muntazam yolg'on ogohlantirish eng yomoni —
odam uni e'tiborsiz qoldirishni o'rganadi.

## Monitoring va alert

| Metrika                    | Alert sharti           | Sabab                             |
| -------------------------- | ---------------------- | --------------------------------- |
| Judge latency p95          | > 15s                  | NFR buzilishi ([04-prd](../04-prd/README.md)) |
| Judge navbat uzunligi      | > 5 min kutish         | worker yetishmaydi                |
| `SECURITY_VIOLATION`       | **har bitta hodisa**   | potensial sandbox escape          |
| `IE` / `DENIAL_OF_JUDGEMENT` | ko'tarilish          | infra nosozligi                   |
| 5xx darajasi               | > 1%                   | API muammosi                      |
| Qvant emissiyasi           | kunlik limitdan oshish | anti-farm buzilishi ([ADR-0002](../07-adr/0002-qvant-economy.md)) |
| Email provayder kvotasi    | 80% yoki shift tugashi | xat yetkazilmay qoladi            |

Email kvotasi — `core.warn_email_quota`, soatiga bir marta. Panel
`/admin/email-quota` da ham ko'rinadi, lekin panelni ochish kerak, ya'ni
ogohlantirish o'zi kelishi shart. Xabar **faqat sayt ichida** (qo'ng'iroq
+ `/notifications`) va ataylab `notify()` ni chetlab o'tadi: xodim
«system» turini o'chirib qo'ysa ham keladi, aks holda kvota jimgina
tugardi. Shart — `core.mail_quota.summary()`, ya'ni chegara bitta joyda.

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

CI, Security va Nightly **GitHub-hosted** da ishlaydi (`runs-on: ubuntu-latest`).
Public repo da standard runner daqiqasi $0; 3 agent PR i bir-birini shu
noutbukda siqmaydi. `deploy.yml` va `runner-selftest.yml` self-hosted
qoladi — deploy jonli Docker stack'iga tegadi, public `pull_request` esa
noutbukda yugurmasligi kerak. PR'da Security va smoke yo'q. Runner
o'rnatish — [tools/runner/README.md](../../tools/runner/README.md).

CI testlari toza `ubuntu-latest` VM da — «menda ishlayapti» sinfi
kamayadi. Smoke/nightly ham hosted; `docker-compose.ci.yml` dagi
`name: rankwant-ci` saqlanadi (hosted VM da jonli preview yo'q).
Deploy self-hosted da qoladi va jonli stack'ga tegadi.

Hosted VM qatlam keshi yo'qoladi, shuning uchun smoke/nightly
`tools/ci_stack.sh` orqali `ghcr.io/<repo>/ci-{api,web,judge}:main`
dan `--cache-from` qiladi va faqat `main` ga yozadi. pip/npm/mypy/
Next kesh — Actions cache (10 GB). API pytest ikki shard. PR da
`--cov` yo'q. Docker `type=gha` kesh ishlatilmaydi — judge obrazi
pip/npm ni siqib chiqaradi.

### Push'dan oldingi darvoza

`.githooks/pre-push` (repo bilan versiyalanadi, `core.hooksPath` orqali
yoqiladi) push'dan oldin faqat tez darvozalarni yuritadi: `push_guard`,
API `ruff`/`format`, web i18n va hardcoded. mypy, pytest, tsc va 153
salbiy test CI da qoladi — hook ularni takrorlasa Windows'da ~5.8 daqiqa
ketardi (2026-09-18). Chetlab o'tish: `git push --no-verify`.

Yangi klonda yoqish:

```bash
git config core.hooksPath .githooks
```

**Interpretator nomi bo'yicha tanlanmaydi.** Hook Python'ni
`tools/pick-python.sh` orqali oladi va u har bir nomzodni ISHGA TUSHIRIB
ko'radi. Sabab Windows'da: `python3` Microsoft Store'ning "App Execution
Alias" stub'iga tushadi — `command -v` uni topadi, lekin ishga
tushirilganda "Python was not found" deb chiqadi. 2026-09-15 da shu
sabab to'rtta tekshiruv «yiqildi» deb ko'rsatilgan, holbuki kod soz edi.
Interpretatorni qotirish kerak bo'lsa: `PYTHON=/path/to/python`.

**Chiqish UTF-8 ga majburlanadi.** Tekshiruvlar `✓`/`✗` chiqaradi, Windows
esa quvurga yozilgan oqim uchun `cp1252` beradi — 2026-09-15 da o'nta
`check_*.py` dan sakkiztasi shu sabab `UnicodeEncodeError` bilan qulagan.
Bu yolg'on yashil manbai edi: `check_negative.py` bolalarni quvur orqali
chaqiradi, qulagan bola nolga teng bo'lmagan kod qaytaradi va salbiy test
uni «buzuq holatni tutdi» deb o'qiydi. Shuning uchun har bir tekshiruv
`tools/_console.py` dagi `force_utf8()` ni chaqiradi — tuzatish
chaqiruvchining muhitiga emas, skriptning o'ziga bog'langan.

## Assumptions

1. **Bitta mashina preview uchun yetarli.** Deploy topologiyasi shunga
   qurilgan; `disaster recovery` bo'limi yo'q — ya'ni mashina yiqilsa
   xizmat to'xtaydi degan **qabul qilingan** holat.
2. **Self-hosted runner xavfi qabul qilinadi.** *"Yolg'iz ishlashda qabul
   qilsa bo'ladigan xavf, jamoada emas"* — va qayta ko'rib chiqish sharti
   yozilgan (ikkinchi odam qo'shilishidan oldin).
3. **Oylik lokal backup + R2 offsite + choraklik tiklash sinovi
   yetarli.** Bu **tanlangan** chegara (2026-09-17, Saidakbar aka): kunlik
   zaxira kerak emas. Offsite nusxa o'sha kundan boshlab R2 ga olinadi.
   RPO va RTO raqamlari `Disaster recovery` bo'limida (RPO ≤ 30 kun,
   RTO ~9 s). Ustidan *"tiklash sinovi o'tkazilmasa, backup yo'q deb
   hisoblanadi"* tamoyili qo'llanadi.
4. **Branch protection va secret scanning siz ishlash mumkin.** GitHub bu
   tarifda branch protection bermaydi (403). 2026-09-17 dan `main` ga
   to'g'ridan-to'g'ri push'ni `.githooks/pre-push` (`tools/push_guard.py`)
   rad etadi; qizil CI bilan merge va `--no-verify` esa hali ham texnik
   jihatdan mumkin — bu qismi *"DoD intizomga tayanadi"*.

## SLO va error budget

Maqsadlar `04-prd` dagi NFR lardan olingan — yangi raqam o'ylab topilmagan.

| SLI | SLO | O'lchov joyi |
|---|---|---|
| Mavjudlik (uptime) | **99.5%** / oy | Cloudflare + `curl /api/v1/health/` |
| Judge latency p50 | **< 5 s** | `Attempt.created_at` → `judged_at` |
| Judge latency p95 | **< 15 s** | shu |
| API 5xx darajasi | **< 1%** | API log |
| Judge navbat kutish | **< 5 min** | navbat uzunligi |

**Error budget.** 99.5% / 30 kun ≈ **3 soat 39 daqiqa** uzilish. Budget tugasa —
yangi funksiya emas, barqarorlik ishi ustuvor bo'ladi.

⚠️ **Bitta mashina — bu maqsadning eng katta xavfi.** Mashina yoki tunnel
yiqilsa, uptime maqsadi shu oy uchun bajarilmaydi. Bu **qabul qilingan
cheklov**, yashirilgan emas.

## On-call va eskalatsiya

**Rotatsiya:** bitta odam — Saidakbar Narzullayev. **Eskalatsiya zanjiri yo'q.**

| Narsa | Qiymat |
|---|---|
| Kim | Saidakbar Narzullayev (yolg'iz maintainer) |
| Aloqa | telefon + Telegram |
| Javob vaqti | ish vaqtida darhol; tunda ertalab |
| Eskalatsiya | **yo'q** — yuqoriga kimdir yo'q |

⚠️ **Bu ataylab qayd etilgan xavf.** Yolg'iz loyihada eskalatsiya zanjiri
bo'lmasligi tabiiy, lekin oqibati bor: **tunda yuz bergan avariya
ertalabgacha davom etadi.**

**Qisman yumshatish:** `RankWant Tunnel Monitor` vazifasi (5 daqiqada bir)
tunnelni yoki o'lgan port ko'prigini avtomatik tiklaydi — eng ko'p uchraydigan
ikki nosozlik turi inson ishtirokisiz tuzaladi. `tools/monitor.ps1` sayt
ildizini ham, `/api/v1/health/` ni ham tekshiradi (faqat ildizni tekshirish
2026-09-15 da API-ning yolg'iz yiqilishini o'tkazib yuborgan) va handoff
oqimini **hurmat qiladi**: `owner=windows` bo'lmasa hech narsa tiklanmaydi
(aks holda ikki tomon bir vaqtda live bo'lardi).

**Qayta ko'rib chiqiladi:** ikkinchi odam jamoaga qo'shilganda.

## Runbook qadamlari

Har bir qadam **haqiqiy buyruq** — mavjud `tools/` skriptlariga tayanadi.

### 0. Universal birinchi qadam — har qanday avariyada

```bash
cd rankwant
bash tools/check_deploy.sh
curl -s -o /dev/null -w '%{http_code}\n' https://rankwant.uz/api/v1/health/
```

Javob uchta yo'lni ajratadi:

| Natija | Ma'nosi | Keyingi |
|---|---|---|
| `503` yoki "texnik ishlar" | tunnel uzilgan | §1 |
| `200`, lekin sahifa buzuq | eski konteyner | §2 |
| `500` | ilova xatosi | §3 |

### 1. Sayt ochilmayapti (503 / texnik ishlar)

**Elektr uzilishi yoki reboot'dan keyin — avval shu.** 2026-09-17 da sayt
~23 daqiqa yiqiq turdi: Docker Desktop ishga tushmagan, `monitor.ps1` esa R2
egaligini `docker run rclone/rclone` bilan o'qiydi — Docker yo'q bo'lsa jurnalga
`UNMEASURED ... R2 state.json o'qilmadi` yozadi va tunnelni ATAYLAB
ko'tarmaydi. Belgisi: `docker info` xato beradi.

```powershell
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"   # konteynerlar restart policy bilan o'zi ko'tariladi
Start-ScheduledTask 'RankWant Tunnel Monitor'                         # egalikni tekshirib tunnelni tiklaydi
```

Tunnelni qo'lda ishga tushirmang — egalik tekshiruvini monitor qiladi.
Doimiy yechim — Docker Desktop logon'da o'zi ishga tushishi, va u IKKI joyda
yoqilgan bo'lishi shart (2026-09-17 da ikkalasi ham o'chiq edi):

```powershell
(Get-Content "$env:APPDATA\Docker\settings-store.json" -Raw | ConvertFrom-Json).AutoStart   # True
(Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run').'Docker Desktop'[0]   # 2 = yoqiq, 3 = Task Manager'da o'chirilgan
```

Logon talab qilinadi: foydalanuvchi tizimga kirmaguncha Docker Desktop ham,
sayt ham ko'tarilmaydi.

Keyin tunnel holati:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\tools\handoff.ps1" status
```

- `tunnel=ishlayapti` → muammo DNS/Cloudflare'da, tunnelda emas
- `tunnel=to'xtagan` va `owner=windows` → ko'tariladi
- `tunnel=to'xtagan` va **`owner=linux`** → **qo'lda tegmaymiz** (ikkinchi
  tunnel ochilib qolardi)
- `.handoff/cloudflared.log` da `graceful shutdown due to signal terminated`
  = kimdir ataylab to'xtatgan

### 2. Konteyner eski kodda (`check_deploy.sh` → 1)

```bash
docker compose -p rankwant --env-file .env.public \
  -f docker-compose.yml -f docker-compose.public.yml up -d --build --wait
```

⚠️ **Kod o'zgarsa `web api worker beat` TO'RTALASI** qayta quriladi.
`worker` va `beat` `api` bilan bir xil kodni baham ko'radi va **jimgina eski
qoladi**. Faqat `web` ni qayta qurish — eng ko'p uchraydigan xato.

⚠️ `--env-file .env.public` tushib qolmasin: usiz `ALLOWED_HOSTS=""` va
`DEBUG=False` bo'lib, **har so'rov 400** qaytaradi.

### 3. Ilova xatosi (500)

```bash
docker compose -p rankwant logs --tail=100 web api
```

- `x-powered-by: Next.js` bo'lsa — web SSR da
- web log `status: 400` ko'rsatsa — sabab **api** tomonda (maydon shartnomasi)

### 4. Sandbox escape shubhasi — **eng yuqori daraja**

Yuqoridagi `## Incident turlari` §1 ga qarang (5 qadam).

### 5. Judge navbat to'lib qolishi

Yuqoridagi `## Incident turlari` §2 ga qarang.

### 6. Backup va tiklash

```bash
bash tools/backup.sh                 # dump + butunlik tekshiruvi
bash tools/backup.sh --restore-test  # alohida bazaga tiklaydi (jonliga tegmaydi)
```

## Disaster recovery (RTO / RPO)

| Narsa | Qiymat | Izoh |
|---|---|---|
| **RPO** | ≤ 30 kun | oylik `pg_dump` + har yurishda R2 offsite (2026-09-17); WAL arxivlash va PITR yo'q |
| **RTO (baza)** | **~9 soniya** | o'lchandi 2026-09-17: `--restore-test` 17 MB dumpni 9 s da tiklandi |
| **RTO (xizmat)** | 1–12 soat | on-call bir kishi; tungi avariya ertalabgacha |
| Failover | **yo'q** | bitta mashina; zaxira R2 da bor, lekin xizmat qayta qurilmaguncha to'xtaydi |

⚠️ **Bitta mashina — eng katta DR riski.** Mashina butunlay yiqilsa baza
backupdan tiklanadi, lekin **xizmat qayta qurilmaguncha to'xtaydi**.
Hosting qarori keyinga qoldirilgan (pastga qarang).

## Release va rollback

**Release:** CI → staging → **prod qo'lda tasdiqlash** (contest oynasi
tekshiriladi).

**Rollback:**

```bash
git revert <sha>
docker compose -p rankwant --env-file .env.public \
  -f docker-compose.yml -f docker-compose.public.yml up -d --build --wait
bash tools/check_deploy.sh           # 0 bo'lishi shart
```

⚠️ **Migratsiya rollback qilinmaydi.** Sxema oldinga mos yoziladi
(`add → backfill → switch → drop`, alohida deploylarda) — ya'ni kod
qaytarilsa ham baza ishlashda davom etadi. `drop` bosqichi alohida deploy,
ya'ni u hali bajarilmagan bo'ladi.

## Holat va tasdiq

### Joriy holat — ommaviy PREVIEW, production emas

Yuqoridagi `## Ommaviy preview` bo'limi o'zi aytadi:

> **Bu production EMAS** — yuqoridagi to'rt-hostli topologiya o'rniga bitta
> mashinada ishlaydigan ko'rsatuv nusxasi.

Ya'ni bu hujjatdagi operatsion tayyorgarlik **production uchun yozilgan**,
lekin **joriy deploy production emas**. Ikkalasini ajratib turish shart —
chalkashsa "production tasdiqlangan" degan yolg'on da'vo paydo bo'ladi.

| Narsa | Holat |
|---|---|
| Operatsion hujjatlar (SLO, on-call, runbook, DR, rollback) | ✅ **tayyor** |
| **To'rt-hostli topologiya** (app · web · judge×N · data) | ❌ **qurilmagan** |
| **Production deploy** | ❌ **yo'q — hozir preview** |

### Production launch tasdig'i

**Tasdiq:** Saidakbar Narzullayev — Repo owner / maintainer, **2026-09-13**.

Bu tasdiq **to'rt-hostli production topologiyasi uchun** — u qurilgach qayta
inson tasdig'i talab qilmaydi, faqat deploy qilinadi.

| Tayyorgarlik | Holat |
|---|---|
| SLO va error budget | ✅ `04-prd` NFR laridan |
| On-call va eskalatsiya | ✅ bir kishi, eskalatsiyasiz — xavf qayd etilgan |
| Runbook qadamlari | ✅ 6 holat, haqiqiy buyruqlar bilan |
| Backup va tiklash sinovi | ✅ choraklik majburiy |
| Release / rollback | ✅ yozildi |
| DR (RTO/RPO) | ✅ yozildi, failover yo'qligi qayd etilgan |

### Preview maqomi — qabul qilingan xavflar

Joriy bitta-mashinali deploy **ommaviy preview** bo'lib qoladi. Xavflar
yashirilmagan:

1. **Bitta mashina** — failover yo'q; mashina yiqilsa xizmat to'xtaydi
2. **Eskalatsiya zanjiri yo'q** — tungi avariya ertalabgacha davom etadi
3. **Dual-boot** — sayt qaysi tizim yoniq bo'lsa o'shandan ishlaydi, va har
   tizimning **o'z bazasi** bor
4. **Production topologiyasi qurilmagan** — yuqoridagi to'rt host hali yo'q

**Qayta ko'rib chiqiladi:** to'rt-hostli topologiya qurilganda (production
launch), ikkinchi odam jamoaga qo'shilganda, yoki uptime 99.5% ikki oy
ketma-ket bajarilmasa.

## Keyinroq to'ldiriladi

- [ ] Hosting provayderi va narx modeli — **qaror keyinga**, hozirgi holat qabul qilindi
- [ ] Runbook qadamlarini real incident tajribasi bilan boyitish
- [ ] SLO ni real trafikdan keyin qayta ko'rib chiqish
