# Register tab yuklamasi — 2026-09-19

**Sana:** 2026-09-19 ~21:38–21:41 (Toshkent)  
**Savol:** login ochilgach odamlar [Ro‘yxatdan o‘tish](https://rankwant.uz/login?tab=register) tabiga o‘tadi. Shu HTML bir vaqtda bosilsa nima bo‘ladi?  
**Usul:** bitta jonli `GET` (CF); keyin k6 → `http://127.0.0.1:8300`. Login o‘lchovi bilan bir xil usul: [2026-09-19-login-load](../2026-09-19-login-load/REPORT.md).

> Tirik hujjat emas. Bu **tab HTML**, forma **POST** emas.  
> NFR: sahifa p95 **< 1000 ms**, xato **< 1%**.

Skrip: `C:\Users\nsn\project\cp\research\2026-09-19-register-load\rw-register-load.js`.

---

## 1. 30 soniyada

| Savol | Javob |
|---|---|
| 100 kishi **bir zumda** register tab ochadimi? | **Ha.** p95 **494 ms**, xato 0%. |
| 200 bir zumda? | **Chegara.** p95 **997 ms**, xato 0%. |
| 300 bir zumda? | Javob bor, xato 0%, p95 **1.43 s** — NFR yiqiladi. |
| Login tabdan farq bormi? | **Yo‘q, shovqin ichida.** Bir xil `page.tsx`, HTML +891 bayt. |
| 100 000 bir zumda? | **Yo‘q.** Shift ~**185–192 sahifa/s**; navbat ~**9 daqiqa**. Worker kvota tugaydi. |
| Forma yuborish (POST)? | **O‘lchanmadi.** Turnstile + `THROTTLE_REGISTER` — boshqa chegara. |

**Hukm:** register tab — login HTML ning ikkinchi zarbasi, arzonroq emas, qimmatroq ham emas. 100–200 bir zumda turadi; 100k bir zumda — yo‘q. Mehmon CDN kesh `/login` ga tegmaydi.

---

## 2. Nima o‘lchandi

- `GET https://rankwant.uz/login?tab=register` — CF, bitta so‘rov.
- `GET http://127.0.0.1:8300/login?tab=register` — jonli `rankwant-web-1`.
- HTML-only `sleep(1)`: 20 / 50 / 100 VU.
- Spike: 100 / 200 / 300.
- Visit: HTML + 5 RSC, 10 VU.

O‘lchanmadi: 1000+ VU, jonli k6, **register POST**, Turnstile/OAuth, `-p rankwant-load`.

**Tuzoq:** `:8300` — jonli `web`. `PAGE_PATH` — konteyner `PATH` emas.

---

## 3. Bitta so‘rov

| | Origin `:8300` register | Origin login | Jonli register |
|---|---|---|---|
| Status | 200 | 200 | 200 |
| Hajm | **40 384 B** | 39 493 B | — |
| Tinch TTFB | **13 ms** | 12 ms | Worker **203 ms** |
| `Cache-Control` | `private, no-store` | xuddi | xuddi |
| `CF-Cache-Status` | — | — | **DYNAMIC** |
| `server-timing` | — | — | `cfEdge 7`, `cfWorker 203` |
| `Set-Cookie` | `rw_exp` | `rw_exp` | `rw_exp` |

SSR: `apps/web/src/app/login/page.tsx` — `tab=register` → `AuthForm mode=register`. `fetchProviders()` + `AuthProof`/`stats`. Turnstile vidjeti **klientda** (`AuthForm.tsx`, 9-qaror); HTML-only k6 uni chaqirmaydi.

---

## 4. HTML-only, `sleep(1)`

| VU | Davomi | Sahifa | p95 | p90 | avg | med | max | Xato | `web` CPU | `api` CPU | `web` RAM |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 40 s | 610 | 24 ms | 19 ms | 15 ms | 13 ms | 37 ms | 0% | — | — | — |
| 50 | 40 s | 1483 | 51 ms | 47 ms | 32 ms | 31 ms | 82 ms | 0% | ~25% | ~9% | 248 MiB |
| 100 | 40 s | 2928 | **105 ms** | 93 ms | 44 ms | 29 ms | 185 ms | 0% | ~38% | ~24% | 257 MiB |

Login 100 VU p95 214 ms edi (issiqlik/shovqin). NFR: 20 ✅ · 50 ✅ · 100 ✅.

---

## 5. Spike — bir zumda N

| Bir zumda | p95 | avg | med | max | Xato | Devor | Shift |
|---|---|---|---|---|---|---|---|
| 100 | **494 ms** | 391 ms | 397 ms | 495 ms | 0% | 0.5 s | 192/s |
| 200 | **997 ms** | 590 ms | 542 ms | 1.01 s | 0% | 1.1 s | 186/s |
| 300 | **1.43 s** | 824 ms | 780 ms | 1.47 s | 0% | 1.6 s | 191/s |

Login spike: 527 ms / 1.00 s / 1.56 s. Register ~xuddi shu, shift ~190/s (login ~180/s).

NFR: 100 ✅ · 200 ⚠ · 300 ❌.

---

## 6. Prefetch (10 VU)

`/`, `/terms`, `/privacy`, `?tab=login`, `?tab=reset-password`.

| | Qiymat |
|---|---|
| Tashrif | 205 |
| So‘rov | 1230 (6×) |
| HTML p95 | 17 ms |
| Xato | 0% |

---

## 7. 100 000 va POST

Tab ochilishi login bilan bir xil qator: 100k / 190 s⁻¹ ≈ **8–9 daqiqa** navbat; CF Worker 100k/kun; HTML `DYNAMIC`.

Reklama oqimi endi **uch to‘lqin** origin’ga: `/` (mehmon kesh yordam beradi) → `/login?tab=login` (kesh yo‘q) → `/login?tab=register` (kesh yo‘q, **shu o‘lchov**). Ikkinchi va uchinchi to‘lqin — bir xil marshrut, ikki marta SSR.

**POST** (odam «Ro‘yxatdan o‘tish» bosadi): o‘lchanmadi. `THROTTLE_REGISTER` (40/soat) + Turnstile + yozuv — HTML shiftidan oldin shu tiqiladi. 100k tab ochish ≠ 100k hisob.

---

## 8. Qilinmasin

- Jonli `rankwant.uz` ga k6.
- 1000+ spike `:8300` ga.
- Register HTML kesh — alohida qaror.

```bash
docker run --rm --add-host=host.docker.internal:host-gateway \
  -v "<script>:/home.js:ro" \
  -e BASE=http://host.docker.internal:8300 \
  -e MODE=spike -e VUS=100 \
  grafana/k6:latest run /home.js
```
