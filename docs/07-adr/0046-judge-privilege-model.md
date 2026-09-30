# ADR 0046 — Judge privilege model

**STATUS:** accepted
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

**STATUS:** ADR 0046 — accepted. Phase 0 chiqish blokeri; U1 (25-case bake-off) PASS/FAIL shart.
