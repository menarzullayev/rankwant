# ADR 0046 — Judge privilege model

**STATUS:** accepted · **amalga oshirildi 2026-11-10** (§ 9)
**Sana:** 2026-09-29
**Tasdiqlagan:** Saidakbar (owner)
**Manba:** D3 (ADR 0046 / A−) · D10 (hardening yo'li) · `owner-decision-closure-matrix-2026-09-29.md`
**Ta'sir doirasi:** Phase 0
**Dalil:** `docker-compose.yml` (`judge` servisi, `privileged: true` kaliti) · `docker-compose.yml` (`judge` servisi, `cgroup: host` kaliti) · `services/judge-go/sandbox.go` (nsjail `inside=65534, outside=0`) · `services/judge-go/Dockerfile` (runtime bosqich `FROM scratch`, `USER` direktivasi **yo'q**)

## 1. Muammo

Judge konteyneri `privileged: true` va `cgroup: host` bilan ishlaydi. Bu konteynerga barcha Linux capabilities beradi, seccomp/AppArmor cheklovini olib tashlaydi va host cgroup namespace'ini ulashadi. `services/judge-go/sandbox.go` da nsjail yuborish jarayonini `inside=65534, outside=0` bilan ishga tushiradi, ya'ni yuborish host uid 0 da bajariladi. Runtime image `FROM scratch` va `USER` direktivasisiz quriladi — konteyner root.

Oqibat: nsjail yoki kernel chegarasidagi bitta zaiflik **host root** darajasiga chiqadi. Judge bir hostda Postgres/Redis/MinIO bilan turadi (ADR 0047 hali bajarilmagan), ya'ni escape blast radius butun testdata va bazani qamraydi.

## 2. Variantlar

1. `privileged` qoldirish (hozirgi holat).
2. To'liq VM (har yuborish uchun mikro-VM).
3. User-namespace rejimi: systemd `Delegate=yes` bilan cgroup delegatsiya + nsjail userns + aniq seccomp profili.
4. Oraliq qadam: `cap_drop: [ALL]` + minimal `cap_add`.

## 3. Tanlov

**Variant 3**, **bir bosqichda** (D10). Judge konteyneri `privileged` **bo'lmaydi**: rootless userns + aniq seccomp profili + runtime image'da `USER` direktivasi. Oraliq `cap_drop` bosqichi **yo'q**.

## 4. Sabab

`privileged` — nsjail uchun qulaylik kaliti, lekin u butun izolyatsiya chegarasini bitta konteynerga bog'laydi. Userns + seccomp + `USER` birgalikda escape blast radius'ni konteynerga qisqartiradi va host root yo'lini yopadi. Oraliq `cap_drop` bosqichi oraliq holat yaratadi — unda judge hali ham kengaytirilgan huquqlarga ega bo'ladi, ya'ni ikki marta deploy va ikki marta xavf. D10 shu sabab **bir bosqichni** tanladi, lekin uni **majburiy 25-case bake-off** bilan shartladi (quyida).

`privileged`siz nsjail ishlashi hali **o'lchanmagan** — bu evidence gate U1 (pastda).

## 5. Oqibatlar

- nsjail sozlash murakkablashadi (seccomp profili, userns mapping).
- CVE yuzasi kamayadi; judge host root yo'li yopiladi.
- Runtime image'ga `USER` qo'shiladi — konteyner root bo'lmaydi.
- M2 — infratuzilma migratsiyasi: `docker-compose.yml`, `services/judge-go/Dockerfile`, `services/judge-go/sandbox.go` bir deploy'da o'zgaradi.
- Judge **host ajratish** (ADR 0047) bu ADR doirasida **emas** — u Phase 1 da qoladi.

## 6. Qaytarilishi

Qiyin: bir bosqichda bajariladi, oraliq holat yo'q. Rollback = compose va Dockerfile diff'ini qaytarish (forward-only migratsiya siyosati, D11A). Deploy oldidan **dump** majburiy. `privileged`siz nsjail ishlamasa — U1 FAIL bo'ladi va **yangi owner decision** ochiladi.

## 7. Tasdiq

- `grep "privileged"` va `grep "cgroup: host"` repo'da → **0 natija**.
- nsjail **bake-off 25 case PASS** (U1 evidence gate).
- Judge **p95 latency raqami** yozilgan.
- Runtime image'da **`USER` direktivasi mavjud**.
- **Bir bosqichda** bajarilgan (oraliq `cap_drop` bosqichi yo'q).

## 8. Bog'liq hujjatlar

- D3 · D10 — `owner-decision-closure-matrix-2026-09-29.md`
- `acceptance-criteria-lock-2026-09-29.md` — WP7 bloki
- Blueprint §21 (ADR 0046) · §22.2 (M2) · §24 (Phase 0/1)
- `phase0-reconciliation-table-2026-09-29.md` — 1-qator (faza nomuvofiqligi)
- ADR 0047 (judge host ajratish) · ADR 0022 (judge tillari)

## 9. Amalga oshirish (2026-11-10)

Egasi audit Q-03 da «ADR-0046 ni bajarish» variantini tanladi. Hammasi
production mashinasida (Docker Desktop, WSL2 kernel 6.18, cgroup v2, AppArmor
yo'q), production stack'ga tegmasdan alohida konteynerlarda o'lchandi.

### Dizayn

Judge binari endi ikki bosqichda ishlaydi (`services/judge-go/userns.go`,
compose'da `JUDGE_USERNS=1`):

1. **launcher** — konteynerning PID 1 i, root sifatida boshlanadi. Worker'ni
   yangi user + mount + cgroup namespace'da ishga tushiradi va unga ikki
   qatorli id map yozadi (`0→0`, `10001→10001`). Keyin o'zi uid 10001 ga
   tushadi, SIGTERM'ni quvur orqali worker'ga yetkazadi va yetim jarayonlarni
   yig'adi (`init: true` — `docker-init` — olib tashlandi: u root bo'lib qolardi
   va uid 10001 dagi launcher'ga signal bera olmasdi).
2. **worker** — o'z namespace'ida uid 0 sifatida konteynerning **o'z**
   cgroup'ini yoziladigan qilib ulaydi (Docker beradigani read-only), daraxtni
   quradi (`init/` — oldingi jarayonlar, `rankwant/` — limitlar root'niki,
   `rankwant/svc/` — worker), `rankwant/` ni cgroup v2 delegatsiyasi bo'yicha
   uid 10001 ga beradi va o'zi uid 10001 ga tushadi.
3. nsjail worker'dan (uid 10001) o'z user namespace'ini yaratadi — sandbox'dagi
   dastur tashqarida **uid 10001** (ilgari host uid 0).

Ishga tushishdan ~100 ms keyin konteynerda uid 0 dagi jarayon yo'q (`docker
top`: ikkala jarayon `10001`; PID 1: `CapEff=0`, `NoNewPrivs=1`, seccomp
yoqilgan). Worker to'rt fail-closed tekshiruvdan keyingina ish oladi:
`PreflightIdentity` (root emas, capability yo'q), tarmoq, cgroup va
`PreflightSandbox` (bitta haqiqiy nsjail yurishi; sandbox tashqarida uid 0
bo'lsa ham rad etadi).

### Har bir sozlama — o'lchov bilan (bittadan olib tashlab)

| Sozlama | Olib tashlansa |
| --- | --- |
| `cap_add: SETUID` / `SETGID` / `SETFCAP` | har biri: launcher worker'ni ishga tushira olmaydi (`fork/exec: operation not permitted`) — ikki qatorli map uchun SETUID/SETGID, uid 0 ni map qilish uchun SETFCAP (kernel ≥ 5.12) |
| seccomp: Docker standarti + `clone`, `clone3`, `mount`, `umount2`, `pivot_root`, `sethostname` | `clone`/`mount` — judge ishga tushmaydi; `clone3` — har yurish `IE`; `umount2`/`pivot_root`/`sethostname` — har yurish `CE`/`RE`. `unshare`, `setns`, `chroot` **kerak emas** — yopiq qoldi |
| `systempaths=unconfined` | judge ishga tushadi, lekin **har** yechim `CE`: Docker'ning `/proc` niqoblari nsjail o'z `/proc` tmpfs'i ostida qolgan submount'larni qayta ulay olmaydi. Endi `PreflightSandbox` buni startup'da ushlaydi |
| `apparmor=unconfined` | Docker Desktop'da ta'siri yo'q (AppArmor o'chiq). Ubuntu host'da `docker-default` profili har qanday `mount` ni rad etadi |
| Docker standart seccomp (o'zgartirishsiz) | launcher ishga tushmaydi |

To'rtinchi capability, `CAP_SYS_ADMIN`, `cgroup: host` yoki `privileged`
**kerak emas**.

### ADR matnidan farqlar (o'lchov bilan)

- **`USER` direktivasi o'rniga launcher.** Image `USER 10001` bilan boshlansa
  cgroup'ni boshqarib bo'lmaydi: Docker non-root foydalanuvchiga `cap_add`
  ni faqat bounding set'ga beradi (o'lchandi: `CapEff=0`), cgroup fayllari esa
  uid 0 niki. Shuning uchun image root sifatida boshlanadi, lekin faqat
  launcher uchun; foydalanuvchi (`judge`, uid 10001) image'da yaratiladi va
  start'dan keyin hech bir jarayon uid 0 da qolmaydi — `PreflightIdentity`
  buni majburlaydi.
- **Ikki «unconfined»** (`systempaths`, `apparmor`) qoldi. Ikkalasi
  `privileged` da ham yo'q edi, ya'ni orqaga qadam emas; `/proc/sys` endi
  faqat uid 0 jarayonlarga yoziladigan, ular esa start'dan keyin yo'q.
- **`--rlimit_nproc` olib tashlandi.** `privileged` da u hech qachon ishlamagan:
  sandbox uid 0 edi, kernel esa uid 0 ni `RLIMIT_NPROC` dan ozod qiladi.
  uid 10001 da birinchi marta ishlagach fork bomb'ning har urinishi arzon
  yiqila boshladi, RCU kutayotgan `task_struct`lar run cgroup'iga yozildi va
  `memory.max` ga yetdi: `09-fork-bomb` 8 tadan 7 tasida `MLE` (slab +177 MB),
  bayroqsiz 6/6 `TLE` 95–139 MB da — `privileged` dagi bilan bir xil (8/8,
  90–118 MB). Jarayon chegarasi — avvalgidek cgroup `pids.max`.
- **Sandbox'ning o'z seccomp siyosati qo'shildi** (`sandbox.go` →
  `sandboxSeccomp`). Konteyner profili nsjail uchun namespace syscall'larini
  ochadi; dastur ularni meros olmasligi uchun nsjail exec'dan oldin ularni
  qayta yopadi (Docker standarti kabi `EPERM`; `clone3` → `ENOSYS`).
  **Production'dagi `privileged` judge'da yangi `33-nested-userns` case'i
  yiqiladi** — dastur `clone(CLONE_NEWUSER)` bilan user namespace yaratadi
  (o'lchandi); yangi judge'da yopiq.

### § 7 tasdig'i

| Mezon | Natija |
| --- | --- |
| `privileged` va `cgroup: host` judge uchun yo'q | compose fayllarida 0; `tools/check_decisions.py` → `judge privileged emas` va 10 salbiy test qo'riqlaydi. Repo bo'ylab `grep` 0 emas — tarixiy yozuvlar va qo'riqchilarning o'zi bu so'zni tilga oladi |
| bake-off PASS (U1) | **33/33**, ketma-ket 3 marta, compose'dan ko'tarilgan judge'da (25 asl case + 26–32 + yangi 33) |
| p95 latency | bake-off funksional to'plami: yangi p50 83–98 ms, p95 1858–2119 ms; o'sha mashinada `privileged`: p50 89 ms, p95 1981 ms — farq yo'q |
| `USER` | launcher bilan almashtirildi (yuqorida, sabab o'lchangan) |
| Bir bosqich | ha — oraliq `cap_drop` holati yo'q |

### Ochiq qoldi

- **Host ajratish** — ADR-0047, alohida mashina kerak (threat model A-1).
- nsjail user namespace talab qiladi — kernel'ning userns kodi konteynerdan
  yetib boriladi (dasturdan emas: u sandbox siyosati bilan yopiq).
- **Ubuntu ≥ 23.10 host** `kernel.apparmor_restrict_unprivileged_userns=0`
  talab qiladi: CI (`tools/ci_stack.sh`) o'zi qo'yadi; dual-boot Linux
  tomoni hujjatda (`docs/10-operations` § Ikki tizimli preview), lekin u
  yerda o'lchanmagan.
- Worker va sandbox bir xil uid (10001). Alohida uid uchun worker'ga
  capability kerak bo'lardi — ataylab qilinmadi.

**STATUS:** ADR 0046 — accepted, amalga oshirildi 2026-11-10. U1 — **PASS** (bake-off 33/33, § 9).
