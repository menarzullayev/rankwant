# Bitta Engine — ijro rejasi

> **Arxiv yozuvi.** Repoga 2026-10-04 da ko'chirildi; matn yozilgan kunidagi holatni aks ettiradi. Tarixiy reja: WSL runner 2026-09-17 da olib tashlangan, hozirgi holat `CLAUDE.md` va [tools/runner/README.md](../../../tools/runner/README.md) da.

**Sana:** 2026-09-17 · **Holat:** ⚠️ **TO'XTATILDI — Faza 2 da nuqson topildi**
**Manba qarorlar:** AskUserQuestion sessiyasi, 2026-09-17

---

## ⚠️ IJRO HOLATI (2026-09-17, yangilangan)

| Faza | Holat |
|---|---|
| **0 — Tayyorgarlik** | ✅ **Bajarildi.** `wsl-keepalive.service` o'chirildi; zaxira tasdiqlandi |
| **1 — CI moslashtirish** | ✅ **Bajarildi va tekshirildi.** Eski runner'da to'liq CI yashil (`changes` ✅ `smoke` ✅ `web` ✅). PR **#42** |
| **2 — Sinov runner** | ✅ **Barqaror.** 14/14 self-test job yashil; WSL runner tegilmagan |
| **3 — Almashtirish** | ❌ Bajarilmadi — **qaror kutilmoqda** |
| **4 — V7 autostart/handoff** | ❌ Bajarilmadi |
| **5 — V8/V9 olib tashlash** | ❌ Bajarilmadi. **Hech narsa o'chirilmadi** |

### 🔄 TUZATISH: avvalgi «broker nuqsoni» xulosasi NOTO'G'RI edi

Avvalgi hisobotda `SocketException (125)` ni nosozlik deb o'qib, brokerni aybladim.
**O'lchov buni rad etdi:**

- Xato **har bir job tugagan lahzada** bir marta chiqadi — va o'sha job **Succeeded**
  bo'ladi. Bu runner'ning uzoq so'rovni bekor qilishi, nosozlik emas.
- `host` va `bridge` tarmoq rejimlari **bir xil** ishlaydi: 9/9 va 5/5 yashil.
  Ya'ni tarmoq rejimi umuman ahamiyatsiz.

**Haqiqiy sabab — ro'yxatdan o'tkazish churn'i:** konteynerni qayta-qayta yaratish
osilgan sessiya (`A session for this runner already exists`) va eski label
(`rankwant-container` vs `rankwant`) qoldirdi — mos kelmagan job'lar **abadiy
`queued`** bo'lib qoldi. Bir marta toza ro'yxatdan o'tkazib, tegilmasa — barqaror.

**Saboq:** alomatning **vaqtini** gumon qilingan sabab bilan solishtiring. Har
tugagan job uchun bitta xato — bu tarmoqni emas, job hayot tsiklini ko'rsatadi.

### Keyingi qadam (Saidakbar aka qarori)

Sinov runner barqaror, lekin u **faqat yengil job** (`runner-selftest.yml`) bajardi —
to'liq CI (stack qurish, smoke, bake-off, E2E) sinov label'ida ishlamaydi, chunki
`check_decisions.py` faqat self-test'ga ruxsat beradi.

1. **Nazorat ostida almashtirish** — WSL runner to'xtatiladi, sinov runner production
   label'ini oladi, to'liq CI o'tkaziladi; yiqilsa darhol qaytariladi. *(tavsiya)*
2. **Self-test'ni og'irlashtirish** — sinov label'ida compose stack'ni qurib sinash
   (ruxsat etilgan, lekin ~20 daqiqa/har yurish).
3. **Ko'chirishdan voz kechish** — CI o'zgarishlarini merge qilib, ikkinchi engine qoladi.

---

## 1. Qabul qilingan qarorlar

| # | Qaror | Tafsilot |
|---|---|---|
| D1 | **Bitta Engine** | WSL2 qoladi; `Ubuntu-24.04` + Engine B olib tashlanadi; runner Docker Desktop ichiga ko'chadi |
| D2 | **Runner modeli: konteyner + socket** | Runner Linux konteynerda; Desktop socket'i ulanadi; keepalive zanjiri yo'qoladi |
| D3 | **Zaxira — yopildi** | Zaxira + avtomatik tiklash sinovi bor; offsite ataylab o'chirilgan (qaror) |
| D4 | **Birinchi qadam: parallel runner** | Hozirgi runner ishlashda qoladi; yangi runner alohida label bilan sinaladi |
| D5 | **Qamrov: hammasi** | V4 · V5 · V6 · V7 · V8 · V9 · V3 |
| D6 | **HITL — rasmiy qoida** | ish qaydlari (repodan tashqarida) majburiy |
| D7 | **Uzilish siyosati** | 🔑 Development bosqichi, real foydalanuvchi yo'q — **uzilish qabul qilinadi** |

### D7 ning amaliy natijasi

- Uptime endi cheklov emas: `wsl --shutdown`, `down`, restart, migrate — oyna shart emas.
- V9 uchun maxsus tungi oyna **kerak emas**.
- ⚠️ **Ma'lumot yo'qolishi hanuz qabul qilinmaydi.** Uzilish qaytariladi, o'chirilgan baza
  qaytmaydi. Zaxira + tiklash sinovi talabi **kuchida qoladi**.
- SEO himoyasi baribir ishlaydi: Cloudflare Worker `503 + Retry-After` qaytaradi, ya'ni
  qisqa uzilish tashqi iz qoldirmaydi.

---

## 2. O'lchangan asos (qarorlar shunga tayanadi)

**Jonli ma'lumot Engine A da** — `docker --context desktop-linux volume ls`:
`rankwant_pgdata`, `rankwant_miniodata`, `rankwant-ci-cache`.
Engine B (Ubuntu) da faqat anonim CI qoldiqlari.
→ **`wsl --unregister Ubuntu-24.04` jonli bazaga tegmaydi.**

**Service container tarmog'i** (bir martalik sinov, port `59068`):

| Yo'l | Natija |
|---|---|
| `localhost:<port>` qardosh konteynerdan | ❌ FAIL |
| `host.docker.internal:<port>` | ✅ OK |
| default gateway `172.17.0.1` | ❌ FAIL |

**Bind mount yo'l yechilishi:**

| Yo'l turi | Natija |
|---|---|
| Windows (`C:/Users/...`) | ✅ OK |
| Linux (`/home/runner/_work/...`) | ❌ VM ichida bo'sh katalog |

**Zaxira holati:** `<backup-dir>` — 492 MB, eng yangisi 2026-09-17 03:45;
tiklash sinovi har yurishda avtomatik; 17 MB dump 9 soniyada tiklanadi.

---

## 3. Ijro rejasi — 6 faza

### Faza 0 — Tayyorgarlik (uzilish yo'q, qaytariladi)

| Qadam | Amal | Tasdiq |
|---|---|---|
| 0.1 | `wsl-keepalive.service` o'chirish (14-sentabr dublikati; `rankwant-holder` va Windows holder qoladi) | og'zaki |
| 0.2 | Oxirgi zaxira + `restore=ok` natijasini yozib qo'yish | — |
| 0.3 | Yangi runner uchun registration token olish; **alohida label** (`rankwant-test`) rejalashtirish | — |
| 0.4 | Sinov branch'i ochish | — |

**Tekshiruv:** `gh api .../actions/runners` → eski runner `online`; `wsl-keepalive` yo'q.
**To'xtash sharti:** runner `offline` bo'lsa — darhol qaytarish, sababni tekshirish.

### Faza 1 — CI moslashtirish (V5, sinov branch'ida)

| Qadam | Fayl | Amal |
|---|---|---|
| 1.1 | `ci.yml:154,160,161` | `localhost:${job.services...ports[...]}` → `host.docker.internal:${...}` |
| 1.2 | `ci.yml:417-421`, `security.yml:50`, `nightly.yml:46-48,85-91` | Mount yo'llarini Windows uslubiga o'tkazish |
| 1.3 | `ci.yml:454`, `deploy.yml:330` | `builder prune` ni loyiha doirasi bilan cheklash |
| 1.4 | `deploy.yml:244,270,280,306` | `-p rankwant` himoyasi (qo'lda tasdiq talab qilinsin) |
| 1.5 | `deploy.yml:288-294` | Konteynerda systemd/sudo yo'q — tunnel qadami qayta ishlanadi |

**Tekshiruv:** har o'zgarishga **salbiy test** (buzib ko'rish, `exit 1` kutiladi).
**To'xtash sharti:** salbiy test o'tmasa — o'zgarish qabul qilinmaydi.

### Faza 2 — Parallel runner (V6)

| Qadam | Amal |
|---|---|
| 2.1 | Konteyner runner ko'tariladi, `rankwant-test` label bilan |
| 2.2 | Sinov branch'ida to'liq CI: `api`, smoke, bake-off, E2E |
| 2.3 | **Reboot sinovi** — qayta ishga tushib runner o'zi tiklanadimi |

**Tekshiruv:** sinov branch'ida barcha job yashil + reboot'dan keyin `online`.
**To'xtash sharti:** biror job yiqilsa — sabab topilmaguncha asosiy runner'ga tegilmaydi.

### Faza 3 — Almashtirish

| Qadam | Amal |
|---|---|
| 3.1 | Eski runner (`<old-runner>`) to'xtatiladi |
| 3.2 | Yangi runner asosiy `rankwant` label'ini oladi |
| 3.3 | `main` da to'liq CI yashil bo'lishini tasdiqlash |

**To'xtash sharti:** `main` da CI yiqilsa — eski runner qaytariladi.

### Faza 4 — V7 (avtostart + handoff)

| Qadam | Amal |
|---|---|
| 4.1 | Docker Desktop `AutoStart` yoqish (`settings-store.json` → `true`; StartupApproved baytini tiklash) |
| 4.2 | `rankwant-handoff-in` task yaratish (logon + 2 daqiqa kechikish) |

**Tekshiruv:** reboot → sayt o'zi ko'tariladi; monitor `503` yozmaydi.

### Faza 5 — V8/V9 (olib tashlash)

| Qadam | Amal |
|---|---|
| 5.1 | ⚠️ Ubuntu'ni `wsl --export` bilan arxivlash (ehtiyot nusxa) |
| 5.2 | Eski runner'ni ro'yxatdan chiqarish (deregister) |
| 5.3 | `wsl --unregister Ubuntu-24.04` |
| 5.4 | `wsl -l -v` → faqat `docker-desktop` qolganini tasdiqlash |
| 5.5 | C: bo'sh joyni o'lchash (62 GB qaytishi kutiladi) |
| 5.6 | Keepalive zanjiri qoldiqlarini olib tashlash: `RankWant-WSL-Holder`, `rankwant-wsl-holder.bat`, `rankwant-holder.service`, ikkinchi `sleep 2147483647` |

**Tekshiruv:** `wsl -l -v`; `du`/disk o'lchovi; sayt `200`; CI yashil.
**To'xtash sharti:** sayt yoki CI buzilsa — arxivdan tiklash.

**Eslatma:** V9 ning "compact" qismi **kerak bo'lmasligi mumkin** — agar `wsl --unregister`
VHDX'ni o'chirsa, 62 GB o'zi qaytadi. Buni 5.5 da o'lchab, kerak bo'lsagina compact qilinadi.
`docker_data.vhdx` (Engine A) o'sadi va kichraymaydi — uni compact qilish `wsl --shutdown`
talab qiladi, lekin D7 tufayli oyna muammo emas.

---

## 4. Umumiy to'xtash shartlari

- Yangi dalil qarorga zid chiqsa — to'xta, qayta taqdim et.
- Reja doirasidan chiqilsa — to'xta.
- Tekshiruv yiqilsa — ko'r-ko'rona qayta urinma, sababni top.
- Zaxira tasdiqlanmagan bo'lsa — qaytarilmas qadam bajarilmaydi.

## 5. Qaytarish yo'llari

| Faza | Qaytarish |
|---|---|
| 0–2 | Hech narsa o'zgarmagan — eski runner ishlashda |
| 3 | Eski runner qayta yoqiladi |
| 4 | `AutoStart` o'chiriladi; task o'chiriladi |
| 5 | `wsl --import` bilan arxivdan tiklash (5.1 nusxasi) |

---

## 6. Ochiq bandlar

- **V9 ning compact qismi** — 5.5 o'lchovidan keyin aniqlanadi.
- **Yangi runner uchun resurs limitlari** — runner konteyneriga qo'yilgan limit uning
  yaratgan test konteynerlari va build'larini cheklamaydi; alohida chegara kerak.
- **`wsl --unregister` VHDX'ni o'chiradimi** — 5.5 da o'lchanadi (hozir tasdiqlanmagan).
