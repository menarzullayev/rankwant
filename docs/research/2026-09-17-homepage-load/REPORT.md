# Bosh sahifa yuklamasi — 2026-09-17

**Sana:** 2026-09-17 ~23:30–23:45 (Toshkent)  
**Savol:** 1000 kishi Google qidiruviga `rankwant.uz` yozib Enter bosganda nima bo‘ladi? Localda, Worker kvotasini tugatmasdan o‘lchash mumkinmi? Natija qoniqarlimi?  
**Usul:** bitta haqiqiy brauzer tashrifi (Chrome DevTools); keyin k6 (`grafana/k6`) → `http://127.0.0.1:8300` (Cloudflare yo‘q). Taxmin yo‘q — jadvaldagi har raqam o‘sha kechki yugurishdan.

> Tirik hujjat emas. Sig‘im image, `web` soni va prefetch o‘zgarsa qayta o‘lchanadi.  
> Amaldagi NFR: [tests/load/README.md](../../../tests/load/README.md) — sahifa p95 **< 1000 ms**, xato **< 1%**.  
> Qisqa raqamlar ham o‘sha faylda, oxirida (§ «Sahifa ochilishi alohida chegara»).

Skrip: `C:\Users\nsn\project\cp\research\2026-09-17-homepage-load\rw-home-load.js` (repo tashqarida).
Xom material (Lighthouse `lighthouse-desktop.html` / `.json`, `rankwant-uz-viewport.png`) ham shu papkada —
`cp/README.md` qoidasi: hujjat repo’da, xom fayllar repo tashqarisida.

---

## 1. 30 soniyada — qoniqarlimi?

| Savol | Javob |
|---|---|
| 50 kishi bir vaqtda faqat bosh sahifani ochadimi? | **Ha.** p95 657 ms, xato 0%. NFR ichida. |
| 100 kishi bir vaqtda? | **Sayt turadi**, xato 0%, lekin p95 **1.65 s** — NFR yiqiladi. |
| 1000 kishi bir soniyada? | **Yo‘q.** 100 da allaqachon sekin; 1000 shu `web` da navbat. |
| Cloudflare orqali 1000 tashrif? | Yomonroq: HTML `DYNAMIC` + Worker har so‘rovda (100k/kun). Bu sinov CF’ga chiqmagan. |

**Hukm:** kechki ochilish / o‘nlab–ellikta odam uchun qoniqarli. «Dunyodan 1000 kishi bir vaqtda Enter» uchun **qoniqarsiz**. Chegara Workers kvotasi emas — bitta Next.js SSR (`force-dynamic`) va menyu prefetch.

---

## 2. Nima o‘lchandi, nima emas

O‘lchandi:

- `GET https://rankwant.uz/` — CF orqali bitta tashrif (TTFB, kesh, so‘rov soni).
- `GET http://127.0.0.1:8300/` — jonli `rankwant-web-1` (public overlay porti). Worker **0**.
- HTML-only: 20 / 50 / 100 VU.
- Brauzer shakli: `/` + 20 ta sidebar RSC prefetch, 5 va 10 VU.

O‘lchanmadi (qasddan):

- 1000 VU (jonli origin’ni yiqitish xavfi).
- 50–100 VU + prefetch.
- Haqiqiy 1000 mamlakat (bitta PC geo emas).
- Register / email / judge (bu ssenariyda yo‘q).
- `https://rankwant.uz` ga k6 (Worker kvotasi).

**Tuzoq:** `127.0.0.1:8300` — ikkinchi dev stack emas. Bu **jonli** `web`. Kvota saqlanadi, CPU saytniki.

k6 `http_reqs` HTML-only da iteration’dan ~2× katta (HTTP/2 yoki dual-stack). Sahifa soni — `html 200` check.

---

## 3. Bitta haqiqiy tashrif (CF orqali)

2026-09-17 23:30 atrofida, mehmon, Chrome:

| | Qiymat |
|---|---|
| HTML `/` | 200, TTFB **431 ms**, ~143 KB |
| `CF-Cache-Status` | **DYNAMIC** |
| `Cache-Control` | `private, no-cache, no-store` |
| `server-timing` | `cfEdge 11 ms`, `cfWorker 151 ms` |
| CSS `/_next/static` | **HIT**, `Age` ~6.4 soat, `immutable` |
| Brauzer jami | **~61 so‘rov** |
| Og‘iri | Sidebar `<Link>` prefetch: ~40 ta RSC, hammasi `DYNAMIC` |
| `robots` | `Disallow: /`, `noindex, nofollow` (`SITE_INDEXABLE = false`) |

Kod: `apps/web/src/app/page.tsx` — `export const dynamic = "force-dynamic"`. SSR: `stats`, `contests`, `leaderboard`, `articles`, `roadmaps`, `posts`, `updates` (+ mehmon uchun ham `getWithSession("/me/")`).

Local origin (CF’siz), tinch: TTFB **27–29 ms**. Sinovdan keyin **18 ms**; ommaviy `rankwant.uz` 200, TTFB **398 ms**.

---

## 4. HTML-only (`GET /`)

k6 `MODE=html`, `sleep(1)`, `discardResponseBodies`. Maqsad: `http://host.docker.internal:8300`.

| VU | Davomi | Sahifa (200) | HTML p95 | p90 | avg | med | max | Xato | `web` CPU | `web` RAM |
|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 40 s | 460 | 521 ms | 343 ms | 172 ms | 124 ms | 4.49 s | 0% | ~30% | 182 MiB |
| 50 | 40 s | 1098 | 657 ms | 491 ms | 197 ms | 139 ms | 1.95 s | 0% | ~66% | 339 MiB |
| 100 | 45 s | 1830 | **1.65 s** | 1.2 s | 406 ms | 243 ms | 4.36 s | 0% | yuqori* | 367 MiB |

\*100 VU paytida bir marta olingan namuna `web` 39% / `api` 4% — kesh issiq bo‘lgach API arzon; p95 baribir 1.65 s (navbat `web` da).

NFR (`p95 < 1000 ms`): 20 ✅ · 50 ✅ · 100 ❌. Xato NFR (`< 1%`): uchtasida ✅.

---

## 5. Prefetch vs prefetch’siz

Bir xil 10 VU, 25 s (5 s ramp + 15 s hold + 5 s down). Avval 50/100 VU isitgan kesh.

| | Faqat `/` | `/` + 20 menyu prefetch |
|---|---|---|
| Tugagan tashrif | 152 | 75 |
| HTML p95 | 575 ms | 331 ms |
| So‘rov/s | ~12 | **~175** |
| Iteration | 1.38 s | **2.88 s** |
| `web` / `api` CPU | past | ~28% / ~20% |
| Xato | 0% | 0% |

5 VU + prefetch (avvalgi yugurish): 38 tashrif, 2356 so‘rov, ~92 req/s, HTML p95 330 ms, xato 0%, `web` ~11%, `api` ~9%.

Prefetch HTML p95 ni yomonlashtirmadi (RSC arzonroq, kesh issiq). Narxi: so‘rov **~15×**, tashrif soni **~2× kam**, API seziladi. 50–100 VU + prefetch **o‘lchanmagan** — 100 ta HTML’ning o‘zi NFR ni yiqitgan.

---

## 6. 1000 kishiga ekstrapolatsiya

O‘lchanmagan. 100 VU HTML-only da p95 1.65 s, `web` bitta konteyner.

| Taxmin | Sabab |
|---|---|
| 1000 × faqat `/` | 100 ning ~10× navbati; p95 soniyalar; 500 bo‘lishi mumkin |
| 1000 × haqiqiy brauzer | 1000 × ~40 RSC + HTML ≈ o‘n minglab origin so‘rov; `anon_internal` 20 000/soat sovuq keshda urilishi mumkin |
| 1000 × CF | Yuqoridagiga qo‘shimcha ~60k Worker so‘rov (100k/kun ning ~60%) |

5–10 daqiqaga yoyilgan 1000 tashrif — boshqa ssenariy; bu hisobot **bir vaqtdagi** ochilish haqida.

---

## 7. Nima qilinmasin / keyin nima

- `https://rankwant.uz` ga 50+ VU k6 — Worker kvotasini yoqadi.
- 1000 VU ni `127.0.0.1:8300` ga otish — jonli `web`.
- Prefetch’ni o‘chirish yoki HTML’ni keshla**sh** — alohida qaror; bu yozuv o‘lchov.

Takrorlash:

```bash
docker run --rm --add-host=host.docker.internal:host-gateway \
  -v "<script>:/home.js:ro" \
  -e BASE=http://host.docker.internal:8300 \
  -e MODE=html -e VUS=50 -e RAMP=10s -e HOLD=20s -e DOWN=10s \
  grafana/k6:latest run /home.js
```

`MODE=visit` — prefetch. Ikkinchi toza stack (`-p rankwant-load`) — jonli saytga tegmaslik uchun; bu kecha qilinmagan.
