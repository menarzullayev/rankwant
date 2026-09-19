# Texnik ishlar sahifasi (Cloudflare Worker)

`rankwant.uz` preview'i bitta mashinada ishlaydi va tashqariga faqat
Cloudflare Tunnel orqali chiqadi ([10-operations](../../docs/10-operations/README.md)).
Mashina o'chsa yoki boshqa tizimga o'tsa, tunnelda ulagich qolmaydi va
Cloudflare foydalanuvchiga xom `Error 1033` sahifasini ko'rsatadi.

Bu Worker sayt oldida turadi va so'rovni o'zgartirmasdan origin'ga uzatadi:

| Origin javobi | Worker nima qiladi |
| ------------- | ------------------ |
| 2xx, 3xx, 4xx, 500, 503 | o'zgarishsiz o'tkazadi — ilovaning o'z xatolari ham |
| 502, 504, 520–526, 530 yoki tarmoq xatosi | `503` va "texnik ishlar" sahifasi (o'zbek, rus, ingliz) |
| shu holatda `/api/*` | `503` va loyiha xato formati: `{"error": {"code": "maintenance", ...}}` |

Sahifa har 60 soniyada o'zi yangilanadi, ya'ni sayt qaytishi bilan
foydalanuvchi uni ko'radi. `503` va `Retry-After: 300` qidiruv tizimlariga
uzilish vaqtinchalik ekanini aytadi — indeks tushib ketmaydi.

## Deploy

```bash
cd services/maintenance-worker
npx wrangler login
npx wrangler deploy
```

`wrangler login` brauzerda Cloudflare hisobiga ruxsat so'raydi (bir marta).
Route'lar `wrangler.toml` da: harf prefikslari + aniq yo'llar
(`leaderboard*`, `problems*`, …). GET `/`, `/login`, `/register`,
`/terms`, `/privacy` ATAYLAB yo'q — mehmon CDN Worker kvotasini yemasin.

Dashboard orqali ham bo'ladi: Workers & Pages → Create → Worker →
`src/index.js` ni joylash → Settings → Domains & Routes → ikkala route.

**Majburiy sozlama:** har route'da *Request limit failure mode* = **Fail open**.
API'da bu `request_limit_fail_open: true` — ochiq hujjatda yozilmagan, lekin
`GET`/`PUT /zones/{zone_id}/workers/routes/{route_id}` uni qaytaradi va qabul
qiladi. Standart qiymat `false`: bepul limit tugaganda sayt Cloudflare'ning
1027 xatosi bilan yopiladi; fail open bo'lsa so'rov to'g'ridan-to'g'ri
origin'ga ketadi. 2026-09-12 da uchala route'da yoqilgan — route qayta
yaratilsa yoki yangisi qo'shilsa, qiymatni tekshiring.

Sozlama ko'rinmaydi (u route'da yashaydi, kodda emas), shuning uchun uni
`tools/check_workers.sh` o'qiydi va `ci-local.sh fast` ichida ishlaydi:

```bash
bash tools/check_workers.sh    # 0 — himoya bor; 1 — yo'q; 2 — o'qib bo'lmadi
```

⚠️ Chiqish kodi **2** — «o'qib bo'lmadi» (token yo'q yoki muddati o'tgan) va
u sayt holati haqida **hech narsa demaydi**. Uni `1` bilan qo'shib
yubormang: odam o'zgarmagan sozlamani tuzatishga ketadi.

⚠️ wrangler'ning OAuth refresh tokeni **rotatsiya** qilinadi — har
yangilashda Cloudflare yangisini beradi va eskisini o'chirib tashlaydi.
Skript yangi tokenni `~/.cloudflared/wrangler_refresh.json` ga saqlaydi.
Birinchi ishlatishdan oldin bir marta brauzerda kirish kerak:

```bash
cd services/maintenance-worker && npx wrangler login
```

## Cheklov

Worker GET `/` dan tashqari HAR so'rovda ishlaydi, sayt soz paytida ham.
Bepul tarif kuniga 100 000 so'rov beradi. Bosh sahifa ochilishi endi
kvotaga kirmaydi. Standings keshi buzilmaydi — Worker ichidagi `fetch`
Cloudflare keshidan o'tadi — lekin chaqiruvlar soni baribir hisoblanadi.
10-operations dagi katta contest ssenariysi (7 300 so'rov/s) bunga sig'maydi:
undan oldin Workers Paid tarifiga o'tish yoki route'ni vaqtincha olib tashlash
kerak.

**2026-09-13 da limit haqiqatan tugadi:** 18:31 da 76%, 20:56 da 94%,
22:35 da 100 000 so'rov tugadi va 00:15 da yana (limit 00:00 UTC da
yangilanadi). Sayt yiqilmadi — sabab faqat fail-open. Ya'ni bu cheklov
nazariy emas; katta contest oldidan tarifni ko'tarish SHART.

## Sinov

```bash
cd services/maintenance-worker && node --test
```

Tarmoq kerak emas: `fetch` soxtalashtiriladi va origin javoblari (200, 404,
500, 503, 502, 504, 520–526, 530, tarmoq xatosi) birma-bir tekshiriladi.
