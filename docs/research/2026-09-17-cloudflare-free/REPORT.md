# Cloudflare Free — RankWant uchun to‘liq imkoniyatlar

**Sana:** 2026-09-17 (Toshkent)  
**Maqsad:** Cloudflare bepul qatlamini rasmiy manbadan o‘lchash; RankWant (`rankwant.uz`, Tunnel, Workers, R2, Turnstile) ga foydasi tegadigan narsani ajratish.  
**Usul:** Cloudflare Docs, Pricing, Personal/Free overview. Taxmin yo‘q — har raqam ostida manba.

> Tirik hujjat emas. Limitlar o‘zgaradi. Zona Free (sayt tarif) va Developers Free (Workers/R2) — **ikki alohida hisob**.

---

## 1. 30 soniyada

Cloudflare Free **kartasiz** CDN, DNS, Universal SSL, L7 DDoS, Free Managed WAF, Turnstile (cheksiz tekshiruv), Tunnel, Email Routing, Web Analytics beradi. Pullik qo‘shimcha (Argo, Load Balancing, Stream, Waiting Room) shart emas.

RankWant uchun **uchta haqiqiy cheklov**:

1. **Workers Free = 100 000 so‘rov/kun** (UTC 00:00). Maintenance Worker har so‘rovda ishlaydi — 2026-09-13 da limit **haqiqatan tugagan**. Fail-open yoqilgan, shuning uchun sayt yiqilmagan.
2. **Bot Fight Mode** Free da bor, lekin **skip qilib bo‘lmaydi**. API/CI/monitor ni challenge qilishi mumkin.
3. **Snippets, Custom Errors, Waiting Room, Super Bot Fight, OWASP Managed Ruleset** — Free da yo‘q.

**Amaliy qoida**

| Vazifa | Free yetadimi? |
|---|---|
| Domen, TLS, CDN, DDoS, ochiq port yo‘q (Tunnel) | **Ha — allaqachon ishlaydi** |
| Register bot himoyasi (Turnstile) | **Ha — cheksiz, kartasiz** |
| Edge da 5 ta WAF qoidasi + 1 ta IP rate limit (10 s) | **Ha** |
| Krauler/AI botni chetlab, Worker 100k ni saqlash | **Ha — Block AI Bots + `robots.txt`** |
| Har so‘rovda Worker (maintenance sahifa) + katta contest | **Yo‘q** — Paid yoki route’ni olib tashlash |
| `/admin` ni Cloudflare Access orqasida | **Ha** — Zero Trust Free, 50 user |
| Private Pages / yopiq sayt Cloudflare’da | Kerak emas (o‘z origin) |
| Email yuborish (1000 verify) | **Yo‘q** — Sending = Workers Paid; Routing faqat kiruvchi |

---

## 2. Ikki Free — aralashtirmang

```
Zona (rankwant.uz)     ≠     Developers (Workers / R2 / KV)
Free / Pro / Biz              Free / Paid (hisob darajasi)
CDN, WAF, SSL, Rules          100k so‘rov/kun, 10 ms CPU
```

Zona Free bo‘lsa ham Workers Paid sotib olish mumkin (va aksincha). RankWant maintenance Worker **Workers Free** kvotasida.

Manba: [plans](https://www.cloudflare.com/plans/), [Workers limits](https://developers.cloudflare.com/workers/platform/limits/), [personal](https://www.cloudflare.com/personal/).

---

## 3. RankWant hozir nima ishlatadi

O‘lchangan / qayd etilgan (repo + ops, 2026-09):

| Mahsulot | Holat | Izoh |
|---|---|---|
| DNS + proxied zone `rankwant.uz` | ✅ | `CF-Ray`, `Server: cloudflare` |
| Cloudflare Tunnel (`cloudflared`) | ✅ | Ochiq inbound port yo‘q; tunnel o‘lsa 503 |
| Universal SSL | ✅ | Brauzer ogohlantirishisiz |
| Maintenance Worker `rankwant.uz/*` | ✅ | 502/52x da 503 sahifa; **fail-open** |
| Workers 100k/kun | ⚠️ **tugagan** (2026-09-13) | Krauler ~246k/kun; `SITE_INDEXABLE=false` |
| R2 (`rankwant-handoff`) | ✅ | Offsite backup; egress bepul |
| Turnstile | ✅ yoqilgan | `enabled()=True`, register 300/soat |
| `HTTP_CF_CONNECTING_IP` | ✅ | Public overlay |
| Email Sending (CF) | ❌ | Brevo zanjiri |
| Bot Fight Mode / WAF custom | ? | Dashboard’da tekshirish kerak |
| `CLOUDFLARE_API_TOKEN` | ⚠️ | Oldin faqat `bugvector.uz` zonasini ko‘rgan; `rankwant.uz` boshqa akkaunt |

**Xulosa:** ~40% “bepul xavfsizlik/qoida” hali yoqilmagan. Kod yozish shart emas — dashboard.

---

## 4. Zona Free — nima kiritilgan

Rasmiy [personal](https://www.cloudflare.com/personal/) va [plans](https://www.cloudflare.com/plans/):

| | Free | Izoh |
|---|---|---|
| Authoritative DNS | ✅ | Cheksiz so‘rov (zona) |
| CDN | ✅ | 335+ PoP (marketing); kesh 512 MB/fayl |
| Universal SSL | ✅ | Apex + 1-daraja subdomain (`www`) |
| Unmetered L7 DDoS | ✅ | Sozlamasiz yoqilgan |
| Free Managed Ruleset | ✅ | OWASP / to‘liq CF Managed — **Pro+** |
| WAF custom rules | ✅ **5 ta** | Regex yo‘q; Log yo‘q |
| IP rate limiting | ✅ **1 qoida** | Period **10 s**, mitigation **10 s**; faqat IP |
| Bot Fight Mode | ✅ | Skip/exception **yo‘q** |
| Block AI Bots | ✅ | Search / Agent / Training alohida |
| Analytics | ✅ | Security Events **24 soat**; Analytics **7 kun** |
| Always Use HTTPS, HSTS, TLS 1.2+ | ✅ | Dashboard |
| HTTP/2, HTTP/3, IPv6, Brotli | ✅ | Network |
| Web Analytics (maxfiylik) | ✅ | Cookie’siz |
| Zaraz | ✅ | Uchinchi tomon skript |
| Community support | ✅ | Ticket — Pro+ |
| Uptime SLA | ❌ | Business+ |
| Polish / Lossless image (zona) | ❌ | Pro+ (pricing) |
| PCI DSS 4.0 | ❌ | Business+ |

**Kesh / upload (zona)**

| | Free |
|---|---|
| Keshlangan fayl | **512 MB** |
| Upload (request body) | **100 MB** |
| Cache Rules | **10** |
| Single Redirects | **10** (regex yo‘q) |
| Bulk Redirects | 15 qoida, 5 list, **10 000** URL |
| Transform Rules | **10** (regex yo‘q) |
| Configuration Rules | **10** |
| Origin Rules | **10** — Free da faqat **destination port**; Host/SNI/DNS override Enterprise |
| Page Rules | **3** (eski; yangi Rules ustun) |
| Snippets | **0** — Pro+ |
| Custom Errors / Error Pages | **0** — Pro+ |

Manba: [custom rules](https://developers.cloudflare.com/waf/custom-rules/), [rate limiting](https://developers.cloudflare.com/waf/rate-limiting-rules/), [cache rules](https://developers.cloudflare.com/cache/how-to/cache-rules/), [default cache](https://developers.cloudflare.com/cache/concepts/default-cache-behavior/), [redirects](https://developers.cloudflare.com/rules/url-forwarding/), [transform](https://developers.cloudflare.com/rules/transform/), [configuration](https://developers.cloudflare.com/rules/configuration-rules/), [origin](https://developers.cloudflare.com/rules/origin-rules/), [snippets](https://developers.cloudflare.com/rules/snippets/), [page rules](https://developers.cloudflare.com/rules/page-rules/), [custom errors](https://developers.cloudflare.com/rules/custom-errors/), [security analytics](https://developers.cloudflare.com/waf/analytics/security-analytics/).

---

## 5. Turnstile — Free to‘liq yetadi

[Turnstile plans](https://developers.cloudflare.com/turnstile/plans/) (yangilangan 2026-08-14):

| | Free | Enterprise |
|---|---|---|
| Narx | **$0** | Sales |
| Tekshiruv / traffic | **Cheksiz** | Cheksiz |
| Widget | 20 | Cheksiz |
| Rejim (Managed / Non-interactive / Invisible) | ✅ | ✅ |
| Hostname / widget | **10** | 200 |
| Any hostname | ❌ | ✅ |
| Analytics | 7 kun | 30 kun |
| Pre-clearance | ✅ | ✅ |
| Offlabel / Ephemeral ID | ❌ | ✅ |
| WCAG 2.2 AAA | ✅ (plans jadvali) | ✅ |

CDN shart emas — istalgan saytda ishlaydi. Karta yo‘q.

RankWant: Managed, `rankwant.uz` (+ preview hostname). Overview sahifasi hali “AA” deb yozishi mumkin; **plans jadvali AAA**.

---

## 6. Developers Free — hisob kvotalari

[Pricing](https://www.cloudflare.com/plans/) + mahsulot docs. Oy/kun reset — mahsulotga qarab.

| Mahsulot | Free kvota | RankWantga |
|---|---|---|
| **Workers** | 100k so‘rov/kun, 10 ms CPU, 100 Worker, 5 cron | Maintenance Worker **shu yerda tiqiladi** |
| **R2** | 10 GB, 1M Class A, 10M Class B; **egress $0** | Handoff/backup; IA class Free da yo‘q |
| **KV** | 1 GB, 100k read/kun, 1k write/kun | Kerak emas (Redis bor) |
| **D1** | 5 GB, 5M read/kun, 100k write/kun | Kerak emas (Postgres) |
| **Durable Objects** | 100k req/kun + kichik SQL | Kerak emas |
| **Queues** | 10k ops/kun | Kerak emas |
| **Hyperdrive** | 100k query/kun | Kerak emas |
| **Analytics Engine** | 100k yozuv, 10k o‘qish/kun | Ixtiyoriy |
| **Workers AI** | 10 000 neuron/kun | Judge o‘rniga **emas** |
| **Vectorize** | 30M query dim / 5M stored | Kerak emas |
| **Images** | 5 000 unique transform/oy | Avatar/og image; oshsa 9422, to‘lov yo‘q |
| **Browser Rendering** | 10 daq/kun, 3 browser | Kerak emas |
| **TURN/SFU** | 1000 GB/oy | Kerak emas |
| **AI Gateway** | Core bepul; log 100k | Agar tashqi LLM bo‘lsa |
| **Email Routing** | Kiruvchi **cheksiz** | `support@rankwant.uz` → Gmail |
| **Email Sending** | Ixtiyoriy recipient = **Workers Paid**; verified destination — bepul | 1000 verify uchun **emas** (Brevo qoladi) |

Workers 100k tugasa: **Error 1027** (fail closed) yoki Worker o‘tkazib yuboriladi (fail open). RankWant fail-open yoqqan — to‘g‘ri.

CPU 10 ms: `fetch()` kutish hisoblanmaydi. Maintenance Worker faqat `fetch` + status tekshiradi — 10 ms odatda yetadi. Muammo — **so‘rov soni**, CPU emas.

Manba: [Workers limits](https://developers.cloudflare.com/workers/platform/limits/), [R2 pricing](https://developers.cloudflare.com/r2/pricing/), [Images pricing](https://developers.cloudflare.com/images/pricing/), [Email Service pricing](https://developers.cloudflare.com/email-service/platform/pricing/), [Email limits](https://developers.cloudflare.com/email-service/platform/limits/).

---

## 7. Tunnel va Zero Trust

**Tunnel** — [barcha rejalar](https://developers.cloudflare.com/tunnel/). Outbound-only, ochiq port yo‘q. RankWant asosiy ingress.

Ogohlantirish: public hostname orqali **katta video/fayl** tarqatish Free/Pro/Business TOS da alohida pullik xizmat (Stream) talab qilishi mumkin. Ordinary HTML/API — muammo emas. ([Tunnel FAQ](https://developers.cloudflare.com/cloudflare-one/faq/cloudflare-tunnels-faq/))

Authenticated Origin Pulls Tunnel da **ishlamaydi** (inbound listener yo‘q) — kerak emas.

**Cloudflare One / Access:** [plans](https://www.cloudflare.com/plans/) — Free “50 users”, log ~24 soat. [SASE architecture](https://developers.cloudflare.com/reference-architecture/architectures/sase/): 50 user, muddatsiz, ko‘p imkoniyat bepul.

**Amaliy:** `/admin` va `/api/v1/staff/*` ni Access (Google/GitHub/one-time PIN) orqasiga qo‘yish. Django `IsAdminUser` qoladi — ikkinchi qavat. 50 user RankWant staff uchun yetadi.

---

## 8. RankWantga foydali — prioritet

### P0 — yoqing (kod yo‘q)

1. **Always Use HTTPS** + SSL/TLS **Full (strict)**  
   Tunnel orqali origin. Flexible qoldirmang.

2. **Block AI Bots** (Security → Settings → AI bot policies)  
   2026-09-15 dan yangi domenlarda Training/Agent default block. RankWantda krauler Worker 100k ni yegan. Training/Agent ni **Block**; Search ni launch’dan oldin o‘ylab qo‘ying (`SITE_INDEXABLE`).

3. **Free Managed Ruleset** yoqilganini tekshirish  
   SQL/XSS keng tarqalgan imzo. False positive bo‘lsa custom rule bilan Skip (Bot Fight Mode emas).

4. **WAF custom (5 ta — 2–3 tasi yetadi)**  
   - `POST /api/v1/auth/register/` + g‘alati UA → Managed Challenge (Turnstile ustiga)  
   - Bo‘sh `User-Agent` / `Accept` → Block yoki Challenge  
   Regex yo‘q — `eq`, `contains`, `starts_with`.

5. **Rate limiting (1 qoida)**  
   Masalan `POST` + path register/login, IP, **10 soniya**da N so‘rov → Challenge. Bu Django `300/hour` o‘rnini **bosmaydi** — faqat qisqa burst. Counting expression (faqat 401) — **Business+**.

6. **`www` → apex** Single Redirect (10 dan 1).

### P0 — ehtiyot

7. **Bot Fight Mode**  
   Butun zona, skip yo‘q. Turnstile + API + health + Search Console botlarini challenge qilishi mumkin. Avval **o‘chiq** qoldiring; Block AI Bots + custom rule yetarli. Yoqsangiz 24 soat Security Events ni qarang.

### P1 — foydali

8. **Cache Rules (10)**  
   `/_next/static/*`, font, rasm — Cache Everything + uzoq Edge TTL. HTML/API — **kesh qilmang** (`Cache-Control: private` allaqachon). `Vary` ni Transform bilan qo‘shish oldin token/zona huquqi tufayli yopiq edi.

9. **Transform Rules (10)**  
   `X-Content-Type-Options`, `Referrer-Policy` (ilova allaqachon beradi — dublikat qilmang). HSTS edge da.

10. **Web Analytics**  
    Cookie’siz RUM. Google Analytics o‘rniga yoki yoniga. Zaraz — agar keyin pixel qo‘shilsa.

11. **Email Routing**  
    `hello@` / `support@rankwant.uz` → shaxsiy pochta. 200 qoida, 200 destination, 25 MiB kiruvchi. Javob destination manzildan ketadi, `rankwant.uz` dan emas. DMARC qattiq bo‘lsa forward yiqilishi mumkin.

12. **Access (`/admin`)**  
    50 user Free. Tunnel + Access = admin internetga ochiq emas.

13. **R2 10 GB**  
    Handoff + db dump. Egress $0. IA storage Free kvotaga kirmaydi.

### P1 — contest oldidan

14. **Workers 100k**  
    Katta oqim (ops: 7300 req/s) Free ga sig‘maydi. Variant:  
    - Workers Paid (kunlik 100k yo‘qoladi)  
    - yoki maintenance route’ni vaqtincha olib tashlash  
    Fail-open saytni saqlaydi, lekin 1033/bo‘sh origin da Worker yordam bermaydi.

### P2 — ixtiyoriy

15. Images 5000 transform — `/.netlify` emas, `/.cloudflare` Image Resizing / Images. Oshsa xato, hisob yo‘q.  
16. Workers AI 10k neuron — kichik tarjima/sinov; contest judge emas.  
17. Access + WARP staff noutbukiga (50 user).

---

## 9. Free da yo‘q / pullik — vaqtirmang

| Mahsulot | Minimal reja | RankWant |
|---|---|---|
| Snippets | Pro | Worker bor; shart emas |
| Custom Errors / branded 1xxx | Pro | Worker 503 sahifasi bor |
| Super Bot Fight Mode | Pro | Exception kerak bo‘lsa |
| CF Managed + OWASP ruleset | Pro | Free Managed yetishi mumkin |
| Waiting Room | Business | Contest navbati — hozir yo‘q |
| Argo / Smart Shield | ~$5+ | Kechikish; shart emas |
| Load Balancing | ~$5+ | Bitta origin |
| Stream | pullik | Video yo‘q |
| Advanced Certificate Manager | add-on | `rankwant.bugvector.uz` chuqur bo‘lsa Total TLS/ACM |
| Advanced Rate Limiting | Enterprise | Django + 1 ta IP qoida |
| Origin Host/SNI/DNS override | Enterprise | Tunnel yetadi |
| Log Explorer / Logpush | pullik | 24 soat Events |
| Cache Reserve | pullik | Trafik kichik |
| Email Sending (ixtiyoriy to) | Workers Paid | Brevo |
| Workers for Platforms / Dynamic Workers | Paid | Yo‘q |
| RealtimeKit | Paid | Yo‘q |

Pro ($20/oy) qachon: Snippets, Super Bot Fight exception, OWASP, ticket, image Polish. Hozir **shart emas**.

---

## 10. Kam ma’lum, bepul, foydali

1. **Turnstile cheksiz** — reCAPTCHA kvotasi yo‘q.  
2. **R2 egress $0** — S3 dan farq.  
3. **Worker fail-open** — 100k tugasa sayt yashil qoladi ( RankWant yoqqan).  
4. **Action: Block AI Bots** — `robots.txt` dan kuchliroq (edge).  
5. **Rate limit 10 s** kuchsiz ko‘rinadi; burst flood uchun yetadi, “300/soat” uchun emas.  
6. **Bulk Redirect 10 000** — eski URL.  
7. **Email Routing catch-all + plus addressing**.  
8. **Access 50 user** — `/admin` uchun “yashirin” Zero Trust.  
9. **Web Analytics** — GDPR-yengil, cookie banner shart emas (o‘zingiz baholang).  
10. **Images 5000** — oshsa to‘lov yo‘q, yangi transform 9422.  
11. **AI Gateway** asosiy cache/limit bepul.  
12. **Zaraz** — keyinroq marketing pixel.  
13. **Total TLS** — chuqur subdomain sertifikat (ba’zi zonalar; ACM pullik yo‘li ham bor). Universal = faqat 1-daraja.  
14. **Trace** — qaysi rule tegishini ko‘rish (sozlashda).  
15. **Tunnel replica** — 4 ulanish / 2 DC; ikkinchi `cloudflared` = HA (hozir bitta PID — yagona nuqta).

---

## 11. Xavflar (Free ni “yoqib yuborish”)

| Harakat | Xavf |
|---|---|
| Bot Fight Mode yoqish | API, mobile, uptime monitor, ba’zan odam — skip yo‘q |
| Cache Everything `/*` | Auth/HTML kesh — sessiya sizib chiqadi |
| SSL Flexible | Tunnel + HTTP origin; mitm |
| Worker fail-closed | 100k dan keyin butun sayt 1027 |
| Managed robots.txt Cloudflare | RankWant o‘zinikini beradi — **o‘chiq qoldiring** |
| Email Sending ni Brevo o‘rniga | Free da 1000 verify chiqmaydi |
| `rankwant.uz` tokenini `bugvector` tokeni bilan boshqarish | Zona ko‘rinmaydi; qoida yozilmaydi |

---

## 12. Qaror ro‘yxati (bajarish tartibi)

Dashboard, kod yo‘q. Boshqa sessiya deploy qilayotgan bo‘lsa — **faqat Security/Rules**, Tunnel/compose tegmang.

1. SSL: Full (strict), Always HTTPS.  
2. AI bots: Training/Agent **Block**.  
3. Free Managed Ruleset on.  
4. Custom: 1–2 qoida (bo‘sh UA; ixtiyoriy register challenge).  
5. 1 ta IP rate limit (10 s) register/login POST.  
6. `www` → `rankwant.uz` redirect.  
7. Cache Rule faqat `/_next/static`.  
8. Web Analytics beacon.  
9. Email Routing `support@`.  
10. Access `/admin` (50 user).  
11. Bot Fight Mode — **o‘chiq**, Events 1 hafta kuzatilgach qaror.  
12. Contest oldidan: Workers Paid **yoki** maintenance route off.

Turnstile + 300/soat **bajarilgan**. Email kvotasi (Brevo 616) Cloudflare Free bilan **hal bo‘lmaydi**.

---

## 13. Tezkor matritsa

| | Free | RankWant |
|---|---|---|
| DNS, CDN, SSL, DDoS, Tunnel | ✅ | Ishlatiladi |
| Turnstile cheksiz | ✅ | Yoqilgan |
| WAF 5 + RL 1×10s | ✅ | Yoqilmagan |
| Bot Fight (skip yo‘q) | ✅ | Ehtiyot |
| Block AI Bots | ✅ | Yoqish kerak |
| Workers 100k/kun | ✅ | **Limitga urilgan** |
| R2 10 GB, egress 0 | ✅ | Handoff |
| Pages / Snippets / Waiting Room | ❌ / Pro / Biz | Kerak emas / Worker bor |
| Email yuborish | Paid | Brevo |
| Access 50 user | ✅ | `/admin` uchun |

---

## Manbalar

- [Cloudflare plans](https://www.cloudflare.com/plans/) · [Free overview](https://www.cloudflare.com/plans/free/) · [Personal](https://www.cloudflare.com/personal/)
- [Workers limits](https://developers.cloudflare.com/workers/platform/limits/) (yangilangan 2026-09-05)
- [Turnstile plans](https://developers.cloudflare.com/turnstile/plans/) (2026-08-14)
- [WAF custom rules](https://developers.cloudflare.com/waf/custom-rules/) · [Rate limiting](https://developers.cloudflare.com/waf/rate-limiting-rules/) · [Managed rules](https://developers.cloudflare.com/waf/managed-rules/)
- [Bot Fight Mode](https://developers.cloudflare.com/bots/get-started/bot-fight-mode/) · [Block AI Bots](https://developers.cloudflare.com/bots/additional-configurations/block-ai-bots/)
- [Cache rules](https://developers.cloudflare.com/cache/how-to/cache-rules/) · [Default cache](https://developers.cloudflare.com/cache/concepts/default-cache-behavior/)
- [Redirects](https://developers.cloudflare.com/rules/url-forwarding/) · [Transform](https://developers.cloudflare.com/rules/transform/) · [Snippets](https://developers.cloudflare.com/rules/snippets/) · [Origin rules](https://developers.cloudflare.com/rules/origin-rules/)
- [R2 pricing](https://developers.cloudflare.com/r2/pricing/) · [Images pricing](https://developers.cloudflare.com/images/pricing/)
- [Email Service](https://developers.cloudflare.com/email-routing/) · [Email pricing](https://developers.cloudflare.com/email-service/platform/pricing/)
- [Tunnel](https://developers.cloudflare.com/tunnel/) · [Cloudflare One](https://developers.cloudflare.com/cloudflare-one/)
- [Universal SSL](https://developers.cloudflare.com/ssl/edge-certificates/universal-ssl/)
- [Security Analytics limits](https://developers.cloudflare.com/waf/analytics/security-analytics/)
- [Web Analytics](https://developers.cloudflare.com/web-analytics/) · [Zaraz](https://developers.cloudflare.com/zaraz/)
- [Waiting Room plans](https://developers.cloudflare.com/waiting-room/plans/)
- [Workers AI pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/) · [AI Gateway pricing](https://developers.cloudflare.com/ai-gateway/reference/pricing/)
- RankWant: `docs/10-operations/README.md`, `services/maintenance-worker/README.md`
