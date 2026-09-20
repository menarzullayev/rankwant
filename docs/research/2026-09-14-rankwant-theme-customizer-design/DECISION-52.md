# D52 — Accent gate ikki xabar

**Sana:** 2026-09-21  
**Qaror:** A — ikki xabar, ikkalasida ham Apply blok  
**Tanlangan variant:** `two-messages-block`  
**CTO tavsiyasi:** A (qabul qilindi)

## Qaror

`customizer.contrastBlocked` («fails AA 4.5:1») faqat **o‘lchan gan**
ratio AA dan yiqilganda. `ground_unreadable` va `contrast_unreachable`
mavjud `error.*` kalitlarini ishlatadi — raqam yo‘q.

Apply `!ok` da bloklanadi (o‘lchov yo‘q ham, AA fail ham).

APP-9 yopildi.

## O‘lchov

Baseline (APP-9): ratio `—` + «fails AA (4.5:1)» when
`contrast_unreachable`.

D52: `accentGateKind({ error: "contrast_unreachable", button: null, ink: null })`
→ `contrast_unreachable`, not `aa`.
