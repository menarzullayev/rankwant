# RankWant — 50 000 foydalanuvchiga masshtab: amaliy tavsiyalar

**Sana:** 2026-09-19  
**Maqsad:** 50 000 foydalanuvchiga bardosh. Bu yozuv **darslik emas** — hozirgi stek, o‘lchovlar va [06-architecture](../../06-architecture/README.md) ustiga qo‘yilgan.  
**Keyin:** Qarorlar qabul qilindi (jadval §12). Kod: [IMPLEMENTATION.md](IMPLEMENTATION.md).

> Tirik siyosat emas. Qaror qabul qilingach ADR / `docs/06` / `docs/10` yangilanadi.

---

## 0. 50 000 nima — va hozir nima bor

**Ishchi ta’rif (shu yozuv uchun):** 50 000 = ro‘yxatdan o‘tgan / oyiga qaytadigan foydalanuvchi. Bir vaqtda 50 000 ochiq sessiya **emas**. Contest paytida yuzlab–mingta bir vaqtda; reklama pulsida o‘n minglab sahifa ochilishi.

50 000 concurrent uchun boshqa reja kerak (multi-region, read-replicas + qalin CDN, judge fermasi). Hozirgi o‘lchovlar buni qo‘llab-quvvatlamaydi.

**Hozir (2026-09-19):**

| Qatlam | Holat |
|---|---|
| Web | Bitta Next.js SSR, `127.0.0.1:8300` = jonli origin |
| API | Django + gunicorn **4 sync** + Celery worker/beat |
| Judge | Go + nsjail, Redis navbat; 1 hostda ~8 worker to‘yinadi |
| Data | Postgres 16 + Redis 7 + S3/R2 (local MinIO) |
| Chekka | Cloudflare; mehmon `GET /` CDN kesh; `/login` `DYNAMIC` + Worker |
| Topologiya | To‘rt host (app · web · judge×N · data) **hujjatda bor, qurilmagan** — preview bitta mashina |
| O‘lchov | Login/register spike shift ~180–190 HTML/s; 300 bir zumda p95 ~1.5 s; homepage 100 VU p95 1.65 s (keshdan oldin) |

50k hisob **mikroservis yetishmasligidan** yiqilmaydi. U bitta origin, `private no-store` sahifalar, 4 sync worker, Worker 100k/kun va judge host yetishmasligidan yiqiladi.

---

## 1. Arxitektura (monolit → mikroservislar)

### 1.1 Modular monolitni saqlash, replika bilan kengaytirish — **tavsiya**

**Muammo:** «Mikroservis qilmasak 50k ko‘tarmaymiz» degan tashvish. Hozirgi og‘riq — jarayonlar soni emas, **bitta nusxa**.

**Yechim:** Qolgan bo‘linishni saqlash: Next `web` · Django `api`+Celery · `judge`×N · `postgres`/`redis`/`s3`. 50k da `web` va `api` ni **2–4 replica**, judge ni contest oldidan **host** qo‘shish. Yangi deployable servis ochilmaydi.

**Afzallik:** o‘lchangan bottleneck’larga to‘g‘ri keladi; bitta transaction (reyting, Qvant, standings); deploy/CI o‘zgarmaydi; odam-soni hozirgi kabi.

**Kamchilik:** bitta Django releasi katta bo‘lib qoladi; jamoa 15+ kishiga o‘ssa releaslar to‘qnashadi.

### 1.2 Hozir 4–6 biznes-servisga bo‘lish (auth, catalog, contest, notify)

**Muammo:** Django ichida contest/auth/judge chaqiruvlari aralash, kelajakda alohida jamoalar.

**Yechim:** Har bounded context — alohida jarayon, o‘z DB yoki schema, REST/event.

**Afzallik:** keyinroq mustaqil scale (standings vs auth).

**Kamchilik:** 50k da **erta**. Distributed transaction (submit → verdict → rating → Qvant) bug va kechikish manbai. Operatsiya narxi 3–5×. O‘lchangan 180 HTML/s muammosini yechmaydi.

### 1.3 To‘liq mikroservis + mesh

**Muammo:** «Katta platforma shunday ko‘rinishi kerak».

**Yechim:** 10+ servis, gRPC, service mesh, har biri CI.

**Afzallik:** nazariy izolyatsiya.

**Kamchilik:** 50k va 1–3 kishilik jamoa uchun zarar. Preview’da to‘rt host hali yo‘q.

**CTO qoidasi:** 50k = **modular monolit + replica**. Mikroservis — bottleneck o‘lchangan va bitta jamoa bitta releasni ushlab tura olmaganda.

---

## 2. Ma’lumotlar bazasi

### 2.1 Sharding — **50k da qilmang**

**Muammo:** bitta Postgres «sig‘maydi» degan qo‘rquv.

**Yechim:** 50k user + yuz minglab attempt — bitta Postgres 16 (indeks + vacuum + yetarli RAM) uchun oddiy. Sharding user_id yoki contest_id bo‘yicha.

**Afzallik (sharding):** petabayt yoki multi-region yozuv.

**Kamchilik:** cross-shard standings/rating deyarli imkonsiz; 50k da foyda yo‘q.

### 2.2 Primary + async replica (o‘qish) — **keyingi bosqich, 50k o‘rtasida**

**Muammo:** standings, katalog, `/me/` primary ni o‘qishda bosadi; yozuv (submit, rating) kechikadi.

**Yechim:** 1 primary (yozuv + transactional o‘qish) + 1 replica (katalog, arxiv, hisobot). Django `DATABASES` replica router. Replica lag > 1–2 s bo‘lsa standings primary’da qoladi.

**Afzallik:** o‘qish 2×; primary backup sifatida.

**Kamchilik:** lag; noto‘g‘ri router — «men submit qildim, ro‘yxatda yo‘q». Avval `pg_stat_statements` bilan isbot kerak.

### 2.3 Indekslash va so‘rov tartibi — **hozir**

**Muammo:** N+1, ketma-ket scan, standings to‘liq jadval.

**Yechim:** `pg_stat_statements` + EXPLAIN. Attempt(contest, user, verdict), rating history, problem filter uchun kompozit indeks. Standings — materialize/kesh, har so‘rovda to‘liq sort emas ([10-operations](../../10-operations/README.md) 110k tomoshabin hisobi).

**Afzallik:** tekinishga yaqin yutuq; sharding’siz 10×.

**Kamchilik:** ortiqcha indeks yozuvni sekinlatadi; «hamma ustunga indeks» — tuzoq.

### 2.4 Connection pool (PgBouncer) — **api replica 2+ bo‘lganda**

**Muammo:** gunicorn/Next har biri Postgres ulanishi ochadi; replica × worker = ulanish tugaydi.

**Yechim:** transaction-mode PgBouncer data hostida. App `max_connections` kichik.

**Afzallik:** 4 → 16 worker xavfsiz.

**Kamchilik:** transaction-mode da session features (advisory lock, listen) ehtiyot. Bitta gunicorn 4 uchun hozir shart emas.

---

## 3. Keshlash (Redis, CDN)

### 3.1 CDN: mehmon o‘qish sahifalarini kengaytirish — **eng yuqori ROI**

**Muammo:** `/` keshlandi; `/login`, `/login?tab=register` `DYNAMIC` + Worker ~200 ms; 100k tashrif = kunlik Worker kvota.

**Yechim:** cookie-aware qoida (homepage dagi kabi): sessiyasiz GET HTML → `s-maxage` + SWR; `sessionid` / `rw_locale` / `rw:markup` → `private`. Login/register da `rw_exp` Set-Cookie keshni o‘ldiradi — avval cookie siyosatini ajratish.

**Afzallik:** origin 180 HTML/s o‘rniga chekka 10k+/s; Worker tejaladi.

**Kamchilik:** noto‘g‘ri kesh — shaxsiy sahifa ommaga. Login POST hech qachon keshlanmaydi.

### 3.2 Redis: fragment + standings + throttle — **bor, to‘g‘ri ishlating**

**Muammo:** har HTML `providers` + `stats`; standings origin’ni yiqitadi; anon throttle maktab NAT’ida 429.

**Yechim:** Redis allaqachon session/Celery/judge. Qo‘shish: `stats` 10–30 s, `providers` 60 s, standings snapshot 3–10 s (ommaviy, `standings/me/` alohida). Throttle: IP + ixtiyoriy session, katalog o‘qishini yozuvdan ajratish.

**Afzallik:** API 200k takror so‘rov yo‘qoladi; maktab sinfi yashaydi.

**Kamchilik:** stale son (ijtimoiy dalil 30 s kechikishi OK); Redis yakka nuqta — persistence + replica keyin.

### 3.3 Next `force-dynamic` ni qatlamma-qatlam yumshatish

**Muammo:** `cookies()` + dynamic = `private no-store`, CDN foydasiz.

**Yechim:** faqat shaxsiy marshrutlar dynamic; mehmon katalog/home — static yoki revalidate. Instrumentation Set-Cookie ni mehmonda kesmasin.

**Afzallik:** kesh ishlaydi.

**Kamchilik:** locale/eksperiment cookie qayta dizayn.

**Redis-as-DB yoki «hamma narsani Kafka orqali keshla» — 50k da yo‘q.**

---

## 4. Xabar almashinuvi (Celery vs Kafka/RabbitMQ)

### 4.1 Celery + Redis ni saqlash — **tavsiya**

**Muammo:** «50k uchun Kafka kerak».

**Yechim:** Hozirgi navbat: Celery (email, og‘ir ish) + Redis judge queue. 50k user / 50 submit/s contest — Redis list/streams + yetarli judge host yetadi. Kafka — ko‘p mustaqil consumer, replay, audit log kerak bo‘lganda (reyting fan-out 5+ servisga).

**Afzallik:** stek o‘zgarmaydi; operatsiya tanish; latency past.

**Kamchilik:** Redis broker — katta backlogda xotira; Kafka kabi multi-week replay yo‘q.

### 4.2 RabbitMQ ga o‘tish

**Muammo:** Celery+Redis visibility/ack zaif, uzoq task yo‘qolishi.

**Yechim:** RabbitMQ broker, Redis result backend.

**Afzallik:** yaxshiroq ack, DLQ.

**Kamchilik:** yana bitta data-plane; 50k da Celery yo‘qotishi o‘lchanmagan. Avval o‘lchash.

### 4.3 Kafka

**Muammo:** hodisa jurnali, bir nechta mustaqil o‘quvchi.

**Yechim:** submit.judged, rating.changed topiclari.

**Afzallik:** replay; kelajakdagi analitika.

**Kamchilik:** klaster (3 broker) narxi va murakkabligi 50k dan katta. Hozir **qilmang**.

**Judge navbatini Kafka ga ko‘chirmang** — worker pull + sandbox izolyatsiyasi Redis/S3 bilan qurulgan ([ADR-0004](../../07-adr/0004-judge-engine.md)).

---

## 5. Load balancing

### 5.1 Chekka: Cloudflare (bor) — origin’ga to‘g‘ri Host

**Muammo:** 301 `Host: host.docker.internal` → jonli domen; Worker kvota.

**Yechim:** CF load balancer / oddiy DNS. Origin pool: 2+ `web`, 2+ `api`. Health: `/` yoki `/api/v1/health` (Host majburiy).

**Afzallik:** DDoS, TLS, geo; yangi LB mahsuloti shart emas.

**Kamchilik:** Free Worker 100k/kun — HTML kesh yoki Worker’ni login’dan chiqarish.

### 5.2 Origin: 2+ replica, sticky faqat kerak joyda

**Muammo:** bitta `web` 395 MiB / 100 VU; o‘lim = sayt o‘lik.

**Yechim:** `web`×2, `api`×2 (gunicorn yoki gthread). Session cookie — Redis/DB, sticky shart emas. WebSocket/SSE bo‘lsa sticky yoki common Redis.

**Afzallik:** nol-downtime deploy; 180 HTML/s × 2.

**Kamchilik:** 2× RAM; sessiyasiz sticky — foydasiz.

### 5.3 gunicorn 4 sync — almashtirish

**Muammo:** 4 sync = 4 bir vaqtda API; login HTML 2 ta API chaqiradi.

**Yechim:** avval worker sonini CPU-1 gacha (masalan 8); keyin `gthread` yoki asgi agar I/O kutish o‘lchansa. Sync CPU-bound view uchun qoladi.

**Afzallik:** kichik o‘zgarish, katta navbat qisqarishi.

**Kamchilik:** ko‘p sync = ko‘p RAM + DB ulanish (PgBouncer).

---

## 6. Konteynerlash va orkestratsiya

### 6.1 Compose + 2–4 VM (to‘rt-host reja) — **50k tavsiya**

**Muammo:** bitta mashina preview; reboot = hammasi.

**Yechim:** Hujjatdagi topologiya: **data** (Postgres+Redis) · **app** (api+celery) · **web** · **judge×N**. `docker compose` + Caddy/CF. Contest oldidan judge VM.

**Afzallik:** `deploy.sh` saqlanadi; xavfsizlik chegarasi (judge kiruvchi port yo‘q) oson; narx past.

**Kamchilik:** qoshlash qo‘lda; multi-AZ avtomatik emas.

### 6.2 Kubernetes endi

**Muammo:** «production = k8s».

**Yechim:** Deployment/HPA/Ingress.

**Afzallik:** judge HPA, rolling; 10+ servisda oqlanadi.

**Kamchilik:** 50k va 3 servis uchun control plane + networking + storage class — odam va pul. Contest spike 10 s — HPA **ulgurmaydi** (allaqachon yozilgan: oldindan scale). K8s spike’ni sehrlamaydi.

### 6.3 Managed container (Cloud Run / Fly / Render)

**Muammo:** VM parvarishi.

**Yechim:** web/api managed; judge **qolmasin** (privileged sandbox).

**Afzallik:** web/api uchun tunda uxla.

**Kamchilik:** judge maxsus host; cold start SSR; narx o‘sadi.

**50k: K8s yo‘q. Avval to‘rt host compose.**

---

## 7. Monitoring (Prometheus, Grafana, va h.k.)

### 7.1 Uch signal hozir — **tavsiya tartibi**

**Muammo:** 180 HTML/s shift, Worker kvota, judge navbat — ko‘rimasdan kengaytirish.

**Yechim:**

1. **Xato:** Sentry (web+api) + CF 5xx.
2. **Yuk:** konteyner CPU/RAM, gunicorn queue, Redis `llen` judge, Postgres `pg_stat_activity`.
3. **SLO:** login/register/home TTFB, standings p95, judge `created_at→judged_at`, Worker qolgan kvota.

Prometheus+Grafana — 3+ host bo‘lganda. Bitta preview mashinada: CF analytics + `docker stats` + Sentry + bitta uptime check yetadi.

**Afzallik:** qaror o‘lchovga tayanadi (login/register hisobotlari kabi).

**Kamchilik:** to‘liq LGTM steki erta — texnik qarz.

### 7.2 «Hamma narsani Grafana Cloud»

**Afzallik:** tez.

**Kamchilik:** narx; kardinalite (user_id label) hisobni yoqadi. Label’da user_id qo‘ymang.

---

## 8. CI/CD

### 8.1 Hozirgi yo‘lni qattiqlashtirish — **tavsiya**

**Muammo:** CI yashil ≠ konteyner yangi; contest paytida deploy taqiqlangan; main’ga to‘g‘ridan push yo‘q.

**Yechim:** saqlash: PR → CI+Security → `deploy.sh --yes` faqat `HEAD==origin/main`. Qo‘shish: deploydan keyin tashqi smoke (login 200, `CF-Cache-Status` `/` uchun HIT/EXPIRED mehmonda); image digest pin; contest oynasi lock (allaqachon qoida).

**Afzallik:** 50k da rollback = oldingi tag.

**Kamchilik:** qo‘lda deploy odamga bog‘liq — 2-operator bo‘lganda OK.

### 8.2 GitOps + K8s CD (Argo)

**Muammo:** ko‘p muhit, ko‘p servis.

**Yechim:** manifest repo.

**Afzallik:** audit.

**Kamchilik:** K8s yo‘q joyda ma’nosiz.

### 8.3 Preview app har PR

**Afzallik:** dizayn/SSR tekshiruv.

**Kamchilik:** judge+DB har PR — qimmat. 50k oldidan ixtiyoriy; web-only preview yetarli.

---

## 9. Xavfsizlik (50k = nishon)

### 9.1 Abuse va maktab NAT

**Muammo:** anon 60/min bitta IP — sinf 429; register ochiq.

**Yechim:** o‘qish vs yozuv throttle; Turnstile register’da (bor); `THROTTLE_REGISTER` ni saqlash; WAF bot score. 50k tab ochish ≠ 50k POST.

**Afzallik:** reklama pulsida baza to‘lmaydi.

**Kamchilik:** qattiq limit — qonuniy sinf. Katalog o‘qishini yumshatish (docs/10 ochiq risk).

### 9.2 Judge izolyatsiyasi

**Muammo:** ommaviy kod, `--privileged`.

**Yechim:** judge host alohida, kiruvchi port yo‘q, DB credential yo‘q (arxiv). 50k submit = 50k untrusted binary. Host qo‘shish = xavf yuzasi; image bir xil, tarmoq yopiq.

**Afzallik:** API yorilsa ham sandbox uyoqda.

**Kamchilik:** privileged qolsa host compromise. Uzoq: rootless/gVisor tadqiqoti — 50k bloklovchi emas.

### 9.3 Sessiya, cookie, kesh

**Muammo:** noto‘g‘ri CDN = sessiya oqishi.

**Yechim:** `Cache-Control` + cookie allowlist; `Set-Cookie` mehmon keshida yo‘q (homepage dars).

**Afzallik:** 50k xavfsiz kesh.

**Kamchilik:** muhandislik intizomi.

### 9.4 Sirlar va admin

**Muammo:** 50k user = dump qimmat.

**Yechim:** env faqat host/secret manager; admin 2FA; backup shifr; `prune`/wipe faqat preview.

---

## 10. Narx va ijro samaradorligi

| Qadam | Taxminiy yutuq | Taxminiy narx | Qachon |
|---|---|---|---|
| Mehmon HTML CDN (`/` kengaytirish, Worker’ni qisqartirish) | Origin va Worker kvota | past (muhandislik) | hozir |
| Redis `stats`/`providers`/standings | API ×2 kam | Redis bor | hozir |
| `web`×2 + `api`×2, gunicorn worker | 180→300+ HTML/s, 4→8 API | 1 qo‘shimcha VM | 4-host qurilganda |
| Judge host ×6–8 contest oldidan | 50 submit/s NFR | CPU soati, contest kuni | birinchi katta contest |
| Postgres replica + pgbouncer | o‘qish zaxirasi | 1 data VM | `pg_stat` isboti |
| K8s / Kafka / 6 mikroservis | past (50k da) | yuqori | **keyinroq yoki hech qachon** |

**Tejash qoidalari:** Worker Free 100k/kun — reklama kuni tugaydi. HTML kesh = pul. Judge’ni 24/7 8 hostda ushlamang — contest oldidan yoqing. Managed K8s oyligi 50k hisobdan qimmatroq bo‘lishi mumkin.

---

## 11. 50k uchun qilinmasin

- Sharding, Kafka, service mesh, K8s «chunki katta».
- Login/register POST ni keshla**sh**.
- Jonli `rankwant.uz` ga 1000 VU k6 (Worker + origin).
- Contest paytida deploy.
- Bitta PR da «to‘liq masshtab».

---

## 12. Qabul qilingan qarorlar

| # | Sessiya | Qaror | Sana |
|---|---|---|---|
| 1 | Arxitektura | **Modular monolit + replica** — web, API/Celery, judge×N; 50k da yangi biznes-servis yo‘q | 2026-09-19 |
| 2 | Ma’lumotlar bazasi | **Bitta Postgres + indeks** — replica/shard yo‘q; avval `pg_stat_statements` | 2026-09-19 |
| 3 | Keshlash | **Redis + mehmon CDN kengaytirish** — login HTML faqat cookie ajratilgach | 2026-09-19 |
| 4 | Navbat | **Celery + Redis** — Kafka/Rabbit yo‘q; judge navbati Redis’da qoladi | 2026-09-19 |
| 5 | Load balancing | **CF + origin replica** — web×2, api×2; sticky yo‘q; multi-region yo‘q | 2026-09-19 |
| 6 | Monitoring | **CF + SLO, Sentry yo‘q** — 5xx, Worker kvota, CPU/RAM, judge navbat, p95; Prometheus 3+ hostda | 2026-09-19 |
| 7 | Deployment | **Compose to‘rt host** — data · app · web · judge×N; K8s/managed yo‘q | 2026-09-19 |

## 13. Qaror sessiyalari (ketma-ketlik)

Har sessiyada **1 savol**, variantlar bir-birini istisno qiladi, CTO bitta variantni ko‘rsatadi.

1. **Arxitektura** — monolit replica vs hozir mikroservis (shu sessiyadan).
2. **Ma’lumotlar bazasi** — bitta Postgres vs replica vs sharding.
3. **Keshlash** — faqat Redis vs CDN kengaytirish vs ikkalasi.
4. **Navbat** — Celery+Redis vs Rabbit vs Kafka.
5. **Load balancing + origin** — CF-only vs 2 replica vs to‘liq 4 host.
6. **Monitoring** — Sentry+CF vs Prometheus endi vs to‘liq LGTM.
7. **Deployment** — compose 4 host vs managed vs K8s.

---

## 14. Manba o‘lchovlar

- [2026-09-17-homepage-load](../2026-09-17-homepage-load/REPORT.md)
- [2026-09-19-login-load](../2026-09-19-login-load/REPORT.md)
- [2026-09-19-register-load](../2026-09-19-register-load/REPORT.md)
- [10-operations](../../10-operations/README.md) — judge 8 worker/host, 50 submit/s ≈ 6–8 host
