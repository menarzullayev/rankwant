/goal — 2026-09-15 qarorlarini bajarish

> **Kim uchun:** yangi sessiya agenti. Bu prompt **o'zini-o'zi yetarli** —
> quyidagidan boshqa kontekst kerak emas.

---

## GOAL

Quyidagi 9 ta qarorni **ko'rsatilgan tartibda** bajar. Har bosqichdan keyin
**tekshirish mezoni** bajarilishi shart — bajarilmasa, **to'xta va hisobot ber**.
Hech narsani taxmin qilma: har da'voni o'lcha.

---

## 0. KONTEKST

| Narsa | Qiymat |
|---|---|
| Loyiha | `C:\Users\nsn\project\cp\rankwant` |
| Branch | `main` · remote `origin` |
| HEAD (qaror vaqtida) | `33ea38f` — **avval `git log -1` bilan tasdiqla** |
| Stack | Django/DRF (`api`/`worker`/`beat`) + Next.js (`web`) + Go (`judge`) + Postgres/Redis/MinIO |
| Live sayt | `https://rankwant.uz` — **ishlab turibdi, to'xtatish mumkin emas** |
| Muhit | Docker Compose, **har doim `-p rankwant --env-file .env.public`** (`build` va `up`) |
| Qarorlar manbasi | `rankwant-review/DECISIONS-2026-09-15.md` |
| Holat hisoboti | `rankwant-review/PLATFORM-STATUS-2026-09-15.md` |

**Birinchi buyruqlar:**
```bash
cd /c/Users/nsn/project/cp/rankwant
git log --oneline -1
git status --short
docker ps --format "{{.Names}}  {{.Status}}"
```
Agar HEAD `33ea38f` bo'lmasa yoki stack ishlamasa — **to'xta va hisobot ber**.

---

## 1. TAYYORGARLIK (5 daqiqa)

1. Ikkita hujjatni o'qi: `DECISIONS-2026-09-15.md` (qarorlar) va
   `PLATFORM-STATUS-2026-09-15.md` §4 (o'lchanmagan ma'lumotlar).
2. Zaxira katalogini yarat: `C:\Users\nsn\backups\rankwant-2026-09-15\`
3. `.env.public` dan Postgres foydalanuvchi/baza nomini o'qi
   (`POSTGRES_USER`, `POSTGRES_DB`).

---

## 2. BAJARISH — 8 BOSQICH

### BOSQICH 1 — T1: Zaxira + tiklanish sinovi 🔴 BLOKLOVCHI

**Nima.** `rankwant_pgdata` va `rankwant_miniodata` — Docker volume,
`docker_data.vhdx` **ichida**. Zaxira yo'q. Qaror: to'liq zaxira +
**tiklanish sinovi**.

**Qadamlar:**
```bash
# 1. Postgres dump (custom format)
docker compose -p rankwant --env-file .env.public exec -T postgres \
  pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc \
  > "C:/Users/nsn/backups/rankwant-2026-09-15/pg-$(date +%Y%m%d-%H%M).dump"

# 2. MinIO volume — alohida konteyner orqali arxivlash
docker run --rm -v rankwant_miniodata:/data \
  -v "C:/Users/nsn/backups/rankwant-2026-09-15:/backup" \
  alpine tar czf /backup/miniodata.tgz /data
```

**Tiklanish sinovi (majburiy):**
```bash
# Vaqtincha baza yarat va dump'ni tikla
docker compose -p rankwant --env-file .env.public exec -T postgres \
  createdb -U "$POSTGRES_USER" rankwant_restore_test
docker compose -p rankwant --env-file .env.public exec -T postgres \
  pg_restore -U "$POSTGRES_USER" -d rankwant_restore_test \
  < "C:/Users/nsn/backups/rankwant-2026-09-15/pg-<vaqt>.dump"
# Jadval sonini tekshir, keyin o'chir
```

**✅ Tekshirish mezoni:**
- dump fayli mavjud va **0 bayt emas**
- `rankwant_restore_test` da jadval soni asl baza bilan **bir xil**
- zaxira fayllari `docker_data.vhdx` dan **tashqarida**
- sinov bazasi o'chirilgan

**🛑 To'xtash sharti:** dump bo'sh, tiklanish xato bersa yoki jadval soni
farq qilsa — **to'xta**, keyingi bosqichga o'tma.

---

### BOSQICH 2 — T16: Disk (faqat build cache)

**Nima.** `C:` da 12.5 GB bo'sh. O'lchandi: Build Cache 23.72 GB,
**ACTIVE=0**, reclaimable **21.24 GB**.

```bash
docker builder prune -f        # ⛔ --volumes YO'Q
docker system df
```

**✅ Tekshirish mezoni:** `C:` kamida **30 GB** bo'sh; 15 ta konteyner
hali ham ishlayapti; `rankwant_pgdata` mavjud.

**⛔ TAQIQLANADI:** `docker system prune --volumes`, `docker volume prune`,
`docker image prune -a` (faqat 702 MB beradi, image'larni qayta qurish kerak).

---

### BOSQICH 3 — G1: `33ea38f` ni lokal tasdiqlash

**Nima.** Bu commit (`identifier` + `terms_accepted` + `check_smoke_payloads`)
CI'da **tasdiqlanmagan** — run `cancelled` (runner offline). CI/CD
to'xtatilgan, shuning uchun **lokal** tasdiqlanadi.

```bash
bash tools/ci-local.sh all      # yoki fast
```

**⚠️ Kutilayotgan xato:** WSL'da `docker compose build` **SIGBUS** berishi
mumkin. Bunda: `wsl.exe --shutdown` → qayta kirish → qayta urinish.
Ikki marta ham SIGBUS bo'lsa — **buni qayd et va keyingi bosqichga o't**,
vaqtni yo'qotma.

**✅ Tekshirish mezoni:** `ci-local.sh` yashil, yoki xato aniq qayd etilgan.

---

### BOSQICH 4 — Parallel: T3 · T5 · T11 · T12

#### T3 — 7 ta xom-`locale` formatlash ❌
Joylar (o'lchandi):
```
app/attempts/page.tsx:67          toLocaleTimeString(locale)
app/calendar/page.tsx:42,53,58    toLocaleDateString/TimeString/String(locale, …)
components/ArenaPlayer.tsx:165    toLocaleTimeString(locale)
components/auth/AuthProof.tsx:34  toLocaleString(locale)      ← SON
components/DuelDetail.tsx:60      toLocaleTimeString(locale)
```
**Yechim:** sana → `dateTime()` / `date()`; **son** → `intlLocale()`
(hammasi `@/i18n/messages`).

**✅ Tekshirish (3 ta naqsh — bittasi yetarli EMAS):**
```bash
grep -rn "toLocaleString(locale\|toLocaleTimeString(locale\|toLocaleDateString(locale" apps/web/src/
# → 0
```

#### T5 — `Event` + `LearningResource` JSON-LD
`contests/[slug]/page.tsx` va `problems/[slug]/page.tsx` — ikkalasida
`generateMetadata` bor. `Organization`/`WebSite` mavjud.

**✅ Tekshirish:** production build + jonli sahifada `"@type":"Event"` ko'rinadi.

#### T11 — `--rw-font-mono` o'lik o'zgaruvchi
Faqat `globals.css:144` da ta'riflangan, **havola 0**. `font-mono` (42 ta)
Tailwind'ning o'z to'plamidan keladi — bog'liq emas.

**Yechim:** ta'rifni **o'chir**.
**✅ Tekshirish:** `grep -rn -- "--rw-font-mono" apps/web/src/` → **0**; build yashil.

#### T12 — `browserslist`
`apps/web/package.json` ga qo'shish (legacy JS 24.9 kB).
**✅ Tekshirish:** build muvaffaqiyatli; FCP/LCP o'zgarmaydi (faqat hajm).

---

### BOSQICH 5 — T8: `Vary` ga qo'shish ⚠️ ENG NOZIQ

**Nima.** `Content-Language` yo'q; `Vary` ga `Accept-Language` qo'shish kerak.

**⚠️ HAL QILUVCHI:** Next.js **allaqachon** `Vary` yozadi:
```
Vary: rsc, next-router-state-tree, next-router-prefetch,
      next-router-segment-prefetch, Accept-Encoding
```
**Qayta yozish MUMKIN EMAS** — RSC/router kesh buziladi.
Faqat `Accept-Language` ni **qo'shish** kerak.

**✅ Tekshirish:** jonli sarlavhada **ham** `Accept-Language`, **ham** Next.js
qiymatlari turibdi; `Content-Language` qo'shilgan.

---

### BOSQICH 6 — T4: `check_contract.py` eski-manzil tekshiruvi

**Nima.** `TABS` "buziladigan havolalar" deb e'lon qilgan har manzil uchun
`page.tsx` mavjudligini tekshirish. M5 regressiyasi aynan shu tekshiruv
yo'qligidan yuz bergan.

**⚠️ Manzillar (hozirgi):** tekshiriladigan juftliklar **`register`** va
**`reset-password`**. `/login` — kanonik (fayl talab qilinmaydi).
`/kirish` va `/parolni-tiklash` **mavjud emas va kerak emas**.

**✅ Tekshirish — salbiy test MAJBURIY:** faylni ataylab o'chirib
`exit 1` ko'rinishi shart; qayta tiklab `exit 0`.

---

### BOSQICH 7 — T2: Anonimlashtirish ⚠️ MIGRATSIYA

**Qaror (sizniki — CTO tavsiyasidan farq):** `UsernameHistory` qatorlarini
o'chirmaslik, `user=None` qilib saqlash.

**Nima qilish:**
1. `apps/api/core/account.py:69` — `UsernameHistory.objects.filter(user=user).delete()`
   o'rniga qatorlarni saqlab, `user=None` qilish
2. `UsernameHistory.user` hozir `on_delete=CASCADE`, **nullable emas** →
   migratsiya (FK `null=True`)
3. `anonymize()` da `SocialAccount` o'chirilishi **qoladi** (Telegram UID bo'sh qolishi kerak)

**⚠️ Tekshirish kerak:** jadvalning **ikkinchi vazifasi** — eski havolani
yo'naltirish. `user=None` qatorlar u yerda **yetim** bo'ladi. `__str__`
va boshqa ishlatilishlarni (`account.py:270`) ko'rib chiq.

**✅ Tekshirish mezoni:**
```python
# anonimlashtirishdan keyin
usernames.reserved('<eski nom>')  # → True
```
**Salbiy test:** yozuv bo'lmaganda `reserved()` → **False**.

**⚠️ Faqat kelajak uchun** — allaqachon anonimlashtirilgan 4 ta hisob
qamrab olinmaydi (`UsernameHistory` hozir jami **0**).

---

### BOSQICH 8 — T7 va T13 (kichik, parallel)

#### T7 — `Dockerfile:19` majburiy default
`ARG NEXT_PUBLIC_API_BASE=http://localhost:8000/api/v1` → bo'sh default +
majburiy tekshiruv (fail-fast).
**Eslatma:** compose har doim build-arg beradi (`docker-compose.yml:119`,
`docker-compose.public.yml:100`) → hech bir workflow buzilmaydi.
**✅ Tekshirish:** argsiz `docker build` → yiqiladi; compose orqali → o'zgarish yo'q.

#### T13 — ildiz `README.md` inglizchaga
Hozir **o'zbekcha**. Faqat shu bitta fayl — `docs/` ga **tegilmaydi**.
**✅ Tekshirish:** fayl inglizcha; texnik atamalar (`slug`, `hreflang`,
`bundle`, `Docker`) asl holida.

---

## 3. TAQIQLAR (hech qachon)

| ⛔ | Nima | Nega |
|---|---|---|
| 1 | `prune --volumes` / `volume prune` | `rankwant_pgdata` o'chadi |
| 2 | `Vary` sarlavhasini **qayta yozish** | Next.js RSC kesh buziladi |
| 3 | Live stack'ni to'xtatish (web/api/postgres) | sayt ishlamay qoladi |
| 4 | CI/CD ishini boshlash, runner'ni onlayn qilish | foydalanuvchi to'xtatgan |
| 5 | `docs/` ga tegish | qaror faqat ildiz `README.md` |
| 6 | `hreflang` qo'shish | qaror: hozircha yo'q |
| 7 | Bitta naqsh bilan tekshirish (`toLocaleString(locale)`) | 6 joy o'tkazib yuboriladi |
| 8 | `MEMORY.md` ni **kontekstdagi nusxadan** qayta yozish | qisqartirilib yuklanadi → ma'lumot o'chadi. Avval to'liq `Read` qil |

---

## 4. COMMIT QOIDALARI

- **Commit-by-concern** — har bosqich alohida commit
- Conventional Commits, **inglizcha**: `fix(api): …`, `feat(seo): …`
- Har commitdan oldin: `bash tools/ci-local.sh fast`
- Har commitdan keyin: `git push origin main`
- `.githooks/pre-push` ishlaydi (`core.hooksPath = .githooks`)

---

## 5. TO'XTASH SHARTLARI

Quyidagilarda **to'xta va hisobot ber** (davom etma):

1. HEAD `33ea38f` emas
2. Live stack ishlamayapti
3. Zaxira bo'sh yoki tiklanish xato berdi
4. `C:` 30 GB dan kam bo'sh qoldi
5. Migratsiya (T2) kutilmagan xato berdi
6. Biror tekshirish mezoni bajarilmadi

---

## 6. YAKUNIY HISOBOT SHAKLI

```
Bajarildi:
  B1 T1  — zaxira + tiklanish sinovi  [dump hajmi, jadval soni]
  B2 T16 — build cache                [oldingi/keyingi bo'sh joy]
  B3 G1  — ci-local.sh                [yashil / xato qayd etildi]
  B4 T3  — 7 ta locale                [grep → 0]
  B4 T5  — Event + LearningResource   [jonli tekshirildi]
  B4 T11 — --rw-font-mono o'chirildi  [grep → 0]
  B4 T12 — browserslist               [build yashil]
  B5 T8  — Vary + Content-Language    [sarlavha ko'rsatilsin]
  B6 T4  — check_contract             [salbiy test exit 1]
  B7 T2  — anonimlashtirish           [reserved() → True]
  B8 T7  — Dockerfile fail-fast       [argsiz build yiqildi]
  B8 T13 — README.md inglizcha

Commitlar: <sha ro'yxati>
Tekshirilmagan / ochiq qolgan: <nima va nega>
Keyingi qadam: <tavsiya>
```

---

**Eslatma:** bu vazifa 8 bosqich va bir necha commit. Har bosqichdan keyin
tekshirish mezonini bajar — yashil natija "tekshirildi" bilan
"chaqirilmadi" ni ajratmaydi.
