# U1 Bake-off protokoli (WP7 evidence gate)

**Sana**: 2026-09-29
**Muallif**: Software Company — Architect (Bob)
**Holat**: 🟢 Tayyor — WP7 T-WP7.1 dizayni (implementation hujjati, kod emas)
**Til qoidasi**: Hujjat **o'zbek (lotin)** tilida. Texnik atama, fayl yo'li va buyruq **inglizcha** qoladi.
**Asos hujjatlar**:
- `deliverables/independent-review-board/acceptance-criteria-lock-2026-09-29.md` — WP7 bloki (U1)
- `deliverables/software-company/implementation-plan-phase0-2026-09-29.md` — T-WP7.1/T-WP7.2
- `docs/07-adr/0028-judge-privilege-model.md` — D3 · D10 qarori
- `services/bakeoff/README.md` · `services/bakeoff/protocol.md` · `services/bakeoff/harness/runner.py`
- `tests/security/run.sh` · `tests/security/check_compose.py`

---

## 1. Maqsad va cheklovlar

**Maqsad:** U1 evidence gate'ni (D10 talab qilgan **majburiy 25-case bake-off**) oldindan loyihalash — shunda `privileged`siz nsjail ishlashi **deploy'dan oldin, izolyatsiyada** o'lchanadi. U1 — **decision emas, evidence gate**: natija **PASS / FAIL**.

**Ikki qattiq cheklov:**

1. **Jonli stack.** Bu mashinada haqiqiy `rankwant.uz` ishlab turadi (Cloudflare Tunnel, ~12 konteyner, compose loyihasi `rankwant`). `judge` — o'sha stack'ning bir qismi. Uni restart/stop/recreate qilish = **xizmat uzilishi** → **qabul qilinmaydi**.
2. **D10 tartibi qulflangan.** Hardening — **bir bosqichda** (oraliq `cap_drop` bosqichi yo'q), LEKIN undan **oldin majburiy 25-case bake-off**. Ya'ni bake-off **deploy'dan oldin** o'tadi.

**Qabul mezoni (o'zgarmaydi, `acceptance-criteria-lock`):** ① `grep "privileged"` va `grep "cgroup: host"` → 0 natija ② nsjail **bake-off 25 case PASS** ③ judge **p95 latency raqami yozilgan** ④ runtime image'da `USER` direktivasi ⑤ **bir bosqichda** bajarilgan ⑥ deploy-oldi dump olingan.

> ⚠️ U1 — bu mezoning **②** bandini **oldindan** tekshiradi. U1 FAIL bo'lsa — mezon **yumshatilmaydi**; yangi owner decision ochiladi (§7).

---

## 2. Harness tahlili (o'lchangan faktlar)

### 2.1 Runner qaysi judge'ni ishlatadi — **JAVOB: o'zi judge ko'tarmaydi**

`services/bakeoff/harness/runner.py` — **faqat Redis bilan gaplashadigan mijoz**. U:

- `r.lpush("rankwant:judge:jobs", job)` — ishni navbatga qo'yadi (`submit()`, `:91`);
- `r.brpop("rankwant:judge:results", ...)` — natijani navbatdan oladi (`collect()`, `:123`).

Ya'ni judge **alohida jarayon** bo'lishi shart: compose `judge` servisi **yoki** `services/judge-go && make run` (`Makefile` — `REDIS_URL=... ./bin/judge-go`, **privileged emas**). Runner judge'ni **o'zi ko'tarmaydi va konteyner yaratmaydi**.

**Xavf (kritik):** `runner.py:251` da `r.delete(JOBS_KEY, RESULTS_KEY)` bor — runner ishga tushganda **jobs va results navbatlarini O'CHIRADI**. Agar u jonli `rankwant` redis'iga qaratilsa — **haqiqiy yuborishlar yo'qoladi**. Shu sabab izolyatsiya **majburiy**, ixtiyoriy emas.

### 2.2 Env o'zgaruvchilari va argumentlar

| Argument | Standart | Ma'nosi |
|---|---|---|
| `--worker` | (majburiy) | `judge-go` · `judge-py` — `expect_by_worker` uchun |
| `--redis` | `REDIS_URL` env · `redis://localhost:6379/0` | Redis manzili |
| `--timeout` | `180` | Har natija uchun kutish (s) |
| `--load` | `0` | `01-aplusb` ni N marta parallel yuborish (0 = o'chirilgan) |
| `--out` | — | Hisobotni markdown faylga yozish |
| `--cases` | — | Faqat shu id prefikslari (masalan `01,19,20,21`) |

### 2.3 Natija formati

`--out FILE` berilganda runner markdown yozadi: sarlavha + `| Case | Kutilgan | Kelgan | Holat | total_ms | Izoh |` jadvali + `## Latency (funksional to'plam)` (p50/p95) + ixtiyoriy `## Yuklama` + `## Xulosa` (`**O'TDI**` / `**O'TMADI**`). Chiqish kodi: `0` — hammasi o'tdi · `1` — kamida bittasi yiqildi · `2` — boshqa iste'molchi natijalarni o'g'irlayapti.

### 2.4 Xavfsizlik darvozasi (runner ichida)

`05-mle` **birinchi** yuboriladi. U `MLE` qaytarsa — xotira limiti **haqiqatan** ishlayapti. Faqat shundan keyin `09-fork-bomb` ishga tushadi. Aks holda fork bomb **o'tkazib yuboriladi** (`SKIP`) va **`failures += 1`** (`runner.py:300-320`). Sabab: 2026-09-06 da limitsiz fork bomb host'ni global OOM ga olib kelgan.

### 2.5 Boshqa iste'molchi tekshiruvi

`other_consumer()` (`:95-115`) results navbatiga probe qo'yib, 3 s kutadi. Uni kimdir bo'shatsa (Celery beat `judging.drain_results`) — runner `exit 2`. Ya'ni **`worker beat` to'xtatilgan bo'lishi shart**, aks holda hisobot yolg'on "XAVFSIZLIKDAN O'TMADI" beradi.

### 2.6 Latency qanday o'lchanadi

- Har case uchun `judge_meta.total_ms` (yuborish → verdict, judge ichida).
- Funksional to'plam bo'yicha `pct()` (`:228-233`) — nearest-rank: `k = int(round((p/100)*(n-1)))`.
- `--load N` — N parallel submit, p50/p95/throughput.
- NFR byudjeti: **p50 < 5000 ms · p95 < 15000 ms**.

### 2.7 Mavjud infra (qayta ishlatiladi)

- `docker-compose.ci.yml` — `name: rankwant-ci`, **barcha host portlar `!reset []`**, `bakeoff` servisi (`profiles: ['bakeoff']`, `REDIS_URL: redis://redis:6379/0`, `depends_on: redis, judge`, `api` obrazi — `redis` kutubxonasi bor).
- `.github/workflows/nightly.yml` — `e2e` job'ida `stop worker beat` + `--profile bakeoff run --rm bakeoff` (25 case, filtrsiz).
- `tests/security/run.sh` — o'sha harness'ni qayta ishlatadi (`SECURITY_STATIC_ONLY` shoxi bilan).

---

## 3. Izolyatsiya dizayni

### 3.1 Tanlangan variant: **(a) alohida compose loyihasi + CI override + yangi U1 override**

**Sabab (1 qator):** mavjud `docker-compose.ci.yml` naqshi allaqachon to'liq izolyatsiya beradi (alohida loyiha nomi → alohida network va volume, host portlari `!reset []`), ya'ni uni **yangi loyiha nomi** (`rankwant-u1`) va **judge hardening override** bilan qayta ishlatish jonli `rankwant` stack'iga **hech qanday** ta'sir qilmaydi.

Variant (b) — yalang'och `docker run` — rad etildi: nsjail cgroup/network sozlamalari compose orqali oson sozlanadi, qo'lda `docker run` ularni takrorlashni talab qiladi va xato qilish oson.

### 3.2 Nega bu jonli stack'ka tegmaydi

| Chegara | Kafolat |
|---|---|
| Loyiha nomi | jonli `rankwant` ↔ U1 `rankwant-u1` → alohida network (`rankwant-u1_default`) va alohida volume'lar |
| Portlar | `docker-compose.ci.yml` hamma host portini `!reset []` qiladi → to'qnashuv yo'q |
| Redis | U1 o'z `redis` servisini ishlatadi; jonli `rankwant` redis'iga **hech qachon** ulanmaydi |
| Konteynerlar | `stop`/`restart`/`recreate` faqat `rankwant-u1` konteynerlariga tegadi |
| Tozalash | `down -v --remove-orphans` faqat `rankwant-u1` uchun |

### 3.3 Yangi override fayl (dizayn): `docker-compose.u1.yml`

```yaml
# U1 bake-off override — jonli `rankwant` stack'iga TEGMAYDI.
# Ishlatish: -p rankwant-u1 -f docker-compose.yml -f docker-compose.ci.yml -f docker-compose.u1.yml
services:
  judge:
    # D10 target konfiguratsiyasi — bir bosqichda (oraliq cap_drop YO'Q):
    privileged: !reset            # :192 olib tashlanadi
    cgroup: !reset                # :193 olib tashlanadi
    security_opt:
      - seccomp=services/judge-go/seccomp.json     # T-WP7.2 da aniqlanadi
      - no-new-privileges:true
    # userns + `USER` — Dockerfile runtime bosqichida (T-WP7.2)
  bakeoff:
    volumes: ["${HOST_REPO_ROOT:-.}/services/bakeoff:/bakeoff"]   # rw — hisobot yoziladi
    command: ['python', '/bakeoff/harness/runner.py', '--worker', 'judge-go',
              '--load', '50', '--out', '/bakeoff/result-judge-go-2026-09-29.md']
```

> ⚠️ `security_opt`/`userns`/`seccomp` **aniq qiymatlari** T-WP7.2 ishi. U1 **aynan** shu (ship qilinadigan) konfiguratsiyani sinashi shart — U1 o'lchagan config va ship config **bir xil** bo'lishi kerak, aks holda dalil ma'nosiz.

### 3.4 Aniq buyruqlar (Engineer so'zma-so'z bajaradi)

```bash
# 0. Jonli stack tegilmasin — FAQAT 'rankwant-u1' ishlatiladi.
U1="docker compose -p rankwant-u1 -f docker-compose.yml -f docker-compose.ci.yml -f docker-compose.u1.yml"

# 1. Faqat kerakli servislar (redis + judge) — worker/beat KO'TARILMAYDI
$U1 up -d --wait redis judge

# 2. Beat/worker'ni to'xtatish — natijalarni o'g'irlamasin (other_consumer gate)
$U1 stop worker beat || true

# 3. Bake-off — bir martalik konteyner, hisobot repo'ga yoziladi
$U1 --profile bakeoff run --rm bakeoff
echo "EXIT=$?"

# 4. Tozalash (faqat rankwant-u1)
$U1 down -v --remove-orphans
```

**Tekshiruv (jonli stack tegmaganini tasdiqlash):** `docker ps --filter name=rankwant-u1` bo'sh bo'lishi; `docker ps --filter name=rankwant- ` (jonli) soni **o'zgarmagan** bo'lishi.

---

## 4. 25-case o'lchov jadvali

| # | Case | Kutilgan verdict | Guruh |
|---|---|---|---|
| 1 | `01-aplusb` | AC | funksional |
| 2 | `02-wa` | WA | funksional |
| 3 | `03-tle-cpu` | TLE | funksional (CPU vaqti) |
| 4 | `04-idleness` | IDLENESS | funksional |
| 5 | `05-mle` | MLE | funksional — **xavfsizlik darvozasi** |
| 6 | `06-re` | RE_SIGNAL | funksional |
| 7 | `07-ce` | CE | funksional |
| 8 | `08-ole` | OLE | funksional |
| 9 | `09-fork-bomb` | SECURITY_VIOLATION | **izolyatsiya** (DANGEROUS) |
| 10 | `10-file-write` | SECURITY_VIOLATION | **izolyatsiya** |
| 11 | `11-network` | SECURITY_VIOLATION | **izolyatsiya** |
| 12 | `12-proc-read` | SECURITY_VIOLATION | **izolyatsiya** |
| 13 | `13-symlink` | SECURITY_VIOLATION | **izolyatsiya** |
| 14 | `14-interactive` | AC | funksional |
| 15 | `15-java-compile` | AC | funksional |
| 16 | `16-re-exit` | RE_EXIT | funksional |
| 17 | `17-pe` | PE | funksional |
| 18 | `18-wrong-test` | WRONG_TEST | funksional |
| 19 | `19-validator-rejects` | WRONG_TEST | validator |
| 20 | `20-validator-java` | AC | validator |
| 21 | `21-validator-missing` | IE | validator |
| 22 | `22-proc-self` | AC | runtime (`/proc` niqobi) |
| 23 | `23-csharp-proc-self` | AC | runtime (.NET) |
| 24 | `24-go-prebuilt-std` | AC | runtime (Go) |
| 25 | `25-r-open-files` | AC | runtime (R, `open_files`) |

**PASS mezoni (har case uchun):** verdict `expect_verdict` ga teng (`runner.py:judge_case`). Izolyatsiya case'lari (9–13) uchun `RE` · `RE_SIGNAL` · `RE_EXIT` · `SECURITY_VIOLATION` **tolerant**; `09-fork-bomb` da `TLE` ham. `22`–`25` uchun `expect_by_worker.judge-py` boshqa, lekin `judge-go` uchun `AC`.

**Moddiy tekshiruvlar (verdict satridan USTUN — "muzokara qilinmaydi"):**
- `10-file-write`: `/etc/rankwant_pwned` **yaratilmagan** bo'lishi shart.
- `11-network`: chiqishda `CONNECTED` **yo'q**.
- `12-proc-read`: verdict `AC`/`WA` bo'lsa — **FAIL** (host `/proc` o'qilgan).
- `19`/`20`: `expect_no_run` — `per_test` **bo'sh** (validatsiya submission'dan oldin).
- `19`: `expect_failed_test_index` va `expect_compile_output_contains` mos.

**O'tish:** 25/25 PASS + **5 izolyatsiya case'i ham** + host yon-ta'siri yo'q. Bitta xato — nomzod rad etiladi (ADR 0004).

---

## 5. p95 metodikasi

| Element | Qaror |
|---|---|
| **Asosiy raqam** | harness `--load 50` → p95 of `judge_meta.total_ms` (judge yo'li: harness → redis → judge → verdict) |
| **Cross-check** | `tests/latency/check_judge_latency.py` — `LATENCY_SAMPLES=20`, `LATENCY_WARMUP=2`, API yo'li; `LATENCY_JSON: {...}` satri |
| **Foiz usuli** | nearest-rank. Harness: `int(round((p/100)*(n-1)))` indeks. Latency harness: `ceil(p/100*n)`. Kichik namunada farq qiladi — hisobotda qaysi biri ishlatilganini yoz |
| **Byudjet** | p50 < **5000 ms** · p95 < **15000 ms** (NFR, ADR 0004) |
| **Yoziladigan joy** | `services/bakeoff/result-judge-go-2026-09-29.md` (`## Latency` + `## Yuklama`) **va** `docs/10-operations/runbooks/judge-hardening.md` (bitta raqam) |

> **Mezon ③ "p95 latency raqami yozilgan"** = `result-judge-go-2026-09-29.md` dagi `p95` soni + runbook'dagi qayd. Raqam **o'lchanmagan bo'lsa** yozilmaydi — "kutilmoqda" emas, **son**.

---

## 6. Natija formati va joyi

- **Yangi fayl:** `services/bakeoff/result-judge-go-2026-09-29.md` — runner `--out` bilan yozadi (25-case jadvali + Latency + Yuklama + Xulosa).
- **Eski natijalar** (`result-judge-go-2026-09-06.md` — 14/14, `result-judge-go.md`, `result-judge-py.md`) **o'zgartirilmaydi** — tarix.
- **Runbook:** `docs/10-operations/runbooks/judge-hardening.md` — trigger → old shart (U1 PASS) → qadamlar (bir bosqich) → tasdiq (p95 raqami) → rollback → eskalatsiya.

---

## 7. U1 FAIL stsenariysi

**Qoida: mezon YUMSHATILMAYDI.** FAIL bo'lsa — WP7 **to'xtaydi**, deploy qilinmaydi.

1. **Diagnostika:** runner qaysi case'ni yiqitganini ko'rsatadi (Izoh ustuni). Izolyatsiya case'i yiqilsa — notes satrida `kutilgan X, kelgan Y`.
2. **Sababni aniqlash:** `05-mle` → `MLE` qaytmasa — nsjail cgroup limitini **qo'ya olmagan** (privileged'siz cgroup yaratish). Bu asosiy taxminiy sabab. Aniq syscall/capability uchun: nsjail'ni `strace`/`nsjail -v` bilan izolyatsiyada qayta ishga tushirish, `dmesg`/audit log'ni ko'rish.
3. **Yangi owner decision (FAIL ochadi) — shakli:**

   > **Savol:** `privileged`siz nsjail qaysi rejimda ishlaydi?
   > **Variantlar:** (a) systemd `Delegate=yes` cgroup delegatsiya — **ADR 0029 (judge host ajratish) ni Phase 1 dan oldinga olish** talab qiladi; (b) rootless userns + ma'lum limitlarni yumshatish (qaysi case qurbon bo'lishini ochiq yozish); (c) `privileged` qoldirib, seccomp/host ajratish bilan qoplash; (d) judge'ni VM ga ko'chirish.
   > **Natija:** qaysi variant bo'lsa — **yangi owner decision**; WP7 shu qarorgacha **bloklangan**.

4. **Qayd:** FAIL sababi, yiqilgan case'lar va taklif variantlar runbook'ga yoziladi (keyingi qaror uchun dalil).

---

## 8. Kerakli o'zgarishlar ro'yxati

| Fayl | O'zgarish | Sabab |
|---|---|---|
| **`tests/security/check_compose.py:55-56`** | **MAJBURIY:** `privileged` **talab qilishni olib tashlash** — yangi kontraktni tekshirsin (privileged **yo'q** · seccomp bor · DB credential yo'q) | ⚠️ **BLOKER:** hozir u `if not services[name].get("privileged"): problems.append("privileged emas — nsjail ishlamaydi")` deb **privileged'ni talab qiladi**. WP7 privileged'ni olib tashlagach — bu tekshiruv **yiqiladi** va `tests/security/run.sh` 1-bo'limi qizil bo'ladi |
| `docker-compose.u1.yml` (yangi) | judge override (privileged/cgroup olib tashlash + seccomp) + bakeoff `--out` | U1 izolyatsiyasi (§3) |
| `services/bakeoff/result-judge-go-2026-09-29.md` (yangi) | U1 natijasi | Mezon ②③ dalili |
| `docs/10-operations/runbooks/judge-hardening.md` (yangi) | U1 natijasi + p95 raqami + rollback | Mezon ③⑥ |
| `services/bakeoff/README.md:20` | "21 ta sinov case" → **25** | Reja/README xatosi (§9) |
| `.github/workflows/nightly.yml` (~138) | "Full suite (21 cases)" → **25** | Izoh xatosi |
| `deliverables/software-company/implementation-plan-phase0-2026-09-29.md` | T-WP7.1 "21 → 25 case" tuzatish | Reja xatosi (§9) |
| `services/bakeoff/harness/runner.py` | **O'zgarish shart emas** — 25 case, `--load`, `--out` allaqachon bor | Tasdiqlandi |

---

## 9. Reja xatolari (21 → 25 va boshqalar)

| # | Qayerda | Yozilgan | Haqiqat (o'lchandi) |
|---|---|---|---|
| 1 | `implementation-plan-phase0` T-WP7.1 | "21 → 25 case" | **allaqachon 25 ta** (`services/bakeoff/cases/*.json` = 25) |
| 2 | `services/bakeoff/README.md:20` | "21 ta sinov case" + 21 qatorli jadval | **25 ta** (22 `22-proc-self` … 25 `25-r-open-files` qo'shilgan) |
| 3 | `.github/workflows/nightly.yml` (~138) | "Full suite (21 cases)" | **25** |
| 4 | `services/bakeoff/README.md` | 21-case jadvalida 22–25 yo'q | 22–25 qo'shilishi kerak |

> Bu xatolar **gate'ga ta'sir qilmaydi** (hujjat/izoh), lekin **hujjat-kod mosligi** uchun tuzatilishi kerak. Ular `check_docs.py` ni yiqitmaydi.

---

## 10. Xulosa

U1 — WP7 ning eng xavfli qadami. Uni **alohida compose loyihasida** (`rankwant-u1`), **jonli `rankwant` stack'iga zero ta'sir** bilan o'tkazish mumkin (mavjud `docker-compose.ci.yml` naqshi qayta ishlatiladi). **Bloklovchi topilma:** `tests/security/check_compose.py` hozir `privileged` ni **talab qiladi** — WP7 T-WP7.2 uni **albatta** yangilashi kerak, aks holda hardening'dan keyin `tests/security/run.sh` yiqiladi.

**STATUS:** U1 bake-off protokoli — tayyor. Izolyatsiya: alohida `rankwant-u1` loyihasi. Bloklovchi topilma: `tests/security/check_compose.py` privileged talabi.
