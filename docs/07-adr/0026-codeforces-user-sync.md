# ADR-0026: Codeforces foydalanuvchilarini sinxronlash — maydon nomlari va manba

**STATUS:** accepted (2026-09-19, HITL — 4 savol)
**Approved by:** Saidakbar aka on 2026-09-19, who chose the option "Avval ADR, keyin nom"
and, on the fields themselves, "RankWant platformamizda ham ana shunday maydonlarni
implement qilishimiz kerak. kelajakda kerak bo'ladi!"
**Research:**
- [1MLN-USERNAME-OLISH.md](../../../research/cf-rating/1MLN-USERNAME-OLISH.md);
- [API-USER-MAYDONLAR.md](../../../research/cf-rating/API-USER-MAYDONLAR.md);
- [SINXRONLASH-TIZIMI.md](../../../research/cf-rating/SINXRONLASH-TIZIMI.md)
**Ta'siri:**
- `apps/api/core/models.py` (`User`);
- `apps/api/core/migrations/0022_user_rating_tier_fields.py` (yangi);
- `apps/api/core/management/commands/sync_codeforces.py` (yangi);
- `apps/api/core/country_map.py` (yangi);
- `apps/api/core/account.py` (`CLEARED_FIELDS` / `KEPT_FIELDS`);
- `apps/api/core/handles.py` (`MAX_LENGTH` **o'zgarmaydi** — quyida);
- `tools/check_decisions.py` (`PARITY_USER_FIELDS` kengayadi).

## Muammo

Maqsad: Codeforces'dagi barcha 974,498 ta foydalanuvchi profili RankWant bazasida
«Codeforces bilan bir xil ko'rinishda va tarkibda» saqlansin. Buning uchun
Codeforces'ning 16 maydonidan 4 tasi `User` da **mos ustunga ega emas**:

| Codeforces maydoni | Turi | Nima uchun mos ustun yo'q |
| --- | --- | --- |
| `rank` | string | Unvon nomi (`"legendary grandmaster"`) — `rating_contest` esa butun son |
| `maxRank` | string | Yuqoridagining maksimumi |
| `friendOfCount` | integer | RankWant'da do'stlar tizimi yo'q |
| `titlePhoto` | string | Banner — `avatar_url` boshqa narsa |

Lekin bu yerda **haqiqiy muammo nomlashda**. Uchta ADR bir-biriga qarama-qarshi
turadi va yangi ADR ularni yarashtirishi kerak:

- **[ADR-0005](0005-content-strategy-own-content.md)** — kontent «to'liq mustaqil»;
  siz nazorat qilmaydigan uchinchi tomon differensiator bo'la olmaydi.
- **[ADR-0014](0014-codeforces-handle-seed.md)** (rejected, 2026-09-09) — aynan shu
  savol haqida. Sabablardan biri so'zma-so'z: *«`cp_uz_article_id` uchinchi tomon
  nomini schema darajasiga kiritardi»*.
- **[ADR-0024](0024-user-competitor-parity-fields.md)** (accepted, 2026-09-18) —
  «User model — fields for parity with **Codeforces**, Robocontest and KEP». User
  46 → 67 maydonga o'sdi. Nomlash **neytral** bo'ldi: `contribution`, `cf_contribution`
  emas.

Ya'ni loyihada allaqachon qabul qilingan naqsh bor: **raqobatchi bilan tenglik
uchun maydon qo'shiladi, lekin uning nomi schema'ga kirmaydi.** Savol shu — yangi
4 maydon ham shu naqshga bo'ysunadimi yoki `cf_*` istisno bo'ladimi.

## Variantlar

1. **`cf_*` prefiksi** (`cf_rank`, `cf_max_rank`, `cf_friend_of_count`,
   `cf_title_photo`). Manba darhol ko'rinadi, sync aniq. Lekin ADR-0014 ning
   «uchinchi tomon nomi schema'ga kirmaydi» degan taqiqiga to'g'ridan-to'g'ri tegadi
   va ADR-0024 ning neytral nom uslubini buzadi.
2. **Neytral nom** (`rank_title`, `max_rank_title`, `friend_count`,
   `title_photo_url`). ADR-0024 uslubi davom etadi, ADR-0005 saqlanadi. Manba
   ustun nomidan emas, **yozuvchi koddan** (`sync_codeforces.py`) va migration
   izohidan bilinadi.
3. **Alohida `cf_profile` jadval** (1:1). `User` ga tegmaydi — eng toza ajratish.
   Lekin ADR-0024 «A separate 1:1 profile table» variantini aynan shu muammo uchun
   rad etgan va leaderboard har so'rovda JOIN qiladi (o'lchanmagan sekinlashuv).

## Tanlov

**2-variant — neytral nom.** Egasi 2026-09-19 da oldin ADR yozishni tanladi
(«Avval ADR, keyin nom»), ya'ni nomlash alohida qaror sifatida qayd etiladi.

To'rtta ustun `User` ga qo'shiladi:

| Yangi ustun | Turi | Manba (Codeforces) | Nima uchun shu nom |
| --- | --- | --- | --- |
| `rank_title` | `CharField(40, blank=True)` | `rank` | «Unvon nomi» — qaysi platformadan kelgani muhim emas |
| `max_rank_title` | `CharField(40, blank=True)` | `maxRank` | Eng yuqori unvon; `max_rating_contest` bilan adashmaydi |
| `friend_count` | `IntegerField(default=0)` | `friendOfCount` | Neytral — kelajakda o'z do'stlar tizimimiz ham shu nom bilan yozadi |
| `title_photo_url` | `URLField(200, blank=True)` | `titlePhoto` | «Profil fon rasmi»; `avatar_url` (kichik doira) dan farqli |

Ular **P3 toifasida** — ya'ni ADR-0024 dagi `plan`, `postal_*`,
`coach_can_view_attempts` kabi **hozir ishlatilmaydigan, lekin kelajakda kerak
bo'ladigan** ustunlar. Egasi buni ochiq aytdi: *«kelajakda kerak bo'ladi!»*.
`tools/check_decisions.py` dagi `PARITY_USER_FIELDS` ro'yxatiga qo'shiladi, ya'ni
kelajakda ularni «o'lik maydon» deb o'chirish imkonsiz bo'ladi.

### Ustunlarning `User` da qolishi

Maydonlar alohida jadvalga chiqarilmaydi, `User` da qoladi — ADR-0017 va ADR-0024
shu yo'lni tanlagan, ya'ni profil maydonlari allaqachon `User` da yashaydi.

### `MAX_LENGTH` o'zgarmaydi

O'lchandi: 974,498 handle ichida 30 belgidan **uzuni bitta** —
`73c0d7da9b514872bb0fa9bc85e839e666a57399` (40 belgi, mashina hisobi). U
`--skip-long` bayrog'i bilan **chetlab o'tiladi**, ya'ni `handles.MAX_LENGTH = 30`
va `handles.validate()` **tegilmaydi**. Bitta avtomatik hisob uchun butun
platforma qoidasini kengaytirish noto'g'ri bo'lardi: foydalanuvchilar 40 belgili
taxallus olishni boshlardi va u URL/`@`eslatma/terminal chiqishida muammo bo'lardi
(`handles.py` dagi izoh kirill haqida aynan shunday mulohaza yuritadi).

### Nima yoziladi, nima yozilmaydi

| Codeforces maydoni | Taqdir | Sabab |
| --- | --- | --- |
| `handle` | `username` | Asosiy kalit (join key) |
| `firstName` + `lastName` | `display_name` | Ommaviy ism — ADR-0016 |
| `country` (nom) | `country` (ISO-2) | `COUNTRY_MAP` orqali, qamrov **100.00%** (o'lchandi: 259,862/259,862) |
| `city` | `city` | To'g'ridan-to'g'ri, 100 belgi bilan cheklanadi |
| `organization` | `school` | Ma'nosi mos |
| `rating` | `rating_contest` | Codeforces reytingi → kontest reytingi |
| `maxRating` | `max_rating_contest` | ADR-0024 ustuni |
| `contribution` | `contribution` | ADR-0024 ustuni allaqachon bor |
| `lastOnlineTimeSeconds` | `last_seen_at` | ADR-0024 ustuni |
| `registrationTimeSeconds` | `date_joined` | **Diqqat** — quyida |
| `avatar` | `avatar_url` | Ma'nosi mos |
| `rank` | `rank_title` | **yangi** |
| `maxRank` | `max_rank_title` | **yangi** |
| `friendOfCount` | `friend_count` | **yangi** |
| `titlePhoto` | `title_photo_url` | **yangi** |

## Sabab

- **Nomlash — bir xil huquqiy emas, arxitekturaviy savol.** ADR-0005 ning maqsadi
  «kontent bizniki bo'lsin» edi, «ustun nomida `cf` bo'lmasin» emas. Ammo
  uchinchi tomon nomini schema'ga yozish kelajakda uni **olib tashlashni
  qimmatlashtiradi** (har so'rov, har serializer, har migration unga bog'lanadi) —
  ADR-0014 aynan shu xavfdan qochgan. Neytral nom bu bog'liqlikni saqlaydi:
  Codeforces yo'qolsa, ustunlar neytral qoladi va o'z do'stlar tizimimiz ularni
  to'ldirib qo'ya oladi.
- **ADR-0024 allaqachon shu yo'lni ochgan.** `contribution` mavjud va u aynan
  Codeforces maydoni; nomi neytral. Yangi 4 maydon shu qatorning davomidir —
  yangi naqsh o'ylab topilmaydi.
- **1 ta uzun handle uchun qoida buzilmaydi.** O'lchov «1 / 974,498» dedi, ya'ni
  qoidani kengaytirish narxi (barcha foydalanuvchi uchun) foydasidan (bitta
  mashina hisobi) katta.
- **`--skip-long` — yo'qotish emas, hisobot.** Chetlangan handle hisobotda
  ko'rinadi, ya'ni ma'lumot jimgina yo'qolmaydi.

## Oqibatlar

- **Ijobiy:** 974,497 yozuv Codeforces modelining 16 maydoni bilan saqlanadi;
  schema uchinchi tomonga bog'lanmaydi; `friend_count` va `title_photo_url`
  kelajakdagi o'z funksiyalari uchun tayyor turadi.
- **Salbiy / cheklovlar:**
  - **`date_joined` ma'nosi almashadi.** Codeforces `registrationTimeSeconds` —
    *Codeforces'dagi* ro'yxat sanasi, RankWant'dagi emas. Ustunga yozilsa,
    «platformada qachondan beri» degan ma'no buziladi. Yechim: yoziladi, lekin
    hujjatlashtiriladi — bu **import sanasi** emas, **manbadagi ro'yxat sanasi**.
    Kelajakda haqiqiy `date_joined` kerak bo'lsa, `SyncReport` uni ajratib olishi
    mumkin.
  - **`country` va `email` yo'q yozuvlar.** `country` bo'sh (73.3%) → `""`;
    `email` Codeforces'da umuman yo'q → `""` + `set_unusable_password()`, ya'ni
    bu hisoblarga **hech kim kira olmaydi** (HITL tasdig'i, 2026-09-19).
  - **`username_skeleton` majburiy.** `bulk_create` `save()` ni chaqirmaydi, ya'ni
    `username_skeleton` **qo'lda to'ldirilishi shart** — aks holda
    `uniq_username_skeleton` cheklovi buziladi. O'lchandi: 974,498 handle
    casefold bo'yicha **0 to'qnashuv** beradi, ya'ni cheklov hech narsani rad
    etmaydi.
  - **Sinxron qatorlar «foydalanuvchi» emas.** Ular statistikada va leaderboardda
    ko'rinadi, lekin kira olmaydi va parol tiklay olmaydi. Bu ataylab.
- **Neytral:** ADR-0014 `rejected` holatida qoladi — u boshqa savolga javob bergan
  (avtomatik tavsiya urug'lantirish). Bu ADR uni bekor qilmaydi.

## Amalga oshirildi (2026-09-19)

| Qadam | Fayl | Holat |
| --- | --- | --- |
| Ustunlar | `core/models.py` (4 maydon) | ✅ |
| Migration | `core/migrations/0022_user_rating_tier_fields.py` | ✅ qo'llandi |
| Buyruq | `core/management/commands/sync_codeforces.py` | ✅ bajarildi |
| Davlat xaritasi | `core/country_map.py` (253 kod, 100%) | ✅ |
| Hisob tasnifi | `core/account.py` (`CLEARED`/`KEPT`) | ✅ |
| Qaror qo'riqchisi | `tools/check_decisions.py` | ✅ 29/29 |
| Docker | `apps/api/.dockerignore` (`.sync-cache/`) | ✅ |
| Hisobot | `research/cf-rating/SINXRONLASH-TIZIMI.md` | ✅ |

### API va frontend (2026-09-19, HITL — 3 savol)

Egasi maydonlarni **API'ga chiqarishni** tanladi («hammasini chiqarish»,
2026-09-19). Ammo bu yerda **ziddiyat** topildi va u ADR darajasida hal
qilindi: RankWant'ning **o'z unvon tizimi** bor (ADR-0018) va u
`rating_contest` dan **hisoblanadi** (`kvark`…`galaktika`, 9 daraja),
Codeforces'niki esa **saqlanadi** (`newbie`…`legendary grandmaster`,
10 daraja). Ikkisi bir xil `title` nomi bilan chiqsa frontend qaysi
birini chizishini bilmay qolardi va ism rangi buzilardi.

**Qaror (HITL):** alohida maydon. `title` — RankWant unvoni (o'zgarmaydi),
`cf_title` / `cf_max_title` — manbadagi daraja.

| Joy | O'zgarish |
| --- | --- |
| `core/serializers.py` `UserPublicSerializer` | `cf_title`, `cf_max_title`, `friend_count`, `title_photo_url` |
| `core/models.py` `PRIVACY_FIELDS` | `title_photo` (banner yashirilishi mumkin) |
| `apps/web/src/lib/api/users.ts` | `UserPublic` tipi 4 maydon bilan |
| `apps/web/src/lib/api/account.ts` | `PrivacyField` + `title_photo` |

O'lchandi (serializer, haqiqiy yozuv):
`tourist` → `cf_title='legendary grandmaster'`, `friend_count=90,843`;
`Petr` → `cf_title='international grandmaster'`,
`cf_max_title='legendary grandmaster'`. `title` ikkisida ham `None`
(reytingli musobaqa yo'q) — ya'ni ikki tizim **mustaqil** ishlaydi.

`tsc --noEmit` → **exit 0** (frontend shartnomasi mos).

**Sync AVTOMATLASHTIRILMADI** (HITL, 2026-09-19): qo'lda qoladi. 974k
yozuv yozadigan jadval xato bo'lsa jimgina har kuni takrorlanardi,
shuning uchun jadval qo'yish alohida qaror bo'lib qoladi.

### Maxfiylik qo'riqchisi — topilgan xato (2026-09-19)

Banner maydoni `PRIVACY_FIELDS` ga qo'shildi, lekin birinchi versiyada
qo'riqchi **ishlamadi**. Sabab: `get_title_photo_url()` yozilgan, ammo
`title_photo_url` maydoni `serializers.SerializerMethodField()` deb
**e'lon qilinmagan** edi. DRF bunday holatda metodni chaqirmaydi va model
atributini to'g'ridan-to'g'ri o'qiydi — natijada maxfiylik tekshiruvi
**o'lik kod** bo'lgan.

O'lchandi (tuzatishdan oldin, konteyner ichida):

```
hidden_fields = ['title_photo']
YASHIRGAN: 'https://userpic.codeforces.org/422/title/50a270ed4a722867.jpg'  ← sizib chiqdi
```

Tuzatish — maydonni e'lon qilish (DRF'da `get_*` yetarli emas):

```python
title_photo_url = serializers.SerializerMethodField()
```

Qayta o'lchandi (build + restart + jonli HTTP):

| Holat | `title_photo_url` | Natija |
| --- | --- | --- |
| `hidden_fields=['title_photo']` | `''` | ✅ yashirildi |
| `hidden_fields=['email']` | `https://userpic…` | ✅ qaytdi |

Qolgan uch maydon (`cf_title`, `cf_max_title`, `friend_count`) maxfiy
emas — ularda bunday tekshiruv yo'q va yashirilmaydi. Saboq kunlik logga
yozildi (DRF `SerializerMethodField` e'loni shart).

### Profil UI (2026-09-19)

Maydonlar API'da edi, lekin profil sahifasida chizilmasdi. Endi chiziladi.

**Muhim topilma:** `/profile/` sahifasi `UserPublicSerializer` ni
**ishlatmaydi** — u `profiles/public.py` dagi `build_profile()` ni
chaqiradi. Ya'ni serializer'ga maydon qo'shish profil sahifasiga
**ta'sir qilmaydi**; ikkalasiga alohida yozish kerak.

| Joy | O'zgarish |
| --- | --- |
| `profiles/public.py` `build_profile()` | 4 maydon qaytaradi; `title_photo_url` — `visible("title_photo")` bilan |
| `apps/web/src/lib/cf-tiers.ts` | **yangi** — 10 daraja, kanonik ranglar, `isCfTier()` |
| `apps/web/src/lib/api/users.ts` `PublicProfile` | 4 maydon tipi |
| `apps/web/src/components/profile/ProfileCard.tsx` | daraja nishoni + banner |
| `apps/web/src/i18n/locales/*.ts` | 14 yangi kalit × 10 til |

**Ikki tizim bir varaqda:** RankWant unvoni (`title`, 9 daraja,
`rw-rank-N` rang) — yuqorida, mavjud joyida. Manba darajasi (10 daraja,
Codeforces kanonik rangi) — pastda, alohida blok. Rang va nom **boshqa**,
shuning uchun chalkashmaydi.

**Daraja nomlari:** `cfTier.*` — 10 ta, har biri 10 tilda (100 qiymat).
Ranglar `lib/cf-tiers.ts` da inline, `rw-rank-*` ga **qo'shilmadi** —
ikki tizim ranglari aralashib ketmasligi kerak.

**Rad etilgan:** manba darajasini `rw-rank-N` ga solish — Codeforces
ranglari kanonik (masalan grandmaster — qizil), RankWant'niki esa
semantik; bir xil sinf ishlatilsa ikki xil ma'no bir xil rang olardi.

O'lchandi: `tsc --noEmit` → exit 0; `check_i18n.py` → 10 til × 1614 kalit;
`check_locales_parity.py` → mos; `check_hardcoded.py` → 294 fayl, toza.
Jonli HTTP: `/api/v1/users/tourist/profile/` → `cf_title='legendary
grandmaster'`, `friend_count=90843`, banner bor; `hidden_fields=
['title_photo']` da banner `''`, `cf_title` esa qoladi.

### 🔴 Manzil xatosi (2026-09-19)

`BASE_API` da `user.` prefiksi tushib qolgan edi:
`/api/ratedList` — prefikssiz manzil **HTTP 404** qaytaradi (HTML sahifa,
JSON emas). Xato **kesh ortida yashirindi**: buyruq avval
`.sync-cache/ratedList.json` ni o'qiydi (24 soat), shuning uchun sessiya
boshida tarmoqqa umuman chiqmadi. Konteyner qayta build qilingach kesh
yo'qoldi va xato ko'rindi.

| Manzil | Natija |
| --- | --- |
| `/api/ratedList?activeOnly=false&includeRetired=true` | **HTTP 404** |
| `/api/user.ratedList?activeOnly=false&includeRetired=true` | **HTTP 200**, 346,604,316 B |

Tuzatishdan keyin **kesh o'chirilib** qayta yurildi (34.8 s yuklash,
346,604,316 bayt — avvalgi o'lchov bilan aynan bir xil, 974,498 yozuv,
`create=0 update=0`).

**Himoya:** buyruq endi import paytida `BASE_API` ni tekshiradi va
`user.` prefiksi bo'lmasa `RuntimeError` bilan to'xtaydi — noto'g'ri
manzil jimgina 404 bo'lib qolmaydi.

**Saboq:** keshli yo'lni sinash "ishlayapti" degani emas. Tarmoqqa
chiqadigan kod keshni **o'chirib** sinaladi.

### Kesh — doimiy volume YO'Q (HITL, 2026-09-19)

Kesh (`.sync-cache/ratedList.json`) konteyner ichida, ya'ni har rebuild'da
yo'qoladi. Doimiy volume qo'yish taklif qilindi va **rad etildi**.

Sabab — o'lchangan nisbat:

| Yo'l | Yuklash | Jami |
| --- | --- | --- |
| Keshsiz (sovuq) | 34.4 s | 1 m 12 s |
| Keshli (issiq) | 0.0 s | 39 s |

Tejamkorlik — **33 sekund**, kesh hajmi esa **331 MB**. Sync qo'lda va
kamdan-kam yuriladi, shuning uchun bu nisbat doimiy disk va zaxira
murakkabligini oqlamaydi. Qaror kodda ham yozib qo'yildi
(`sync_codeforces.py`, `CACHE_DIR` izohi) — kelajakda volume qo'shmoqchi
bo'lgan odam avval shu ikki raqamni qayta o'lchashi kerak.

**Qayta yurgizish uchun:** `python manage.py sync_codeforces --fetch`
keshni qayta yaratadi (34 s).


**O'lchandi (`--apply --batch 5000`):**

| Ko'rsatkich | Qiymat |
| --- | --- |
| Yaratildi | **972,497** (2,000 avvaldan bor edi) |
| O'zgarmagan | **2,000** |
| Yozish vaqti | **165.7 s** (~5,870 yozuv/s) |
| Tahlil | 7.1 s |
| Bazadagi jami | **974,498** |
| Skelet to'qnashuv | **0** (974,498 unikal) |

**Takroriy yurish (idempotentlik):** `create=0 update=0 same=2,000` — dublikat yo'q.

**Topilgan tuzoqlar (kodda tuzatildi):**
- `bulk_create` `save()` ni chaqirmaydi → `username_skeleton` **qo'lda**
  to'ldiriladi, aks holda `uniq_username_skeleton` buzilardi.
- Build konteksti `./apps/api` → repo ildizidagi `tools/country_map.py`
  konteynerga **yetib bormaydi**. Xarita `core/country_map.py` ga ko'chirildi.
- Codeforces 2 yozuvda `rank` ga taxallus yozgan (`jiangly` → `"jiangly"`,
  `tourist` → `"tourist"`) → `TIERS` tekshiruvi qo'shildi, noto'g'ri qiymat
  tashlanadi va hisobotga tushadi.

## Ochiq savollar

1. **Sync qachon ishga tushadi?** Hozir qo'lda (`manage.py sync_codeforces`).
   Cron/Celery jadvali kerakmi — alohida qaror.
2. **`friend_count` haqiqiy ma'noga ega bo'lganda** — Codeforces qiymati o'z
   do'stlarimiz soni bilan almashadimi yoki ikkisi ajratiladimi?
3. **Uzun handle** (`73c0d7…`) kelajakda kerak bo'lsa, alohida
   `imported_handle` ustuni ochiladimi?
4. **Kesh joyi.** `.sync-cache/` konteyner ichida, ya'ni qayta build'da
   yo'qoladi. Doimiy volume kerakmi?
