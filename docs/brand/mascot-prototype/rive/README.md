# Rive — Crest Spirit state machine

`.riv` fayl **binary** — repoda hozir yo'q. Quyidagi qadamlarni Rive editorida bajaring; keyin `crest-spirit.riv` ni shu papkaga qo'ying.

## Rive loyihasi

1. [rive.app](https://rive.app) → yangi fayl **512×512**.
2. `crest-spirit.svg` import → Artboard «CrestSpirit».
3. **State machine** `MascotSM`:
   | Input | Tur | Holatlar |
   |-------|-----|----------|
   | `hover` | boolean | `idle` ↔ `wave` (nuqta yuqoriga + kichik scale) |
   | `success` | trigger | `celebrate` (1 s, keyin `idle`) |
   | `mode` | number | 0 = Crest, 1 = Qvant (orbit layer opacity) |

4. Animatsiyalar faqat **transform/opacity** — 3D rotate yo'q (brend flat).

## Eksport

- Format: **Rive 7.x** (runtime `@rive-app/canvas` bilan mos).
- Fayl nomi: `crest-spirit.riv`
- `mascot-review.html` avtomatik yuklaydi; yo'q bo'lsa sahifada **SVG state machine** namunasi ishlaydi.

## Runtime (integratsiya eslatmasi)

```html
<script src="https://unpkg.com/@rive-app/canvas@2.21.2"></script>
```

Production uchun bundle ~100 KB + `.riv` hajmi — alohida PR va bundle budjeti kerak.
