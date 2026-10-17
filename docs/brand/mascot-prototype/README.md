# Mascot animatsiya prototipi

**Maqsad:** Crest Spirit / Qvant helper uchun **Lottie**, **Rive**, **SVG/CSS** va **3D solishtiruv** — bitta brauzer sahifasida.

Bu papka **production emas**; `apps/web` ga runtime qo'shilmagan (D62: yuklanish hali sof CSS).

## Ochish

PNG/SVG/Lottie/RIV yo'llari HTTP orqali yuklanadi — **`file://` ochilsa fetch va Lottie buziladi**.

### Variant A — Python (tavsiya)

```powershell
cd d:\Linux\Web_Projects\rankwant\docs\brand\mascot-prototype
python -m http.server 8765
```

Brauzer: [http://127.0.0.1:8765/mascot-review.html](http://127.0.0.1:8765/mascot-review.html)

### Variant B — repo ildizidan

```powershell
cd d:\Linux\Web_Projects\rankwant
python -m http.server 8765
```

Brauzer: [http://127.0.0.1:8765/docs/brand/mascot-prototype/mascot-review.html](http://127.0.0.1:8765/docs/brand/mascot-prototype/mascot-review.html)

## Fayllar

| Fayl | Texnologiya | Izoh |
|------|-------------|------|
| `mascot-review.html` | barchasi | Bosh sahifa, CDN: lottie-web + Rive canvas |
| `crest-spirit.svg` | SVG | Crest maskot qatlamlari (`#spirit-body`, `#goal-dot`, …) |
| `lottie/crest-spirit.json` | Lottie | Nuqta puls + cho'qqi nafasi (prototip JSON) |
| `lottie/qvant-orbit.json` | Lottie | Orbita + zarra |
| `ae/EXPORT.md` | After Effects | Bodymovin eksport qadamlari |
| `rive/README.md` | Rive | State machine + `crest-spirit.riv` joylash |
| `rive/crest-spirit.riv` | Rive | *(ixtiyoriy)* editor eksporti — repoda yo'q |

## Sahifa bo'limlari

1. **SVG/CSS** — productionga yaqin; `Harakat → O'chiq` = platforma `data-motion=off`.
2. **Lottie** — AE oqimini sinash; JSON ni `ae/EXPORT.md` bo'yicha almashtiring.
3. **Rive** — `.riv` qo'yilsa canvas; aks holda SVG state machine (hover / success).
4. **3D CSS** — nima **qilmaymiz** (flat brend qoidasi).
5. **EmptyState** — `illustration` o'lchamida joylashuv namunasi.

## Keyingi qadam (integratsiya)

1. Dizayn tasdiqi — LOCK-GATE dan **mustaqil** (yordamchi personaj, asosiy Crest emas).
2. Birinchi kod: `EmptyState` `illustration` + statik SVG.
3. Animatsiya PR: faqat SVG/CSS yoki alohida Lottie PR (bundle + `check_contrast` + motion prefs).
