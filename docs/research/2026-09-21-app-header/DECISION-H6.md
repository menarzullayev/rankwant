# H6 — mavzu tugmasi uslublari

**Sana:** 2026-09-21  
**Tanlov:** sozlagichda 7 uslub; standart `doira` (prototip 03).

## Nima

Owner theme-toggle-studio dan tanladi: 01, 02, **03 default**, 04, 07, 08, 10.
05 (tutilish), 06 (uch holat), 09 (chip) kirmadi.

## Qaror

- Headerga `ThemeToggle` qaytadi (H1 tartib: Customizer dan keyin, til oldida).
- Uslub `appearance.themeToggle` da saqlanadi; tanlov — sozlagich Rang guruhi.
- Standart: `doira` → sahifa View Transition `circle` (mavjud ThemeContext).
- `parda` → `curtain`. Qolganlari → `fade` + tugma animatsiyasi.
- `system` sozlagich radio da qoladi (06 headerga kirmadi).
- StylePicker qaytmaydi (D3 qismi).
- `dual: false` uslublarda tugma yashirin (D6).
- `/login` da yo‘q (qidiruv/sozlagich kabi).

## Rad etilgan

- Faqat sozlamalar sahifasidagi 3 effekt (`none/fade/circle`) — yetarli emas.
- 06 uch holatni headerga qo‘yish — H4 zichlik.
