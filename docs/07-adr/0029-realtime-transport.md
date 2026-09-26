# ADR-0029 — Real vaqtli aloqa: chegara, transport va ish rejimi

- **Holat:** **qabul qilingan (accepted)** — 2026-09-27
- **Sana:** 2026-09-27
- **Approved by:** Saidakbar Narzullayev — repo owner, 2026-09-27
- **Bog'liq:** [ADR-0003](0003-stack-django-next.md) (stack va «SSE, WebSocket emas» qarori) ·
  [ADR-0008](0008-auth-session-plus-pat.md) (cookie sessiyasi) ·
  [ADR-0028](0028-judge-container-isolation.md) (Redis'ni ish turi bo'yicha ajratish) ·
  `docs/06-architecture` (🔒 qulflangan) · `docs/10-operations` § Standings sig'imi

---

## 1. Muammo

Platformada real vaqtli aloqa yo'q. Uchta joyda kerak bo'ladi:

| Joy | Nima kutadi | Kim ko'radi |
| --- | --- | --- |
| Urinish natijasi | «Navbatda» → verdikt, sahifani yangilamasdan | **Faqat egasi** |
| Bildirishnomalar | yangi xabar/hack/reyting o'zgarishi | **Faqat egasi** |
| Duel / Arena | raqibning holati, sub-sekund | Ishtirokchilar |
| Musobaqa standings | jadval yangilanishi | **Hamma bir xil** |

To'rtinchisi qolgan uchtasidan tubdan farq qiladi va bu farq butun qarorni belgilaydi.

## 2. Dalil — o'lchangan holat

**Hozirgi yuklama (o'lchandi, 2026-09-27, jonli stack):**

```
jami urinish: 5        oxirgi 24 soat: 0
PENDING: 0             RUNNING: 0
api CPU 0.01%          redis CPU 2.04%      web 322 MiB
```

Ya'ni **yuklama bo'yicha ehtiyoj nolga teng**. Bu muhim: qaror sig'imga emas,
**mahsulot talabiga** tayanadi.

**ADR-0003 sharti bajarilganini tekshirish.** O'sha ADR aynan shunday deydi:

> «SSE, WebSocket emas — contest standings 10–30 soniyada yangilansa yetarli.
> Django Channels/ASGI murakkabligi MVP'da **asossiz**. **O'lchangan ehtiyoj
> bo'lsa keyin qo'shiladi**.»

Demak savol «qo'shamizmi?» emas, **«qaysi ehtiyoj o'lchandi?»**. Javob:
sig'im emas — **foydalanuvchi kutishi**. Sud hukmi 2 sekunddan 5 daqiqagacha
kechikadi (`drain_results` har 2 s, gavjum musobaqada navbat chuqur), va
foydalanuvchi shu vaqt davomida sahifani qo'lda yangilab turadi. Bu
funksional bo'shliq, yuklama muammosi emas.

**Ommaviy jadval uchun esa teskari dalil bor** (`docs/10-operations`, o'lchandi
2026-09-10): 110 000 tomoshabin × 15 s polling = **7 300 so'rov/s, 330 MB/s**,
origin esa ~130 so'rov/s ko'taradi. U yerda yechim — **chekka kesh** (45 KB
javob, 500 qator, hamma uchun bir xil). O'sha hujjat ochiq yozadi:

> «Alohida SSE xizmati bu muammoni YECHMAYDI: 110 000 ochiq ulanishni ushlab
> turish, hamma bir xil hujjatni kutayotgan joyda, chekka keshi tekinga
> beradigan narsani qimmat qiladi.»

## 3. Qaror 1 — chegara: shaxsiy oqim + ommaviy jadvalga INVALIDATSIYA signali

**Qabul qilindi (Saidakbar Narzullayev, 2026-09-27):** ommaviy jadval ham real
vaqtga o'tadi. Quyidagi jadval shu qaror bilan yangilangan.

| Oqim | Kesh | Transport | Yuboriladigan narsa |
| --- | --- | --- | --- |
| **Urinish verdikti** | yo'q (shaxsiy) | **SSE** | hodisa yuki |
| **Bildirishnomalar** | yo'q (shaxsiy) | **SSE** | hodisa yuki |
| **Ommaviy standings** | chekka (CDN) | **SSE + mavjud polling** | ⚠️ **faqat versiya belgisi** |
| **Duel / Arena** | yo'q | **WebSocket** (keyin) | hodisa yuki |

### ⚠️ Nega jadval oqimi YUKNI emas, BELGINI tashiydi

`docs/10` o'lchovi (2026-09-10) o'z kuchida qoladi: 110 000 tomoshabin × 15 s
polling = **7 300 so'rov/s, 330 MB/s**, origin esa ~130 so'rov/s ko'taradi.
Yechim — **chekka kesh** (500 qator = 45 KB, hamma uchun bir xil).

Shu sababli jadval oqimi **jadvalni o'zi yubormaydi**. U faqat bitta qisqa
hodisa yuboradi:

```
event: standings
data: {"version":"c1f8a2","at":"2026-09-27T02:10:11Z"}
```

Mijoz versiyani oxirgi ko'rgani bilan solishtiradi va **faqat farq bo'lsa**
mavjud keshli endpointdan jadvalni qayta oladi. Ya'ni:

- 45 KB hujjat **hamon CDN keshidan** ketadi — origin yuki o'zgarmaydi;
- oqim faqat «o'zgargan/o'zgargan emas» degan bir bitni tashiydi;
- kesh ishlamay qolsa ham xatti-harakat **aynan bugungidek** qoladi.

### ⚠️ Va chegara — ochiq ulanish soni

`docs/10` ning e'tirozi yuk hajmida emas, **110 000 ochiq ulanishni ushlab
turishda** edi. Shuning uchun qaror shartli:

1. **Ulanish chegarasi bor** (§8). Chegaradan oshgan mijoz **503** oladi va
   **polling'ga qaytadi** — ya'ni o'sha keshli yo'lga.
2. Ya'ni SSE — keshli polling **ustidagi optimizatsiya**, uning o'rnini
   bosuvchi emas. Katta miqyosda ko'pchilik baribir CDN dan oladi.
3. Real miqyos o'lchandi (§2): **5 urinish, 0 foydalanuvchi**. 110 000 —
   loyihaviy taxmin, bugungi yuklama emas. Shu sababli hozir SSE arzon,
   va u **o'chirilsa hech narsa buzilmaydi** (§13).

Bu shartlar bajarilmasa (chegara olib tashlansa yoki oqim jadvalning o'zini
tashiy boshlasa) qaror `docs/10` o'lchoviga zid bo'lib qoladi va qayta
ko'rilishi kerak.


## 4. Qaror 2 — transport: SSE hozir, WebSocket keyin

| | SSE | WebSocket |
| --- | --- | --- |
| Yo'nalish | bir tomonlama (server → mijoz) | ikki tomonlama |
| Protokol | oddiy HTTP/1.1+ | Upgrade, alohida protokol |
| Auth | cookie avtomatik ketadi | qo'lda (handshake sarlavhalari) |
| Qayta ulanish | `EventSource` o'zi qiladi | **qo'lda yoziladi** |
| Chekka | Cloudflare Tunnel HTTP sifatida o'tkazadi | upgrade yo'li sinalishi kerak |
| Fan-out | Redis pub/sub, sticky shart emas | guruh qatlami kerak |
| Brauzer qo'llab-quvvatlashi | `EventSource` — hamma joyda | hamma joyda |

**Qaror: SSE.** Uchta ehtiyojning ikkitasi bir tomonlama, ya'ni WebSocket
beradigan qo'shimcha qobiliyat ishlatilmaydi, lekin uning narxi
(qayta ulanish mantiqi, upgrade, guruh qatlami) to'lanadi.

**Birgalikda ishlatish strategiyasi:** bitta **hodisa modeli** (Redis kanali +
JSON sxema), ikki **transport**. Server tomonda hodisa qanday yuborilishini
bilmaydi; Duel paydo bo'lganda o'sha model ustiga WS uzatgichi qo'shiladi.
Ya'ni bugungi ish WS ni bloklamaydi ham, oldindan qurmaydi ham.

## 5. Qaror 3 — ish rejimi: alohida `realtime` xizmati

⚠️ **Bu qarorning eng muhim sababi — `gunicorn`.** Hozir `api` shunday ishlaydi:

```
CMD gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers ${GUNICORN_WORKERS}  # 4
```

**Sync worker** bir vaqtda bitta so'rovni bajaradi. SSE ulanishi esa
**butun umri davomida ochiq turadi** — ya'ni bitta ulanish bitta worker'ni
egallaydi. To'rt worker ⇒ **beshinchi ochiq ulanish butun API ni to'xtatadi**.
Bu nazariy xavf emas, sync modelning ta'rifi.

| Variant | Afzallik | Kamchilik | Hukm |
| --- | --- | --- | --- |
| A. `api` ni ASGI ga o'tkazish | bitta xizmat | butun API runtime'i almashadi; 4 worker'ning hammasi oqimga ochiladi | rad |
| B. `gthread` + ulanish chegarasi | kichik o'zgarish | thread baribir band; chegara = sig'im shifti | rad |
| C. **alohida `realtime` (ASGI/uvicorn)** | **API tegilmaydi; nosozlik izolyatsiyasi** | yangi servis, deploy qadamiga qo'shiladi | **qabul** |
| D. Django Channels | tayyor auth/guruh qatlami | ADR-0003 uni «asossiz murakkablik» deb atagan; SSE uning tabiiy protokoli emas | keyin (WS bilan) |

**Qaror: C.** `config/asgi.py` qo'shiladi va **tor ASGI ilova** ishga tushadi —
u faqat `/api/v1/events/` (va health) yo'lini biladi, qolganiga 404 qaytaradi.
Ya'ni u «ikkinchi API» emas, bitta vazifali xizmat.

Nima uchun bu muhim: agar oqim to'yingan bo'lsa, **`realtime` yiqiladi, API
emas**. Foydalanuvchi sahifani yangilay oladi, yubora oladi, faqat jonli
yangilanish ishlamaydi — va u polling'ga tushadi (§9).

## 6. Oqim

```
judge (Go) ──▶ Redis navbat ──▶ drain_results (Celery, 2 s)
                                        │
                                        ▼  apply_result() — DB tranzaksiyasi
                                        │
                             transaction.on_commit  ◀── ⚠️ SHART
                                        │
                                        ▼
                          Redis pub/sub   rw:user:{user_id}
                                        │
                                        ▼
                    realtime (ASGI, N worker) ──▶ SSE ──▶ brauzer
                                                              EventSource
```

⚠️ **`transaction.on_commit` shart.** Usiz obunachi hali commit qilinmagan
qator haqida xabar oladi, keyin uni REST dan qayta o'qisa — eski holatni
ko'radi va «verdikt o'zgardi-yu, qaytib ketdi» degan taassurot qoladi.

**Kanal nomlari:** `rw:user:{user_id}` (verdikt + bildirishnoma, bitta oqimda),
`rw:attempt:{attempt_id}` (faqat shu urinishni kuzatayotganlarga).
Kanal nomi **sessiyadan** olinadi, mijozdan emas (§7).

## 7. Autentifikatsiya

- **Cookie** (ADR-0008). `EventSource` bir xil origin'ga cookie'ni **o'zi**
  yuboradi — qo'shimcha kod yo'q.
- Sessiya `cached_db` (`SESSION_ENGINE`) da, ya'ni Redis+DB orqali
  **har qanday jarayon** tekshira oladi — `realtime` shu sababli Django
  sessiyasini o'zi o'qiy oladi.
- ⚠️ **Query-string'da token TAQIQLANADI.** U `Referer` va kirish loglariga
  tushadi. Bu SSE ning eng ko'p tarqalgan xatosi.
- ⚠️ **Kanal sessiyadan olinadi.** Mijoz `?user_id=` bera olmaydi — aks holda
  begona odamning verdiktini kuzatish mumkin bo'lardi (IDOR).
- ⚠️ **Oqim faqat o'qish uchun.** CSRF GET orqali holat o'zgartira olmaydi,
  lekin oqim orqali hech qanday buyruq qabul qilinmaydi — bu shartnoma.
- Avtorizatsiya oqim boshlanishidan **oldin**: anonim so'rov 401 oladi, yarim
  ochiq oqim emas.
- Sarlavhalar: `Content-Type: text/event-stream`, `Cache-Control: no-store`,
  `X-Accel-Buffering: no` (proksi buferini o'chirish), `Connection: keep-alive`.

## 8. Ulanish boshqaruvi

- **Bitta ko'p kanalli oqim.** Bir varaq (tab) uchun **bitta** `EventSource`;
  verdikt ham, bildirishnoma ham shu oqimda, `event:` turi bilan ajratiladi.
  Har tur uchun alohida ulanish ochish brauzerning 6-ulanish limitini yeb qo'yardi.
- **Heartbeat har 15 s** — `: ping` izohi. Sabab: Cloudflare proksisi bo'sh
  turgan ulanishni ~100 s da uzadi; muntazam izoh buni oldini oladi.
  ⚠️ Heartbeat **hodisa emas**, izoh (`:` bilan boshlanadi) — mijoz uni
  `message` deb o'qimaydi.
- **`retry:` maydoni** oqim boshida — mijozning qayta ulanish oralig'ini
  server boshqaradi (standart 3000 ms o'rniga 5000 ms).
- **Har foydalanuvchi uchun ulanish chegarasi** (5). Oshsa eng eskisi
  yopiladi: ochiq qolgan tablar to'planib qolmasin.
- **Umumiy chegara.** Oshsa yangi ulanish **503** oladi (osilib qolmaydi) —
  mijoz darhol polling'ga tushadi.
- ⚠️ **Sekin iste'molchi.** Har ulanish uchun navbat **chegaralangan**; to'lib
  ketsa ulanish yopiladi. Cheksiz bufer — OOM ning eng qisqa yo'li.

## 9. Qayta ulanish va uzilishlar

- `EventSource` uzilganda **o'zi** qayta ulanadi (`retry:` oralig'ida).
- **`Last-Event-ID`** — mijoz yuboradi, server o'sha ID dan keyingi hodisalarni
  Redis'dagi **qisqa replay buferi**dan (oxirgi 50 hodisa, TTL 5 daqiqa) qaytaradi.
- Bufer yo'q bo'lsa server **`resync`** hodisasini yuboradi — mijoz holatni
  REST dan qayta o'qiydi.
- ⚠️ **Asosiy qoida: oqim — optimallashtirish, haqiqat manbasi EMAS.**
  Yo'qolgan hodisa hech qachon noto'g'ri holatga olib kelmasligi kerak; eng
  yomon holat — bir marta ortiqcha so'rov.
- Takroriy uzilishda eksponensial backoff + jitter; N urinishdan keyin mijoz
  **butunlay polling'ga** o'tadi va bir necha daqiqadan keyin qayta sinaydi.
- Server tomonda: `asyncio.CancelledError` da **obuna albatta tozalanadi**
  (aks holda Redis obunalari sizib chiqadi); yozishda xato bo'lsa ulanish yopiladi.
- Redis yiqilgan bo'lsa `realtime` **503** qaytaradi — ochiq, lekin jim
  turgan ulanish emas.

## 10. Masshtablash va yuk taqsimoti

- **Sticky sessiya kerak emas.** Fan-out Redis pub/sub orqali, ya'ni istalgan
  `realtime` worker istalgan foydalanuvchiga xizmat qiladi. Bu
  `docker-compose.replicas.yml` dagi «sticky shart emas» qarori bilan mos.
- **Sig'im:** bitta ulanish ≈ bitta asyncio task + kichik bufer ≈ o'nlab KB.
  1 000 ulanish ≈ 50–100 MB. Hozirgi o'lchov **0**, ya'ni bir worker bilan
  boshlash yetarli.
- **Gorizontal:** `docker compose ... up -d --scale realtime=N` (mavjud
  replicas overlay). Chegara Redis pub/sub ning o'zida emas, xotirada.
- **Amplifikatsiya yo'q:** kanal per-user, ya'ni bitta hodisa faqat o'sha
  foydalanuvchining ulanishlariga boradi (broadcast kanal bu yerda xato bo'lardi).
- ⚠️ **Redis pub/sub saqlanmaydi.** Obunachi uzilganda hodisa yo'qoladi —
  shu sababli replay buferi va `resync` qoidasi (§9) ixtiyoriy emas, **shart**.
- Redis'ni ajratish: ADR-0028 `judge-queue` ni allaqachon ajratgan. Pub/sub
  uchun alohida DB indeksi yetarli; yangi instans **hozircha kerak emas**
  (o'lchangan yuklama 0) — lekin bu qayta ko'riladigan nuqta.

## 11. Monitoring va loglash — talablar

⚠️ Hozirgi holat: `LOGGING` faqat konsol handler, **metrika umuman yo'q**.
Ya'ni bu bo'lim yangi ish, mavjudni sozlash emas.

**Metrikalar (majburiy):**

| Metrika | Tur | Nima uchun |
| --- | --- | --- |
| `realtime_connections_active` | gauge | sig'im; to'yinganlikni birinchi ko'rsatadi |
| `realtime_connections_total` | counter | oqim hajmi |
| `realtime_connection_seconds` | histogram | ulanish umri; qisqa ulanishlar = qayta ulanish bo'roni |
| `realtime_events_published_total` | counter | nashr tomoni ishlayaptimi |
| `realtime_events_delivered_total` | counter | yetkazish; nashr bilan farqi = yo'qotish |
| `realtime_connections_dropped_total` | counter | sekin iste'molchi / xato |
| `realtime_redis_errors_total` | counter | pub/sub sog'lig'i |
| `realtime_rejected_total` | counter | chegara; 503 lar soni |
| `realtime_client_reconnects_total` | counter | **mijoz** hisobot qiladi |

⚠️ **Mijoz metrikasi shart.** Server tomondan hamma ulanish sog'lom
ko'rinadi — foydalanuvchi sekin tarmoqda bo'lsa ham. Reconnect/drop
hisoboti (namunalangan) yagona haqiqiy signal.

**Loglar:** ulanish uchun **bitta** qator — `user_id`, davomiylik, yuborilgan
hodisa soni, yopilish sababi (`client_closed`, `heartbeat_failed`,
`slow_consumer`, `limit_exceeded`, `redis_error`).
⚠️ Cookie ham, hodisa yuki ham **yozilmaydi** (verdikt matni, bildirishnoma
mazmuni — shaxsiy ma'lumot).

**Health:** `/api/v1/realtime/health/` — Redis ulanishi + aktiv ulanishlar soni.
Deploy `--wait` shuni kutadi.

**Alertlar:** aktiv ulanishlar chegaraning 80% idan oshsa · Redis pub/sub
xatolari ketma-ket 3 marta · heartbeat nosozliklari ulushining o'sishi ·
`published − delivered` farqining o'sishi.

## 12. Rad etilgan variantlar

| Variant | Rad sababi |
| --- | --- |
| Ommaviy standings ni SSE ga o'tkazish | `docs/10` o'lchovi: 110k ulanish chekka kesh tekinga bergan narsani qimmat qiladi |
| Query-string token bilan auth | `Referer` va loglarga tushadi |
| `api` ni to'liq ASGI ga o'tkazish | butun API runtime'i almashadi; nosozlik izolyatsiyasi yo'qoladi |
| `gthread` + cheksiz SSE | thread baribir band; sig'im shifti qoladi |
| Mijoz tomonda `setInterval` bilan polling | mavjud usul; lekin kutish vaqti uzun bo'lsa yuklama doimiy |
| Cheksiz bufer per ulanish | OOM |
| Broadcast kanal (`rw:all`) | begona ma'lumot sizib chiqadi |

## 13. Qaytarilishi

**Qaytarilishi mumkin.** Oqim qo'shimcha yo'l: mijoz SSE ni sinab ko'radi,
ishlamasa **hozirgi polling'ga** qaytadi (feature flag + `resync` qoidasi).
`realtime` xizmatini to'xtatish saytni buzmaydi — faqat jonli yangilanish
yo'qoladi. Bu §5 dagi izolyatsiya qarorining bevosita natijasi.

## 14. Qabul qilingan qarorlar (2026-09-27)

| # | Savol | Qaror |
| --- | --- | --- |
| 1 | Chegara | **Ommaviy jadval ham real vaqtga o'tadi** — lekin oqim **versiya belgisini** tashiydi, hujjatni emas (§3) |
| 2 | Ish rejimi | **Alohida `realtime` xizmati** (tor ASGI ilova); `api` tegilmaydi (§5) |
| 3 | Transport tartibi | **SSE hozir, WebSocket Duel/Arena bilan** (§4) |
| 4 | Tunnel | **Path-based**, bir xil domen: `/api/v1/events/*` → `realtime` |

### ⚠️ 1-qaror shartli — quyidagilar bajarilishi SHART

1. Jadval oqimi **hech qachon** jadvalning o'zini tashimaydi — faqat versiya.
2. Ulanish chegarasi bo'ladi va chegaradan oshgan mijoz **polling'ga qaytadi**.
3. Keshli polling endpointi **saqlanadi va o'chirilmaydi** — u haqiqat manbasi.

Bu uchtasi buzilsa, qaror `docs/10` ning o'lchangan xulosasiga zid bo'lib
qoladi (110 000 ochiq ulanish chekka kesh tekinga bergan narsani qimmatlashtiradi)
va qayta ko'rilishi kerak.

