# RankWant — Phase 0 Reconciliation Jadvali (authoritative)

**Sana**: 2026-09-29
**Muallif**: Software Company — Architect (Bob)
**Holat**: 🟢 Tayyor — **WP0 asosiy artefakti** (D2 natijasi)
**Til qoidasi**: Hujjat **o'zbek (lotin)** tilida. Texnik atama, fayl yo'li va kod **inglizcha** qoladi.
**Asos hujjatlar**:
- `deliverables/independent-review-board/acceptance-criteria-lock-2026-09-29.md` — muzlatilgan mezonlar (1-daraja)
- `deliverables/independent-review-board/owner-decision-closure-matrix-2026-09-29.md` — qarorlar + scope freeze (2-daraja)
- `deliverables/engineering-assurance/system-design-phase0-decision-closure-2026-09-29.md` — texnik asos (4-daraja)
- `deliverables/software-architecture/software-architecture-rankwant-2026-09-29.md` — blueprint (§21–26) (5-daraja)
- `deliverables/software-company/implementation-prd-phase0-2026-09-29.md` — PM PRD (incremental)

> ⚠️ **Bu jadval AUTHORITATIVE.** U Phase 0 uchun faza↔komponent va scope bo'yicha **yagona haqiqat manbasi**. Quyi darajali hujjat (jumladan butun blueprint) bu jadvalga **retrospektiv** bo'ysunadi. Ziddiyat chiqsa — quyidagi tie-break qoidasi qo'llanadi.

---

## 1. Maqsad va §24 tie-break qoidasi

**Maqsad:** Phase 0 ni boshlashdan oldin blueprint faza ro'yxatlari (§21 tartib taklifi, §24 Phase ro'yxatlari, §22 migratsiya rejasi) bilan owner qarorlari (D1–D11B, D8-F) va muzlatilgan mezonlar orasidagi **har bir nomuvofiqlikni** bir jadvalda yozib qo'yish, shunda Engineer qaysi manbaga tayanishini aniq biladi.

**Tie-break qoidasi (D2):**

1. Blueprint faza ro'yxati (§21 · §22 · §24) bilan **§24 done-condition** orasida zid chiqsa — **§24 done-condition ustun**.
2. §24 bilan **owner qarori** (D#) orasida zid chiqsa — **owner qarori ustun** (owner override, D3).
3. Owner qarori bilan **muzlatilgan mezon** (`acceptance-criteria-lock`) orasida zid chiqsa — **muzlatilgan mezon ustun** (1-daraja).
4. Har qanday holatda: past daraja hujjat yuqori daraja hujjatga bo'ysunadi (manba ierarxiyasi, PRD §2.1).

Ya'ni amaliy tartib: **mezon → owner qarori → §24 done-condition → blueprint faza ro'yxati**.

**Nomuvofiqlik turlari (taksonomiya):**
- `Faza nomuvofiqligi` — komponent blueprint'da bir fazada, qarorda boshqa fazada.
- `Guruh nomuvofiqligi` — A / B / C triage a'zoligi farqi.
- `Scope nomuvofiqligi` — ish hajmi kengroq yoki torroq belgilangan.
- `Artefakt nomuvofiqligi` — yangi artefakt talab qilinadi yoki bekor qilinadi.
- `Migratsiya nomuvofiqligi` — M# qaysi fazada bajarilishi farqi.
- `Komponent ↔ done-condition nomuvofiqligi` — komponent ro'yxatida bor, done-condition'da yo'q (yoki aksi).

---

## 2. Reconciliation jadvali

| # | Manba (fayl §bo'lim) | Blueprint da yozilgan | §24 done-condition / boshqa manba | Nomuvofiqlik turi | Yozilgan qaror | Qaror manbasi (D#) | Status |
|---|---|---|---|---|---|---|---|
| 1 | blueprint §21 Tartib taklifi · §24 Phase 0/1 | §21: ADR 0028 Phase 0 (Trust); §24 Phase 0 migration `M2 (boshlanishi)`; §24 Phase 1 done-condition ④ `privileged:true` yo'q | §24 Phase 0 komponentlar ro'yxatida judge privilege **yo'q** (ichki zid); D3: M2 **to'liq** Phase 0 da | Faza nomuvofiqligi (ichki) | `M2` **to'liq Phase 0 da** (WP7); `0028` → **A**; judge **host ajratish** (0029 · M6) Phase 1 da qoladi | D3 · D10 | Yopilgan |
| 2 | blueprint §21 Tartib taklifi | `0029` → **Phase 0 (Trust)** | D4 triage: `0029` → **B** guruhi (Phase 1) | Faza nomuvofiqligi | `0029` B guruhi; WP0–WP7 dan **tashqarida** (Phase 1) | D4 | Yopilgan |
| 3 | blueprint §21 Tartib taklifi | `0032` → **Phase 0 (Trust)** | D4 triage: `0032` **≠ A**; Phase 0 da faqat **o'lchov** (kod emas); qarori Phase 4 | Guruh + scope nomuvofiqligi | `0032` A emas; Phase 0 da faqat o'lchov; **kod yozilmaydi** | D4 | Yopilgan |
| 4 | blueprint §21 Tartib taklifi | `0042` → **Phase 1 (Production)**; `0036` → **Phase 3 (AI)** | D4 triage: `0042`↑ va `0036`↑ → **Phase 0 (A)**; ikkalasi Phase 0 done-condition ⑤ | Faza nomuvofiqligi (yuqoriga) | `0036` → **WP5**; `0042` → **WP6**; ketma-ket shart `0036 → 0042` | D4 · D6 · D7 | Yopilgan |
| 5 | blueprint §24 Phase 0 komponentlar | "verdict taksonomiyasi (RE split, o'lik kodlar, i18n)" — to'liq hajmda Phase 0 komponenti | D11B: **faqat qolgan ish** — 4 kod nomlash + M10; `RE_SIGNAL`/`RE_EXIT` split va i18n parity allaqachon **shipped** | Scope nomuvofiqligi | Faqat qolgan ish; shipped qism **qayta yozilmaydi** | D11B | Yopilgan |
| 6 | blueprint §22.3 Migratsiya tamoyillari | tamoyil 3: "Feature flag (F62 — bugun **yo'q** → Phase 0 da kerak)"; assurance §9.2 · §9.3 `Gate-0` ni **yangi artefakt** sifatida taklif qiladi | D11A: **Mavjud tekshiruv + siyosat** — `check_deploy_window.py` majburiy; **yangi artefakt yo'q** | Artefakt nomuvofiqligi | Yangi artefakt yo'q; feature flag **kiritilmaydi**; mavjud gate + siyosat | D11A | Yopilgan |
| 7 | assurance §3.2 · §9.3 | **A−** guruhi kiritilgan (Phase 0 chiqish blokeri, ADR 0028 uchun) | D3: **A− toifasi ishlatilmaydi**; `0028` → **A** | Guruh nomuvofiqligi | `A−` **bekor**; `0028` A guruhiga; ijro Phase 0 da | D3 | Yopilgan |
| 8 | blueprint §21 Tartib taklifi · §24 Phase 2 | §21: `0030` → **Phase 0 (Trust)**; LEKIN §24 Phase 2 migration = `M3, M4` (data origin) | D9: `M3` **Phase 0** (WP3); `User.origin` (Attempt'siz) | Faza + migratsiya nomuvofiqligi (ichki) | `M3` **Phase 0** (WP3); `0030` → A | D9 | Yopilgan |
| 9 | blueprint §24 Phase 0 migration | `M5 (o'lchov)` Phase 0 migration ro'yxatida | Scope freeze WP0–WP7: `M5` **ish birligi emas** — faqat o'lchov (PRD ilova) | Migratsiya + scope nomuvofiqligi | `M5` **o'lchov**, ish birligi emas (out-of-scope) | D4 · D11A | Yopilgan |
| 10 | blueprint §24 Phase 0 | Komponentlar ro'yxatida `check_metrics.py` **bor** | §24 Phase 0 done-condition ⑤ faqat `check_architecture` / `check_ai_boundary` ni sanaydi (`check_metrics` yo'q) | Komponent ↔ done-condition nomuvofiqligi | `check_metrics.py` Phase 0 da qoladi (**WP3**); mezoni WP3 AC orqali yopiladi | D9 | Yopilgan |

**Izoh:** 1–10-qatorlar blueprint (§21–26), assurance (§3.2 · §9.2 · §9.3) va owner qarorlari o'rtasidagi barcha topilgan faza↔komponent, guruh, scope, artefakt va migratsiya nomuvofiqliklarini qamraydi. Har bir qator manba satriga havola qiladi (taxmin emas).

---

## 3. Xulosa

| Ko'rsatkich | Qiymat |
|---|---|
| Topilgan nomuvofiqlik | **10** |
| Yopilgan (qaror qabul qilingan) | **10** |
| Ochiq qolgan | **0** |
| Yangi owner decision talab qiladigan | **0** |

- Barcha nomuvofiqliklar **mavjud owner qarorlari** (D3 · D4 · D6 · D7 · D9 · D10 · D11A · D11B) bilan yopilgan. Yangi qaror talab qilinmadi.
- Blueprint **retrospektiv** reconciliation'ga bo'ysunadi: §21 tartib taklifi va §24 Phase ro'yxatlari endi bu jadval orqali o'qiladi.
- **Ichki ziddiyatlar** (1, 8-qator) — blueprint'ning o'zida: §21 bilan §24 bir xil komponentni turli fazaga qo'ygan. Ular §24 tie-break + owner qarori bilan yopildi.
- **Decision conflict** (muzlatilgan qarorlar o'rtasida): **YO'Q**. Faqat blueprint/assurance ↔ qaror nomuvofiqliklari topildi — hammasi ierarxiya qoidasi bilan yopilgan.

---

## 4. Migration / deploy siyosati (D11A — WP0 mezon ④)

> Bu bo'lim WP0 ning ④ mezonini qoplaydi. **Yangi artefakt yaratilmaydi** — mavjud tekshiruv + siyosat qayd etiladi.

**Qoida 1 — Forward-only migratsiya.** Sxema **oldinga** yoziladi: `add → backfill → switch → drop`, har qadam **alohida deploy**. Migratsiya **rollback qilinmaydi**; tuzatish ham oldinga migratsiya bilan (`git revert` sxemaga qo'llanmaydi). Manba: blueprint §22.3, `docs/06-architecture`.

**Qoida 2 — `check_deploy_window.py` majburiy.** Har deploy oldidan `tools/check_deploy_window.py` ishga tushadi (chaqiruv: `.github/workflows/deploy.yml:230`). Uch chiqish kodi: `0` — oyna bo'sh; `1` — faol contest/arena bor (deploy **taqiqlanadi**); `2` — aniqlanmadi. `2` holati «0 ta» deb o'qilmaydi (yolg'on yashil taqiqlanadi).

**Dalil — majburiylik (T-WP0.2, o'lchandi 2026-09-29).** Qadam `.github/workflows/deploy.yml:218` («Live contest window»); chaqiruv `:230` da, `set +e`/`set -e` orasida (chiqish kodi ushlanadi); faol contest'da `:233-236` `exit 1` beradi. Qadamda `continue-on-error: true` **yo'q**, uni o'tkazib yuboruvchi `if:` sharti **yo'q**, `|| true` **yo'q** — ya'ni chaqiruv **majburiy**. `2` holatida qadam ogohlantiradi va davom etadi — bu **ataylab** (`:224-227` izohi): «API javob bermadi» ni «to'xta» deb o'qish aynan sayt yiqilganda tuzatish deploy'ini bloklardi. Siyosat `2` ni «0 ta» deb **o'qimaydi** — faqat qo'lda tasdiqlashga chaqiradi.

**Qoida 3 — Deploy-oldi dump talabi.** Har M# (M1 · M2 · M3 · M10) deploy'idan oldin **DB dump** olinadi (majburiy). `tools/backup.sh` da `restore_test()` va `verify_dump` mavjud — dump shu bilan tasdiqlanadi.

**Qoida 4 — Contest oynasi himoyasi.** Faol contest/arena oynasida deploy **yo'q** (10-operations, qoida №1). `check_deploy_window.py` shu qoidani majburlaydi.

**Qoida 5 — Har o'zgarish ADR bilan.** Har arxitektura o'zgarishi ADR yozuvi bilan bog'lanadi (AP10). `check_decisions.py` darvozasi buni tekshiradi.

**Qoida 6 — Feature flag kiritilmaydi.** Blueprint §22.3 tamoyil 3 da «Phase 0 da kerak» deyilgan `F62` feature flag **D11A bilan bekor qilindi** — Phase 0 da yangi artefakt yaratilmaydi (6-qator, 2-ustun).

**Qoida 7 — `check_deploy.sh` va `GIT_SHA` yorlig'i.** Deploydan keyin ishlab turgan konteynerlar manba kodga mos ekanini `tools/check_deploy.sh` tekshiradi: Python konteynerlari uchun fayl hash'i, Next.js uchun esa `org.rankwant.git-sha` build yorlig'i solishtiriladi (`tools/check_deploy.sh:57` · `:361` · `:498` — `git rev-parse HEAD`). `tools/deploy.sh:84` `GIT_SHA="$(git rev-parse HEAD …)"` ni o'qiydi va `export` qiladi (compose `${GIT_SHA:-unknown}` ni oladi); `tools/deploy.sh:302` va `:413` `check_deploy.sh` ni chaqiradi. Chiqish: `0` — mos; `1` — eskirgan konteyner bor.

**Qoida 8 — Rollback qaydi (forward-only).** Kod qaytarish: kerakli commitni deploy worktree'da checkout qilib `bash tools/deploy.sh --yes` (qayta quriladi). Sxema **avtomatik qaytarilmaydi** — deploy oldidagi `pg-deploy-*.sql.gz` dump **qo'lda** tiklanadi (`tools/rollback.sh:9-11`). `2026-09-20` dan SHA obraz teglari **saqlanmaydi** (`tools/rollback.sh:2-7`), shuning uchun `rollback.sh <sha>` ataylab rad etadi. Deploy oynasida `IMAGE_TAG: ${{ github.sha }}` (`.github/workflows/deploy.yml:62-63`) rollback uchun asos sifatida qayd etiladi.

---

## 5. Ochilgan yangi fakt (qayd)

Owner **production launch: 2027 Q1** deb belgiladi (`owner-decision-closure-matrix` §9). Bu blueprint'da yo'q bo'lgan yagona sanali ma'lumot. Oqibati: D7 da «velocity yo'q → sanalar fabrikatsiya» asosi bilan rad etilgan **sanali remediation** varianti qayta ko'rilishi mumkin. Bu — **ochiq belgi**; D7 **qayta ochilmagan** va bu jadvalga nomuvofiqlik qatori sifatida kirmaydi.

---

**STATUS:** WP0 Reconciliation Jadvali — **yopilgan** (authoritative). 10 nomuvofiqlik topildi, 10 yopilgan, 0 ochiq. D11A migration/deploy siyosati §4 da qayd etildi.

**WP0 mezonlari — dalil (4/4 yopilgan):**

① **Reconciliation jadvali artefakti mavjud** — shu fayl (§2, 10 nomuvofiqlik qatori); `tools/check_docs.py` yashil.
② **Har faza↔komponent nomuvofiqligi uchun qaror qayd etilgan** — §2 jadvalining «Yozilgan qaror» va «Qaror manbasi (D#)» ustunlari; 10/10 «Yopilgan».
③ **§24 tie-break qoidasi yozilgan** — §1 «Tie-break qoidasi (D2)» (mezon → owner qarori → §24 → blueprint, 4 qadam).
④ **Migration/deploy siyosati hujjatlashtirilgan** — §4 (8 qoida: forward-only · deploy-oldi dump · contest oynasi · `check_deploy_window.py` majburiy · ADR · feature flag yo'q · `check_deploy.sh` GIT_SHA · rollback qaydi). Majburiylik dalili: `.github/workflows/deploy.yml:218` · `:230` · `:233-236` (`continue-on-error`/`if`/`|| true` yo'q).
