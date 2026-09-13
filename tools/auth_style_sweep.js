/**
 * Auth sahifasini BRAUZERDAGI 18 palitrada tekshiradi.
 *
 * ═══════════════════════════════════════════════════════════════════
 * NEGA 24 EMAS, 18
 * ═══════════════════════════════════════════════════════════════════
 * `styles.ts` da `dual` bayrog'i bor:
 *   dual: true  — dashboard, swiss, flat, material, editorial, brutal
 *   dual: false — terminal, glass, neu, clay, aurora, skeu
 * `dual: false` uslublar BITTA muhitga chizilgan (terminal qorong'u,
 * gil yorug'), ya'ni ularda tema tugmasi umuman ko'rsatilmaydi.
 * Shuning uchun to'g'ri hisob: 6×2 + 6 = **18 palitra**.
 *
 * Ilgari bu skript 24 variantni yugurtirardi va `glass-light`,
 * `aurora-light`, `skeu-light` kabi MAVJUD BO'LMAGAN muhitlarni
 * o'lchab, yolg'on "FAIL" chiqarardi.
 *
 * `check_contrast.py` (CI, `fast`) ham xuddi shu 18 raqamni yozadi —
 * bu yerdagi tekshiruv CSS matematikasini TAKRORLAMAYDI: u
 * `globals.css` dagi qiymatlarni o'qiydi, bu esa HAQIQATDA
 * renderlangan pikselni o'lchaydi. Ikkisi mos kelishi kerak.
 *
 * ═══════════════════════════════════════════════════════════════════
 * METOD — `localStorage` + IFRAME
 * ═══════════════════════════════════════════════════════════════════
 * Uslub `data-style` atributi bilan almashadi va u `layout.tsx` dagi
 * `STYLE_INIT` orqali `localStorage` dan HIDRATSIYADAN OLDIN o'qiladi.
 * `document.documentElement.dataset.style` ni JS bilan keyin
 * almashtirish ISHLAMAYDI — o'lchandi, `getComputedStyle` eski
 * qiymatni qaytardi (bir xil `div.rw-strong` toza sinovda to'g'ri
 * javob berdi, ya'ni xato o'lchovda edi, kodda emas).
 *
 * Shuning uchun har variant uchun `localStorage` yoziladi va sahifa
 * YANGI IFRAME'da yuklanadi — iframe'larning `localStorage` i
 * bo'lishilsa ham, har biri o'z `load` ida yangi qiymatni o'qiydi.
 *
 * ═══════════════════════════════════════════════════════════════════
 * ⚠️ TEMA — `dark` EMAS, `null`
 * ═══════════════════════════════════════════════════════════════════
 * `THEME_INIT`: `if (t !== "light") root.classList.add("dark")`.
 * Ya'ni qorong'i — STANDART; yorug' faqat `theme === "light"` da.
 * Shuning uchun qorong'i uchun kalit O'CHIRILADI.
 *
 * ═══════════════════════════════════════════════════════════════════
 * ⚠️ `measure()` GA IFRAME OYNASI UZATILISHI SHART
 * ═══════════════════════════════════════════════════════════════════
 * `measure(win)` — `win` bermasangiz `window` ishlatiladi, ya'ni
 * YUQORIDAGI sahifa o'lchanadi, iframe emas. Bu jimgina noto'g'ri
 * natija beradi: sinovda aynan shu sababdan salybiy test "o'tib
 * ketgan" edi (ataylab buzilgan uslub ham `ok: true` chiqqan).
 *
 * ═══════════════════════════════════════════════════════════════════
 * ⚠️ `color(srgb ...)` — KANALLAR 0–1
 * ═══════════════════════════════════════════════════════════════════
 * `getComputedStyle` ba'zi shaffof qiymatlarni `color(srgb .61 .61 .61)`
 * ko'rinishida qaytaradi. `[\d.]+` bilan o'qilsa `0.61` «0.61/255» deb
 * talqin qilinadi, ya'ni rang DEYARLI QORA bo'lib chiqadi va nisbat
 * 1.1 ga tushadi. Aynan shu sababdan `material-dark` chegarasi 6.91:1
 * o'rniga 1.12:1 ko'rsatgan edi. Shuning uchun faqat `parseColor()`.
 *
 * Gradientli uslublar (`glass`, `skeu`) bu yerda `skip` bilan
 * belgilanadi — ularni `tools/check_gradient_styles.py` qo'lda
 * tasdiqlaydi (har bir pog'ona alohida).
 *
 * Brauzer ichida ishlaydi (chrome-devtools MCP `evaluate_script`).
 */

/** Ikkala muhitni ham qo'llab-quvvatlaydigan uslublar. */
export const DUAL = ["dashboard", "swiss", "flat", "material", "editorial", "brutal"];
/** Bitta muhitga chizilgan — faqat bir marta o'lchanadi. */
export const SINGLE = ["terminal", "glass", "neu", "clay", "aurora", "skeu"];

/** 18 ta variant: 6 dual × 2 + 6 single.
 *
 *  ⚠️ `dual: false` uslub uchun muhit YORUG' deb belgilanadi, chunki
 *  `theme` ni o'chirmaslik standart holat. Bu shunchaki yorliq emas:
 *  o'sha uslub ikkala holatda ham BIR XIL chiziladi (`aurora`,
 *  `terminal` — qorong'u; `clay`, `glass`, `neu`, `skeu` — yorug').
 *  Ya'ni ikkinchi muhitni o'lchash MA'NOSIZ takror bo'lardi. */
export function plan() {
  const out = [];
  for (const s of DUAL) {
    out.push([s, false, `${s}-light`]);
    out.push([s, true, `${s}-dark`]);
  }
  for (const s of SINGLE) {
    // Bir muhitli uslublar o'z muhitida yorliqlanadi.
    const darkOnly = ["terminal", "aurora"];
    const dark = darkOnly.includes(s);
    out.push([s, dark, `${s}${dark ? "-dark" : "-light"}`]);
  }
  return out;
}

/** `rgb()` / `rgba()` / `color(srgb ...)` → `[r, g, b, a]` (0–255 va 0–1).
 *
 *  ⚠️ `color(srgb r g b / a)` — bu YANGI sintaksis va unda kanallar
 *  0–1 oralig'ida, `rgb()` da esa 0–255. Uni `rgb()` deb o'qish
 *  JIMGINA noto'g'ri natija beradi: `color(srgb 0.616 0.616 0.616)`
 *  `[\d.]+` bilan `[0.616, 0.616, 0.616]` bo'lib chiqadi va kod uni
 *  `rgb(0.6, 0.6, 0.6)` — ya'ni DEYARLI QORA deb hisoblaydi. Aynan shu
 *  sababdan `material-dark` chegarasi 6.91:1 o'rniga 1.12:1 ko'rsatgan
 *  edi (yolg'on "PAST").
 *
 *  O'qib bo'lmagan qiymat — `null`. Bu XATO, o'tkazib yuborilmaydi. */
export function parseColor(color) {
  if (typeof color !== "string") return null;
  const text = color.trim();
  if (!text) return null;

  // `color(srgb 0.616 0.616 0.616 / 0.9)` yoki `color(srgb 1 1 1)`
  const srgb = text.match(/^color\(\s*srgb\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*(?:\/\s*([\d.]+)\s*)?\)$/);
  if (srgb) {
    const [r, g, b] = [srgb[1], srgb[2], srgb[3]].map(Number);
    const a = srgb[4] === undefined ? 1 : Number(srgb[4]);
    if ([r, g, b, a].some((v) => !Number.isFinite(v))) return null;
    return [r * 255, g * 255, b * 255, a];
  }

  const rgb = text.match(/^rgba?\(([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)\s*(?:[,/]\s*([\d.]+)\s*)?\)$/);
  if (rgb) {
    const [r, g, b] = [rgb[1], rgb[2], rgb[3]].map(Number);
    const a = rgb[4] === undefined ? 1 : Number(rgb[4]);
    if ([r, g, b, a].some((v) => !Number.isFinite(v))) return null;
    return [r, g, b, a];
  }

  // `transparent` va noma'lum sintaksis — chaqiruvchi hal qiladi.
  return null;
}

/** Rang → nisbiy yorqinlik (WCAG 2.x). Shaffof/o'qilmas — `null`. */
export function luminance(color) {
  const parsed = parseColor(color);
  if (parsed === null) return null;
  const [r, g, b, a] = parsed;
  if (a === 0) return null;
  const lin = [r, g, b].map((v) => {
    const s = Math.min(255, Math.max(0, v)) / 255;
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2];
}

/** Kontrast nisbati; o'qib bo'lmasa `null` (bu XATO deb hisoblanadi). */
export function ratio(fg, bg) {
  const a = luminance(fg);
  const b = luminance(bg);
  if (a === null || b === null) return null;
  const [hi, lo] = a > b ? [a, b] : [b, a];
  return (hi + 0.05) / (lo + 0.05);
}

/** `color-mix(in srgb, A w, B 1-w)` — brauzer hisoblaganidek.
 *  Har ikkisi `parseColor` bilan o'qiladigan bo'lishi shart. */
export function mix(a, b, w = 0.65) {
  const pa = parseColor(a);
  const pb = parseColor(b);
  if (pa === null || pb === null) return null;
  const out = [0, 1, 2].map((i) => Math.round(pa[i] * w + pb[i] * (1 - w)));
  return `rgb(${out.join(", ")})`;
}

/** Ikkita rangni qatlamlaydi: `top` ostida `bottom`.
 *  `top` qattiq bo'lsa — o'zi qaytadi. Kerak bo'lganda — kompozitsiya. */
export function over(top, bottom) {
  const a = parseColor(top);
  const b = parseColor(bottom);
  if (a === null) return null;
  if (a[3] >= 1) return `rgb(${a.slice(0, 3).map((v) => Math.round(v)).join(", ")})`;
  if (b === null) return null;
  const alpha = a[3];
  const out = [0, 1, 2].map((i) => Math.round(a[i] * alpha + b[i] * (1 - alpha)));
  return `rgb(${out.join(", ")})`;
}

/** Elementning HAQIQIY foni — shaffoflar bo'ylab yuqoriga yuradi.
 *
 *  `glass`/`aurora` kabi uslublarda karta foni shaffof va ostida
 *  GRADIENT yotadi; bunday holatda o'lchab bo'lmaydi — `null`. */
export function backdrop(el, win) {
  const w = win || window;
  let node = el;
  while (node && node.nodeType === 1) {
    const cs = w.getComputedStyle(node);
    const bg = cs.backgroundColor;
    const parsed = parseColor(bg);
    if (parsed !== null && parsed[3] >= 0.999) return bg;
    if (cs.backgroundImage && cs.backgroundImage !== "none") return null; // gradient
    node = node.parentElement;
  }
  return null;
}

/**
 * Joriy (yuklangan) variantni o'lchaydi.
 *
 * MUHIM: chegara — elementning O'Z foniga qarshi. WCAG 1.4.11
 * «qo'shni rang» ni talab qiladi, bu maydon uchun uning o'z foni.
 * `globals.css` `.rw-field-bg` aynan shu juftlikni hisoblaydi
 * (`color-mix(text 65%, field)`), ya'ni bu yerdagi o'lchov CSS
 * matematikasini TASDIQLAYDI.
 */
export function measure(win) {
  const w = win || window;
  const root = w.document.documentElement;
  const style = root.getAttribute("data-style");
  const dark = root.classList.contains("dark");
  const problems = [];
  const skipped = [];
  let checked = 0;

  const target = (what, sel, min, opts) => {
    opts = opts || {};
    const el = w.document.querySelector(sel);
    if (!el) {
      if (opts.optional) skipped.push(what);
      else problems.push({ what, issue: "MAJBURIY nishon topilmadi", fatal: true });
      return;
    }
    checked += 1;
    const cs = w.getComputedStyle(el);

    // Matn nishoni: satrning o'z rangi.
    if (!opts.border && !opts.field) {
      const fg = cs.color;
      // Tugma `rw-accent-bg` bilan to'ldirilgan bo'lishi mumkin, ya'ni
      // uning HAQIQIY foni `body` emas — o'z foni. Gradient bo'lsa
      // (`skeu`) `backgroundColor` uni ko'rsatmaydi va o'lchov
      // ishonchsiz bo'ladi.
      if (opts.ownBg) {
        const own = cs.backgroundColor;
        const parsedOwn = parseColor(own);
        const hasGrad = cs.backgroundImage && cs.backgroundImage !== "none";
        if (hasGrad && (parsedOwn === null || parsedOwn[3] < 0.999)) {
          problems.push({ what, issue: "tugma foni gradient — qo'lda", skip: true, fg });
          return;
        }
        let bg = null;
        if (parsedOwn !== null) {
          bg = parsedOwn[3] >= 0.999 ? own : over(own, backdrop(el.parentElement, w) || "");
        }
        if (bg === null) {
          problems.push({ what, issue: "tugma foni o'qib bo'lmadi", skip: true, fg });
          return;
        }
        const r = ratio(fg, bg);
        if (r === null) problems.push({ what, issue: "o'qib bo'lmadi", fg, bg });
        else if (r < min)
          problems.push({ what, issue: "PAST", ratio: +r.toFixed(2), need: min, fg, bg });
        return;
      }
      const bg = backdrop(el, w);
      if (bg === null) {
        problems.push({ what, issue: "fon gradient/oqib bo'lmadi", skip: true, fg });
        return;
      }
      const r = ratio(fg, bg);
      if (r === null) problems.push({ what, issue: "o'qib bo'lmadi", fg, bg });
      else if (r < min)
        problems.push({ what, issue: "PAST", ratio: +r.toFixed(2), need: min, fg, bg });
      return;
    }

    // Maydon chegarasi: maydon foni + chegara rangi.
    if (opts.field) {
      const own = cs.backgroundColor;
      const parsedOwn = parseColor(own);
      if (parsedOwn === null) {
        problems.push({ what, issue: "maydon foni o'qib bo'lmadi", skip: true, fg: own });
        return;
      }
      const hasGrad = cs.backgroundImage && cs.backgroundImage !== "none";
      if (hasGrad && parsedOwn[3] < 0.999) {
        problems.push({ what, issue: "maydon foni gradient — qo'lda", skip: true });
        return;
      }

      // Shaffof maydon foni — ostidagi qattiq fonga kompozitsiya qilinadi.
      let fieldBg;
      if (parsedOwn[3] >= 0.999) {
        fieldBg = own;
      } else {
        const under = backdrop(el.parentElement, w);
        fieldBg = under === null ? null : over(own, under);
      }
      if (fieldBg === null) {
        problems.push({ what, issue: "maydon foni ostidagi gradient — qo'lda", skip: true });
        return;
      }

      const border = cs.borderTopColor;
      const bw = parseFloat(cs.borderTopWidth) || 0;
      // Chegara yo'q va uslub soya ishlatadi (`clay`, `neu`) — xato emas.
      const parsedBorder = parseColor(border);
      if (bw === 0 || parsedBorder === null || parsedBorder[3] === 0) {
        problems.push({ what, issue: "chegara yo'q (uslub soya ishlatadi)", skip: true });
        return;
      }
      const r = ratio(border, fieldBg);
      if (r === null) problems.push({ what, issue: "o'qib bo'lmadi", fg: border, bg: fieldBg });
      else if (r < min)
        problems.push({
          what,
          issue: "PAST",
          ratio: +r.toFixed(2),
          need: min,
          fg: border,
          bg: fieldBg,
        });
      return;
    }
  };

  // ── Matn nishonlari (AA 4.5:1) ──
  target("tab aktiv", '[aria-current="page"]', 4.5);
  target("tab passiv", "nav a:not([aria-current])", 4.5);
  target("karta sarlavhasi", "h1, h2", 4.5, { optional: true });
  target("maydon yorlig'i", "label", 4.5);
  target("tugma yorlig'i", 'button[type="submit"]', 4.5, { ownBg: true });
  target("havola", "main a[href], form a[href]", 4.5);
  // ── Shakl nishonlari (WCAG 1.4.11 — 3:1) ──
  target("maydon chegarasi", "input", 3.0, { field: true });

  const fatal = problems.some((p) => p.fatal);
  return {
    style,
    dark,
    checked,
    skipped,
    problems,
    fatal,
    ok: checked > 0 && !fatal && !problems.some((p) => !p.skip),
  };
}
