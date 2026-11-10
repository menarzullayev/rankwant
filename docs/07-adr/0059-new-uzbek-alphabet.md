# ADR 0059 — Yangi o'zbek alifbosi: o'giruvchi va qidiruv

**STATUS:** accepted (1-bosqich: o'giruvchi va qidiruv; interfeys, kontent, pochta va Telegram — keyingi bosqichlar)
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

## 3. Keyingi bosqichlar

- Interfeys lug'ati yangi alifboda va eski alifbo tanlovi. Lug'at reyestri tilga bog'langan
  (`t(locale, key)`, `/i18n/<til>.js`), serverda bir vaqtda ikkala alifbodagi so'rovlar bo'ladi —
  tanlov so'rov kontekstidan o'qilishi kerak; mehmon CDN keshi (`/`, `/problems`, login) tanlov
  cookie'sini ham chetlab o'tishi shart.
- Kontent (masala shartlari, kurslar, maqolalar, yangiliklar) o'quvchi tanlagan alifboda.
- Pochta, Telegram, sertifikatlar.

## 4. Oqibatlar

- Turkcha matndagi `ş`, `ç`, `ö`, `ğ` ham katlanadi (`çeviri` ↔ `cheviri`) — ikkala tomon bir xil
  katlangani uchun moslik buzilmaydi.
- Migratsiya `core.0036` ishlab chiqarishda ikki indeksni `CONCURRENTLY` quradi (avvalgisi
  ~6 s har biri, ~974k qator).
