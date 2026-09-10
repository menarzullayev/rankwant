# Belgi promptlari

Yigirma to‘rtta prompt rasm generatorlari uchun. Yigirma tasi konsepsiyalarga to‘g‘ri keladi — shunda ikkala natijani yonma-yon solishtirish mumkin. To‘rttasi ro‘yxatda yo‘q yo‘nalishlar.

Generatsiya natijalari: [`belgi-generated/`](./belgi-generated/) (birinchi o‘tish: har konsepsiyadan 1 ta PNG).

## Qorong‘i

Avval bitta haqiqat. Rasm generatorlari vektor chiqara olmaydi — natija PNG bo‘ladi, chetlari esa yaqindan qaralganda notekis. Logotip uchun bu yetarli emas: u 16px dan bannergacha bir xil tiniq bo‘lishi kerak. Shuning uchun to‘g‘ri ish tartibi — generator bilan shaklni topish, keyin uni toza SVG qilib qayta chizish.

## Umumiy qism

Har promptga qo‘shiladi. Generator alohida «negative prompt» maydonini so‘rasa, ikkinchi blokni o‘sha yerga qo‘ying.

### BASE

Har promptning oxiriga:

```
flat vector logo mark, minimal geometric construction, even stroke weight, perfectly centered on a plain white background with generous empty margin, single isolated symbol, brand blue #5b8cff with a deeper #4470e6 accent, dark ink #14171c, must stay legible when scaled down to 16 pixels, symmetrical and precise, app icon quality
```

### NEG

Negative prompt (11–12 harf promptlarida `text, letters, words, typography` ni olib tashlang):

```
text, letters, words, typography, watermark, signature, gradient, glow, drop shadow, 3d render, bevel, emboss, photorealistic, photo, mockup, business card, stationery, background scene, frame, border, multiple objects, cluttered, busy detail, hand drawn, sketch, texture, noise
```

NEG (harf — 11, 12):

```
watermark, signature, gradient, glow, drop shadow, 3d render, bevel, emboss, photorealistic, photo, mockup, business card, stationery, background scene, frame, border, multiple objects, cluttered, busy detail, hand drawn, sketch, texture, noise
```

---

## Ko‘tarilish

«Rank» ning to‘g‘ridan-to‘g‘ri ma’nosi. Generator bu guruhni eng yaxshi uddalaydi — shakllar sodda va simmetrik.

### 01 — Uch ustun

```
Three vertical rounded bars standing side by side on an invisible baseline, each taller than the one to its left, equal widths, equal gaps, the tallest right-hand bar filled in bright blue and the two shorter ones in dark ink, reading as a rising rank chart, flat vector logo mark, minimal geometric construction, even stroke weight, perfectly centered on a plain white background with generous empty margin, single isolated symbol, brand blue #5b8cff with a deeper #4470e6 accent, dark ink #14171c, must stay legible when scaled down to 16 pixels, symmetrical and precise, app icon quality
```

### 02 — Ikki shevron

```
Two upward-pointing chevrons stacked one above the other like a military rank insignia, sharp clean angles, identical thickness, the upper chevron bright blue and the lower one dark ink, nothing else in the frame, flat vector logo mark, minimal geometric construction, even stroke weight, perfectly centered on a plain white background with generous empty margin, single isolated symbol, brand blue #5b8cff with a deeper #4470e6 accent, dark ink #14171c, must stay legible when scaled down to 16 pixels, symmetrical and precise, app icon quality
```

### 03 — Pog‘ona

```
A single thick stroke drawn as a three-step staircase ascending from lower left to upper right, square stroke ends, with one solid bright blue circle resting on the top step, nothing else, flat vector logo mark, minimal geometric construction, even stroke weight, perfectly centered on a plain white background with generous empty margin, single isolated symbol, brand blue #5b8cff with a deeper #4470e6 accent, dark ink #14171c, must stay legible when scaled down to 16 pixels, symmetrical and precise, app icon quality
```

### 06 — Qo‘sh cho‘qqi

```
Two nested upward chevrons forming a double peak: a large wide chevron above and a smaller narrower chevron directly below it, rounded stroke ends, the smaller inner one bright blue, the outer one dark ink, flat vector logo mark, minimal geometric construction, even stroke weight, perfectly centered on a plain white background with generous empty margin, single isolated symbol, brand blue #5b8cff with a deeper #4470e6 accent, dark ink #14171c, must stay legible when scaled down to 16 pixels, symmetrical and precise, app icon quality
```

### 10 — Cho‘qqi

```
A solid angular mountain silhouette with two peaks, the left peak higher, straight facets and no texture, with one small solid bright blue circle floating in the empty space above the higher peak, flat vector logo mark, minimal geometric construction, even stroke weight, perfectly centered on a plain white background with generous empty margin, single isolated symbol, brand blue #5b8cff with a deeper #4470e6 accent, dark ink #14171c, must stay legible when scaled down to 16 pixels, symmetrical and precise, app icon quality
```

### 18 — Olti burchak nishon

```
A regular hexagon drawn as a thin even outline, standing on a flat bottom edge, containing three short vertical bars of increasing height, the tallest bar bright blue, plenty of space between the bars and the hexagon edge, flat vector logo mark, minimal geometric construction, even stroke weight, perfectly centered on a plain white background with generous empty margin, single isolated symbol, brand blue #5b8cff with a deeper #4470e6 accent, dark ink #14171c, must stay legible when scaled down to 16 pixels, symmetrical and precise, app icon quality
```

---

## Kod tili

Dasturlashning tinish belgilari. Generator bu yerda «harf yozmaslik» buyrug‘ini buzishi mumkin — natijani tekshiring.

### 04 — Qavs ichida o‘q

```
Two curly braces facing each other, left and right, with a clean straight upward arrow standing between them, the arrow bright blue and the braces dark ink, even stroke weight throughout, flat vector logo mark, minimal geometric construction, even stroke weight, perfectly centered on a plain white background with generous empty margin, single isolated symbol, brand blue #5b8cff with a deeper #4470e6 accent, dark ink #14171c, must stay legible when scaled down to 16 pixels, symmetrical and precise, app icon quality
```

### 05 — Terminal

```
A command line prompt symbol: a large greater-than chevron on the left and a short horizontal cursor bar to its lower right, rounded ends, the cursor bar bright blue and the chevron dark ink, flat vector logo mark, minimal geometric construction, even stroke weight, perfectly centered on a plain white background with generous empty margin, single isolated symbol, brand blue #5b8cff with a deeper #4470e6 accent, dark ink #14171c, must stay legible when scaled down to 16 pixels, symmetrical and precise, app icon quality
```

### 20 — Nuqtali vergul

```
A semicolon shape enlarged into a symbol: one solid circle above a comma with a short curved tail, both dark ink, accompanied by three small bright blue circles ascending diagonally to the upper right, flat vector logo mark, minimal geometric construction, even stroke weight, perfectly centered on a plain white background with generous empty margin, single isolated symbol, brand blue #5b8cff with a deeper #4470e6 accent, dark ink #14171c, must stay legible when scaled down to 16 pixels, symmetrical and precise, app icon quality
```

---

## Qvant

Zarra va orbita. Generator orbitani ko‘pincha uch-to‘rt halqa qilib yuboradi; promptda «single» so‘zi shuning uchun turibdi.

### 07 — Q qidiruv

```
A ring outline with a short straight tail extending from its lower right, reading at once as a magnifying glass and as a rounded Q, plus one small solid bright blue circle floating at the upper right of the ring, flat vector logo mark, minimal geometric construction, even stroke weight, perfectly centered on a plain white background with generous empty margin, single isolated symbol, brand blue #5b8cff with a deeper #4470e6 accent, dark ink #14171c, must stay legible when scaled down to 16 pixels, symmetrical and precise, app icon quality
```

### 08 — Zarra

```
A solid bright blue circle at the centre with one single thin elliptical orbit ring tilted about thirty degrees around it, dark ink orbit, exactly one ring and no more, flat vector logo mark, minimal geometric construction, even stroke weight, perfectly centered on a plain white background with generous empty margin, single isolated symbol, brand blue #5b8cff with a deeper #4470e6 accent, dark ink #14171c, must stay legible when scaled down to 16 pixels, symmetrical and precise, app icon quality
```

---

## Musobaqa

Pyedestal, qalqon, nishon. Eng «xavfsiz» guruh va shu sababli eng ko‘p uchraydigan.

### 09 — Pyedestal

```
Three rounded rectangular podium blocks standing side by side on a shared baseline, the centre block clearly the tallest and filled bright blue, the left block medium height, the right block shortest, both dark ink, flat vector logo mark, minimal geometric construction, even stroke weight, perfectly centered on a plain white background with generous empty margin, single isolated symbol, brand blue #5b8cff with a deeper #4470e6 accent, dark ink #14171c, must stay legible when scaled down to 16 pixels, symmetrical and precise, app icon quality
```

### 17 — Qalqon

```
A heraldic shield outline with a flat top and a pointed bottom, thin even stroke, containing a single upward chevron in bright blue floating in its centre with clear space around it, flat vector logo mark, minimal geometric construction, even stroke weight, perfectly centered on a plain white background with generous empty margin, single isolated symbol, brand blue #5b8cff with a deeper #4470e6 accent, dark ink #14171c, must stay legible when scaled down to 16 pixels, symmetrical and precise, app icon quality
```

### 19 — Nishon

```
A target of exactly two concentric thin circle outlines in dark ink with a solid bright blue dot at the very centre, evenly spaced rings, nothing else, flat vector logo mark, minimal geometric construction, even stroke weight, perfectly centered on a plain white background with generous empty margin, single isolated symbol, brand blue #5b8cff with a deeper #4470e6 accent, dark ink #14171c, must stay legible when scaled down to 16 pixels, symmetrical and precise, app icon quality
```

---

## O‘zbek geometriyasi

Eng qiziq va eng qiyin guruh. Generator «Islamic geometric» so‘zini eshitib naqshni haddan tashqari murakkab qiladi — promptlarda soddalik qayta-qayta ta’kidlangan.

### 13 — Ravoq

```
The outline of a pointed Central Asian portal arch as found on a Samarkand madrasa, four-centred ogee shape, drawn as one even thin stroke, standing on two straight legs, with a small solid bright blue rounded doorway inside at the base, radically simplified with no ornament, flat vector logo mark, minimal geometric construction, even stroke weight, perfectly centered on a plain white background with generous empty margin, single isolated symbol, brand blue #5b8cff with a deeper #4470e6 accent, dark ink #14171c, must stay legible when scaled down to 16 pixels, symmetrical and precise, app icon quality
```

### 14 — Ikat

```
Four solid diamonds arranged around a shared centre so that together they read as one larger diamond rosette, top and bottom diamonds dark ink, left and right diamonds bright blue, flat solid fills, inspired by Uzbek ikat textile motifs, extremely simplified, only four shapes, flat vector logo mark, minimal geometric construction, even stroke weight, perfectly centered on a plain white background with generous empty margin, single isolated symbol, brand blue #5b8cff with a deeper #4470e6 accent, dark ink #14171c, must stay legible when scaled down to 16 pixels, symmetrical and precise, app icon quality
```

### 15 — Girih yulduzi

```
An eight-pointed star formed by exactly two overlapping squares, one rotated forty-five degrees over the other, drawn as thin even outlines only, one square dark ink and one bright blue, based on Islamic girih geometry, no infill pattern, flat vector logo mark, minimal geometric construction, even stroke weight, perfectly centered on a plain white background with generous empty margin, single isolated symbol, brand blue #5b8cff with a deeper #4470e6 accent, dark ink #14171c, must stay legible when scaled down to 16 pixels, symmetrical and precise, app icon quality
```

### 16 — Quyosh

```
A rising sun reduced to a symbol: a solid bright blue half disc sitting on a straight horizontal baseline, with five short straight dark ink rays radiating evenly above it, no curves in the rays, flat vector logo mark, minimal geometric construction, even stroke weight, perfectly centered on a plain white background with generous empty margin, single isolated symbol, brand blue #5b8cff with a deeper #4470e6 accent, dark ink #14171c, must stay legible when scaled down to 16 pixels, symmetrical and precise, app icon quality
```

---

## Harf shakli

Faqat shu ikkitasida harf ruxsat etiladi. Negative promptdan `text, letters, words, typography` ni olib tashlang.

### 11 — R harfi

```
The capital letter R constructed from pure geometry: a straight vertical stem, a perfect half circle bowl, and one straight diagonal leg, even stroke weight, the diagonal leg bright blue and the rest dark ink, no serifs, flat vector logo mark, minimal geometric construction, even stroke weight, perfectly centered on a plain white background with generous empty margin, single isolated symbol, brand blue #5b8cff with a deeper #4470e6 accent, dark ink #14171c, must stay legible when scaled down to 16 pixels, symmetrical and precise, app icon quality
```

### 12 — W harfi

```
The capital letter W built from two identical V shapes joined at the top, thick strokes with rounded ends, the right-hand V bright blue and the left one dark ink, wide open angles, flat vector logo mark, minimal geometric construction, even stroke weight, perfectly centered on a plain white background with generous empty margin, single isolated symbol, brand blue #5b8cff with a deeper #4470e6 accent, dark ink #14171c, must stay legible when scaled down to 16 pixels, symmetrical and precise, app icon quality
```

---

## Ro‘yxatda yo‘q (yangi)

To‘rtta boshqa yo‘nalish — generator kutilmagan narsa topishi mumkin.

### 21 — Paxta va sxema

```
A cotton boll reduced to four rounded petals around a centre, with the stem replaced by a straight circuit board trace ending in a small square pad, bright blue trace and dark ink petals, joining Uzbek cotton and electronics in one simple symbol, flat vector logo mark, minimal geometric construction, even stroke weight, perfectly centered on a plain white background with generous empty margin, single isolated symbol, brand blue #5b8cff with a deeper #4470e6 accent, dark ink #14171c, must stay legible when scaled down to 16 pixels, symmetrical and precise, app icon quality
```

### 22 — Suzani rozetkasi

```
A suzani embroidery rosette radically simplified into a logo: one central circle surrounded by six identical teardrop petals, flat solid fills, alternating dark ink and bright blue petals, perfectly radial, no stitching texture, flat vector logo mark, minimal geometric construction, even stroke weight, perfectly centered on a plain white background with generous empty margin, single isolated symbol, brand blue #5b8cff with a deeper #4470e6 accent, dark ink #14171c, must stay legible when scaled down to 16 pixels, symmetrical and precise, app icon quality
```

### 23 — Tarmoq girihi

```
A small network graph of five nodes connected by straight lines, arranged so the lattice also reads as a girih star panel, nodes as solid circles with two of them bright blue, thin connecting lines in dark ink, flat vector logo mark, minimal geometric construction, even stroke weight, perfectly centered on a plain white background with generous empty margin, single isolated symbol, brand blue #5b8cff with a deeper #4470e6 accent, dark ink #14171c, must stay legible when scaled down to 16 pixels, symmetrical and precise, app icon quality
```

### 24 — Ikat shevroni

```
An upward chevron built out of two elongated ikat diamonds meeting at the apex, stepped diamond edges, left half dark ink and right half bright blue, reading at once as a rank chevron and as Uzbek textile geometry, flat vector logo mark, minimal geometric construction, even stroke weight, perfectly centered on a plain white background with generous empty margin, single isolated symbol, brand blue #5b8cff with a deeper #4470e6 accent, dark ink #14171c, must stay legible when scaled down to 16 pixels, symmetrical and precise, app icon quality
```

---

## Amaliy maslahat

- **Kvadrat va katta.** 1024×1024 yoki undan katta so‘rang — kichik rasmda chetlar bulanadi va trace qilib bo‘lmaydi.
- **Har promptdan 4 ta variant** (keyingi o‘tishlar). Birinchi o‘tishda har biridan 1 ta saqlangan.
- **Simmetriya** — eng zaif joyi. Ikkala tomoni bir xil bo‘lishi kerak bo‘lgan belgilarda (14, 15, 19) natijani diqqat bilan tekshiring.
- **Rangni keyin ham o‘zgartirsa bo‘ladi.** Shakl to‘g‘ri bo‘lsa yetarli — ranglashni SVG bosqichida aniq qilamiz.
- **16px sinovi.** Yoqqan rasmni 16×16 ga kichraytirib ko‘ring. Nima qolgani — logotipning haqiqiy mazmuni.
- **Uchtadan ko‘p yoqmasin.** Ikki-uchtasini tanlab SVG chizishga o‘ting.

Promptlar ingliz tilida — generatorlar ingliz tilida ancha aniqroq ishlaydi.
