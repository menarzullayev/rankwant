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
| `robots.txt` | Bizniki beriladi — `rankwant.uz` zonasida Cloudflare'ning managed robots.txt'i o'chiq. **Launch'gacha yopiq** (2026-09-15): `apps/web/src/lib/site.ts` dagi `SITE_INDEXABLE = false` bo'lganda `robots.txt` `Disallow: /` beradi (sitemap qatorisiz), sahifalar esa `noindex, nofollow`. Sabab: kraulerlar kuniga ~246 ming so'rov yubordi (82% GPTBot, 16% Google), asosan 10 001 ta `neytron_*` sinov profiliga, va Cloudflare Workers'ning kunlik 100 ming limiti har kuni tugardi. Launch'da `true` qilinadi — shunda `Sitemap: https://rankwant.uz/sitemap.xml` qaytadi. Search Console (domen resursi) va Yandex Webmaster'da DNS TXT orqali tasdiqlangan, sitemap ikkalasiga yuborilgan (2026-09-11) — apex'dagi `google-site-verification` va `yandex-verification` TXT'larini o'chirmang |

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

Monitor har 5 daqiqada saytni tashqaridan tekshiradi:

| Holat | Nima qiladi |
| ----- | ----------- |
| Sayt `200` | hech narsa (log'ga ham yozmaydi) |
| Sayt `200` emas, origin ham javob bermayapti | ogohlantiradi — tunnelni ko'tarish yordam bermaydi, konteyner aybdor |
| Sayt `200` emas, origin sog'lom, R2 `owner=windows` | tunnelni qayta ko'taradi |
| Sayt `200` emas, lekin R2 `owner` boshqa (yoki noma'lum) | **tunnelni ko'tarmaydi**, ogohlantiradi — handoff qoidasi: ikki tomon bir vaqtda live bo'lmasin |

Egalik tekshiruvi `handoff.ps1` bilan bir xil R2 `state.json` dan o'qiladi. R2
javob bermasa `unknown` deb qaraladi va tunnel ko'tarilmaydi (xavfsiz tomon).
Holat `.handoff/monitor.log` ga, muammo esa `.handoff/monitor-alert.txt` ga
yoziladi.

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

## Assumptions

1. **Bitta mashina preview uchun yetarli.** Deploy topologiyasi shunga
   qurilgan; `disaster recovery` bo'limi yo'q — ya'ni mashina yiqilsa
   xizmat to'xtaydi degan **qabul qilingan** holat.
2. **Self-hosted runner xavfi qabul qilinadi.** *"Yolg'iz ishlashda qabul
   qilsa bo'ladigan xavf, jamoada emas"* — va qayta ko'rib chiqish sharti
   yozilgan (ikkinchi odam qo'shilishidan oldin).
3. **Kunlik backup + choraklik tiklash sinovi yetarli.** RTO/RPO raqami
   yo'q, lekin *"tiklash sinovi o'tkazilmasa, backup yo'q deb hisoblanadi"*
   tamoyili qo'llanadi.
4. **Branch protection va secret scanning siz ishlash mumkin.** *"DoD
   intizomga tayanadi"* — ya'ni `main` ga to'g'ridan-to'g'ri push va qizil CI
   bilan merge texnik jihatdan mumkin.

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
tunnelni avtomatik ko'taradi — eng ko'p uchraydigan nosozlik turi inson
ishtirokisiz tuzaladi. `tools/monitor.ps1` handoff oqimini **hurmat qiladi**:
tunnel `owner=linux` bo'lsa ko'tarmaydi (aks holda ikki tunnel ochilardi).

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
bash tools/backup.sh --restore-test  # alohida bazaga tiklab solishtiradi
```

## Disaster recovery (RTO / RPO)

| Narsa | Qiymat | Izoh |
|---|---|---|
| **RPO** | ≤ 24 soat | kunlik full backup + WAL |
| **RTO (baza)** | ~1 soat | `--restore-test` bilan mashq qilingan |
| **RTO (xizmat)** | 1–12 soat | on-call bir kishi; tungi avariya ertalabgacha |
| Failover | **yo'q** | bitta mashina — zaxira nusxa yo'q |

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
