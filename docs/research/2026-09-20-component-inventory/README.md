# Komponentlar umumlashtirish inventari — RankWant

> **Arxiv yozuvi.** Repoga 2026-10-04 da ko'chirildi; matn yozilgan kunidagi holatni aks ettiradi. Matndagi `cp/…-studio` papkalari repodan tashqarida.

Sana: 2026-09-20 · Manba: `rankwant/` repo, `main` = `5d29bd3`

Bu ro'yxat **taxmin emas** — har bir band kod ochib o'lchandi (`wc -l`, `grep -rn`,
`ls`). Raqamlar shu o'lchovdan olingan.

## Belgi

| Belgi | Ma'nosi |
|---|---|
| ✅ | Baza **allaqachon bor** — umumlashtirilgan, faqat chetlanishlar qoldi |
| 🔁 | **Takrorlanuvchi** — bir xil vazifani bajaruvchi bir nechta nusxa |
| 🔗 | **O'zaro bog'liq** — birgalikda qaror qilinishi kerak, alohida emas |
| ⚪ | Nomzod — hali umumlashtirilmagan, lekin naqsh yetilgan |

---

# A. Web — interfeys qatlami

Jami: `apps/web/src/components/` — **138** `.tsx` fayl, 9 papka
(`admin`, `auth`, `customizer`, `form`, `kit`, `overlay`, `profile`, `settings`, `ui`).

## A1. Forma maydonlari oilasi 🔁🔗

Eng zich takrorlanish shu yerda: **bitta mantiq 6 ta faylga yoyilgan**.

| Fayl | Qator | Eksport | Vazifa |
|---|---|---|---|
| `form/FormKit.tsx` | 388 | `FormCheck`, `FormBox`, `FormRadios`, `FormFile`, `FormDate` | Asosiy maydon turlari |
| `form/chrome.ts` | — | `FM_CTL`, `FM_INP`, `FM_LAB` | Umumiy CSS sinflar (haqiqiy baza) |
| `kit/FormExtras.tsx` | 161 | `FormIconSwitch`, `FormSeg3`, `FormStepper`, `FormTreeItem`, `InfoMark` | Qo'shimcha maydon turlari |
| `settings/kit.tsx` | 189 | `TextArea`, `Select`, `Check`, `Status`, `Hint`, `Loading`, `useAction`, `useLoad`, `describeError` | Sozlamalar uchun o'ramlar |
| `ui/Field.tsx` | 92 | `Field`, `FieldStatus` | Input + sana + holat |
| `ui/SelectField.tsx` | 68 | `SelectField`, `Checkbox` | Tanlash maydoni |

**Umumlashtirish asosi:**
- `FormCheck` / `Check` / `Checkbox` — **uch qatlam** bir xil ish uchun.
- `Select` (settings/kit) va `SelectField` (ui) — ikkalasi ham `Dropdown` ni o'raydi;
  `Select` **sof pass-through** (8 props hech narsa qo'shmasdan uzatiladi).
- `Field` (ui) ichida `FormDate` ga delegatsiya bor — ya'ni `ui` ↔ `form` allaqachon
  aralashgan.
- Barcha 5 fayl `FM_CTL`/`FM_INP`/`FM_LAB` ga tayanadi — baza bir, yuza uch xil.

## A2. Holat va yuklanish ko'rsatkichlari 🔁

| Komponent | Fayl | Qator | Vazifa |
|---|---|---|---|
| `Status` (to'liq) | `ui/Status.tsx` | 230 | Amal holati — rang + belgi + matn |
| `Status` (qisqa) | `settings/kit.tsx` | 29 | Xato / saqlandi satri |
| `Loading` (to'liq) | `ui/Loading.tsx` | 151 | Skelet, spinner, progress |
| `Loading` (qisqa) | `settings/kit.tsx` | 8 | «Yuklanmoqda…» satri |
| `EmptyState` | `ui/EmptyState.tsx` | 103 | Bo'sh ro'yxat holati |
| `Verdict` | `ui/Verdict.tsx` | 206 | Judge natijasi (Accepted/WA…) |
| `Badge`, `DifficultyBadge` | `ui/Badge.tsx` | 56 | Yorliq |

**Umumlashtirish asosi:** `Status` va `Loading` **ikki nusxada**. `Verdict` va `Status`
ataylab alohida (`lib/theme/status.ts` da sabab yozilgan) — lekin `settings/kit`
nusxalari tasodifiy, hujjatsiz.

## A3. Overlay va tasdiq 🔗

| Komponent | Fayl | Qator | Vazifa |
|---|---|---|---|
| `OverlayProvider`, `useOverlay`, `useConfirm`, `useToast`, `OverlayDialog` | `overlay/OverlayHost.tsx` | 806 | Modal, drawer, toast, kontekst menyu |
| `InlineConfirm` | `kit/ConfirmExtras.tsx` | 142 | Sahifa ichida tasdiq |
| `Dropdown` | `ui/Dropdown.tsx` | 244 | Qidiruvli tanlash |
| `CommandPalette` | `kit/CommandPalette.tsx` | 147 | Buyruq qidiruvi |

**Umumlashtirish asosi:** **ikki tasdiq mexanizmi** (`useConfirm` modal ↔ `InlineConfirm`
inline) — ataylabmi yoki tasodifmi, hujjatda javob yo'q. `Dropdown` va `CommandPalette`
ikkalasi ham ro'yxat + filtr + klaviatura navigatsiyasini takrorlaydi.

## A4. Jadval va sahifalash ⚪

| Komponent | Fayl | Qator | Vazifa |
|---|---|---|---|
| `Table`, `THead`, `TH`, `SortHeader`, `TBody`, `TR`, `TD`, `EmptyRow` | `ui/Table.tsx` | 178 | Jadval primitivlari |
| `Pager`, `PAGE_SIZES` | `ui/Pager.tsx` | 143 | Sahifalash |
| `ListCard` | `ui/ListCard.tsx` | — | Ro'yxat kartasi |

**Umumlashtirish asosi:** `Table` primitivlari bor, lekin **saralash + filtr + sahifalash**
birikmasi har bir ro'yxatda qayta yig'iladi. `Pager` va `Table` bog'lanmagan.

## A5. Tab va segment 🔁

| Komponent | Fayl | Qator | Vazifa |
|---|---|---|---|
| `TabBar`, `KitTab` | `kit/TabBar.tsx` | 99 | Tab panel |
| `Segmented` | `ui/Segmented.tsx` | 126 | Segment tugmalar |
| `ActivityTabs` | `profile/ActivityTabs.tsx` | 364 | Profil tablari |
| `ProfileNav`, `AuthTabs` | `profile/ProfileNav.tsx`, `auth/AuthTabs.tsx` | — | Tab navigatsiya |

**Umumlashtirish asosi:** to'rt xil tab/segment yuзаси, umumiy baza yo'q.

## A6. Nusxa olish oilasi 🔁

| Fayl | Qator | Eksport |
|---|---|---|
| `kit/CopyControl.tsx` | 157 | `CopyButton`, `CopyAllBar`, `CodeCopy`, `CopyCell`, `useCopiedFlash` |

**Umumlashtirish asosi:** bitta faylda **5 variant** — farq faqat joylashuv va
formatlashda. Bitta komponent + `variant` prop bilan qoplanadi.

## A7. Admin CRUD ✅

| Fayl | Qator | Izoh |
|---|---|---|
| `admin/CrudPage.tsx` | — | **Baza** — `CrudPage<T>`, `ColumnDef`, `FieldDef` |

**Qamrov o'lchandi:** `admin/` da 21 komponent; **18 tasi** `CrudPage` dan foydalanadi.
Faqat 3 tasi yo'q: `AdminNav` (navigatsiya), `AnalyticsDashboard` (boshqa turdagi ekran),
`EmailQuotaPanel` (maxsus panel).

**Xulosa:** bu qatlam **allaqachon umumlashtirilgan** — nomzod emas, namuna.

## A8. Admin marshrut sahifalari 🔁

**19 ta** `app/admin/*/page.tsx` — har biri **aynan 16 qator**, jami 337 qator.

Namuna (`admin/users/page.tsx`): `generateMetadata` + `t(locale, "admin.section.users")`
+ `<UsersAdmin />`. Farq — faqat komponent nomi va i18n kaliti.

**Umumlashtirish asosi:** 19 nusxa bir xil qolip. Bitta fabrika yoki registry bilan
16 × 19 = 304 qator ~20 qatorga tushadi.

## A9. Profil tablari ⚪🔗

| Komponent | Qator |
|---|---|
| `ActivityTabs` | 364 |
| `AboutTab` | 323 |
| `SolvedTab` | 199 |
| `AttemptsTab` | 150 |
| `ContestsTab` | 138 |
| `CertificatesTab` | 120 |

Jami **1294** qator. Qolganlari: `ProfileCard`, `ProfileNav`, `Medal`, `ProblemMap`,
`RatingChart`, `RatingHistoryTable`, `ActivityHeatmap`, `SolvedOverview`, `TopicStrength`,
`LanguageCards`, `FollowButton`, `PinButton`, `ShareButton`, `SectionHint`.

**Umumlashtirish asosi:** 6 tab bir xil skelet (yuklash → bo'sh holat → ro'yxat)
ustida qurilgan. `ActivityTabs` + `SolvedTab` + `AttemptsTab` — bir xil ro'yxat mantig'i.

## A10. Sozlamalar bo'limlari ⚪🔗

| Bo'lim | Qator |
|---|---|
| `InfoSection` | 505 |
| `ProfileSection` | 452 |
| `SecuritySection` | 339 |
| `SkillsSection` | 332 |
| `CareerSection` | 230 |
| `TeamsSection` | 210 |
| `AppearanceSection` | 176 |
| `SocialSection` | 134 |
| `NotificationsSection` | 134 |
| `SettingsShell` | 94 |

Jami **2606** qator.

**O'lchangan qamrov:** 9/9 bo'lim `Status` + `useAction` ni ishlatadi; 7/9 qo'shimcha
`useLoad` ni ishlatadi. Ya'ni `settings/kit.tsx` haqiqatan umumiy — lekin `Select`/`Check`
aliaslari (A1) va `Status`/`Loading` nusxalari (A2) shu yerda tugun bo'lib turadi.

## A11. Geo va kod ro'yxatlari 🔁

| Modul | Qator | Eksport |
|---|---|---|
| `lib/countries.ts` | 72 | `countryName`, `countryOptions` |
| `lib/country-names.ts` | 265 | `COUNTRY_NAMES` |
| `lib/regions.ts` | 271 | `regionName`, `REGION_CODES`, `districtOptions`, `districtName` |
| `lib/grades.ts` | 48 | `GRADE_CODES`, `GRADE_GROUPS`, `isGradeCode`, `gradeLabel` |
| `apps/api/core/country_map.py` | 261 | (backend nusxasi) |

UI: `ui/CountryFlag.tsx`, `ui/CountrySelect.tsx`, `ui/UzFallbackBadge.tsx`.

**Umumlashtirish asosi:** `COUNTRY_NAMES` / `REGION_CODES` / `GRADE_CODES` — **bir xil
«kod ro'yxati» naqshi uch marta**. Ustiga, davlat ma'lumoti **web va api da ikki nusxa**.

## A12. API klient ⚪🔗

| Fayl | Qator |
|---|---|
| `lib/api/users.ts` | 403 |
| `lib/api/problems.ts` | 312 |
| `lib/api/account.ts` | 260 |
| `lib/api/endpoints.ts` | 234 |
| `lib/api/platform.ts` | 207 |
| `lib/api/client.ts` | 189 |
| `lib/api/contests.ts` | 174 |
| `lib/api/content.ts` | 104 |
| `lib/api/hacks.ts` | 74 |
| `lib/api/qvant.ts` | 46 |
| `lib/api/index.ts` | 28 |

Jami **2031** qator. `client.ts` bazasi: `get`, `postJson`, `putJson`, `patchJson`,
`deleteJson`, `postForm`, `getJson`.

**Umumlashtirish asosi:** `contests.ts` da **takrorlanuvchi tiplar** —
`Standing` / `ArenaStanding` / `TournamentStanding` (3 ta) va
`ContestDetail` / `ArenaDetail` / `TournamentDetail` (3 ta). Bu B3 dagi event oilasining
oynasi.

## A13. Navigatsiya 🔗

`layout/nav.ts` (90) → `NAV_GROUPS`, `NAV` · `layout/nav-config.ts` (106) →
`NAV_SHAPES`, `NAV_MODES`, `SIDENAV_WIDTH`, `TOPNAV_HEIGHT`

UI: `AppHeader`, `AppTopNav`, `AppSidebar`, `AppShell`, `AppFooter`, `UserMenu`,
`LocaleSwitch`, `SearchBox`, `BrandMark`, `HeaderStatus`, `SkipLink`.

**Umumlashtirish asosi:** ikkala modul bir xil konfiguratsiya yuzasi; 4 xil nav shakli
bir xil elementlardan yig'iladi.

## A14. i18n ⚪

10 locale: `uz` (1821), `tg` (1778), `kk` (1778), `tr` (1777), `ru` (1777), `ky` (1777),
`kaa` (1777), `es` (1777), `zh` (1774), `en` (1774). Jami **17810** qator.

**Umumlashtirish asosi:** qatorlar soni deyarli bir xil → kalitlar to'plami bir xil.
Tarjima **ma'lumoti** umumlashtirilmaydi, lekin **kalit shartnomasi** bitta bazadan
(`en`) tip bilan chiqarilishi mumkin. `check_locales_parity.py` allaqachon bor.

---

# B. API — backend qatlami

Jami: `apps/api/` — **21** Django ilova.

## B1. Model bazalari ⚪

**O'lchandi:** repo bo'ylab `abstract = True` — **nol**. Ya'ni abstrakt model yo'q.

| Maydon | Nechta modelda | Shakl |
|---|---|---|
| `created_at` | **31** | `models.DateTimeField(auto_now_add=True)` |
| `created_at` (indexli) | **9** | `...auto_now_add=True, db_index=True)` |
| `updated_at` | **14** | `models.DateTimeField(auto_now=True)` |

**Umumlashtirish asosi:** 40 `created_at` + 14 `updated_at` = **54 e'lon**, ikkitasi
bir xil matn. Bu — eng katta yagona nomzod.

## B2. Staff qatlami ✅

| Fayl | Soni | Qator |
|---|---|---|
| `*/staff_views.py` | 13 | **1506** |
| `*/staff_serializers.py` | 11 | **1098** |
| `core/staff.py` → `StaffViewSet` | 1 | **40** |

**Qamrov o'lchandi:** 19 `class ...(StaffViewSet)` — 12/13 fayl bazadan meros oladi.
`@crud_summaries` — 13/13 faylda.

**Xulosa:** bu qatlam ham **allaqachon umumlashtirilgan**. Qolgan kichik takror:
`filter_backends = [DjangoFilterBackend, ...]` qayta e'loni (roadmap, updates) —
sabab kod izohida yozilgan.

## B3. Event oilasi ⚪🔗

| Model | Fayl | Qator | `TimeWindowMixin` |
|---|---|---|---|
| `Contest` | `contests/models.py` | 207 | ✅ |
| `ArenaRound` | `arena/models.py` | 128 | ✅ |
| `Tournament` | `tournaments/models.py` | 69 | ✅ |
| `Hackathon` | `hackathons/models.py` | 64 | ✅ |
| `Duel` | `duels/models.py` | 97 | ❌ (sabab hujjatda) |

Umumiy maydonlar (o'lchandi): `slug`, `title`, `description`, `start_at`, `end_at`,
`is_public`, `created_at`.

**Umumlashtirish asosi:**
- 4 model bir xil maydon to'plamini takrorlaydi.
- `core/mixins.py::TimeWindowMixin` — `is_running`/`is_finished` **to'rt nusxadan**
  chiqarilgan (hujjatda yozilgan). Ya'ni naqsh tan olingan, lekin **maydonlar** hali
  umumlashtirilmagan.
- **Chetlanish o'lchandi:** `contests.start_at` da `db_index` **yo'q**, `arena` /
  `tournaments` / `hackathons` da `db_index=True` bor. Nusxalar allaqachon bir-biridan
  uzoqlashgan.

Amal darajasida takror: `standings` (arena, contests, tournaments), `finalize`
(arena, contests, duels), `my_standing` (arena, contests).

## B4. Ishtirok oilasi ⚪🔗

| Model | Ilova |
|---|---|
| `ContestRegistration` | contests |
| `ArenaParticipation` | arena |
| `TournamentStanding` | tournaments |
| `HackathonSubmission` | hackathons |

**Umumlashtirish asosi:** to'rttasi ham «foydalanuvchi ↔ event» bog'lanishi + natija.
Maydonlari bir xil turdagi, nomlari har xil.

## B5. Masala-bog'lash oilasi ⚪🔗

| Model | Ilova |
|---|---|
| `ContestProblem` | contests |
| `ArenaQuestion` | arena |
| `DuelProblem` | duels |

**Umumlashtirish asosi:** «event ↔ masala» + tartib/ball. Uchta mustaqil nusxa.

## B6. Pochta oilasi ⚪🔗

| Modul | Qator |
|---|---|
| `core/email_text.py` | 418 |
| `core/mail_quota.py` | 236 |
| `core/mail_providers.py` | 226 |
| `core/mailer.py` | 130 |
| `core/emails.py` | 96 |

Jami **1106** qator, bitta papkada, 5 modul.

**Umumlashtirish asosi:** yuborish oqimi (matn → provayder → kvota → jurnal) 5 bo'lakka
bo'lingan; shartnoma bitta emas. `mail_providers.py` allaqachon ko'p-provayder
abstraksiyasi — qolganlari shunga moslashmagan.

## B7. `core/` ko'ndalang modullar 🔗

39 modul. Guruhlar:

| Guruh | Modullar |
|---|---|
| Auth/sessiya | `auth.py`, `sessions.py`, `oauth.py`, `recovery.py`, `verification.py`, `turnstile.py`, `groups.py` |
| Hisob | `account.py`, `account_views.py`, `usernames.py`, `handles.py`, `prefs.py` |
| Pochta | `email_text.py`, `emails.py`, `mailer.py`, `mail_providers.py`, `mail_quota.py` |
| Infratuzilma | `cache.py`, `http_retry.py`, `throttling.py`, `middleware.py`, `pagination.py`, `errors.py` |
| API yuzasi | `views.py`, `serializers.py`, `permissions.py`, `staff.py`, `staff_views.py`, `staff_serializers.py`, `mixins.py` |
| Domen | `models.py`, `user_stats.py`, `country_map.py`, `school_views.py`, `avatars.py` |
| Hujjat | `openapi_docs.py`, `i18n.py` |

**Umumlashtirish asosi:** guruhlar aniq ajralgan, lekin `account.py` ↔ `account_views.py`
va `usernames.py` ↔ `handles.py` juftliklari bir xil domenni ikki yuzadan ushlaydi.

---

# C. Vositalar va xizmatlar

## C1. `tools/check_*.py` ✅🔁

**22** skript, jami **13043** qator. Umumiy baza: `_console.py` — 20/22 faylda
ishlatiladi (`check_confusables.py` ishlatmaydi).

**Umumlashtirish asosi:** baza bor, lekin har bir skript `main()` + o'z exit-kod
mantig'ini qayta yozadi. `check_confusables.py` bazadan tashqarida — chetlanish.

## C2. Judge 🔗

| Xizmat | Qator | Holat |
|---|---|---|
| `judge-go` | **2848** | Faol (`docker-compose.yml`) |
| `judge-py` | **1127** | **Nofaol** — ADR-0004 bo'yicha saqlanadi |
| `bakeoff` | — | Taqqoslash protokoli |

**Umumlashtirish asosi:** `judge-py` — **ataylab** parallel nusxa, nomzod emas
(ADR-0004 da qaror yozilgan). `judge-go` ichida `checker.go` / `validator.go` /
`sandbox.go` / `interactive.go` — o'zaro bog'liq, birgalikda o'zgaradi.

## C3. Deploy va tekshiruv skriptlari 🔗

`tools/` da: `deploy.sh`, `deploy_scope.py`, `check_deploy.sh`, `check_deploy_gate.py`,
`check_deploy_window.py`, `rollback.sh`, `auto_deploy.sh`, `measure_deploy.sh`,
`backup.sh`, `restore_canonical.sh`.

**Umumlashtirish asosi:** deploy oqimi 10 skriptga bo'lingan, shartnoma
`check_deploy_gate.py` da. Boshqa tekshiruvlar (`check_i18n`, `check_contrast`, …) bilan
**umumiy «darvoza» interfeysi yo'q** — har biri o'z exit-kodini o'zi hal qiladi.

---

# D. Takrorlanuvchi va o'zaro bog'liq — alohida

## D1. Aniq takrorlar (bir xil vazifa, bir nechta nusxa) 🔁

| # | Takror | Nusxalar | Joy |
|---|---|---|---|
| 1 | **Checkbox** | 3 | `form/FormKit.tsx::FormCheck`, `settings/kit.tsx::Check`, `ui/SelectField.tsx::Checkbox` |
| 2 | **Select** | 2 | `settings/kit.tsx::Select` (sof alias), `ui/SelectField.tsx::SelectField` |
| 3 | **Status** | 2 | `ui/Status.tsx` (230 qator), `settings/kit.tsx` (29 qator) |
| 4 | **Loading** | 2 | `ui/Loading.tsx` (151 qator), `settings/kit.tsx` (8 qator) |
| 5 | **Tasdiq** | 2 | `overlay/OverlayHost.tsx::useConfirm` (modal), `kit/ConfirmExtras.tsx::InlineConfirm` |
| 6 | **Tab/Segment** | 4 | `kit/TabBar.tsx`, `ui/Segmented.tsx`, `profile/ProfileNav.tsx`, `auth/AuthTabs.tsx` |
| 7 | **Nusxa olish** | 5 | `kit/CopyControl.tsx` ichida: `CopyButton`, `CopyAllBar`, `CodeCopy`, `CopyCell`, `useCopiedFlash` |
| 8 | **Admin marshrut sahifasi** | 19 | `app/admin/*/page.tsx` — har biri 16 qator |
| 9 | **Kod ro'yxati** | 3 | `lib/country-names.ts`, `lib/regions.ts`, `lib/grades.ts` |
| 10 | **Davlat ma'lumoti** | 2 | `lib/countries.ts`+`country-names.ts` (web) ↔ `core/country_map.py` (api) |
| 11 | **Standing tipi** | 3 | `lib/api/contests.ts`: `Standing`, `ArenaStanding`, `TournamentStanding` |
| 12 | **Detail tipi** | 3 | `lib/api/contests.ts`: `ContestDetail`, `ArenaDetail`, `TournamentDetail` |
| 13 | **created_at / updated_at** | 54 | 21 ilova modeli bo'ylab |
| 14 | **Event modeli** | 4 (+1) | `Contest`, `ArenaRound`, `Tournament`, `Hackathon` (+`Duel`) |
| 15 | **Ishtirok modeli** | 4 | `ContestRegistration`, `ArenaParticipation`, `TournamentStanding`, `HackathonSubmission` |
| 16 | **Masala-bog'lash modeli** | 3 | `ContestProblem`, `ArenaQuestion`, `DuelProblem` |
| 17 | **Pochta moduli** | 5 | `core/` ichida 1106 qator |
| 18 | **Admin ro'yxat sahifasi** | 18 | `admin/*Admin.tsx` — barchasi `CrudPage` da (bu ✅, takror emas) |

## D2. O'zaro bog'liq — birgalikda qaror qilinishi kerak 🔗

| # | Guruh | Nega birga |
|---|---|---|
| 1 | `form/FormKit.tsx` + `kit/FormExtras.tsx` + `settings/kit.tsx` + `ui/Field.tsx` + `ui/SelectField.tsx` | Bitta `FM_*` bazasidan oziqlanadi; birini o'zgartirsang qolgani siljiydi |
| 2 | `ui/Status.tsx` + `settings/kit.tsx::Status` + `lib/theme/status.ts` | Holat tushunchasi 3 joyda |
| 3 | `ui/Loading.tsx` + `settings/kit.tsx::Loading` + `lib/theme/loading.ts` | Yuklanish tushunchasi 3 joyda |
| 4 | `overlay/OverlayHost.tsx` + `ui/Dropdown.tsx` + `kit/CommandPalette.tsx` + `kit/ConfirmExtras.tsx` | Bir xil qatlam: fokus tuzog'i, Escape, tashqariga bosish |
| 5 | `lib/theme/*` (15 fayl) + `components/ui/*` (19 fayl) | Token qatlami va komponent qatlami juftlikda yuradi |
| 6 | `core/mixins.py` + event modellari (B3) | `TimeWindowMixin` bor, maydonlar yo'q |
| 7 | `contests` + `arena` + `tournaments` + `duels` + `hackathons` | `standings` / `finalize` / `join` / `submit` amallari kesishadi |
| 8 | `core/email_text.py` + `emails.py` + `mailer.py` + `mail_providers.py` + `mail_quota.py` | Bitta oqim, 5 bo'lak |
| 9 | `lib/countries.ts` + `country-names.ts` + `regions.ts` + `grades.ts` + `ui/CountrySelect.tsx` + `ui/CountryFlag.tsx` | Bitta ma'lumot, ikki qatlam |
| 10 | `tools/check_*.py` (22) + `_console.py` | Bitta baza, 22 mustaqil exit-kod |

## D3. Chegaradan tashqarida — nomzod emas

| Nima | Nega |
|---|---|
| `services/judge-py` (1127 qator) | ADR-0004: ataylab saqlanadi, nofaol |
| `lib/theme/verdict.ts` ↔ `lib/theme/status.ts` | Ataylab alohida, sabab hujjatda yozilgan |
| `admin/AnalyticsDashboard.tsx`, `EmailQuotaPanel.tsx` | `CrudPage` dan tashqarida — ataylab |
| `cp/dropdown-studio`, `form-studio`, `overlay-studio`, `scrollbar-studio` | Eskiz taxtalari — «RankWant kodiga ulanmagan» (README) |
| `i18n/locales/*.ts` (10 fayl) | Tarjima ma'lumoti — umumlashtirilmaydi, faqat kalit shartnomasi |

---

# Eng zich nomzodlar — zichlik bo'yicha

| O'rin | Nomzod | Nusxa | Qator | Toifa |
|---|---|---|---|---|
| 1 | Model vaqt tamg'alari (B1) | 54 | — | API |
| 2 | Admin marshrut sahifalari (A8) | 19 | 337 | Web |
| 3 | Event modeli (B3) | 4 (+1) | 565 | API |
| 4 | Forma maydonlari (A1) | 6 fayl | 898 | Web |
| 5 | Pochta moduli (B6) | 5 | 1106 | API |
| 6 | Sozlamalar bo'limlari (A10) | 9 | 2606 | Web |
| 7 | Nusxa olish (A6) | 5 | 157 | Web |
| 8 | Ishtirok modeli (B4) | 4 | — | API |
| 9 | Kod ro'yxatlari (A11) | 3 (+1 api) | 656 | Web |
| 10 | Ishtirok / masala-bog'lash (B5) | 3 | — | API |

---

## Usul

O'lchov buyruqlari (takrorlanadigan):

```bash
ls -1 apps/web/src/components/*/            # komponent papkalari
find . -name "*.tsx" | wc -l                # fayl soni
wc -l <fayl>                                # hajm
grep -rn "CrudPage" --include=*.tsx .       # baza qamrovi
grep -c "created_at = models" */models.py   # maydon takrori
grep -rn "abstract = True" */models.py      # abstrakt baza bormi
grep -l "StaffViewSet" */staff_views.py     # staff baza qamrovi
```

Cheklov: bu **statik o'lchov** — ish vaqti xatti-harakati, ishlash tezligi va
xavfsizlik tekshirilmagan. Ro'yxat «umumlashtirish mumkin», «umumlashtirish kerak»
degani emas.
