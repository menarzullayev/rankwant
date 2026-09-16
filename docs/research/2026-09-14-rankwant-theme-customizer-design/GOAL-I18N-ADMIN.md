/goal — admin panelni i18n'ga ulash va ishni qotirish

Quyidagi matnni `/goal` ga bering.

---

## Vazifa

`GOAL-I18N.md` bo'yicha ish qisman bajarilgan. Hozirgi holat **o'lchandi**
(2026-09-14, kechqurun):

| Ko'rsatkich | Raqam |
|---|---|
| Lug'atlarda kalit | **1026 × 10 til** |
| `check_i18n.py` | **toza ✓** |
| `check_negative.py` | **16/16 ✓** |
| `tsc --noEmit` (quvursiz) | **exit 0** |
| `admin.label.*` kalitlar | **86** |
| Kodda `t(locale, "admin.label…")` | **0** |
| Admin panelda qattiq yozilgan `label: "…"` | **274 satr / 144 noyob** |
| Commit qilinmagan fayl | **60 (+3077 / −230)** |

Ya'ni: **86 kalit e'lon qilingan, lekin jonsiz** (`GOAL-I18N.md` 8-qoidasi
buzilgan), admin panel esa hozir to'liq o'zbekcha. Uchta ish bor:
**(A)** tarqoq ishni commit qilib qotirish, **(B)** admin panelni ulash,
**(C)** qolgan mayda fayllarni yopish.

**Birinchi qadam — o'qi, keyin boshla:**

- `rankwant-theme-customizer-design/GOAL-I18N.md` — **asosiy hujjat**,
  8 qoida va 13 band. Uning qoidalari bu promptda ham to'liq amal qiladi.
- `rankwant-theme-customizer-design/I18N-STACK-ANALYSIS.md` — 10 qaror.
  ⚠️ **Admin panel u yerda YO'Q** — bu yangi ish, qarorlardan kelib chiqadi.
- `rankwant/.workbuddy-ai/memory/2026-09-14.md` — bugungi ish jurnali.
  Oxiridagi «Audit sessiyasi» bo'limi aynan shu vazifaning kirish nuqtasi.
- `~/.workbuddy-ai/MEMORY.md` + `rankwant/.workbuddy-ai/memory/MEMORY.md`
  — til siyosati, doimiy qoidalar.
- `PLAYBOOK.md` — deploy, tekshirish tartibi, o'lchash usullari.

---

## Qat'iy qoidalar (buzilmaydi)

1. **O'lchov taxmindan ustun.** Har da'vo yonida dalil turi: `[o'lchandi]`
   (raqam bilan), `[kod]`, `[o'lchanmagan]`.
2. **Har yangi tekshiruvga SALBIY TEST shart.** Qiymatni ataylab buz,
   `exit 1` ni ko'r, tikla, `exit 0` ni ko'r.
3. **Klient tomonda yiqiladigan xato uchun brauzerda ochish shart.**
   `curl 200` + yashil CI **isbot emas**.
4. **Deploydan keyin `bash tools/check_deploy.sh`** — `0` bo'lsin.
5. **Til siyosati:** muloqot va hisobot — o'zbekcha; kod, buyruq, izoh,
   commit — inglizcha. Interfeys matni — **"siz"**.
6. **Commit — Conventional Commits**, inglizcha, sabab bilan.
7. **`docs/` — inglizcha.**
8. **Jonsiz e'lon qoldirma.** Ishlatilmaydigan kalit, chaqirilmaydigan
   tekshiruv, o'rnatilmagan hook — yo ishlat, yo olib tashla.
9. ⚠️ **QUVUR (pipeline) EXIT KODIGA ISHONMA.** `npx tsc | head; echo $?`
   **`head`ning** kodini beradi. Bu tuzoq shu ishda **ikki marta** xato
   hisobotga olib keldi. Har tekshiruvni **quvursiz** yuritib
   `REAL_EXIT=$?` ni o'qi.
10. ⚠️ **CRLF hushyorligi** (`core.autocrlf=true`). Lug'atlar CRLF.
    Skript bilan yozganda `write_text()` ~1000 qatorning qator oxirini
    jimgina o'zgartiradi. **Bayt bilan** o'qi va yoz. Anchor'ni **kalit
    nomiga** bog'la, qiymatga emas (qiymat har tilda boshqacha).

---

## Ish tartibi

Tartib **ataylab shunday** — (A) ni tugatmasdan (B) ga o'tilmaydi: tarqoq
holatda keyingi o'zgarishlarni ajratib bo'lmaydi.

### A. Tarqoq ishni qotir (commit)

`git status` — **60 fayl, +3077 / −230, hech narsa commit qilinmagan**.

1. `.tmp/` va `.workbuddy-ai/` ni `.gitignore` ga qo'sh. `.tmp/` — mahalliy
   skriptlar (skaner, kalit qo'shuvchilar); `.workbuddy-ai/` — agent xotirasi.
   Ikkalasi ham repoga tushmasin.
2. O'zgarishlarni **mantiqiy bo'laklarga** ajratib commit qil. Taklif:
   - `feat(i18n): add problem, filter, style, pager and admin label keys`
     — 10 ta lug'at fayli.
   - `feat(i18n): route ProblemFilters, styles, pager and admin nav through t()`
     — komponentlar.
   - `refactor(i18n): return accent errors as codes instead of prose`
     — `lib/theme/apply.ts` + `CustomizerContext` + `Customizer`.
   - `fix(i18n): stop hardcoding the Uzbek locale in date formatting`
     — `toLocaleString("uz")` → `date()/dateTime()` (4 joy).
   - `test(i18n): whitelist loanwords and fix kaa scoring label`
     — `check_i18n.py`.
   - `chore(i18n): localize admin route metadata`
     — 19 ta `generateMetadata`.
3. Har commit'dan keyin: `git status` toza bo'lsin, `tsc` **quvursiz**
   yuritilsin.

### B. Admin panelni i18n'ga ulash (asosiy ish)

**B0. Qarorni tasdiqla.** 274 satrni to'liq qilish kerakmi yoki faqat
ko'rinadigan jadval sarlavhalari + maydon nomlari? Standart: **to'liq**,
chunki yarim qilingan i18n keyingi o'quvchini chalg'itadi. Lekin hajm katta
— **birinchi navbatda so'ra**, javobni hisobotga yoz.

**B1. Yetishmayotgan 58 kalitni qo'sh.** Hozir 86 kalit bor, 144 noyob
qiymatning **58 tasi qoplamagan**:

```
"Sana" "Holat" "Nomi" "Tavsif" "Turi" "Slug" "Muallif" "Izoh" "Kod" "Narx"
"Muddat" "Mavzular" "Masalalar" "Savollar" "Qadamlar" "Bosqichlar" "Reytinglar"
"Til" "Versiya" "Repo" "Flag" "Ovoz" "Kim" "Sabab" "Natija" "Raqib" "Yakun"
"Manba" "Checker" "Testlar" "Nashr qilingan" "Standart" "Maxsus" "Kategoriya"
"Mukofot" "Qvant" "Xodim" "Bio" "Ism" "Login" "Email" "Modul" "Xabar"
"Maqola" "Muallif" "Tartib" "Egalari" "Asset" "Interactive" "Do'kon" "s/savol" …
```

⚠️ **Kalit nomi semantik inglizcha bo'lsin** (`admin.label.text.author`),
qiymatga qarab emas. Mavjud uslub: `admin.label.status.running`,
`admin.label.date.startAt`, `admin.label.text.problemExample`.

⚠️ **Tarjima — sifat ishi, mexanik emas.** Har bir kalit 10 tilda
**mazmunli** bo'lishi kerak. Qoraqalpoq (`kaa`) — o'zbekchaga eng yaqin,
lekin aynan nusxa emas; `check_i18n.py` bir xil qiymatni **xato** deb
hisoblaydi. Har bir holatda qaror: **ma'lumotni tuzat** yoki **whitelist**ga
qo'sh (faqat haqiqiy atoqli ot/o'zlashma bo'lsa, **sabab izohi bilan**).

**Kalit KERAK EMAS** bo'lgan qiymatlar: `"#"`, `"ACM/ICPC"`, `"IOI"`,
`"uz"`/`"ru"`/`"en"`, `"Asset"` — bular texnik kod yoki atoqli nom, qattiq
qolsin.

**B2. `CrudPage` ni tuzat.** ⚠️ **Bu markaziy nuqta.** Hozir u uch joyda
xom `label` chiqaradi:

- `{f.label}` — maydon nomi (286-qator)
- `{o.label}` — `<option>` matni (317-qator)
- `{c.label}` — jadval sarlavhasi (373-qator)

Uch yo'ldan birini tanla va **hujjatlashtir**:

- **(a)** `ColumnDef.label` ni majburiy `labelKey: MessageKey` ga aylantir
  va `CrudPage` da `t(locale, …)` chaqir. **Eng toza**, lekin 18 fayldagi
  274 satrni tahrirlashni talab qiladi.
- **(b)** `label?: string` ni saqlab, yoniga `labelKey?: MessageKey`
  qo'sh; `CrudPage` `labelKey ? t(locale, labelKey) : label` qilsin.
  **Kichikroq diff**, lekin vaqtincha ikki yo'l yonma-yon yashaydi.
- **(c)** `label` ni `MessageKey` deb qabul qil (TS majburiy), qiymatlarni
  kalit nomiga almashtir. Tahrir hajmi (a) bilan bir xil.

⚠️ `render` allaqachon `locale` ni uchinchi argument oladi (`ReportsAdmin`
shunga tayanadi) — bu naqshni saqlab qol.

**B3. 18 faylni ketma-ket o't.** `label:` → kalit. Hajm:

| Fayl | `label:` |
|---|---|
| `ProblemsAdmin.tsx` | 40 |
| `PostsAdmin.tsx` | 22 |
| `ArticlesAdmin.tsx` | 22 |
| `ContestsAdmin.tsx` | 20 |
| `UpdatesAdmin.tsx` | 19 |
| `HackathonsAdmin.tsx` | 19 |
| `PlatformRoadmapAdmin.tsx` | 17 |
| `ArenaAdmin.tsx` | 17 |
| `ShopAdmin.tsx` | 16 |
| `QuestsAdmin.tsx` | 13 |
| `TournamentsAdmin.tsx` | 12 |
| `RoadmapsAdmin.tsx` | 12 |
| `UsersAdmin.tsx` | 11 |
| `QuizzesAdmin.tsx` | 10 |
| `DuelsAdmin.tsx` | 10 |
| `ReportsAdmin.tsx` | 7 |
| `RoadmapCommentsAdmin.tsx` | 5 |
| `AnalyticsDashboard.tsx` | 2 (+ `title`, `object-value` matnlar) |

⚠️ `ShopAdmin.tsx` va `AnalyticsDashboard.tsx` da **`label` dan tashqari**
ham matn bor (`title=`, `name=`, `object-value` qiymatlar, JSX matn). Ular
ham skanerda chiqqan — birga yopilsin.

**B4. Qolgan 46 matn (`ShopAdmin` savol/izoh, `AnalyticsDashboard`
`EVENT_LABEL`, voronka sarlavhalari).** Skaner «admin BO'LMAGAN» ro'yxatida
48 satr ko'rsatdi. Ularni ham ko'rib chiq.

**B5. Tekshiruv — bu bandning mezoni.**

⚠️ **`check_i18n.py` bu xatoni TUTMAYDI.** U faqat **kod → lug'at**
yo'nalishini tekshiradi (kodda chaqirilgan kalit lug'atda bormi). U
**lug'at → kod** yo'nalishini ko'rmaydi, ya'ni ishlatilmayotgan kalitni
ham, qattiq yozilgan matnni ham o'tkazib yuboradi.

Shuning uchun **yangi tekshiruv yoz** — masalan
`tools/check_hardcoded.py`, `.tmp/scan_hardcoded.py` ning ishlaydigan
mantiqidan foydalanib:

- Admin komponentlarida `label: "…"` qolgan bo'lsa → `exit 1`.
- Qiymat «prose» bo'lsa (qisqa texnik kod/atoqli nom emas) → `exit 1`.
- Chiqarish o'zbekcha, xato matni aniq fayl:qator ko'rsatsin.

**Salbiy test shart:** ataylab bitta `label: "Sana"` qo'yib, `exit 1` ni
ko'r; kalitga almashtirib, `exit 0` ni ko'r.

### C. Maydа fayllarni yopish

Skaner kontent qatlamidan (498 + 39 = `country-names.ts` / `legal.ts`,
kechiktirilgan) tashqari **~101 satr** ko'rsatdi. Ular:

| Fayl | Satr |
|---|---|
| `app/rating/page.tsx` | 13 |
| `lib/external-links.ts` | 12 |
| `lib/prefs.ts` | 7 |
| `app/problems/[slug]/stats/page.tsx` | 5 |
| `lib/api.ts` | 5 |
| `lib/staff.ts`, `proxy.ts` | 3 + 3 |
| `app/manifest.ts`, `ui/Field.tsx`, `ui/Table.tsx`, `lib/analytics.ts` | 2 × 4 |
| `register/page.tsx`, `FavouriteToggle.tsx`, `ui/ListCard.tsx`, `ThemeContext.tsx`, `AppShell.tsx`, `lib/cosmetics.ts` | 1 × 6 |

⚠️ Ba'zilari **soxta musbat** bo'lishi mumkin (klass nomi, `"use client"`,
HTTP sarlavhasi, til kodi). Har birini ko'rib chiqib, sabab yoz —
«o'tkazib yuborildi» yoki «kalit qo'shildi».

### D. Brauzer dalili (majburiy)

`GOAL-I18N.md` 3-qoidasi. `curl 200` isbot emas.

- O'zbek **bo'lmagan** tilda admin panelni ochib, **jadval sarlavhasi va
  maydon nomi tarjima bo'lganini** tasdiqla.
- Kamida ikki til (masalan `ru` va `en`), ikki sahifa (`/admin/problems`,
  `/admin/shop`).
- Natijani hisobotga yoz: til, sahifa, nima ko'rindi.
- ⚠️ Bu mashinada `agent-browser` ishlamasa — **Linux tomonidan** yoki
  foydalanuvchidan skrinshot so'rab bajarilsin. `[o'lchanmagan]` deb
  qoldirish mumkin, lekin **yashirin qoldirilmaydi**.

---

## Tayyorlik mezoni

| Mezon | Talab |
|---|---|
| `.gitignore` | `.tmp/`, `.workbuddy-ai/` qo'shilgan |
| Commit | tarqoq ish bo'laklangan, har biri sababli |
| `admin.label.*` kalitlar | admin'ning **har** ko'rinadigan satri uchun |
| `t(locale, "admin.label…")` chaqiruvlari | **> 0** va 274 dan ancha ko'p |
| `label: "Sana"` ko'rinishidagi qoldiq | **0** (yoki sabab bilan ro'yxatda) |
| **Yangi** qattiq-matn tekshiruvi | yozilgan + **salbiy test bilan** |
| `python tools/check_i18n.py` | **exit 0** |
| `python tools/check_negative.py` | **16/16** (yoki yangi testlar bilan ko'proq) |
| `tsc --noEmit` (**quvursiz**) | **exit 0** |
| `npx eslint .` | **0 error** |
| Brauzer dalili (o'zbek bo'lmagan til) | ✅ yoki ochiq `[o'lchanmagan]` |
| `origin/main` ga push | ✅ (runner online bo'lsa) |

---

## To'xtash sharti

**To'xta va so'ra, agar:**

- B0 savoliga javob kelmasa (274 satrning ko'lami).
- Biror tarjima **noto'g'ri ma'no** berishi mumkin bo'lsa — o'zingcha
  yozma, so'ra. Ayniqsa `kaa`/`tg`/`ky` (men yaxshi bilmaydigan tillar).
- Yangi tekshiruv **soxta musbat** berib, yashil natijani yashirayotgan
  bo'lsa — buz, tut, keyin tuzat.
- Runner `offline` bo'lib CI ishlamasa — push qilib **kutib qolma**;
  mahalliy tekshiruvlar bilan davom et va holatni hisobotda yoz.

**Vaqt tugaganda:** bajarilganini commit qil, ochiq bandlarni hisobotda
aniq yoz. Yarim ishni «bajarildi» deb belgilama.

---

## Hisobot (o'zbekcha, 7 bo'lim)

1. **Nima qilindi** — commit'lar jadvali (hash + mazmun).
2. **Nima qoldi** — band bo'yicha, sabab bilan.
3. **O'zim qabul qilgan qarorlar** — promptda yo'q edi, lekin kerak bo'ldi.
   Ayniqsa: `CrudPage` uchun (a)/(b)/(c) tanlovi va **nima uchun**.
4. **O'lchangan raqamlar** — oldin/keyin (kalitlar soni, `label:` qoldiqlari,
   qancha fayl, commit soni).
5. **Jonli tekshiruv** — har amal va natijasi, `REAL_EXIT` bilan.
6. **Topilgan yangi nuqsonlar** — tuzatilgani va qolgani.
7. **Qayerda to'xtadim va nima uchun** — keyingi qadam.

⚠️ **«O'lchandi» va «taxmin» aralashmasin.** O'lchanmaganini
`[o'lchanmagan]` deb belgila.

---

## Oxirgi eslatma

Bu ishda **ikki marta yashil natija buzuq holatni o'tkazdi**:

1. `check_i18n.py` — u faqat kod→lug'at yo'nalishini ko'radi, shuning uchun
   **86 o'lik kalit**ni va **274 qattiq yozilgan satr**ni «toza» deb
   tasdiqlab turdi.
2. `npx tsc | head; echo $?` — quvur tufayli **`exit 0`** ko'rinib turdi,
   holbuki haqiqiy kod **`exit 1`** va **3 ta xato** bor edi.

Shuning uchun: **har yangi tekshiruvga salbiy test**, **har tekshiruv
quvursiz**, **har klient o'zgarishiga brauzer dalili**.
