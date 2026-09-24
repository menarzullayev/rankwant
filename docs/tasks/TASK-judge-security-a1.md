# TASK: Judge xavfsizligi — A-1 remediation (ADR-0028)

**Beruvchi:** HITL sessiya (2026-09-24) — 4 qaror foydalanuvchi tomonidan qabul qilindi  
**Ijrochi:** agent (Freebuff X-slot, `buffy-x1`)  
**Manba:** threat model [§8 A-1](../10-operations/threat-model.md) · [ADR-0004 §Xavfsizlik shartlari](../07-adr/0004-judge-engine.md) · rankwant.txt tahlili (bosqich 14 tavsiyasi)  
**Holat:** Phase 0–4 bajarildi (2026-09-24; compose topologiyasi resolved config'da
tekshirildi) — keyingi: Phase 5 Nightly isboti, Phase 6 hujjatlar

> **Deploy + oqim isboti (2026-09-24 09:22 UTC):** jonli stack 9402e69 —
> `check_deploy.sh` «Hamma konteyner joriy kodda» ✓, judge `judge-net`da
> preflight zanjiri bilan yashil (tarmoq + cgroup), `judge-queue` healthy,
> `minio-init` exited:0 (judge-ro self-test), prod health 200, api
> `judge-queue` ping ✓. Deploy oqimida topilgan ikki haqiqiy teshik va
> tuzatishlari: ① MinIO healthcheck yo'q edi (bazaviy chain — #254);
> ② `deploy.sh up --no-deps` infra servislarini ko'tarmasdi, judge
> crash-loop (`lookup judge-queue`) — 6a/8 qadami (#255). Shoshilinch
> contest-paytida redeploy yo'li usage header'ga yozildi
> (`RANKWANT_ALLOW_LIVE_CONTEST=1 RANKWANT_DEPLOY_SCOPE=all`).

> **2026-09-24, Phase 4 + HITL:** egasi «Phase 4 to'liq bajarilsin, merge +
> deploy hammasi bajarilsin» buyrug'ini berdi — bu ADR-0028 ni `accepted`ga
> o'tkazdi va Phase 7 darvozasini ochdi. Compose amalga oshirildi: `judge-net`
> (`internal: true`), alohida `judge-queue` Redis, `minio-init` (judge-ro
> read-only, self-test bilan), API/worker `JUDGE_QUEUE_URL` seam,
> bake-off default'i navbat endpoint'ini o'qiydi (case'lar tegilmagan).
> Phase 5–6 (Nightly isboti, threat model §7–§9, check_decisions qoidasi)
> keyingi PR'ga qoldirildi — topologiya o'zi shu PR'da to'liq.

> **Qo'shimcha qaror (Phase 4, 2026-09-24):** judge navbati endpoint'i kodga
> ham seam sifatida qo'shildi — `JUDGE_QUEUE_URL` (api/worker/bake-off).
> Sabab: judge faqat `judge-net`da, sessiya Redis'iga tarmoq darajasida
> yo'q; bitta Redis'da qolishi uchun tarmoqni buzish kerak bo'lardi.
> Kartadagi asl reja shu seamni nazarda tutmagan edi.

---

## Maqsad

Threat model'dagi eng katta ochiq risk **A-1**: judge `privileged: true` +
`cgroup: host` bilan Postgres va Redis bilan **bir mashinada**, bitta compose
tarmog'ida ishlaydi. ADR-0004 ning ikki sharti bugun faqat konventsiya bilan
turadi, tarmoq siyosati bilan emas:

| ADR-0004 sharti | Bugungi holat |
|---|---|
| Judge → API/DB **yo'q** | Base compose'da `networks:` yo'q ⇒ judge, postgres, redis, minio **bitta default tarmoqda**. Judge konteyneri `postgres:5432` ga ulana oladi |
| Judge host'dan tashqi tarmoqqa chiqish **yopiq** | Judge konteyneri internetga chiqishi cheklanmagan |

Sandbox qatlami o'lchangan (Nightly'da 5 izolyatsiya case'i real nsjail
ustida), konteyner qatlami — **hech qayerda**. Threat model §7⑦ aynan shuni
yozadi: *"the sandbox is verified, the container is not"*.

Yechim (HITL 2026-09-24): **konteyner darajasida ajratish hozir**, to'rt-host
topologiya gated yo'l sifatida ADR'da qoladi.

## HITL qarorlari (2026-09-24)

1. **Yo'l:** konteyner darajasida hozir (`judge-net`, `internal: true`); to'rt-host topologiya ADR'da keyingi gated qadam.
2. **Egress majburlash:** ikki mustaqil qatlam — fail-closed `PreflightNetwork` kodi + compose tarmoq ajratish.
3. **Queue:** alohida `judge-queue` Redis (sessiya Redis'idan ajraladi — threat model §④ SPOF ham torayadi).
4. **Qamrov:** task card kengaytiriladi (compose + tools + docs + CLAUDE.md), **bitta PR** — S3 (kod) va S4 (compose) birga yurishi shart, aks holda preflight judge'ni o'ldiradi.

---

## Qattiq cheklovlar

1. **`nsjail` talablari o'zgarmaydi:** `privileged: true` + `cgroup: host` qoladi (PreflightCgroup bilan tekshiriladi). Bu task tarmoq chegarasi haqida, runtime izolyatsiyasi haqida emas.
2. **Bake-off case to'plamiga tegilmaydi:** `ISOLATION_CASES` va 25 case o'zgarmasdi; S4 dan keyin Nightly'da 25/25 o'tishi shart (regressiya).
3. **Deploy darvozasi:** merge faqat CI yashil bo'lgach; deploy faqat `tools/deploy.sh`. Migratsiya YO'Q — rollback = oldingi commit qayta deploy.
4. **ADR-0028 `STATUS: proposed` bilan yoziladi** — `accepted` faqat HITL tasdig'idan keyin (L6 tamoyil: agent PRODUCTION_READY bera olmaydi).
5. **Hot file'lar** — har biri uchun `.agent/locks/` lock majburiy: `docker-compose.yml`, `docker-compose.ci.yml`, `.env.example`, `CLAUDE.md`, `tools/check_decisions.py`, `tools/check_negative.py`, `tools/check_security_boundary.py`, `.github/workflows/nightly.yml`.
6. **`docs/06`, `docs/08`, `docs/09` 🔒 tegilmaydi** — ularni tegish = yangi ADR, aynan shu ADR-0028 o'zi.
7. **`.env.public` commit qilinmaydi**, worktree'dan tashqarida (`RANKWANT_ENV_FILE` naqshi).
8. **Salt edge eslatma:** threat model §3 — bugungi real adversary crawler, lekin launch buni o'zgartiradi; shu sababli tuzatish auditga qadar qilinadi.

---

## Fazalar

### Phase 0 — AOP registratsiya (bloker)

- [x] `manifests/buffy-x1.yml` + `status/buffy-x1.md` — X-slot o'zini ro'yxatdan o'tkazadi (2026-09-24)
- [x] Task card `tasks/A1-JUDGE-SEC-001.md` (bus) — `owned_paths` (pastda) bilan
- [x] Worktree: `wt/freebuff/judge-security`, branch `feat/judge-security-a1` (@ 462e327 = origin/main)
- [ ] Lock'lar: Phase 3–6 dagi hot file'lar (o'sha fazalar boshlanishida)

`owned_paths` (kengaytirilgan karta, HITL 2026-09-24 №4):

```text
services/judge-go/**
services/judge-py/**
services/bakeoff/**
tests/security/**
docker-compose.yml
docker-compose.ci.yml
.env.example
docs/07-adr/0028-judge-container-isolation.md
docs/10-operations/threat-model.md
docs/tasks/TASK-judge-security-a1.md
docs/research/2026-09-24-judge-security/**
tools/check_decisions.py
tools/check_negative.py
tools/check_security_boundary.py
.github/workflows/nightly.yml
CLAUDE.md
```

### Phase 1 — Chegarani O'LCHASH (dalil oldin, o'zgartirish keyin)

- [x] Bir martalik konteyner default compose tarmog'ida `postgres:5432` ga ulanadi — **kutilgan natija: ULANADI** (bo'shliqning moddiy isboti) — **OPEN** (shuningdek `api:8000` OPEN; judge o'zidan va neytral probe'dan bir xil)
- [x] `judge` konteyneridan internetga chiqish tekshiriladi — **kutilgan: ochiq** — **OPEN** (`1.1.1.1:443`)
- [x] Barchasi `docs/research/2026-09-24-judge-security/README.md` ga yoziladi (qoida: qaror dalilsiz qabul qilinmaydi; o'lchov sanasi bilan) — qo'shimcha: negative control `judge:8000` REFUSED; DNS `getent` beshala nom resolve; `internal:` = 0 resolved configda

### Phase 2 — ADR-0028 draft (`STATUS: proposed`)

Fayl: `docs/07-adr/0028-judge-container-isolation.md`

- [x] **Context:** A-1 + ADR-0004 §Xavfsizlik shartlari + Phase 1 o'lchovi
- [x] **Decision:** judge faqat `judge-net` (`internal: true`) da; `judge-queue` alohida Redis; `PreflightNetwork` fail-closed; judge MinIO kredensiali read-only scope'li; to'rt-host topologiya keyingi gated qadam
- [x] **Alternatives (rad etilgan, sabab bilan):** to'rt-host endi (ikkinchi mashina + deploy zanjiri, hozirga shart emas) · rootless nsjail qayta o'rganish (bake-off qaroriga zid, vaqt) · auditgach kutish (launch riskni oshiradi)
- [x] **Consequences:** `docker network inspect` bilan tekshiriladigan chegara; bake-off/barkamollik regressiya riski; `internal: true` internet chiqishini uzadi (ADR-0004 sharti konteyner darajasida bajariladi)

### Phase 3 — Kod: `PreflightNetwork` (judge-go + judge-py)

`main.go` dagi ikki mavjud naqshning aynan davomi: `DATABASE_URL` rad etish
(27–31-qatorlar) + `PreflightCgroup` (fail closed).

- [x] `PreflightNetwork()` — ishga tushishda `postgres:5432` va `api:8000` ga 2 s timeout bilan ulanish harakati; **ulash MUVAFFAQIYATLI bo'lsa `exit 1`** (fail closed: ulanish = chegara buzilgan) — `judge-go/preflight_net.go` + `preflight.py check_network()`; test seam: `POSTGRES_HOST/PORT`, `API_PORT`, `JUDGE_FORBIDDEN_HOSTS`
- [x] Ulanish xatosi (refused/timeout/unknown host) = o'tdi — tarmoq ajratilgan (testlar real socketlar bilan: ochiq listener / refused / `.invalid` DNS)
- [x] Gate: `JUDGE_NET_PREFLIGHT` env (compose'da `1`); `.env.example` ga yoziladi (`check_env_example` ✓ 77 o'zgaruvchi)
- [x] judge-py'da parity (`preflight.py` ga qo'shiladi) — pytest 7/7, ruff/format/mypy ✓
- [x] Unit test: default tarmoqda `exit 1`, izolyatsiyada o'tish — judge-go: go vet + `go test ./...` ✓ (golang:1.25-alpine, Docker'da); tuzoq qayd etildi: targets mapida host-kalit to'qnashuvi test yolg'on yiqitgan (127.0.0.2 bilan tuzatildi)

### Phase 4 — Compose: `judge-net` + `judge-queue`

- [x] Yangi tarmoq: `judge-net`, `internal: true` — `networks:` bloki, baza faylda
- [x] **judge: faqat `judge-net`** (default'dan chiqariladi) — resolved config'da tekshirildi
- [x] redis + minio + **yangi `judge-queue`** (redis:7): ikkala tarmoqda — api/worker default'dan navbatga yozadi, judge `judge-net`dan o'qiydi (api/worker/beat/bake-off `JUDGE_QUEUE_URL` seam orqali)
- [x] postgres, api, worker, beat, web: **faqat default** — `judge-net`da EMAS (resolved config'da tekshirildi; `check_compose.py` + `check_security_boundary.py` endi shuni qo'riqlaydi)
- [x] judge env: `REDIS_URL` → `judge-queue`; `JUDGE_NET_PREFLIGHT: '1'`
- [x] **A-2 qismli yopilishi (bir PR'da arzon):** judge env'dan `S3_SECRET: devdevdev` (root cred) chiqariladi → MinIO'da `judge-ro` user, bucket'ga **faqat read** policy; threat model §11 ga qayd — `compose/minio-init/minio-init.sh` (idempotent, self-test: o'qish OK / yozish YO'Q), judge `minio-init` `service_completed_successfully` kutadi; public overlay'da `S3_SECRET: ${JUDGE_S3_SECRET:-...}` passthru
- [x] `docker-compose.ci.yml`: ci stack'ga xuddi shu tarmoqlar (bake-off servisi default'da qoladi — navbatga `JUDGE_QUEUE_URL` bilan ulanadi; `judge-queue`/`minio` bazadan ikkala tarmoqni meros oladi)
- [x] S3 + S4 **bitta PR**da: ajratilsa, tarmogisiz preflight judge'ni o'ldiradi (HITL qarori №4)

### Phase 4.5 — Guardlar (shu PR, karta kengayuvida qo'shildi)

- [x] `tests/security/check_compose.py`: judge = faqat `judge-net`; `judge-net` = internal; `judge-queue`/`minio` = ikkala tarmoq; default-only ro'yxati judge tarmog'ida EMAS; judge env'da root parol QIYMATI yo'q (A-2); `judge-queue` prefix-tekshiruvdan chiqarildi (yolg'on qizil oldini olish)
- [x] `tools/check_security_boundary.py`: `networks:` parse (inline list; noma'lum shakl = exit 2); judge/both/default qoidalari; `internal: true` regex-langari; `judge-queue`/`minio-init` INTERNAL_ONLY'ga qo'shildi; portlar bo'limi o'zgarmasdi (2 nashr etilgan port qoladi)
- [x] `.env.example`: `JUDGE_QUEUE_URL`, `JUDGE_S3_SECRET` hujjatlangan (check_env_example ✓ 79 var)

### Phase 5 — Nightly: konteyner qatlamining dinamik isboti

Yangi heavy job **YO'Q** (`pr_skips_heavy_ci` va MAX_HEAVY=2 buzilmaydi).

- [ ] Mavjud `e2e` job'ida (stack allaqachon turibdi, bake-off qadamidan keyin) bitta qadam: `judge-net`ga ulangan bir martalik konteyner bilan — `postgres:5432` **YO'Q**, `redis`/`judge-queue`/`minio` **BOR** ni isbotlaydi
- [ ] `run.sh` statik yarmiga compose tarmoq tekshiruvi qo'shiladi (`check_compose.py` kengaytmasi): judge faqat `judge-net`da, postgres uning tarmog'ida yo'q
- [ ] `check_security_boundary.py` yangi overlay zanjirini o'qiydi va tarmoq qoidasini qo'riqlaydi (portlar qismi o'zgarmasdi — 2 nashr etilgan port qoladi)

### Phase 6 — Hujjatlar + qoidalar (hot file'lar, lock bilan)

- [ ] `threat-model.md` §7⑦ E qatori: control'ga yangi qatlamlar yoziladi
- [ ] **§8 A-1 yangilanadi:** status `accepted → narrowed (container-level)`, *Revisit when* o'lchanadigan triggerlarga almashadi: ① to'rt-host topologiya deploy bo'lsa → risk yopiladi; ② tashqi audit hisoboti kelsa; ③ `judge-net` konfiguratsiyasi o'zgarsa (guard qizaradi)
- [ ] §9 jadval: ADR-0004 ning ikki buzilgan satri «container level bajarildi, host level gated» holatiga o'tadi
- [ ] `CLAUDE.md` qarorlar jadvaliga qator: sana, qaror, kodda qayerda (`judge-net` + `PreflightNetwork` + `check_decisions` rule id)
- [ ] `check_decisions.py` yangi qoida: ADR-0028 accepted bo'lsa compose'da `judge-net: internal: true` va `PreflightNetwork` borligini tekshiradi
- [ ] `check_negative.py` ga 2–3 salbiy test (qoida langari mutatsiyalari — `security-suite` yozuvidagi ikki tuzoq naqshiga qarshi)

### Phase 7 — HITL darvoza va joriy etish

- [x] ADR-0028 (proposed) + Phase 1 o'lchovi foydalanuvchiga ko'rsatiladi
- [x] Egasining 2026-09-24 buyrug'i («merge + deploy hammasi») — ADR `accepted`; PR + merge + deploy shu buyruq asosida
- [ ] Deploy'dan keyin `check_deploy.sh` — «Hamma konteyner joriy kodda»
- [ ] Bake-off 25/25 Nightly'da yashil (regressiya isboti)

---

## Qabul mezonlari (Definition of Done)

1. `docker compose -f docker-compose.yml -f docker-compose.public.yml config` → judge **faqat** `judge-net`da; postgres `judge-net`da YO'Q (guard buni qo'riqlaydi).
2. Nightly evidence: `judge-net`dan postgres ulanishi YO'Q, redis/judge-queue/minio BOR.
3. `PreflightNetwork` fail-closed: izolyatsiyasiz muhitda judge `exit 1` (unit test isboti).
4. Bake-off 25/25 izolyatsiya case'i regressiyasiz o'tadi.
5. ADR-0028 **accepted** (HITL); threat model §8 A-1 yangilangan; §7⑦/§9 mos.
6. Judge MinIO kredensiali read-only (A-2 qismli yopilishi §11 da qayd etilgan).
7. `check_decisions.py` yangi qoida yashil + 2–3 salbiy test.
8. CLAUDE.md qarorlar jadvalida qator bor.
9. Deploy faqat HITL + `deploy.sh` orqali; migratsiya yo'q.

---

## Fayllar — tegmaslik / ehtiyot

| Fayl | Sabab |
|---|---|
| `docker-compose.public.yml` | Deploy zanjiri — o'zgarish `deploy_scope.py` / `check_security_boundary.py` bilan sinchiklab |
| `services/bakeoff/harness/runner.py` | Case to'plami muzlatilgan (`ISOLATION_CASES`); tegish = ikki haqiqat manbasi |
| `services/judge-go/sandbox.go` | nsjail primitivi — bu task tarmoq haqida, sandbox haqida emas |
| `.env.public` | Hech qachon commit qilinmaydi |
| `docs/06`, `docs/08`, `docs/09` | 🔒 locked — ADR-0028 o'zi shu farqni rasmiylashtiradi |

## Foydali havolalar

- [ADR-0004 — judge engine](../07-adr/0004-judge-engine.md) — §Xavfsizlik shartlari, PULL protokoli
- [Threat model](../10-operations/threat-model.md) — §7⑦, §8 A-1, §9, §11, §12
- [Four-host README](../../compose/four-host/README.md) — gated keyingi qadam
- [AOP](../10-operations/parallel-agents.md) — worktree, lock, handoff qoidalari
- Naqsh manbalari: `services/judge-go/main.go` (27–31, 52–60), `tests/security/check_compose.py`

---

## Boshlash buyrug'i (copy-paste)

```
RankWant monorepo: repo ildizi (`git rev-parse --show-toplevel`)

TASK faylini to'liq o'qi: docs/tasks/TASK-judge-security-a1.md

Qisqa: A-1 remediation — judge konteynerini judge-net (internal) tarmog'iga
o'tkaz, alohida judge-queue Redis, judge-go/judge-py ga fail-closed
PreflightNetwork, ADR-0028 proposed, threat model §8 A-1 yangilash,
check_decisions qoidasi + salbiy testlar, Nightly'da tarmoq isboti.
Fazalar ketma-ket; Phase 1 o'lchovsiz Phase 4 boshlanmaydi.
ADR `accepted` faqat HITL tasdig'idan keyin. Bake-off case'lariga tegma.
```
