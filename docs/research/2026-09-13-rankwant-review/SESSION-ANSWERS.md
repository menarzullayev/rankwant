# Savol-javob sessiyasi — javoblar

Boshlangan: 2026-09-13 · Reja: [SESSION-PLAN.md](SESSION-PLAN.md)

---

## Raund 1 — Faktik savollar ✅

### A1 — Yo'qolgan tahlil fayllari

**Javob (Saidakbar aka):** *"Belgilansin · Yangi audit ko'chirilsin · Qayta
tadqiqot · **Ikki tahlil Linux dagi sessiyada qolib ketgan!**"*

**Qidiruv natijasi (javobdan oldin):**

| Tekshirilgan joy | Natija |
|---|---|
| Workspace (chuqurlik cheklovisiz) | yo'q |
| `C:\Users\nsn` (depth 7) | yo'q |
| `C:\` (depth 5) | yo'q |
| Desktop · Downloads · Documents · OneDrive | yo'q |
| `project.zip` | yo'q |
| Handoff eksporti (`.handoff/in/`) | faqat `pg.sql.gz` + `minio.tar.gz` |
| WSL | faqat `docker-desktop` — Linux tomoni WSL emas |

**Linux bo'limlari topildi** (Disk 0): uchta `0fc63daf-8483-4772-8e79-3d69d8477de4`
= **Linux filesystem** — 100 GB, 372.53 GB, 181.01 GB.

**Iz:** `INDEX.md` da `/home/nsn/Telegram/handlechecker/...` yo'li bor — ya'ni
workspace Linux'da `/home/nsn/project/cp`. Fayllar o'sha tomonda.

**Bajarildi:**

| Ish | Holat |
|---|---|
| Beshta havola joyi yangilandi (`03/README`, `03/competitor-summary`, `08/README`, `docs/README`, `INDEX.md`) | ✅ |
| Raqamlar "TEKSHIRIB BO'LMAYDI" deb belgilandi | ✅ |
| `rankwant-audit/` repo'ga ko'chirildi → `docs/03-market-research/audit/` (19 fayl, 1.1 MB) | ✅ commit `b680fbb` |
| Audit uchun `README.md` yozildi (nima bor / nima yo'q) | ✅ |
| Qayta tadqiqot | ⏳ **alohida sessiya** — fayllar Linux'dan kelgach mazmunliroq |

⚠️ **Muhim:** yangi audit **foydalanuvchi sonlarini o'z ichiga olmaydi** —
u UI tuzilmasini o'lchaydi. Ya'ni bozor hajmi raqamlari tiklanmadi.

### A2 — Approver yozuvi

**Javob:** *"To'g'ri — shunday qolsin"*

**Qaror:** `Saidakbar Narzullayev — Repo owner / maintainer` (01–09 `Qulflash`
yozuvlarida) tasdiqlandi. O'zgartirish kerak emas.

### A3 — `rankwant-handoff/` taqdiri

**Javob:** *"Arxivlansin"*

**Bajarildi:** `rankwant-handoff/` (26 MB, 807 fayl) →
`.archive/rankwant-handoff-2026-09-13/`. O'chirilmadi — qaytarish mumkin.

`cp` ildizi endi: `auth-analysis` · `clist-analysis` · `mail-newsletters` ·
`project-alpha-audit` · `rankwant` · `rankwant-review` · `skills-audit`.

---

## Raund 2 — Bloklovchi qaror ✅

### B1 — 10 Operations: A yoki B?

**Javob:** **A — to'liq production launch.**

Uch qo'shimcha savolga javoblar:

| Savol | Javob |
|---|---|
| B1a — On-call | **Men — eskalatsiyasiz** (telefon + Telegram, zanjir yo'q) |
| B1b — Hosting | **Hozirgi holat qoladi** (bitta mashina + Cloudflare Tunnel) |
| B1c — SLO | **Mavjud NFR'lardan** (uptime 99.5%, p50<5s, p95<15s, 5xx<1%, navbat<5min) |

**Bajarildi** — commit `2ff7632` (`docs/10-operations/README.md`, +187/−21):

| Bo'lim | Mazmun |
|---|---|
| `SLO va error budget` | 4 maqsad NFR lardan; 99.5%/30 kun ≈ 3 soat 39 daqiqa budget |
| `On-call va eskalatsiya` | bir kishi, eskalatsiyasiz — **xavf sifatida qayd etilgan** |
| `Runbook qadamlari` | 6 holat, haqiqiy `tools/` buyruqlari bilan |
| `Disaster recovery` | RPO ≤24 soat · RTO ~1 soat (baza) · failover **yo'q** |
| `Release va rollback` | migratsiya nima uchun qaytarilmaydi |
| `Holat va tasdiq` | **preview va production ajratildi** (pastga qarang) |

⚠️ **O'Z XATOIMNI TUZATDIM.** Avval "production launch tasdig'i" deb yozgandim —
lekin hujjatning o'zi aytadi: *"**Bu production EMAS** — to'rt-hostli topologiya
o'rniga bitta mashinada ishlaydigan ko'rsatuv nusxasi."* Ya'ni men hujjatga
**yolg'on da'vo** kiritdim.

To'g'ri shakl: tasdiq **to'rt-hostli topologiya uchun** (u hali qurilmagan),
joriy deploy esa **ommaviy preview** bo'lib qoladi.

**Natija:** 10 Operations gate'i `BLOCK` → **`PASS`**. Umumiy hisob:
**2 PASS · 8 WARN · 0 BLOCK · 1 yo'q bosqich.**

**Qabul qilingan xavflar** — yozildi, yashirilmadi:

1. Bitta mashina — failover yo'q
2. Eskalatsiya zanjiri yo'q — tungi avariya ertalabgacha davom etadi
3. Dual-boot — har tizimning o'z bazasi
4. **Production topologiyasi qurilmagan**

---

## Raund 3 — Hujjat qarorlari (qisman ✅)

### B2 — `idea-selection`

**Javob:** *"Bir nechta variant orasidan"* — to'rt kategoriya tanlandi:
**Raqobatchi tanlovi · Brend va nom tanlovi · Mahsulot shakli · Boshqa soha
g'oyalari**.

**Bajarildi** — commit `97e32df`, yangi papka `docs/idea-selection/` (5841 bayt).

⚠️ **Hujjat RETROAKTIV** — o'sha paytda yozilmagan. `docs/README.md` ning o'zi
aytadi: *"RankWant — raqobatchi benchmark + aniq brend bilan boshlangan."*

**Uch kategoriya mavjud hujjatlardan tiklandi** (har biri manba bilan):

| Kategoriya | Manba | Natija |
|---|---|---|
| Raqobatchi tanlovi | `03/competitor-summary.md` | Uchtasi ham qoldi — har biri boshqa qatlam uchun |
| Brend va nom tanlovi | `03/brand-discovery.md` | **Eng to'liq**: 30 nom skaneri, 16 Tier A, 4 rad etish toifasi, RankWant vs Rankvant |
| Mahsulot shakli | `02` og'riqlari | Fragmentatsiya og'rig'i → OJ + contest + kontent |

⚠️ **To'rtinchi kategoriya tiklanmadi.** CP'dan tashqari ko'rilgan g'oyalar
haqida **birorta yozuv yo'q** — repo'da, `rankwant-audit/` da, `cp/` da.
Siz bunday variantlar bo'lganini tasdiqladingiz, lekin mazmunini o'ylab topa
olmayman. Hujjatda **ochiq** deb belgilandi.

**Hujjat to'liq emas** — 4-variant to'ldirilmaguncha.

### B3 — Deployment

**Javob:** **Faqat prod + mahalliy dev** (staging yo'q).

**Bajarildi** — commit `ee91559`, `06-architecture/README.md` ga
`## Deployment` bo'limi (64 qator): hozirgi holat · maqsad topologiyasi ·
muhitlar · deploy oqimi · rollback.

**Ikki nomuvofiqlik topildi** va yashirilmadi:

1. `10-operations` CI/CD tavsifi *"…→ staging deploy"* deydi, lekin staging
   muhiti **yo'q**. Ikkalasidan biri xato.
2. `ci-local.sh` va `.git/pre-push` **manbani** sinaydi, ishlab turgan
   konteynerni emas — staging o'rnini bosmaydi.

### B4 — Substitutes va voyaga yetmaganlar regulyatsiyasi

**Javob:** **Ikkalasi ketma-ket** — avval regulyatsiya, keyin substitutes.

⏳ kutilmoqda (keyingi ish)

---

## Raund 4 — Mahsulot yo'nalishi

### C1 — Keyingi qadam · C2 — Narx · C3 — `web-access`

⏳ kutilmoqda

---

## Raund 4 — Mahsulot yo'nalishi

### C1 — Keyingi qadam · C2 — Narx · C3 — `web-access`

⏳ kutilmoqda
