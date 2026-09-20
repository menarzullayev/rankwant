# D54 — Import file input a11y

**Sana:** 2026-09-21  
**Qaror:** B — `aria-hidden` input + labeled tugma  
**Tanlangan variant:** `aria-hidden-button`  
**CTO tavsiyasi:** B (qabul qilindi)

## Qaror

`type="file"` vizual emas, tab tartibida emas (`sr-only`, `tabIndex={-1}`)
va endi a11y daraxtida ham emas (`aria-hidden="true"`). Import
`customizer.importFile` tugmasi `file.current.click()` orqali ochadi.

Native «Fayl tanlanmagan» qaytmaydi (CUST-100).

## Trade-off

Input e’lon qilinmaydi — to‘g‘ri, chunki u UI emas.
