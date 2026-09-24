# ADR-0028: Judge konteyner izolyatsiyasi — judge-net, judge-queue va PreflightNetwork

**STATUS:** accepted (2026-09-24) — egasi buyrug'i bilan qabul qilindi
(HITL: «Phase 4 to'liq bajarilsin, merge + deploy hammasi bajarilsin» —
joriy etish buyrug'i qarorni ratifikasiya qiladi; task card Phase 7 darvozasi
shu buyruq bilan ochildi)
**Supersedes:** [ADR-0004](0004-judge-engine.md) § Xavfsizlik shartlari —
*qisman*: topologiya talabi hozircha konteyner darajasida bajarilishini
aniqlaydi; to'rt-host topologiya gated keyingi qadam bo'lib qoladi
**Impacted:** threat model §7⑦ / §8 A-1 / §9, `docker-compose.yml`,
`docker-compose.ci.yml`, judge-go, judge-py
**Task:** `docs/tasks/TASK-judge-security-a1.md`
**Dalil:** [research/2026-09-24-judge-security](../research/2026-09-24-judge-security/README.md)

## Muammo

ADR-0004 (2026-09-06) § Xavfsizlik shartlari ikki qator yozadi:

> Judge host **hech qachon** API/DB bilan bir serverda emas.
> Judge hostdan tashqi tarmoqqa chiqish yopiq.

Bu shartlar kodga emas, **topologiyaga** bog'langan edi — va topologiya
shartni bajarolmadi. O'lchangan dalil (2026-09-24, jonli stack):

- 9 konteyner — judge, postgres, redis, minio, api, web, worker, beat,
  adminer — bitta `rankwant_default` tarmog'ida;
- judge o'zidan **va** neytral probe konteynerdan `postgres:5432`,
  `api:8000`, `minio:9000`, `web:3000` — TCP **OPEN**; internet `1.1.1.1:443`
  — **OPEN**; negative control `judge:8000` — REFUSED (matritsa «hamma narsa
  ochiq» emasligi isbotlandi);
- resolved compose zanjirida `internal:` — 0 marta.

Threat model §7⑦ buni aniq yozgan: **«the sandbox is verified, the container
is not»** — nsjail qatlami Nightly'da 5 izolyatsiya case'i bilan o'lchanadi,
konteyner qatlami esa hech qayerda. §8 A-1 aynan shu bo'shliq: `privileged:
true` + `cgroup: host` bilan Postgres va Redis bilan bir mashinada.

Himoyaning bugungi yagona qatlami — **credential** qatlami: judge'da
`DATABASE_URL` yo'q, worker uni ko'rsa o'chib qoladi. Lekin A-1 ning
premizasi aynan shu qatlamni mag'lub qiladi (qochish = ixtiyoriy kod +
judge imkoniyatlari), va judge env'ida allaqachon ochiq qiymatli MinIO root
kredensiali bor (`S3_SECRET=devdevdev`, ochiq repo) — yashirin testlar
shu orqali o'qilishi mumkin. Tarmoq qatlami credential oqqandanda portlash
radiusini cheklaydi — bugun u yo'q.

## Variantlar

1. **Konteyner darajasida ajratish — hozir.** Judge alohida `judge-net`
   (`internal: true`) tarmog'iga o'tadi; navbat alohida Redis'da; qoida
   kod darajasida ham majburlanadi (fail-closed preflight).
2. **To'rt-host topologiya — endi.** `compose/four-host/README.md` (2026-09-19)
   ko'zlagan maqsad: judge alohida mashinada. ADR-0004 asl sharti to'liq
   bajariladi, lekin ikkinchi mashina, deploy zanjiri va xarajat talab qiladi.
3. **Rootless/isolate bilan qayta bake-off.** `privileged` ni umuman
   yo'qotish. ADR-0004 bake-off'i bu yo'lni o'lchagan va rad qilingan
   variantni qayta ochish — vaqt va regressiya riski.
4. **Tashqi auditgach qoldirish.** ADR-0004 allaqachon auditni majburiy qilgan;
   u hech narsa tuzatmaydi — faqat qancha vaqt bunday holatda qolganini qayd
   etadi. Threat model §3: launch real adversary'ni o'zgartiradi.

## Tanlov

**Variant 1 — konteyner darajasida ajratish, hozir.** Variant 2 gated keyingi
qadam sifatida qoladi; variant 3 rad etilgan; variant 4 rad etilgan (audit
kutish riskni kamaytirmaydi).

Qarorning to'rtta qatlami — bular **birgalikda** ishlaydi, bittasi buzilsa
ikkinchisi ushlaydi (HITL 2026-09-24, «Preflight + tarmoq»):

### 1. Tarmoq: `judge-net` (`internal: true`)

- Judge **faqat** `judge-net`da — `default`dan chiqariladi.
- `default`da qoladi: postgres, api, worker, beat, web, migrate.
- Ikkala tarmoqda: redis, minio, **yangi `judge-queue`**.
- `internal: true` — Docker tarmog'iga tashqi yo'nalish yo'q: judge'dan
  internetga egress **konfiguratsiya darajasida** yopiladi (ADR-0004 ning
  «tashqi tarmoq yopiq» sharti birinchi marta bajariladi).

### 2. Navbat: alohida `judge-queue` Redis

Judge navbati (`rankwant:judge:jobs`/`rankwant:judge:results`) sessiya va
Celery broker'dan **alohida** Redis instansiyasiga ko'chadi. Bitta Redis uch
vazifa — threat model §④ qayd etgan **SPOF**; bu qaror o'sha bo'shliqni ham
toraytiradi. Qo'shimcha servis narxi — bitta kichik redis konteyneri.

### 3. Kod: `PreflightNetwork` — fail closed

Ishga tushishda worker `postgres:5432` va `api:8000` ga ulanish harakatini
qiladi. **Ulanish MUVAFFAQIYATLI bo'lsa — `exit 1`** (ulanish = chegara
buzilgan). Ulanish xatosi (refused / timeout / unknown host) — o'tdi. Bu
`DATABASE_URL`-ni-rad-etish naqshining tarmoqqa tatbiqi: qoida hujjat matni
emas, **kod**. Gate: `JUDGE_NET_PREFLIGHT` env (compose'da `1`).

### 4. Kredensial: judge MinIO scope'i read-only

Judge env'dan `S3_SECRET: devdevdev` (root) chiqariladi; MinIO'da `judge-ro`
useri — bucket'ga **faqat o'qish**. Qochish bo'lsa ham yashirin testlarni
**yozish** mumkin bo'lmaydi. Bu A-2 ning judge tomonidagi qimmat yarmini
bir PR'da yopadi.

## Sabab

1. **Risk real, lekin remediation arzon.** To'rt-host ikkinchi mashina so'raydi;
   `judge-net` + preflight — compose va 2 fayl. A-1 og'irligi bitta-host
   preview'dan kelib chiqadi (threat model §9) — demak bo'shliq konteyner
   qatlamida bog'lash arzon bo'lgan qatlamda.
2. **Qatlamlik** repodagi muhim nuqtalarni ushlaydi: credential qatlami
   (`DATABASE_URL` rad etish) butun qoldi va u tarmoq qatlamining buzilish
   rejimini yopadi; preflight esa tarmoq sozlamasini tushirib qo'ygan deploy'ni
   ishga tushirmaydi (fail closed — `PreflightCgroup` bilan bir sulola).
3. **internal: true** egressni ham yopadi — ya'ni ikki buzilgan ADR-0004
   satri bittasiga kelib bajariladi.
4. **Kredensial scope'i** ochiq repo'da yashovchi yagona kalitni (A-2)
   judge imkoniyatlaridan chiqaradi — mag'lubiyat portlash radiusini
   o'zgartiradi.

## Oqibatlar

- Judge navbati `REDIS_URL` → `judge-queue` (compose'da ikkinchi redis);
  api/worker/beat navbatlari o'zgarmaydi — **kodda endpoint yo'q**.
- `docker compose … config` endi judge uchun `networks: [judge-net]` va
  `internal: true` beradi — bu qoida `check_decisions`/`check_compose`
  guard'lari bilan qo'riqlanadi (salbiy testlar bilan).
- Nightly'da konteyner qatlamining **dinamik isboti** paydo bo'ladi:
  `judge-net`dan `postgres` ulanishi YO'Q, `judge-queue`/`minio` BOR —
  yangi heavy job yo'q, mavjud `e2e` stack'ida bir qadam
  (`pr_skips_heavy_ci` buzilmaydi).
- Bake-off 25 case regressiyasi Nightly'da tekshiriladi — `ISOLATION_CASES`
  o'zgarmaydi.
- Migratsiya YO'Q → rollback = oldingi commit qayta deploy.
- **Egress ta'siri:** `internal: true` tarmoqdagi konteyner image pull qilmaydi
  (pull build vaqtida, Docker daemon tomonidan — ta'sir yo'q), lekin kelajakda
  judge ichidan tashqi manzarga egress talab qiladigan xususiyat (masalan,
  remote judge) bu ADRni qayta ko'rishni talab qiladi.

### To'rt-host topologiya — gated keyingi qadam

`compose/four-host/README.md` dagi maqsadli topologiya endi **B**, emas,
**A-0** holatdan boshlaydi: judge host allaqachon tarmoq darajasida izolyatsiya
qilingan. Unga o'tish shartlari: ikkinchi mashina byudjeti, deploy zanjirining
kengayishi, va tashqi auditining hisoboti. Bunga o'tganda A-1 to'liq yopiladi
(threat model §8 triggerlari yozadi).

## Bog'liq hujjatlar

- [0004-judge-engine.md](0004-judge-engine.md) — § Xavfsizlik shartlari (supersedes, qisman)
- [../research/2026-09-24-judge-security/README.md](../research/2026-09-24-judge-security/README.md) — o'lchangan dalil
- [../tasks/TASK-judge-security-a1.md](../tasks/TASK-judge-security-a1.md) — 7 fazali reja
- [../../compose/four-host/README.md](../../compose/four-host/README.md) — gated keyingi qadam
