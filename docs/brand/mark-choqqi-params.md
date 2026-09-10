# RankWant belgi — Cho‘qqi (10) dizayn parametrlari

**Manba:** `belgi-generated/10-choqqi.png` (1024×1024)  
**SVG:** [`mark-choqqi.svg`](./mark-choqqi.svg)  
**STATUS:** locked candidate (2026-09-10)

## Konsept

Ikki cho‘qqi (chap — balandroq) + cho‘qqi tepasidagi mustaqil nuqta (maqsad / «want»). Low-poly / faceted tog‘ silueti. Codeforces ustunlaridan farq qiladi.

## Koordinata tizimi

| Parametr      | Qiymat                                                                |
| ------------- | --------------------------------------------------------------------- |
| Canvas        | **1024 × 1024** px                                                    |
| `viewBox`     | `0 0 1024 1024`                                                       |
| Kelib chiqish | yuqori-chap `(0,0)`, Y pastga                                         |
| Content bbox  | x **117–914**, y **163–827** (kenglik 798, balandlik 665)             |
| Markazlash    | belgi canvas markaziga yaqin; chap cho‘qqi + nuqta o‘qi **x ≈ 420.5** |

## Ranglar (PNG dan o‘lchangan)

| Token  | Hex       | RGB           | Vazifa                             |
| ------ | --------- | ------------- | ---------------------------------- |
| `blue` | `#44A0FC` | 68, 160, 252  | Asosiy to‘ldirish + nuqta          |
| `mid`  | `#1074DC` | 16, 116, 220  | O‘rta soyali facet                 |
| `navy` | `#102038` | 16, 32, 56    | Kontur + chuqur facet              |
| `bg`   | `#FFFFFF` | 255, 255, 255 | Fon (transparent SVG da ixtiyoriy) |

Brand palitra bilan moslash: `#5b8cff` / `#4470e6` keyinroq SVG tokenlarida almashtirilishi mumkin; **1:1 PNG match** uchun yuqoridagi hex saqlanadi.

## Nuqta (circle)

| Parametr                            | Qiymat                 |
| ----------------------------------- | ---------------------- |
| Markaz `(cx, cy)`                   | **(420.5, 206.76)**    |
| Radius `r`                          | **44.1**               |
| Fill                                | `blue`                 |
| Chap cho‘qqi uchi                   | `(420.0, 294.5)`       |
| Nuqta pastki cheti                  | `cy + r ≈ 250.9`       |
| **Bo‘shliq (gap)** nuqta ↔ cho‘qqi  | **≈ 43.6 px**          |
| Nuqta diametri / content balandligi | 88.2 / 665 ≈ **13.3%** |

## Tog‘ silueti (tashqi kontur)

Yopiq poligon, soat yo‘nalishi (boshlanish — pastki o‘yilma o‘ng):

| #   | Nuqta            | Rol                        |
| --- | ---------------- | -------------------------- |
| 1   | `(116.5, 799.0)` | Chap tashqi toe            |
| 2   | `(420.0, 294.5)` | **Chap cho‘qqi** (baland)  |
| 3   | `(559.0, 501.5)` | Vodiy                      |
| 4   | `(649.0, 396.5)` | **O‘ng cho‘qqi** (pastroq) |
| 5   | `(914.5, 798.0)` | O‘ng tashqi toe            |
| 6   | `(649.0, 799.5)` | O‘ng tag platforma         |
| 7   | `(595.0, 826.5)` | Pastki o‘yilma o‘ng        |
| 8   | `(365.0, 826.5)` | Pastki o‘yilma chap        |
| 9   | `(313.0, 799.5)` | Chap tag platforma         |
| →   | Z                | yopiladi                   |

### Proporsiyalar

| O‘lchov                                 | Qiymat                                                 |
| --------------------------------------- | ------------------------------------------------------ |
| Chap cho‘qqi balandligi (toe y − tip y) | 799 − 294.5 ≈ **504.5**                                |
| O‘ng cho‘qqi balandligi                 | 798 − 396.5 ≈ **401.5** (~**80%** chapdan)             |
| Vodiy chuqurligi (tip chap → vodiy)     | 501.5 − 294.5 ≈ **207**                                |
| Asos kengligi (toe–toe)                 | 914.5 − 116.5 = **798**                                |
| Pastki o‘yilma kengligi                 | 595 − 365 = **230**                                    |
| Pastki o‘yilma chuqurligi               | 826.5 − 799 ≈ **27.5**                                 |
| Kontur qalinligi (stroke)               | **≈ 36 px** (32–40 px oralig‘ida o‘lchangan)           |
| `stroke-linejoin`                       | `round` yoki `miter` (PNG yumshoqroq — SVG da `round`) |

## SVG qurilishi (1:1 match)

Ikki asosiy path — kontur qalinligi va pastki «tosh» navy qatlami shu farqdan chiqadi:

### 1) `outer` — to‘liq navy siluet

Yuqoridagi 9 nuqtali poligon, `fill=#102038`.

### 2) `body` — yorug‘ ko‘k yadro (PNG blue+mid konturi)

| #   | Nuqta          | Rol                         |
| --- | -------------- | --------------------------- |
| 1   | `(159.5, 771)` | Chap past                   |
| 2   | `(420, 323.5)` | Chap cho‘qqi (stroke inset) |
| 3   | `(553, 558.5)` | Vodiy                       |
| 4   | `(648, 421.5)` | O‘ng cho‘qqi                |
| 5   | `(860.5, 764)` | O‘ng past                   |
| 6   | `(666, 709.5)` | O‘ng tag jag                |
| 7   | `(565, 776.5)` | Past markaz o‘ng            |
| 8   | `(378, 776.5)` | Past markaz chap            |
| 9   | `(325, 707.5)` | Chap tag jag                |
| →   | Z              |                             |

`outer \ body` = navy kontur (~36 px) + pastki jagged baza.

### 3) Mid facetlar (`#1074DC`)

1. Chap: `(162,772) → (174,753) → (359,562) → (324,706) → Z`
2. O‘ng: `(569,774) → (671,584) → (860,764) → (667,708) → Z`

### 4) Nuqta

`circle cx=420.5 cy=206.76 r=44.1`

## Qatlam tartibi (z-order)

1. `outer` (navy)
2. `body` (blue)
3. Mid facetlar
4. Nuqta

## Tekshiruv

PNG vs SVG raster: o‘rtacha abs farq **~5** (0–255), farq>40 bo‘lgan piksellar **~2%**. Solishtirish: `mark-choqqi-compare.png`.

## 16px / favicon

- Saqlanadi: ikki cho‘qqi silueti + nuqta
- Yo‘qolishi mumkin: mayda facetlar — favicon uchun facetlarsiz sodda variant mumkin
- Minimal export: `circle` + mountain path, stroke ≥ 2 px @16

## Export o‘lchamlari

| Fayl              | O‘lcham               |
| ----------------- | --------------------- |
| `mark-choqqi.svg` | vektor, viewBox 1024  |
| favicon           | 32 / 48 / 180 (apple) |
| app icon          | 512 / 1024            |

## O‘zgartirish qoidalari

- Nuqta **doim** chap cho‘qqi o‘qida (`cx = leftPeak.x`)
- Gap ≈ **0.044 × canvas** (1024 da ~44 px)
- O‘ng cho‘qqi chapning ~**80%** balandligida
- Ranglar CSS custom property orqali: `--rw-blue`, `--rw-mid`, `--rw-navy`
