# D49 — Shablon kit identiteti

**Sana:** 2026-09-21  
**Qaror:** B — shablon kengayadi  
**Tanlangan variant:** `widen-templates`  
**CTO tavsiyasi:** B (qabul qilindi)

## Qaror

Jamoa shabloni (D19) endi kit oilalarini ham o‘z identitetiga oladi:
`verdictStyle`, `statusStyle`, `loadingStyle`, `overlayStyle`,
`formStyle`, `iconPack`.

Sakkizta built-in shablon **bitta** `TEMPLATE_KIT_DEFAULTS` blokini
ulashadi (auto / auto / spinner / qogoz / maydon / lucide).

- `templateAppearance` apply paytida shu 6 kalitni tiklaydi.
- `matchTemplate` ularni solishtiradi (`undefined` = default).
- A11y hali ham shablonning qismi emas.

## Sabab

D48 kit oilalarini musobaqachi mahsulot sozlamasi qildi. D19-tor match
Klassik + doira verdiktni hali ham «Klassik» deb ko‘rsatardi — yolg‘on
identitet. Apply tiklamasa, keyingi share/cookie qarori ham shu yolg‘onga
yopishardi.

## Trade-off

- Shablon bosish shaxsiy chrome ni defaultga qaytaradi. Undo (D24) bor.
- nav / card / pattern / size / width hali ham matchga kirmaydi (APP-8) —
  alohida qaror.
- Saqlangan shaxsiy shablonlar to‘liq `appearance` blob — o‘zgarmaydi.

## Ta’sirlanadigan komponentlar

- `apps/web/src/lib/theme/templates.ts`
- `CustomizerContext.applyTemplate` (o‘qish orqali `templateAppearance`)
- Appearance «Shablon o‘zgartirilgan» banneri

## O‘lchov

Baseline (D19-tor, `2d993db` dan oldingi mantiq):
`style=dashboard + verdictStyle=circle` → match `classic`.

D49: xuddi shu holat → `null`. Apply Klassik → kit default + match `classic`.
