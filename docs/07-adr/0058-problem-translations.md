# ADR 0058 — Masala tarjimalari

**STATUS:** accepted
**Sana:** 2026-11-11
**Tasdiqlagan:** Saidakbar (owner) — 2026-11-11 ([qaror yozuvi](../decisions/2026-11-11-content-and-archive.md): «tarjima modelini shu sessiyada, Abramyan importidan oldin quraman»)
**Ta'sir doirasi:** `problems` (yangi `ProblemTranslation`, `Problem.statement_locale` kengayadi, qidiruv), studiya va xodim paneli, masala sahifasi va arxiv ro'yxati
**Dalil:** Abramyan paketi (`D:\Linux\coding\abramyan-export\package\`) har masalani 4 tilda olib keladi: uz, ru, en, qq (qoraqalpoq — bizda `kaa`); `docs/05` diagrammasida `ProblemTranslation (Phase 2)` rejalashtirilgan, lekin ta'rifsiz

## 1. Muammo

`Problem` da shart bitta tilda: `title`, `statement`, `input_format`, `output_format`, `note`,
`editorial` va `statement_locale` (`max_length=2` — uch harfli `kaa` sig'maydi). Saytning 10 tili
bor, lekin masala o'qiydigan odam shartni faqat muallif tilida ko'radi; ruscha qidiruv
o'zbekcha nomli masalani topmaydi.

## 2. Qaror

1. **Asosiy matn `Problem` da qoladi** (muallif tili, `statement_locale`); boshqa tillar —
   `ProblemTranslation` qatorlari: `problem`, `locale` (sayt tillaridan biri), `title`,
   `statement`, `input_format`, `output_format`, `note`, `editorial`. Bitta masala × bitta til —
   bitta qator. Asosiy til uchun tarjima qatori saqlanmaydi.
2. **O'quvchi tili:** `?lang=` (sayt tili bo'lsa), aks holda so'rov tili. Shu tilda tarjima bo'lsa
   u, bo'lmasa asosiy matn. Bo'sh maydon (masalan, tarjimada `note` yo'q) asosiy matndan olinadi —
   kurslardagi kabi qisman tarjima blokni bo'sh qoldirmaydi. Javobda `locale` (ko'rsatilgan til) va
   `locales` (mavjud tillar).
3. **Tarjima nashr versiyasiga kirmaydi**: shart kabi «jonli» — tarjimani tuzatish yangi revision
   talab qilmaydi; nashr paketi (`snapshot_package`) mavjud tarjimalarni ham yozib oladi.
4. **Qidiruv** tarjima nomlarini ham topadi: nomlar `Problem.translated_titles` ga
   normallashtirilgan holda yig'iladi (qidiruv bog'langan jadvalga join qilmaydi — natija
   takrorlanmasin).
5. **Kim tahrirlaydi:** muallif o'z qoralamasi uchun (studiya, «Tarjimalar» tabi), xodim har qanday
   masala uchun (xodim paneli). Ommaviy masalani muallif tahrirlay olmaydi — shartdagi kabi.
6. `statement_locale` 3 belgigacha kengayadi (`kaa`).

## 3. Oqibatlar

- Abramyan importi 4 tilni bir yo'la yozadi (`qq` → `kaa`).
- Ro'yxatlarda (urinishlar, musobaqa jadvali va boshqalar) nom hozircha asosiy tilda; masala sahifasi,
  arxiv ro'yxati va qidiruv o'quvchi tilida.
- Yangi alifbo (O'RQ-1184) bu ADR'dan alohida: tarjima tillar orasida, alifbo esa o'zbek matnining
  yozilishi; o'giruvchi keyingi bosqichda har ikkala matnga qo'llanadi.
