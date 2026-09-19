# Login yuklamasi — 2026-09-19

**Sana:** 2026-09-19 ~21:20–21:25 (Toshkent)  
**Savol:** kuchli reklamadan so‘ng 100 000 kishi saytga kirib, keyin `https://rankwant.uz/login?tab=login` ni **bir vaqtda** bossalar nima bo‘ladi?  
**Usul:** bitta jonli `HEAD`/`GET` (CF orqali); keyin k6 (`grafana/k6`) → `http://127.0.0.1:8300` (Cloudflare yo‘q). Taxmin yo‘q — jadvaldagi har raqam o‘sha kechki yugurishdan.

> Tirik hujjat emas. `web` soni, login SSR yoki Worker qamrovi o‘zgarsa qayta o‘lchanadi.  
> Amaldagi NFR: [tests/load/README.md](../../../tests/load/README.md) — sahifa p95 **< 1000 ms**, xato **< 1%**.  
> Bosh sahifa o‘lchovi: [2026-09-17-homepage-load](../2026-09-17-homepage-load/REPORT.md).

Skrip: `C:\Users\nsn\project\cp\research\2026-09-19-login-load\rw-login-load.js` (repo tashqarida).

---

## 1. 30 soniyada — 100K bir vaqtda?

| Savol | Javob |
|---|---|
| 100 kishi **bir zumda** login HTML ochadimi? | **Ha.** p95 **527 ms**, xato 0%. NFR ichida. |
| 200 kishi bir zumda? | **Chegara.** p95 **1.00 s**, xato 0%. NFR p95 chizig‘ida. |
| 300 kishi bir zumda? | **Sayt javob beradi**, xato 0%, p95 **1.56 s** — NFR yiqiladi. |
| 100 000 kishi bir zumda? | **Yo‘q.** O‘lchanmadi. Shift ~**180 sahifa/s**; 100k navbat ~**9 daqiqa**. Brauzer/CF timeout. |
| 100 000 tashrif 10 daqiqaga yoyilsa? | Origin login HTML uchun **ehtimol turadi** (~167/s < 180). CF Worker **kunlik 100k kvota shu to dda tugaydi**. |
| `https://rankwant.uz/login` keshdami? | **Yo‘q.** `CF-Cache-Status: DYNAMIC`, `Cache-Control: private, no-store`, har so‘rovda Worker **194 ms**. |

**Hukm:** o‘nlab–ikki yuzta odam bir vaqtda login ochishi — origin **qoniqarli**. «Reklamadan keyin 100 ming kishi bir sekundda Kirish» — **qoniqarsiz**. Chegara Workers kvotasi **va** bitta Next.js SSR (`private no-store`). Bosh sahifadagi mehmon CDN kesh `/login` ga tegmaydi.

---

## 2. Nima o‘lchandi, nima emas

O‘lchandi:

- `GET https://rankwant.uz/login?tab=login` — CF orqali bitta so‘rov (kesh, Worker).
- `GET http://127.0.0.1:8300/login?tab=login` — jonli `rankwant-web-1`. Worker **0**.
- HTML-only, `sleep(1)`: 20 / 50 / 100 VU (bosh sahifa usuli bilan solishtirish).
- **Spike** (bir zumda, `sleep` yo‘q): 100 / 200 / 300 parallel `GET`.
- Brauzer shakli: HTML + 5 ta RSC prefetch, 10 VU.

O‘lchanmadi (qasddan):

- 1000 yoki 100 000 VU / spike (jonli origin).
- `https://rankwant.uz` ga k6 (Worker kvotasi).
- Login **POST** (parol), register, OAuth start, Turnstile.
- Ikkinchi toza stack (`-p rankwant-load`).

**Tuzoq:** `127.0.0.1:8300` — ikkinchi dev stack emas. Bu **jonli** `web`. Kvota saqlanadi, CPU saytniki.

k6 `PATH` muhitini o‘qimasin: konteyner `PATH` `/usr/local/sbin:…` — skriptda `LOGIN_PATH`.

---

## 3. Bitta so‘rov (origin va CF)

2026-09-19 21:23, mehmon, `curl`:

| | Origin `:8300` | Jonli `rankwant.uz` |
|---|---|---|
| Status | 200 | 200 |
| `Cache-Control` | `private, no-cache, no-store, max-age=0, must-revalidate` | xuddi shu |
| `CF-Cache-Status` | — | **DYNAMIC** |
| `server-timing` | — | `cfEdge 6 ms`, `cfOrigin 0`, **`cfWorker 194 ms`** |
| `Set-Cookie` | `rw_exp=…` | `rw_exp=…` |
| Tinch TTFB | **12–13 ms** | DevTools (shu kun): HTML TTFB **351 ms** |

Kod: `apps/web/src/app/login/page.tsx`. Mehmon: `isSignedIn()` cookie yo‘q → `/me/` yo‘q. Har HTML: `fetchProviders()` → `/auth/providers/`, `AuthProof` → `api.stats()`. Static chunk’lar CF da **HIT** bo‘lishi mumkin; HTML yo‘q.

---

## 4. HTML-only, `sleep(1)` — «soniyada N ochish»

k6 `MODE=html`, `Host: rankwant.uz`, `redirects: 0`. Maqsad: `http://host.docker.internal:8300`.

Bu **bir zumda N so‘rov emas**: har VU 1 sahifa + 1 s kutadi. 100 VU ≈ soniyada ~100 ochilish, bir vaqtda ~7 SSR (avg 72 ms).

| VU | Davomi | Sahifa (200) | HTML p95 | p90 | avg | med | max | Xato | `web` CPU | `web` RAM |
|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 40 s | 605 | 42 ms | 39 ms | 20 ms | 15 ms | 62 ms | 0% | ~13% | 190 MiB |
| 50 | 40 s | 1479 | 46 ms | 43 ms | 32 ms | 30 ms | 204 ms | 0% | ~23% | 214 MiB |
| 100 | 40 s | 2850 | **214 ms** | 184 ms | 72 ms | 26 ms | 316 ms | 0% | (namuna o‘tmadi) | 395 MiB |

50 VU da `api` ~8%. NFR: 20 ✅ · 50 ✅ · 100 ✅ (bosh sahifa 100 VU da p95 **1.65 s** edi).

Login bosh sahifadan arzon: kamroq API, ~40 KB HTML (bosh ~143 KB).

---

## 5. Spike — «bir zumda N kishi»

`MODE=spike`: `shared-iterations`, N VU = N so‘rov, `sleep` yo‘q. 100 000 ning kichik modeli.

| Bir zumda | Sahifa | HTML p95 | avg | med | max | Xato | Devor |
|---|---|---|---|---|---|---|---|
| 100 | 100 | **527 ms** | 417 ms | 422 ms | 529 ms | 0% | 0.6 s |
| 200 | 200 | **1.00 s** | 569 ms | 514 ms | 1.02 s | 0% | 1.1 s |
| 300 | 300 | **1.56 s** | 861 ms | 791 ms | 1.61 s | 0% | 1.7 s |

Uchala spike da o‘tkazish **~176–184 sahifa/s**. Bu shu `web` konteynerning login HTML shiftiga yaqin.

NFR (`p95 < 1000 ms`): 100 ✅ · 200 ⚠ · 300 ❌. Xato: uchtasida ✅.

---

## 6. Prefetch (`MODE=visit`)

10 VU, 25 s, issiq kesh. DevTools (shu kun): login hujjat + `/`, `/terms`, `/privacy`, `?tab=register`, `?tab=reset-password`.

| | Qiymat |
|---|---|
| Tashrif (HTML 200) | 205 |
| Jami so‘rov | 1230 (6× — HTML + 5 RSC) |
| HTML p95 | 17.5 ms |
| RSC arzon | umumiy avg 5.6 ms |
| Xato | 0% |

10 VU + prefetch origin’ni siqmaydi. 100+ spike + prefetch **o‘lchanmagan**.

---

## 7. 100 000 ga ekstrapolatsiya

100 000 spike o‘lchanmagan. 300 da xato yo‘q, lekin p95 allaqachon 1.56 s; shift 180/s atrofida qotib qolgan.

| Taxmin | Sabab |
|---|---|
| 100k **bir zumda** origin | 100 000 / 180 s⁻¹ ≈ **556 s (~9 daqiqa)** navbat. Birinchi ~180 kishi <1 s; keyingilar o‘sadi. 30–100 s dan keyin brauzer/CF (odatda 100 s, 524) uziladi. |
| 100k **bir zumda** CF | Yuqoridagiga qo‘shimcha: har HTML Worker (~194 ms) + **100k/kun kvota bir pulsda**. Static HIT; HTML `DYNAMIC`. |
| 100k tashrif **10 daqiqa** | ~167 HTML/s — shiftga yaqin, origin **ehtimol** turadi. Worker baribir 100k — kun tugadi. |
| 100k tashrif **1 soat** | ~28 HTML/s — origin bo‘sh. Worker kvota baribir 100k. |
| 100k × haqiqiy brauzer | HTML + 5 RSC + static. Static CF HIT. RSC (`/`, terms, boshqa tab) ham `private`/`DYNAMIC` bo‘lsa origin’ga qo‘shiladi. |
| API | Har login HTML: `providers` + `stats` (mehmonda `/me/` yo‘q). 100k HTML ≈ 200k API. gunicorn 4 sync — HTML shiftidan oldin shu tiqilishi mumkin. |

Reklama oqimi odatda **ikki to‘lqin**: avval `/` (mehmon CDN kesh endi yordam beradi), keyin `/login` (kesh yo‘q — mana shu o‘lchov).

5–10 daqiqaga yoyilgan 100k tashrif — boshqa ssenariy; §1 dagi «yo‘q» **bir vaqtdagi** bosish haqida.

---

## 8. Nima qilinmasin / keyin nima

- `https://rankwant.uz` ga 50+ VU k6 — Worker kvotasini yoqadi.
- 1000+ spike ni `127.0.0.1:8300` ga otish — jonli `web`.
- Login HTML ni keshla**sh** — alohida qaror (`rw_exp` Set-Cookie + `private no-store`; bosh sahifa kesh `/` only). Bu yozuv o‘lchov.

Takrorlash:

```bash
docker run --rm --add-host=host.docker.internal:host-gateway \
  -v "<script>:/home.js:ro" \
  -e BASE=http://host.docker.internal:8300 \
  -e MODE=html -e VUS=50 -e RAMP=10s -e HOLD=20s -e DOWN=10s \
  grafana/k6:latest run /home.js
```

`MODE=spike` `VUS=100` — bir zumda 100. `MODE=visit` — prefetch. `LOGIN_PATH` — yo‘l (`PATH` emas).
