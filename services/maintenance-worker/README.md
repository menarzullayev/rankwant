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
Route'lar `wrangler.toml` da: `rankwant.uz/*` va `www.rankwant.uz/*`.

Dashboard orqali ham bo'ladi: Workers & Pages → Create → Worker →
`src/index.js` ni joylash → Settings → Domains & Routes → ikkala route.

**Majburiy sozlama:** route'da *Request limit failure mode* = **Fail open**.
Aks holda bepul limit tugaganda sayt Worker xatosi bilan yopiladi; fail open
bo'lsa so'rov to'g'ridan-to'g'ri origin'ga ketadi.

## Cheklov

Worker HAR so'rovda ishlaydi, sayt soz paytida ham. Bepul tarif kuniga
100 000 so'rov beradi. Standings keshi buzilmaydi — Worker ichidagi `fetch`
Cloudflare keshidan o'tadi — lekin chaqiruvlar soni baribir hisoblanadi.
10-operations dagi katta contest ssenariysi (7 300 so'rov/s) bunga sig'maydi:
undan oldin Workers Paid tarifiga o'tish yoki route'ni vaqtincha olib tashlash
kerak.

## Sinov

```bash
cd services/maintenance-worker && node --test
```

Tarmoq kerak emas: `fetch` soxtalashtiriladi va origin javoblari (200, 404,
500, 503, 502, 504, 520–526, 530, tarmoq xatosi) birma-bir tekshiriladi.
