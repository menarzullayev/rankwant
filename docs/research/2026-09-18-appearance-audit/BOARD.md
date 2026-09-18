# Appearance audit board

**Sana:** 2026-09-17 (UTC) / 2026-09-18 ~01:20–01:35 (Toshkent)  
**Maqsad:** RankWant Appearance (customizer + Settings `/settings/korinish`) ni kod + live MCP da tekshirish.  
**Muhit:** `https://rankwant.uz` · Chrome DevTools MCP · admin sessiya (`username=admin`)  
**Holat:** tuzatish **yozilmagan**. In Progress bo‘sh.  
**Hisob tiklandi:** `style=glass`, `theme=dark`, `font=jakarta`, `density=comfortable`, `accent=null`.

Bu hujjat boshqa agentga topshirish uchun. Avval P0. Live admin da **Reset** bosma (`clay` + `system` qo‘llanadi). `card` / `navMode` / `motion=off` bilan `PATCH /me/` 400 beradi — test qilgach hisobni pastdagi baseline ga qaytar.

---

## Qisqa holat

| Metrika | Qiymat |
|---|---|
| OK funksiya (MCP) | 18 |
| Xato / sinxron fail | 10 |
| To Do chipta | 9 (APP-1 … APP-9) |
| In Progress | 0 |
| Done | 3 (audit + tiklash, kod emas) |

**Ikkita ildiz:**

1. **Klient o‘lchovi** — `parseColor` faqat `#rrggbb` va `rgb()`. Glass/Swiss tokenlari gradient / 8-xonali hex → accent AA gate yolg‘on «fails AA».
2. **Server sxemasi** — `core/prefs.py` appearance da faqat `style, accent, font, size, density`. Klient 15+ maydon yuboradi → `PATCH /api/v1/me/` 400, `PrefsSync` jim yutadi.

---

## Board

### To Do

#### APP-1 · P0 · Accent AA gate Glass/Swiss da o‘lmaydi

- **Ta’sir:** Glass va Swiss da Preview `—` / `✗`, Apply disabled, xabar «This colour is unreadable — it fails AA (4.5:1) and will not be saved». Aslida kontrast o‘lchanmagan (`ground_unreadable`). Flat + Light da Hue 140 ishladi (`--rw-accent: #22763e`).
- **Sabab:** `apps/web/src/lib/theme/color.ts` → `parseColor` faqat `#([0-9a-fA-F]{6})` va `rgba?()`. `readBackgrounds()` `--rw-ground/surface/surface-2/chrome/chip/field/hover` ni parse qiladi. Glass da:
  - `--rw-ground`: `linear-gradient(135deg, #341d65 0%, #15376c 55%, #0c5151 100%) fixed`
  - `--rw-surface`: `#0000009e` (8 hex)
  - `--rw-chrome`: `#0a061ab8`
  - `--rw-hover`: `#ffffff14`
  Flat da `--rw-surface: #fff` ham 3-xonali — parse fail, lekin boshqa 6-xonali tokenlar yetarli, shuning uchun Flat ishlaydi.
- **Tuzatish:** `parseColor` ga `#rgb`, `#rrggbbaa` (alpha tashla yoki blend), `color()`, gradientdan birinchi stop. `previewAccent` / UI da `ground_unreadable` ni AA fail bilan aralashtirma (APP-9).
- **Tekshir:** Glass + Dark va Swiss + Light/Dark da Hue 140 → Apply yoqiladi, `--rw-accent` o‘zgaradi, xabar yo‘qoladi.

#### APP-2 · P0 · PATCH `/me/` appearance kalitlarini rad etadi

- **Ta’sir:** Customizer `navMode`, `card`, `pattern`, `iconPack`, `fontHeading`, `scale`, `verdictStyle`, `statusStyle`, `loadingStyle` ni hisobga yozolmaydi. A11y `motion: off|full|mild` ham yiqiladi. `PrefsSync` `.catch(() => {})` — foydalanuvchi xato ko‘rmaydi. Lokal `localStorage` ishlaydi, boshqa qurilma eski ko‘rinishni oladi.
- **O‘lchangan 400:**

```http
PATCH https://rankwant.uz/api/v1/me/
```

```json
{
  "theme": "dark",
  "ui_prefs": {
    "a11y": { "vision": "normal", "motion": "system", "bigTargets": false, "strongFocus": false },
    "sound": false,
    "effect": "fade",
    "version": 2,
    "templates": [],
    "appearance": {
      "font": "jakarta",
      "style": "glass",
      "accent": null,
      "density": "comfortable",
      "navMode": "sidenav",
      "navShape": "default",
      "fontHeading": null,
      "size": 100,
      "scale": 1,
      "card": "default",
      "pattern": "none",
      "verdictStyle": "auto",
      "statusStyle": "auto",
      "loadingStyle": "spinner",
      "iconPack": "lucide"
    }
  }
}
```

Javob:

```json
{
  "error": {
    "code": "invalid",
    "message": "Kiritilgan ma'lumot noto'g'ri",
    "details": { "ui_prefs": ["Noma'lum appearance kaliti: card"] }
  }
}
```

- **O‘lchangan 200** (faqat ruxsat etilgan kalitlar):

```json
{
  "theme": "dark",
  "ui_prefs": {
    "version": 2,
    "appearance": { "font": "jakarta", "style": "glass", "accent": null, "density": "comfortable" },
    "a11y": { "vision": "normal", "motion": "system", "bigTargets": false, "strongFocus": false },
    "sound": false,
    "effect": "fade"
  }
}
```

- **Sxema farqi:**

| Qatlam | Appearance | Font | Motion |
|---|---|---|---|
| API `apps/api/core/prefs.py` `_clean_appearance` | `style, accent, font, size, density` | `plex, inter, jakarta, roboto, dm-sans` | `system, reduce` |
| Klient `lib/api/account.ts` + Customizer | + `fontHeading, scale, lineHeight, tracking, width, navMode, navShape, card, pattern, verdictStyle, statusStyle, loadingStyle, iconPack` | + `lexend` | `system, full, mild, off` |

- **Tuzatish:** `prefs.py` ni klient `AppearancePrefs` / `A11yPrefs` bilan tenglashtir. `FONTS` ga `lexend`. `MOTIONS` = `system \| full \| mild \| off` (yoki klientni `reduce` ga map qil — lekin UI `off/mild/full`). `apps/api/tests/test_prefs.py` ni yangila. Ixtiyoriy: PrefsSync 400 ni yutmasin (toast / console).
- **Tekshir:** Top bar + Outline card + Lexend + motion Off → `PATCH /me/` 200; boshqa brauzer/hisobda qayta kirishda saqlanadi.

#### APP-3 · P1 · Suzuvchi hide bir tomonlama

- **Ta’sir:** `HIDDEN_KEY = "rw:customizer-hidden"`. `writeHidden(false)` bor (yashirilgan tugmadan qayta ochish). `writeHidden(true)` **hech qayerda** chaqirilmaydi. `customizer.hide` i18n kaliti yo‘q (`customizer.show` bor).
- **Fayl:** `apps/web/src/components/customizer/Customizer.tsx` (~81–156).
- **Tuzatish:** panel/headerga Hide → `writeHidden(true)` + i18n; yoki o‘lik kodni olib tashla.
- **Tekshir:** Hide → float yo‘qoladi, `localStorage rw:customizer-hidden=1`, show tugmasi qaytaradi.

#### APP-4 · P1 · `applySaved` theme ni qo‘llamaydi

- **Ta’sir:** `applyTemplate` `setMode(template.theme)` qiladi. `applySaved` faqat `applyStyle` + `commit` — `setMode` yo‘q. Saqlangan shablon light/dark ni qaytarmaydi.
- **Fayl:** `apps/web/src/context/CustomizerContext.tsx` `applySaved` (~323–338).
- **Tuzatish:** `ThemeTemplate` ga `theme` qo‘sh; `applySaved` da `setMode`. `exportAppearance` / `importAppearance` ham theme olib yursin (`share.ts` KEYS da theme yo‘q — APP-6).
- **Tekshir:** Dark + Terminal ni saqla → Light qil → saqlanganni bos → theme dark qaytadi.

#### APP-5 · P2 · Ctrl+. faqat Control, Meta emas

- **Ta’sir:** Windows MCP `Control+.` ochdi. macOS `Cmd+.` ishlamaydi. Tooltip «Ctrl+.».
- **Fayl:** `CustomizerContext.tsx` ~358–364: `event.ctrlKey && event.key === "."`.
- **Tuzatish:** `(event.ctrlKey || event.metaKey) && event.key === "."`.
- **Tekshir:** Win Ctrl+.; mac Cmd+.; ikkalasi ham toggle.

#### APP-6 · P2 · Share URL theme va React holatini yozmaydi

- **Ta’sir:** `share.ts` `KEYS` da `theme` yo‘q. Mount effekti `decodeAppearance` → `applyAll` + `rememberAppearance` + `replaceState`; `setAppearanceState` / `announcePrefs` yo‘q. Keyingi `setAppearance` eski React state bilan URL ni yeydi.
- **Fayllar:** `apps/web/src/lib/theme/share.ts`; `CustomizerContext.tsx` ~344–352.
- **Tuzatish:** URL ga `theme`; mount da `commit` yoki `setAppearanceState` + `setMode`.
- **Tekshir:** Copy link → yangi tabda theme+style mos; keyin shrift o‘zgartirish URL sozlamalarini o‘chirmasin.

#### APP-7 · P2 · Reset clay + system; shablonlar qoladi

- **Ta’sir:** `DEFAULT_APPEARANCE.style = "clay"`. Admin/sayt baseline `glass`. `resetAll` `templates` ni `commit` ga yubormaydi — saqlangan shablonlar qoladi. Live da Reset **bosilmagan**.
- **Fayl:** `CustomizerContext.tsx` `DEFAULT_APPEARANCE`, `resetAll` (~284–293).
- **Tuzatish:** Reset `siteAppearance` ga; `commit(..., [])` yoki alohida «shablonlarni o‘chirish».
- **Tekshir:** Reset → glass (yoki jamoa defaulti), theme system yoki sayt defaulti; shablonlar kutilganidek.

#### APP-8 · P3 · `matchTemplate` to‘liq emas

- **Ta’sir:** Moslik faqat `style, font, density, accent, theme, vision`. `navMode/card/pattern/fontHeading` o‘zgarsa ham «Template modified» chiqmasligi mumkin.
- **Fayl:** `apps/web/src/lib/theme/templates.ts` `matchTemplate`.
- **Tuzatish:** taqqoslashga nav/card/pattern/fontHeading qo‘sh.
- **Tekshir:** Day flat + Top bar → «Template modified».

#### APP-9 · P3 · Accent xato matni o‘lchov yo‘qligini AA deb yozadi

- **Ta’sir:** Glass da ratio `—`, lekin matn «fails AA (4.5:1)».
- **Fayl:** `Customizer.tsx` AccentSection — `!ok` ni bitta satrga yig‘adi; `AccentResult.error` `ground_unreadable` | `contrast_unreachable`.
- **Tuzatish:** `error === "ground_unreadable"` uchun alohida i18n (APP-1 bilan).
- **Tekshir:** o‘lchov yo‘q vs haqiqiy AA fail — ikki xil xabar.

---

### In Progress

*(bo‘sh — implementatsiya boshlanmagan)*

---

### Done

#### APP-10 · Kod inventarizatsiyasi

O‘qilgan: `Customizer.tsx`, `CustomizerTrigger.tsx`, `CustomizerContext.tsx`, `apply.ts`, `color.ts`, `templates.ts`, `share.ts`, `prefs.ts`, `PrefsSync.tsx`, `ThemeContext.tsx`, `StyleContext.tsx`, `AppearanceSection.tsx`, `apps/api/core/prefs.py`, `serializers.py` `validate_ui_prefs`.

#### APP-11 · MCP funksiya o‘tkazish

`https://rankwant.uz/` da panel ochiq holda har boshqaruv ketma-ket bosildi (bir tickda ko‘p `click` React stale state beradi — artifact, user-click bug emas). Settings: `https://rankwant.uz/settings/korinish`.

#### APP-12 · Admin appearance tiklandi

To‘liq appearance PATCH 400. Ruxsat etilgan kalitlar bilan PATCH 200. Home qayta ochilganda:

| Maydon | Qiymat |
|---|---|
| `data-style` | `glass` |
| `html.dark` | `true` |
| `theme` (localStorage) | `dark` |
| `data-font` | `jakarta` |
| `data-density` | `comfortable` |
| `data-nav` | `sidenav` |
| `rw:appearance` | `{"font":"jakarta","style":"glass","accent":null,"density":"comfortable"}` |
| `--rw-accent` | `#ffffffeb` (uslubning o‘zi) |

---

## Funksiya holati

Manba: live MCP + kod. **Kod** = UI bor, brauzerda to‘liq bosilmadi.

| Funksiya | Holat | Dalil |
|---|---|---|
| Panel ochish / yopish | OK | Trigger, Esc, Ctrl+. |
| Ctrl+. | OK | Escape dan keyin panel qayta ochildi |
| Cmd+. | Xato | Faqat `event.ctrlKey`; Meta yo‘q |
| Escape | OK | `aria-expanded=false`, heading yo‘qoldi |
| 12 ta uslub | OK | `data-style` dashboard…skeu |
| Light / Dark | OK | `html.dark` + `localStorage.theme`; View Transition ~1 s kechikishi |
| System | Kod | Dual uslubda chiqadi; MCP da bosilmadi |
| Accent · Flat | OK | Hue 140 → `--rw-accent #22763e`, Apply yoqilgan |
| Accent · Glass/Swiss | Xato | Gradient / `#rrggbbaa`; Apply o‘chiq |
| Shrift / heading | OK | Inter, Jakarta; `data-font-heading=inter` |
| Lexend | Xato | Klientda bor; API `FONTS` da yo‘q (`plex` bor) |
| Density | OK | compact / comfortable / spacious |
| Sidebar / Top bar | OK | `topnav` da complementary yo‘qoldi |
| Slim (topnav) | OK | `data-nav-shape=slim`; sidenav da yashirin |
| Kenglik / karta / naqsh | OK | width, `card=outline`, `pattern=grid` |
| Verdict / status / loading | OK | badge, iconText, skeleton |
| Icon pack + gallery | OK | Phosphor; Show all → 278 svg |
| Day flat shablon | OK | flat + light + inter + comfortable |
| Copy link | OK | Tugma «Link copied» |
| Save form | OK | Nom `audit-tmp` — Save enabled; hisobga yozilmadi |
| Export / Import fayl | Kod | `download()` / `importAppearance`; fayl tanlanmadi |
| applySaved | Xato | `setMode` chaqirilmaydi |
| Undo | Qisman | Tugma yoqildi; alohida qadam o‘lchanmadi |
| Reset | Kod | clay + system; live admin da bosilmadi |
| Hide float | Xato | `writeHidden(true)` mavjud emas |
| A11y (lokal) | OK | protan, motion=off, targets=big, focus=strong |
| A11y → hisob | Xato | `motion=off` API da yo‘q; PATCH butun `ui_prefs` ni yiqitadi |
| PrefsSync PATCH | Xato | 400 `card`; `.catch()` jim |
| Settings `/settings/korinish` | OK | Til, theme, 12 uslub, sound, fade/circle — to‘liq customizer emas |
| Share URL theme | Xato | `KEYS` da theme yo‘q; React state yangilanmaydi |

---

## Fayllar (tuzatish uchun)

| Fayl | Nima |
|---|---|
| `apps/web/src/lib/theme/color.ts` | `parseColor`, `readBackgrounds` |
| `apps/web/src/lib/theme/apply.ts` | `applyAccent`, `previewAccent`, `applyAll` |
| `apps/web/src/components/customizer/Customizer.tsx` | Accent UI, hide, A11y motion chips |
| `apps/web/src/context/CustomizerContext.tsx` | commit, applySaved, resetAll, Ctrl+., URL mount |
| `apps/web/src/lib/theme/share.ts` | encode/decode KEYS |
| `apps/web/src/lib/theme/templates.ts` | `matchTemplate` |
| `apps/web/src/context/PrefsSync.tsx` | `PATCH /me/`, jim catch |
| `apps/web/src/lib/api/account.ts` | `AppearancePrefs`, `A11yPrefs` |
| `apps/web/src/components/settings/AppearanceSection.tsx` | subset (til/theme/style/sound/effect) |
| `apps/api/core/prefs.py` | validator — asosiy P0 |
| `apps/api/tests/test_prefs.py` | sxema testlari |

---

## Agent uchun cheklovlar

- Tuzatish yozilsa — kichik, fokuslangan MR. Conventional commit (`fix:`).
- Live `.env.public`, Docker restart, auth fayllar, commit/push — so‘ralmaguncha yo‘q.
- Admin appearance ni buzib qolmaslik: test oxirida baseline (yuqoridagi jadval).
- Settings slug: `/settings/korinish` (EN label «Appearance»).
- Theme almashinuvi View Transition (`effect=fade`) tufayli `html.dark` ~1 s kechikishi mumkin — darhol `evaluate` yolg‘on fail bermasin.
- Bir tickda bir nechta `button.click()` React `setAppearance` ni stale qiladi — ketma-ket, render orasida kut.

---

## Tavsiya etilgan tartib

1. APP-2 (API sxema + test) — aks holda qolgan UI saqlash 400.
2. APP-1 + APP-9 (parseColor + xato matni) — Glass default.
3. APP-4, APP-6 (shablon/share theme).
4. APP-3, APP-5, APP-7, APP-8.
