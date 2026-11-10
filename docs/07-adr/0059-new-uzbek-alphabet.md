# ADR 0059 — Yangi o'zbek alifbosi: o'giruvchi va qidiruv

**STATUS:** accepted (1-bosqich: o'giruvchi va qidiruv; 2-bosqich: interfeys va tanlov; 3-bosqich: kontent; 4-bosqich: xat, Telegram, sertifikatlar; 5-bosqich: ro'yxatlar, nomlar, tilsiz matn)
**Sana:** 2026-11-11
**Tasdiqlagan:** Saidakbar (owner) — 2026-11-11 ([qaror yozuvi](../decisions/2026-11-11-new-alphabet.md): 4 savol)
**Ta'sir doirasi:** `packages/shared` (`alphabet.ts`), `apps/api/core` (`alphabet.py`, `search.py`), web qidiruvi; migratsiyalar `core.0036`, `problems.0038`
**Dalil:** [O'RQ-1184, 21.10.2026](https://lex.uz/docs/8548754) — 931-XII-son qonunning 1-moddasi yangi tahrirda (lex.uz'da o'qildi, 2026-11-11); Robocontest interfeysi yangi alifboda, shartlari eskisida (o'lchandi)

## 1. Muammo

Qonun 22.04.2027 dan kuchga kiradi: 28 harf va tutuq belgisi `ʼ`; `oʻ → ö`, `gʻ → ğ`,
`sh → ş`, `ch → ç`; `ng` endi alohida harf birikmasi emas. Eski shakldagi hujjatlar amal
qiladi. Platformadagi butun o'zbekcha matn — interfeys lug'ati, masala shartlari, kurslar,
maqolalar — eski alifboda. Egasi qarori: hozirdan standart — yangi alifbo, eskisi ham
ishlayveradi, qidiruvda ikkalasi bir.

## 2. Qaror (1-bosqich)

1. **Bitta o'giruvchi, ikki nusxa**: `packages/shared/src/alphabet.ts` (brauzer va Next server)
   va `apps/api/core/alphabet.py` (API, pochta, Telegram). Ikkalasi bitta holatlar faylidan
   tekshiriladi — `packages/shared/src/alphabet-cases.json` — ya'ni biri o'zgarsa, ikkinchisining
   testi yiqiladi.
2. **O'girilmaydi**: kod (blok va qator ichida), LaTeX, URL, e-pochta, fayl nomi, o'rinbosar
   (`{count}`), HTML teg, havola manzili va o'zbekcha bo'lmagan so'z — tuya yozuvi (`GitHub`),
   qisqa qisqartma (`SSH`), o'zbek tilida yo'q harf (`w`, `ch` dan tashqari `c`, `oo`, `th`,
   `ü`…) yoki ro'yxatdagi so'z (`Shift`, `Bash`). O'giruvchi — boshlang'ich nuqta: xatosini xodim
   qo'lda tuzatadi.
3. **Eski → yangi**: `oʻ`/`o'`/`` o` `` → `ö`, `gʻ` → `ğ`, `sh` → `ş`, `ch` → `ç`, so'z ichidagi
   boshqa apostrof → `ʼ`; eski `s'h` (Is'hoq) → `sh`. **Yangi → eski**: `ö` → `oʻ` (U+02BB),
   `ğ` → `gʻ`, `ş` → `sh`, `ç` → `ch`; `ʼ` qoladi.
4. **Qidiruv ikki alifboni bir deb oladi**: katlama `ö ğ ş ç` ni `o g sh ch` ga tushiradi va `ʼ`
   ni ham tashlaydi — «Özbekiston», «O'zbekiston» va «Ozbekiston» bitta so'rov. Python
   (`normalize_search`), SQL (`Fold`, `FOLD_PG`) va brauzer (`foldText`) bitta jadvaldan.
   `core_user` trigram indekslari yangi ifoda bilan qayta quriladi (avval yangisi, keyin eskisi
   o'chadi — qidiruv indekssiz qolmaydi); saqlangan `title_search`, `name_search`,
   `translated_titles` qayta katlanadi.
5. **Matn yozilganidek saqlanadi** — o'girish ko'rsatishda bo'ladi (keyingi bosqichlar).

## 3. 2-bosqich: interfeys lug'ati va alifbo tanlovi

1. **Lug'at manbasi o'zgarmaydi** — `uz.ts` eski alifboda yoziladi; server uni modul yuklanganda
   bir marta o'giradi: `uz` = yangi alifbo (standart), eski matn — `uz` ning `old` varianti.
2. **Tanlov — `rw_alphabet=old` cookie'si**, faqat o'zbekchaga ta'sir qiladi. Til tanlagichda ikki
   qator: «Özbekça — yangi alifbo» va «O'zbekcha — eski alifbo». Alifbo almashganda lug'at fayli ham
   almashadi (`/i18n/uz.js` va `/i18n/uz-old.js`), shuning uchun sahifa to'liq qayta yuklanadi.
3. **Server alifboni so'rovdan biladi.** Lug'at reyestri jarayonda bitta, `t()` sinxron, server esa
   ikkala alifbodagi so'rovlarni bir vaqtda chizadi. `instrumentation.ts` har so'rovni
   `AsyncLocalStorage` kontekstida yurgizadi (cookie'dan), `t()` esa o'zbekcha uchun shu kontekstdagi
   variantni o'qiydi — server komponentlari ham, mijoz komponentlarining SSR'i ham. O'lchandi:
   `next start` da bir URL ikki cookie bilan ikki alifboda chizildi; 36 ta parallel aralash so'rovda
   aralashish 0.
4. **Kesh**: eski alifbo cookie'si bilan sahifa mehmon keshiga tushmaydi (`home-cache.ts`); eski
   alifbo tanlanganda `rw_locale=uz` ham yoziladi — Cloudflare qoidasi `rw_locale` bor so'rovni
   allaqachon chetlab o'tadi, ya'ni chekka qoidasini o'zgartirish shart emas.
5. **E2E** eski alifboga qadalgan (mavjud matnlar va vizual baseline'lar eski alifboda); standart
   yangi alifbo `alphabet.spec.ts` da tekshiriladi.

## 4. 3-bosqich: kontent o'quvchi alifbosida

1. **Kontent saqlanganidek qoladi** — o'girish ko'rsatishda: `inReaderAlphabet(matn, til)`.
   Faqat matnning O'Z tili o'zbekcha bo'lsa o'giriladi (`til` — kontentniki, interfeysniki emas):
   inglizcha shartdagi `should`, `check` buzilmasin. O'quvchi alifbosi — tanlov cookie'si, interfeys
   tilidan qat'i nazar (ruscha interfeysdagi o'quvchi o'zbekcha shartni ham tanlagan alifbosida ko'radi).
2. **Server va brauzer bir xil o'qiydi**: serverda so'rov konteksti (2-bosqichdagi `AsyncLocalStorage`),
   brauzerda `document.cookie` — ikkalasi bitta cookie, ya'ni gidratsiya bir xil matnni ko'radi.
3. **Qamrov**: `Markdown` komponenti `lang` oladi (kod, formula va havola o'girilmaydi). Masala sahifasi
   (sarlavha, shart, kirish/chiqish, izoh, tahlil, sahifa nomi), arxiv ro'yxati va o'xshash masalalar
   (API endi har qator uchun `locale` beradi), maqola, blog posti, kurs va dars sahifalari.
4. **Daraja nomlari** API'ning o'zbekcha `level_label` matni o'rniga lug'atdan (`level.*`) — tarjima ham,
   alifbo ham shu bilan hal bo'ladi.

## 5. 4-bosqich: xat, Telegram va sertifikatlar

1. **Tanlov hisobda ham** — `User.alphabet` (`new` | `old`, standart `new`). Xat, Telegram va
   sertifikat brauzersiz yoziladi, ya'ni cookie'ni ko'rmaydi. Til tanlagich ikkalasini yozadi (hisobni
   sahifa qayta yuklanishidan OLDIN — aks holda so'rov bekor bo'lardi). Kirganda: cookie hisobdan farq
   qilsa — bu qurilmadagi tanlov, hisob yangilanadi; cookie yo'q, hisob `old` — boshqa qurilmadagi
   tanlov, bu qurilmaga urug' bo'ladi (sahifa bir marta qayta yuklanadi).
2. **Xat**: shablon matni (`email_text`) hisob alifbosida, faqat o'zbekcha xatda.
3. **Bildirishnoma katalogi** (sayt zaxira matni, Telegram, xat): shablon PARAMETRLARDAN OLDIN o'giriladi
   — musobaqa yoki post nomi yozilganidek. Odam yozgan erkin matn (hakam izohi) o'girilmaydi.
4. **Sertifikatlar** (kurs va musobaqa): o'zbekcha yorliqlar egasining alifbosida; ism va musobaqa nomi
   yozilganidek; kurs nomi kurs tili o'zbekcha bo'lsa o'giriladi.

## 6. 5-bosqich: ro'yxatlar, nomlar va tilsiz matn

1. **Ro'yxatlar**: blog, maqolalar, yo'nalishlar, kurslar katalogi, bosh sahifadagi postlar, arxiv yon
   paneli (yo'nalish va masala nomlari) — har qator o'z tili bilan.
2. **Mavzu va ko'nikma nomlari**: `@/i18n/messages` dagi nom yordamchilari (`topicName`, `localName` va
   `*Info`) o'zbekcha ustundagi nomni o'quvchi alifbosiga o'tkazadi — barcha chaqiruv joylari bir yo'la.
3. **Lug'atsiz yozilgan o'zbekcha matn** lug'atga ko'chdi: arxivdagi «/ N masala», «Oxirgi urinish», yo'nalish
   kartasidagi «N qadam» — ular endi tarjima ham qilinadi.
4. **Til maydoni yo'q matn** (turnir va xakaton tavsifi, platforma yo'l xaritasi, o'zgarishlar jurnali
   asl matni) — platformaning o'zi o'zbek tilida yozadi, shuning uchun o'zbekcha deb olinadi. O'lchandi
   (2026-11-11): jonli turnir va xakaton tavsiflari o'zbekcha. **Nomlar** (musobaqa, turnir, xakaton,
   arena) yozilganidek qoladi — sertifikatdagi kabi.

5. **Kurs dasturi, dars navigatsiyasi, sinfdagi kurs**: API endi har qator (modul, bo'lim, dars, qo'shni dars,
   sinfga berilgan kurs) uchun matn tilini (`locale`) beradi.
6. **Test va arena savollari**: modelda til maydoni yo'q (`docs/05` qulflangan — maydon qo'shilmadi), ya'ni
   platforma matni sifatida o'zbekcha deb olinadi. Javob variantlari ko'pincha kod bo'lgani uchun o'giruvchi
   endi ortidan `(` keladigan so'zni funksiya chaqiruvi deb o'girmaydi (`chr(65)`, `push(x)`).

## 7. Oqibatlar

- Turkcha matndagi `ş`, `ç`, `ö`, `ğ` ham katlanadi (`çeviri` ↔ `cheviri`) — ikkala tomon bir xil
  katlangani uchun moslik buzilmaydi.
- Migratsiya `core.0036` ishlab chiqarishda ikki indeksni `CONCURRENTLY` quradi (avvalgisi
  ~6 s har biri, ~974k qator).
