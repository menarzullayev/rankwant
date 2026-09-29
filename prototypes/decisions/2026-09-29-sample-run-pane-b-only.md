# DECISION: Namunada sinash — faqat pane-b konsol

**Sana:** 2026-09-29  
**Kontekst:** `statement-builder.html` P0 prototip — ikki parallel sinash yo‘li chalkashlik qilardi.

## Qaror

**Tanlangan variant:** Faqat o‘ng panel (kod ostidagi sample-console) — chap namunalar jadvalidan ▶ va inline natija olib tashlanadi.

## Sabab

- Bitta foydalanuvchi harakati (Namunada sinash + combobox + IO) muharrir kontekstida;
- Statement jadvali faqat Kirish/Chiqish ko‘rsatish va nusxalash uchun qoladi;
- Keyingi `apps/web` portida `SubmitPanel` bilan kelishuv osonlashadi.

## Trade-off

- Jadvaldan tez bitta namunani ishga tushirish yo‘qoladi (o‘rniga konsolda namuna tanlanadi).
- RC uslubidagi qator ▶ prototipda endi ko‘rsatilmaydi.

## Ta’sir

- `prototypes/statement-builder.html` — jadval, CSS, JS, P0 jurnal.
