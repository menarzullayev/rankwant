# RankWant — Independent Review Board: Owner Decision Memo

**Sana**: 2026-09-29
**Bosqich**: Independent Review Board (IRB) — Human-in-the-Loop qarori oldidan
**O'rindiqlar**: Architecture · Content/Data · Security · Process/Governance · Documentation
**Manba**: `deliverables/engineering-assurance/system-design-phase0-decision-closure-2026-09-29.md` (rev.2), `deliverables/engineering-assurance/implementation-ready-gate-archi-2026-09-29.md`, `deliverables/software-architecture/software-architecture-rankwant-2026-09-29.md`, repo kodi.

> **IRB QAROR QABUL QILMAYDI.** Bu memo sizni (egasi) qaror qabul qilishga tayyorlaydi: faktlar → variantlar → trade-offlar → dissent → ochiq savol. Har band **sizning savolingiz** bilan tugaydi, tavsiya bilan emas.

---

## 📌 TL;DR

- **11 ta qaror**, 5 ta o'rindiq bo'yicha ko'rib chiqildi. Har biriga: framing · variantlar · evidence kuchi · **dissent** · qaytarilish · savol · defer narxi.
- **IRB 8 ta da'voni tekshirdi — 6 tasi tuzatishga muhtoj chiqdi.** Eng jiddiylari: ADR tili da'vosi rad etildi; 0037 ning o'lchov mezoni **mavjud bo'lmagan faylga** bog'langan; verdict-taxonomy ishi allaqachon **bajarilgan**; production sirlari haqidagi blueprint da'vosi **FALSE**.
- **A− guruhi dalilga tayanmaydi** — Process o'rindig'i uni "ziddiyatni yopmaydi, qayta nomlaydi" deb topdi.
- **3 triage tuzatishi** — uchta xato emas, **bitta tizimli naqsh** (§21 ↔ §24 mos kelmaydi).

---

## 🎯 核心结论卡片

| 项目 | 内容 |
|------|------|
| Qarorlar soni | **11 ta** (5 guruh) |
| IRB topgan tuzatishlar | **6 ta** (2 da'vo rad etildi, 4 qayta talqin) |
| Eng arzon qaror | ADR tili (bir jumla, lekin 18 ADR ni bloklaydi) |
| Eng qimmat qaror | ADR 0028 (bir tomonlama eshik, eng katta blast radius) |
| Eng zaif dalil | ADR 0036 (chegara hali mavjud bo'lmagan komponent haqida) |
| Eng ko'p o'lchangan | ADR 0042 (417 / 244 / 137 / 67 raqamlari) |
| Qaror qilinmasa | 18 ADR yozilmaydi → Phase 0 chiqmaydi → `Software Company` boshlanmaydi |

---

## A. IRB topgan tuzatishlar

Bu bo'lim muhim: quyidagi da'volarni qaror qabul qilishdan **oldin** bilishingiz kerak.

| # | Oldingi da'vo | IRB topilmasi | Holat |
|---|---|---|---|
| A1 | "ADR-0001..0027 **o'zbekcha**" | O'lchandi: **23 o'zbek + 4 ingliz** (0022, 0023, 0024, 0027). Ustiga `CONTRIBUTING.md:90-91` (2026-09-17) **yangi** hujjatni **inglizcha** talab qiladi | **RAD ETILDI** |
| A2 | 0037 mezoni ① `tests/regression/test_ref_solution_verdicts.py` ga bog'langan | Bu fayl repo'da **mavjud emas**; `tests/regression/` papkasi ham yo'q | **TUZATISH KERAK** |
| A3 | "Verdict taxonomy (RE split, o'lik kod, i18n) — ochiq ish" | RE split **kodda bajarilgan** (`judging/verdicts.py:19-20`); i18n parity + o'lik-kod detektori **CI'da** (`check_verdict_codes.py:56,121,124-129`, `check_negative.py:5504,5517,6091`). **Ochiq qolgani faqat 2 ta:** (a) qaysi 4 kod o'lik ekanini **nomlash**, (b) 18 163 `RE` qatorning **M10 tarixiy qayta yorliqlanishi** — ikkalasi ham **data/qaror** ishi, ADR-kontrakt emas | **QISQARTIRILDI** |
| A4 | "A− guruhi — Phase 0 chiqish blokeri toifasi" | Blueprint'da bunday toifa **yo'q**; blueprint o'zi 0028 ni Phase 0 (`:1857` M2 boshlanishi) va Phase 1 (`:1870` done-condition) ga qo'ygan | **ASOSSIZ** |
| A5 | "3 triage tuzatishi — uchta alohida xato" | Bitta **tizimli naqsh**: §21 (ADR→faza) §24 (faza→komponent) bilan mos emas | **QAYTA TALQIN** |
| A6 | Blueprint: "haqiqiy sirlar `.env.public`da" (`:1269`, `:1388`) | `.env.public` DB/MinIO/S3 kalitlarini **umuman e'lon qilmaydi** → production haqiqatan `dev` / `devdevdev` | **FALSE** |
| A7 | "1 222 testsiz · 870 IE · 2 096 import" | Hammasi **kod izohlarida** (`staff_serializers.py:104-105,120-121`), import paytidagi bir martalik o'lchov. Jonli qiymat emas | **QAYTA SANASH KERAK** |
| A8 | "10 001 `neytron_*` user" | Uch xil son: **10 000** (seeder default) · **10 001** (ADR-0023) · **10 068** (kod izohi) | **NOANIQ** |

**A2 va A3 alohida diqqat talab qiladi:** gate o'z mezonini mavjud bo'lmagan faylga bog'lagan, va "katta ochiq ish" deb hisoblangan taxonomy aslida **asosan bajarilgan**. Ya'ni Phase 0 hajmi **kichikroq** bo'lishi mumkin.

---

## B. Qarorlar

### B1. Architecture o'rindiqi

#### B1.1 — ADR 0036: AI Gateway modulmi yoki alohida servis?

| Blok | Mazmun |
|---|---|
| **Framing** | AI Gateway birinchi versiyada monolit ichidagi modul bo'ladimi yoki alohida servis — va chegara qaysi darajada o'lchanadi |
| **Variantlar** | **A)** modul (`apps/api/ai/`) — gate Python import bilan ishlaydi, DB credential bir muhitda qoladi · **B)** alohida servis — OS/process darajasida chegara (judge naqshi), lekin yangi konteyner + Python import-gate uni **ko'rmaydi** · **C)** hozircha yo'q — gate vakuumli yashil qoladi |
| **Evidence kuchi** | **PROVEN:** repo'da AI kodi **yo'q**; `check_ai_boundary.py` **mavjud emas**; pretsedent real — `services/judge-go/main.go:27-31` (`DATABASE_URL` bo'lsa `exit 1`). **ASSUMED:** "AI DB'ga tegmaydi" bugun **bo'sh shart** (0 fayl). **ZIDDIYAT:** blueprint §12.1 "modul yoki servis", §12.6 "alohida servis", §22 "monolith + 1 servis" — uch xil |
| **DISSENT** | Hujjat "alohida servis"ga og'adi, lekin gate dizayni "modul"ni nazarda tutadi — ikkalasi **birga turmaydi**. B tanlansa, gate `check_security_boundary.py` kabi compose-env gate'ga qayta yozilishi shart. Ustiga repo o'zi "microservice'ga o'tish yo'q" deydi (§22) |
| **Qaytarilish** | **Ikki tomonlama eshik** (A↔B: kod ko'chadi, gate qayta yoziladi). Yarim bir-tomonlama: B da "DB credential yo'q" invarianti o'rnatilib, modulga qaytilsa uni saqlash qiyinlashadi |
| **Egasi savoli** | "AI Gateway birinchi versiyada modulmi yoki alohida servis?" |
| **Defer narxi** | `check_ai_boundary.py` qaysi darajada o'lchashini bilmaydi → WP5 yozilmaydi → done-condition ⑤ ochiq. Va `0036 → 0042` ketma-ketligi uziladi (0042 allowlist AI joylashuvini bilishi kerak) |

#### B1.2 — ADR 0042: mavjud import'lar grandfather yoki darhol fail?

| Blok | Mazmun |
|---|---|
| **Framing** | Cross-app `models` import'lari allowlist'ga grandfathered bo'ladimi yoki darhol build'ni yiqitadimi |
| **Variantlar** | **A)** grandfather · **B)** darhol fail · **C)** faqat hujjat qoidasi (gate yo'q) |
| **Evidence kuchi** | **PROVEN (o'lchandi):** cross-app model import — **417 qator** (testlar bilan) · **244 qator production** · **137 production fayl** · shundan **67 tasi `core.models`** (shared kernel `User`). Non-core production ≈ **177 qator**. `check_architecture.py` **mavjud emas**. `problems/services.py` va `problems/selectors.py` **yo'q**, holbuki blueprint §8.2 ularni talab qiladi. **ASSUMED:** "grandfathering foydali" — allowlist'da **ratchet** bo'lishiga bog'liq, blueprint ratchetni aytmaydi |
| **DISSENT** | Grandfathering — **eng zaif** tanlov: ratchetsiz u allowlist'ni faqat-o'sadigan ro'yxatga aylantiradi va gate'ni **hujjatga** qaytaradi — bu repo'ning o'z aksiomasiga zid (§8.4 AP11: chegara gate skript bilan majburlanadi). Ammo "darhol fail" ham **soxta tanlov**: 177 importning ko'pi service qatlami **yo'qligidan** kelib chiqadi — fail qilish avval katta refactorni talab qiladi, bu Phase 0 scope'ida emas |
| **Qaytarilish** | **Ikki tomonlama eshik**, bir tomonlama qism yo'q. Xarajat: "muzlatilgan son" bilan yozilsa, keyin qisqartirish har import uchun kod ishi |
| **Egasi savoli** | "Mavjud 177 non-core import grandfather (ratchet bilanmi yoki ratchetsiz) bo'ladimi, yoki gate darhol fail qiladimi?" |
| **Defer narxi** | WP6 va done-condition ⑤ ochiq; `0036 → 0042` to'xtaydi; TD18 himoyasiz |

#### B1.3 — ADR 0028: oraliq `cap_drop` yoki to'liq userns + seccomp?

| Blok | Mazmun |
|---|---|
| **Framing** | Judge konteyneriga oraliq `cap_drop:[ALL]` + minimal `cap_add` qo'llaniladimi, yoki to'g'ridan-to'g'ri rootless user-namespace + seccomp |
| **Variantlar** | **A)** oraliq (`privileged` olib tashlanadi, `cgroup:host` qoladi) · **B)** to'liq (rootless userns 65534:65534 + seccomp + systemd `Delegate=yes`) · **C)** status quo |
| **Evidence kuchi** | **PROVEN:** `docker-compose.yml:192-193` `privileged: true` + `cgroup: host`; `services/judge-go/sandbox.go:237-244` nsjail `--user 65534`, **`outside=0`** (izoh: `newuidmap/subuid` yo'q); `services/judge-go/Dockerfile:222` runtime `FROM scratch`, **`USER` direktivasi YO'Q** → konteyner root. O'lchov naqshi bor: `check_negative.py:4139-4145` `privileged: true` ga tegadi. ADR-0004 `accepted`: alohida server + "launch oldidan tashqi audit majburiy". **ASSUMED:** "`privileged` siz nsjail ishlaydi" — prototip qilinmagan (Q7); seccomp profili yo'q. **UNVERIFIED:** host cgroup v1/v2; escape → host root tasdiqlovchi test yo'q |
| **DISSENT** | Oraliq `cap_drop` xavfni **kamaytirmasligi mumkin**: asosiy zaiflik capability emas — `cgroup: host` + `outside=0` + konteyner root. `CAP_SYS_ADMIN` olib tashlansa nsjail cgroup yozolmay **umuman ishga tushmasligi** mumkin → "oraliq qadam" ishlamaydi va vaqt yo'qoladi. Ustiga ADR-0004 isolate'ni "setuid root binary — qo'shimcha hujum yuzasi" deb **rad etgan**, holbuki nsjail bugun aynan shu holatda (`outside=0`) ishlaydi — hujjat o'z daliliga zid |
| **Qaytarilish** | A↔B ikki tomonlama (compose + nsjail args). Bir tomonlama qism — **M2 forward-only migratsiya intizomi**: deploy-oldi dump shart; judge stateless, lekin contest oynasida regressiya = **0 verdict** |
| **Egasi savoli** | "M2 uchun oraliq `cap_drop:[ALL]` yetarlimi, yoki `privileged`ni olib tashlash userns + seccomp bilan bir qadamda bajariladimi?" |
| **Defer narxi** | **Eng yuqori.** M2 boshlanmaydi; `privileged:true` qoladi va har qanday nsjail/kernel bug → host root → DB + butun testdata |

---

### B2. Content / Data o'rindiqi

#### B2.1 — ADR 0037: `Problem.readiness`

| Blok | Mazmun |
|---|---|
| **Framing** | Masalaning "ishonchli" holatini qanday belgilaymiz — va mavjud 1 222 ishonchsiz masalani public ro'yxatda qoldiramizmi yoki delist qilamizmi |
| **Variantlar** | ① status quo (faqat publish-time to'siq) · ② `readiness` enum + transition + graded gate · ③ alohida `ProblemReadiness` modeli · ④ AI-generatsiya |
| **Evidence kuchi** | **PROVEN:** `Problem.readiness` **yo'q**, faqat `is_public` (`problems/models.py:229`); `save()`/`clean()` da test gate **yo'q** (`:268-313`); publish-time gate **bor**, lekin faqat staff serializer'da va faqat **yangi** publish uchun (`staff_serializers.py:116-130`); mass-delist vositasi **allaqachon mavjud** (`unpublish_testless.py:38-69`, dry-run bilan); bypass bor (`publish_problems.py:29-33`, `--allow-testless`). **ASSUMED:** "1 222 / 870" — kod izohlarida (A7). "Remediation inson-bound" — **yarim to'g'ri**: delist **mexanik**, faqat **test yozish** inson-bound. **UNVERIFIED:** `print('3 2 1')` → AC (takrorlanadigan harness yo'q); **`tests/regression/` papkasi umuman mavjud emas** (A2); "≥5" chegarasi hech qanday taqsimotga tayanmaydi |
| **DISSENT** | Gate **allaqachon bor** va arxivni tozalash buyrug'i **allaqachon yozilgan**. Ya'ni `readiness` holat-mashinasi yangi forward-only migratsiya qo'shadi, lekin **inson-bound ishni bir kun ham qisqartirmaydi** — testlarni baribir odam yozadi → ② over-engineering bo'lishi mumkin. Yetishmayotgani holat-mashinasi emas, balki (a) `unpublish_testless` ni ishga tushirish va (b) 870 IE ni tuzatish. Ikkinchi qarshi argument: 1 222 ni delist qilish arxivni ~4 masalaga tushiradi — platforma bo'sh ko'rinadi; warning-banner ma'qul bo'lishi mumkin. **Uchinchi (kuchaytiruvchi):** verdict taxonomy allaqachon **shipped** (A3) — ya'ni 0037 ning "kontrakt ishi" deyarli qolmagan, qolgani **jarayon va data** |
| **Qaytarilish** | **Aralash.** Ustun qo'shish 2 tomonlama; lekin migratsiya forward-only → `readiness` drop bir tomonlama. Delist 2 tomonlama (`Problem.code` saqlanadi), lekin `update()` bilan qaytarish qo'lda |
| **Egasi savoli** | "`validated` uchun nechta yashirin test shart — va bu son nimaga asoslanadi? 1 222 public qoladimi (ogohlantirish bilan) yoki delist qilinadimi? Kim `validated` ni trigger qiladi — muallif, harness yoki staff?" |
| **Defer narxi** | M1 backfill yozilmaydi (default shu javoblarga bog'liq); `readiness` hamma joyda NULL; graded-contest gate o'qiydigan narsa topmaydi; `print('3 2 1')` → AC saqlanadi. **Eslatma (A3):** taxonomy qismi allaqachon bajarilgan — ochiq qolgani faqat *4 kodni nomlash* va *M10 qayta yorliqlash* |

#### B2.2 — ADR 0030: data origin

| Blok | Mazmun |
|---|---|
| **Framing** | Real foydalanuvchi/harakatni demo/imported/staff'dan qanday ajratamiz |
| **Variantlar** | ① `is_seeded` boolean · ② `User.origin` enum + `Attempt.origin` · ③ faqat event darajasi · ④ `neytron_` prefiks evristikasi |
| **Evidence kuchi** | **PROVEN:** `User.origin` ham, `is_seeded` ham **yo'q**; seeder mavjud (`seed_stress.py:26,84`, default **10 000** `:51`); o'chirish vositasi + cascade + `recount_problems` mavjud (`prune_test_users.py:40-65`); ADR-0023 buni ochiq follow-up deb yozgan (`0023-...:22,79`). **ASSUMED:** "10 001" — ADR-0023 da, lekin default **10 000**, izoh **10 068** (A8). Prefiks evristikasi `imported` ni `demo` dan ajrata oladi degan da'vo — dalil yo'q. **UNVERIFIED:** 384 569 attempt kimga tegishli; `neytron_*` bugun indekslanadimi |
| **DISSENT** | Platformada **0 real user** bor. Real/demo segmentatsiyasi hali **mavjud bo'lmagan** metrikalarni himoya qiladi, narxi esa `Attempt.origin` uchun **384 569 qatorli backfill** + yozish yo'lini o'zgartirish. North Star SQL allaqachon `is_seeded` ishlatadi — **bir bit darhol maqsadga yetadi**. `Attempt.origin` — hech bir dashboard hali o'qimaydigan so'rov uchun **erta optimizatsiya**. Bu kuchli argument; "o'rta-yuqori" ishonch shunga dosh berishi kerak |
| **Qaytarilish** | `User.origin` add→backfill→NOT NULL — forward-only. **Haqiqiy bir tomonlama eshik — 10 000 userni o'chirish**: cascade attempt/solved qatorlarini ham olib ketadi, backup'siz qaytarilmaydi. Tartib muhim: oldin o'chirilsa, backfill evristikasi tekshirilmaydi |
| **Egasi savoli** | "`neytron_*` o'chiriladimi — agar ha, origin backfill'dan **oldinmi yoki keyinmi**? Va `imported` alohida origin'mi, holbuki yagona evristika (email yo'q + prefiks) imported muallifni demo userdan ajrata olmaydi?" |
| **Defer narxi** | `check_metrics.py` yozilmaydi; North Star hisoblanmaydi; demo data "384 569 attempt" illyuziyasini saqlaydi |

---

### B3. Security o'rindiqi

#### B3.1 — ADR 0044: secrets management

| Blok | Mazmun |
|---|---|
| **Framing** | Qaysi sir menejeri (env fayl · Docker secrets · Vault), sirlar qaysi **tartibda** aylantiriladi, va `security.yml` git tarixini buzmasdan qanday qayta yoqiladi |
| **Variantlar** | ① `.env.public` + compose `${VAR:?}` + fail-fast · ② Docker secrets (swarm'siz) · ③ Vault |
| **Evidence kuchi** | **PROVEN:** hardcode literallar (`docker-compose.yml:39,69,92,106,136,151,199`; `DATABASE_URL: postgres://rankwant:dev@` `:87,101,131,146`); **hech bir overlay override qilmaydi** (public/ci/replicas/tools bo'ylab 0 moslik); **`.env.public` DB/MinIO/S3 kalitlarini umuman e'lon qilmaydi** (0 moslik) — ya'ni prod paroli haqiqatan `dev`; sir literallari git tarixida (`442cf1d`, `efbffa8`); `security.yml:32` = `if: false`; prod port'lari yopiq (`ports: !reset []`). **ASSUMED:** `POSTGRES_PASSWORD` mavjud `pgdata` uchun o'zgarmaydi (Docker xatti-harakati, repo'da o'lchanmagan). **UNVERIFIED:** jonli runtime env; Cloudflare ingress qoidasi |
| **DISSENT** | **"Hozir aylantirish" ni birinchi qilish — eng qimmat va eng ko'p SOXTA signal beradigan qadam**, chunki uch qadamning old sharti bajarilmagan: (a) compose env faqat `initdb` da qo'llanadi → yangi parol **hech qachon qo'llanmaydi**, jamoa esa "aylantirdik" deb o'ylaydi; (b) fail-fast wiring'dan oldin → **stack ko'tarilmaydi** (downtime); (c) Docker secrets `settings.py` qo'llamaguncha → **jim no-op**; (d) `SECRET_KEY` aylantirish hamma sessiya/PAT'ni o'ldiradi, va `check_deploy_window.py` **rotation'ni to'xtatmaydi** |
| **Qaytarilish** | Menejer tanlovi — **two-way**. Sir aylantirish (exposed qiymat) — amalda **ONE-WAY**. Git tarixini qayta yozish — **one-way va samarasiz** (public repoda fork/klon eski tarixni saqlaydi). Fail-fast — two-way |
| **Egasi savoli** | "Sir menejeri qaysi (env fayl · Docker secrets · Vault) va sirlarni qaysi tartibda aylantiramiz — wiring/fail-fast'dan **oldinmi yoki keyinmi**?" |
| **Defer narxi** | Prod `dev`/`devdevdev` da qolaveradi (public repo → parol **ma'lum**); `security.yml` o'chiq → yangi sizish ham sezilmaydi. **Zanjir:** API'da istalgan RCE/SSRF → env'da `DATABASE_URL=rankwant:dev` → **to'liq DB** (crack kerak emas). Judge `privileged` + `outside=0` → konteyner root; judge env'da `S3_SECRET: devdevdev` → **MinIO/S3 to'liq** (testdata, statement asset) |

---

### B4. Process / Governance o'rindiqi

#### B4.1 — Migration/deploy discipline: alohida Gate-0 yoki 0037 ichida?

| Blok | Mazmun |
|---|---|
| **Framing** | Forward-only + `check_deploy_window.py` + feature flag alohida **Gate-0** konstrukti sifatida e'lon qilinadimi, yoki mavjud mexanizmga singdiriladimi |
| **Evidence kuchi** | **PROVEN:** `check_deploy_window.py` mavjud (exit 0/1/2), chaqiriladi `deploy.yml:230` va `deploy.sh:290`; forward-only qoidasi hujjatlashtirilgan (`docs/06:139`). **PROVEN (yo'qligi):** feature-flag infratuzilmasi app kodida **topilmadi** (0 natija); blueprint §22.3 F62 ni "bugun yo'q" deb tasdiqlaydi |
| **DISSENT** | Gate-0 — **yangi mexanizm emas, mavjud mexanizmga yangi nom**. `check_deploy_window.py` PR-CI'da emas, faqat **deploy vaqtida** ishlaydi → u "gate" emas, "deploy-shart"; contest oynasidan tashqari hech narsani bloklamaydi. Uni "chiqish darvozasi" deb e'lon qilish himoyani **bor holidan kuchliroq ko'rsatadi**. Ustiga ro'yxat **to'liq emas**: `check_verdict_codes.py` allaqachon ishlaydi, ro'yxatda yo'q |
| **Qaytarilish** | **Ikki tomonlama** (Gate-0 ni 0037 ichiga ko'chirish = hujjat o'zgarishi). Bir tomonlama qism: feature flag **kodga** kirsa, olib tashlash migratsiya talab qiladi |
| **Egasi savoli** | "Migration/deploy discipline o'z artefaktiga ega bo'lishi shartmi, yoki mavjud `deploy.yml` sharti + hujjat qoidasi kifoyami?" |
| **Defer narxi** | WP0 egasiz qoladi; M1/M2/M10 boshqaruvsiz boshlanadi; feature flag yo'qligi M2/M3 dual-write ni xavfli qiladi. To'liq bloklanish emas — **nazorat yo'qolishi** |

#### B4.2 — Verdict-taxonomy qamrovi: 0037 ichida yoki `0037a`?

| Blok | Mazmun |
|---|---|
| **Framing** | RE split, o'lik kodlar va i18n yorliqlari 0037 ichiga kiradimi yoki alohida ADR talab qiladimi |
| **Evidence kuchi** | **PROVEN — da'vo qisqartirildi:** `RE_SIGNAL`/`RE_EXIT` **allaqachon mavjud** (`judging/verdicts.py:19-20`), `RE` esa `:16-18` da "LEGACY, 18 163 qator". i18n parity + o'lik-kod detektori **CI'da** (`check_verdict_codes.py`, 10 til), salbiy test bilan o'ralgan (`check_negative.py:5504,5517,6091`). **UNVERIFIED:** *aynan qaysi 4 kod* o'lik (F05 da nom yo'q) |
| **DISSENT** | Taxonomy ni 0037 ga "work package" sifatida qo'shish **takroriy ish**: RE split bajarilgan, parity gate ishlaydi, detektor mavjud. Qolgan haqiqiy ish — *18 163 qatorni qayta yorliqlash* (M10) va *qaysi 4 kod* ekanini nomlash — ikkalasi ham **ADR-kontrakt emas, data/qaror** ishi. Ya'ni "0037 ichida" varianti 0037 ni **sun'iy kattalashtiradi** |
| **Qaytarilish** | ① (0037 ichida) qimmat — taxonomy o'zgarishi ADR qayta ochilishini talab qiladi. ② (`0037a`) arzon. ③ (mavjud gate'ni kengaytirish) eng arzon |
| **Egasi savoli** | "Allaqachon kodda va CI'da mavjud verdict mexanizmini yangi ADR qamroviga kiritish kerakmi, yoki faqat *qaysi 4 kod* va *M10 tarixiy qayta yorliqlash* qarori kifoyami?" |
| **Defer narxi** | 0037 "yopildi" deb e'lon qilinadi-yu, M10 va 4 kod ochiq qoladi. Regressiya emas — **tarixiy izchillik** xavfi |

#### B4.3 — "A− guruhi" kontseptsiyasi asoslimi?

| Blok | Mazmun |
|---|---|
| **Framing** | "Phase 0 chiqish blokeri, lekin kod-start blokeri emas" toifasi haqiqiy konstruktmi yoki hal qilinmagan ziddiyatni yashiruvchi workaroundmi |
| **Evidence kuchi** | **PROVEN:** ziddiyat blueprint **ichida** — §24 (`:1857`) Phase 0 migratsiyasiga "M2 (boshlanishi)" kiradi, lekin §24 (`:1866,:1870`) "seccomp + `privileged` olib tashlash" va "`privileged:true` yo'q" ni **Phase 1** done-condition qiladi. **ASSUMED:** "A− qarori hozir, ijrosi Phase 1" — rahbarning talqini; blueprint'da bunday toifa **yo'q** |
| **DISSENT (asosiy ish)** | A− **ziddiyatni yopmaydi, qayta nomlaydi**. Amaliy natija A− yoki A bo'lishidan **farq qilmaydi**: ikkalasida ham M2 dan oldin qaror kerak. Ustiga A− **pretsedent** yaratadi — har qanday qaror "kod-start blokeri emas" deb A− ga surilib, toifa "keyinroq" ma'nosiga aylanadi. Uchinchisi: toifa **mezonsiz** — "chiqish blokeri" va "kod-start blokeri" chegarasi hech qayerda yozilmagan. **To'rtinchisi (Architecture qo'shimchasi):** A− egasidan **noto'g'ri savolga** tasdiq so'raydi — A− ni A yoki B deb belgilash 0028 ning o'zini bir qadam ham yaqinlashtirmaydi. Haqiqiy qaror — **M2 ning Phase 0 dagi "boshlanishi" nima bilan tugaydi**, ya'ni Phase 0 chiqishida `privileged` holati qanday bo'lishi kerak |
| **Qaytarilish** | **Ikki tomonlama** — sof hujjat/tasnif qarori, kodga tegmaydi |
| **Egasi savoli** | **Asosiy:** "M2 ning Phase 0 dagi *boshlanishi* nima bilan tugaydi — Phase 0 chiqishida `privileged` holati qanday bo'lishi kerak?" **Ikkinchi:** "A− alohida toifa sifatida mavjud bo'lishi shartmi, yoki 0028 ni A deb belgilab, ijrosini Phase 1 ga surish yetarlimi?" |
| **Defer narxi** | Triage rasmiylashmaydi, har jamoa o'z talqinida qoladi; va Phase 0 ning "ishonch" chiqish mezoni `privileged` bo'yicha **o'lchanmay** qoladi |

#### B4.4 — 3 triage tuzatishi asoslimi?

| Blok | Mazmun |
|---|---|
| **Framing** | 0042/0036 ni yuqoriga, 0028/0029 ni pastga, 0032 ni A dan chiqarish asoslimi — va bu blueprint'ga ishonchni pasaytiradimi |
| **Evidence kuchi** | **PROVEN (qayta tekshirildi, satr raqamlari bilan):** blueprint ichida ziddiyat — `:1741` (§21 tartib): 0042 → **Phase 1**, 0036 → **Phase 3**, 0028 → **Phase 0**; lekin `:1855` (§24 Phase 0 komponentlari): `check_architecture.py` va `check_ai_boundary.py` **Phase 0 ichida**; `:1857`: Phase 0 migratsiyasi = M1, M10, **M2 (boshlanishi)**, M5 (o'lchov); `:1859`: Phase 0 done-condition ①–⑥ — **`privileged` umuman tilga olinmagan**; `:1870`: Phase 1 done-condition ④ = "`privileged:true` **yo'q**". Ya'ni **0028 blueprint'da ikki faza orasida bo'lingan**. **ASSUMED:** "Phase 0 komponenti ⇒ ADR Phase 0 da bo'lishi shart" mantiqi — blueprint bunday qoidani yozmagan |
| **DISSENT** | Uchtasi ham **bir naqshdan**: §21 (ADR→faza) §24 (faza→komponent) bilan mos kelmaydi. Demak muammo "uchta xato" emas — **§21 tartib jadvali manba emas**, taxminiy taklif edi. Bu ishonchni **§21 ga** tushiradi, **§3–§20 o'lchangan faktlariga emas**. Xavf: agar shu naqsh boshqa joyda ham bo'lsa (done-condition ↔ migration ro'yxati), "Phase 0 to'plami" qaytadan tekshirilishi kerak. Ya'ni tuzatishlar **to'g'ri, lekin yolg'iz emas** |
| **Qaytarilish** | **Ikki tomonlama** — tasnif o'zgarishi. ③ (errata) bir tomonlama: blueprint qulflangan bo'lsa, qaytarish yangi ADR talab qiladi |
| **Egasi savoli** | **Birinchi:** "3 tuzatish qabul qilinadimi?" **Ikkinchi (Architecture qo'shimchasi):** "Phase 0 to'plami §21 dan olinadimi yoki §24 dan — va ikkisi ziddiyatlashsa **qaysi biri ustuvor**?" **Uchinchi:** "blueprint'ning §21 faza-tayinlash qatlami boshqa joyda ham tizimli tekshirilishi kerakmi?" |
| **Defer narxi** | Gate a'zoligi noaniq qoladi — "`Software Company` qachon boshlanadi?" savoliga javobsizlik. Tuzatishlar rad etilsa: Phase 0 done-condition ⑤ **o'z-o'zidan bajarilmaydigan** bo'lib qoladi |

---

### B5. Documentation o'rindiqi

#### B5.1 — Yangi ADR'lar (0028–0045) qaysi tilda?

| Blok | Mazmun |
|---|---|
| **Framing** | Mavjud ADR korpusi tili va repo'ning yozma qoidasi zid chiqqanda yangi ADR qaysi tilda yoziladi |
| **Variantlar** | ① o'zbek (lotin) · ② ingliz · ③ ikki tilli · ④ bo'lim nomlari inglizcha + nasr o'zbekcha |
| **Evidence kuchi** | **PROVEN (va A1 tuzatildi):** `docs/07-adr/` — **23 o'zbek + 4 ingliz** (0022, 0023, 0024, 0027). `CONTRIBUTING.md:82-96` (2026-09-17): "repo **aralash tilda qoladi**; yangi fayl **inglizcha**, mavjud fayl o'z tilida". `check_docs.py` da **til qoidasi YO'Q** — faqat yozuv aralashuvi (`CYRILLIC` regexp (kirill belgilar diapazoni), `:21`). Root `README.md` inglizcha; `CLAUDE.md` o'zbekcha. **UNVERIFIED:** "yangi fayl inglizcha" qoidasi ADR'ga tegishlimi (matn "README, docs/, CONTRIBUTING" deb sanaydi) |
| **DISSENT** | Oldingi hisobot "o'zbek" tomonga suyangan, lekin **o'lchov xato** edi: eng yangi 4 ADR **to'liq inglizcha**, va repo'ning o'z qoidasi yangi hujjatni **inglizcha** talab qiladi → "o'zbek" tanlovi qoidaga *rioya* emas, **qoidadan chetlanish** bo'lardi. O'zbekcha tanlovning yagona dalili — hujjat matni (§7 shabloni), **o'lchov emas** |
| **Qaytarilish** | **Asbob jihatidan ikki tomonlama** (gate tilda darvoza qo'ymaydi; havolalar fayl yo'li bo'yicha → saqlanadi). **Korpus jihatidan bir tomonlama**: "mavjud ADR tahrirlanmaydi" qoidasi tufayli 23 o'zbekcha ADR **qolib ketadi** |
| **Egasi savoli** | "0028–0045 qaysi tilda yozilsin — o'zbek, ingliz, ikki tilli, yoki bo'lim inglizcha + nasr o'zbekcha?" |
| **Defer narxi** | 18 ADR **umuman yozilmaydi** → 6 gate qarori faylga ega bo'lmaydi → indeks kengaytirilmaydi → `Software Company` boshlanmaydi. Bu — **1-raqamli 🔴 BLOCKING** band |

**Yon topilma:** `docs/07-adr/README.md` indeksi **0027 ni sanamaydi** — fayl bor, indeksda yo'q. Yangi 18 qator qo'shilishidan oldin indeks baribir qo'lda yangilanishi shart.

---

## C. Qarorlar orasidagi bog'lanish

```text
Mustaqil (parallel qaror qilinishi mumkin):
   0036 (AI boundary)  ·  0030 (origin)  ·  0044 (secrets)  ·  ADR tili

Ketma-ket SHART:
   0036  →  0042          (allowlist AI joylashuvini bilishi kerak)

Bloklaydigan (boshqa qarorlar kutadi):
   ADR tili   →  18 ADR ning hammasi
   Gate-0 qarori (B4.1)  →  WP0  →  barcha migration'lar
   B4.4 (triage)  →  gate a'zoligi  →  qaysi ADR Phase 0 da
```

**Eng arzon → eng qimmat tartib (siz uchun amaliy yo'l):**

| Bosqich | Qarorlar | Nega shu tartibda |
|---|---|---|
| 1 | **ADR tili** (B5.1) | Bir jumla; 18 ADR ni ochadi. Boshqa hech narsa kutmasdan hal qilinadi |
| 2 | **B4.4 triage + §21↔§24 ustuvorligi + B4.3 A−** | Gate a'zoligini qotiradi; qolgan barcha qarorlar shunga tayanadi. Ustuvorlik savoli javobsiz qolsa, "Phase 0 to'plami" har jamoa uchun boshqacha bo'ladi |
| 3 | **0044** (B3.1) | Eng katta joriy xavf; boshqa qarorlarga bog'liq emas |
| 4 | **0036 + 0042** (B1.1, B1.2) | Juftlik; 0036 → 0042 ketma-ket |
| 5 | **0037 + 0030** (B2.1, B2.2) | Kontent/data; eng ko'p sub-savol |
| 6 | **0028** (B1.3) | Eng qimmat; ijro Phase 1, lekin qaror M2 dan oldin |
| 7 | **B4.1 + B4.2** | Jarayon; mavjud mexanizmga tayanadi |

---

## D. Umumiy defer narxi

Barcha 11 qaror kechiktirilsa, bugungi holat **o'zgarmaydi**: `privileged: true` qoladi, prod paroli `dev` qoladi, `security.yml` o'chiq qoladi, `print('3 2 1')` AC beraveradi, metrikalar iflos qoladi, 18 ADR yozilmaydi.

**Kritik yo'l nuqtai nazaridan:** eng uzun zanjir — kontent remediatsiyasi (inson-bound), va u **qarorlardan qat'i nazar** boshlanishi mumkin bo'lgan yagona ish: `unpublish_testless.py` allaqachon mavjud. Ya'ni qarorlar kechiksa ham, **delist mexanizmini ishga tushirish** parallel bora oladi — lekin **qaysi masalani delist qilish** siyosati 0037 qaroriga bog'liq.

---

## E. Manba va o'rindiq hissasi

| O'rindiq | Ko'rib chiqqan qarorlar | Asosiy hissa |
|---|---|---|
| **Architecture** | 0036, 0042, 0028 | 0042 uchun eng ko'p o'lchangan raqamlar (417/244/137/67); 0028 da `FROM scratch` + `USER` yo'qligini topdi; ADR-0004 ning o'z daliliga zidligini ko'rsatdi |
| **Content/Data** | 0037, 0030 | `unpublish_testless.py` va publish-time gate **allaqachon mavjud**ligini topdi; "inson-bound" da'vosini yarim rad etdi; `tests/regression/` yo'qligini aniqladi |
| **Security** | 0044 | Production `dev` parolini **konfiguratsiya yo'li bo'yicha tasdiqladi**; rotation tartibining soxta-signal xavfini topdi; 7 qadamli blast radius zanjirini tuzdi |
| **Process/Governance** | Gate-0, taxonomy, A−, triage | **A− asossiz** ekanini ko'rsatdi; taxonomy da'vosini **qisqartirdi**; 3 tuzatishni **bitta tizimli naqsh** sifatida qayta talqin qildi |
| **Documentation** | ADR tili | **A1 ni rad etdi** (23 UZ / 4 EN); `CONTRIBUTING.md:90-91` qoidasini topdi; indeks 0027 ni sanamasligini aniqladi |

---

> Bu memo Independent Review Board tomonidan AI yordamida tayyorlandi. IRB **qaror qabul qilmaydi** — barcha yakuniy qarorlar egasi (Saidakbar) tomonidan qabul qilinadi.
