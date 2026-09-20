# D48 — Kit-oila yozuvchisi

**Sana:** 2026-09-21  
**Qaror:** A — musobaqachi Interfeys  
**Tanlangan variant:** `contestant-interfeys`  
**CTO tavsiyasi:** B (rad etildi — egasi A ni tanladi)

## Qaror

Kit-oila preferencelarini
(`verdictStyle`, `statusStyle`, `loadingStyle`, `overlayStyle`,
`formStyle`, `iconPack`) **musobaqachi Appearance → Interfeys** yozadi.

`/admin/kit` playground va galereya — **namuna**. U `setAppearance`
chaqirmaydi va hisobga yozmaydi.

## Sabab

Egasi to‘liq nazoratni tanladi: har oila picker Interfeysda qoladi.
CUST-100 playgroundni labga olib chiqqan, lekin pickerlar panelda
qolgan — A shu holatni **chegaraga** aylantiradi, tasodifiy drift
emas.

## Trade-off

- Interfeys katalog bo‘lib qoladi: hozir **50** kit-oila chip
  (11 verdikt + 11 holat + 10 yuklanish + 4 oyna + 5 forma + 9 ikonka).
- Har yangi variant tab byudjetini oshiradi.
- D19 shablonlari bu kalitlarni hali solishtirmaydi — alohida
  Data/State qaror.

## Ta’sirlanadigan komponentlar

- `apps/web/src/components/customizer/AppearanceTab.tsx` (yozuvchi)
- `apps/web/src/components/customizer/chrome.ts` (`KIT_FAMILY_KEYS`)
- `apps/web/src/app/(site)/admin/kit/page.tsx` (namuna, yozmaydi)
- `apps/web/src/lib/theme/templates.ts` (`matchTemplate` — keyingi qaror)
- `AppearancePrefs` / PrefsSync / share URL / `rw:markup` cookie
  (sxema o‘zgarmaydi)

## Qilinmagan

Prefsni ikki hujjatga bo‘lish (D), xodimlar uchun uchinchi tab (C),
pickerlarni labga ko‘chirish (B) — rad etildi.
