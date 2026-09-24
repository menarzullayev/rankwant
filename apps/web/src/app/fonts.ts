/** Shrift ta'riflari — Google'dan emas, repodan.
 *
 *  Ilgari bu yerda `next/font/google` turardi. U har `next build` da
 *  `fonts.googleapis.com` ga jonli HTTPS so'rov yuborardi va shu bilan
 *  build'ni tashqi xizmatga bog'lardi. Google'ning javobi barqaror emas:
 *  taxminan 60 javobdan bittasi shrift `src` URL'ini kengaytmasiz shaklda
 *  qaytaradi (`https://fonts.gstatic.com/l/font?kit=...`). Turbopack uni
 *  o'qiy olmaydi va butun build yiqiladi:
 *
 *      Error while looking up import map:
 *      next/font/google queries have exactly one entry
 *
 *  Next'ning o'z `retry()` i faqat tarmoq xatosi va 200 bo'lmagan javobni
 *  qamraydi; bu esa 200 — ya'ni hech qachon qayta urinilmaydi. Natijada
 *  CI tasodifiy yiqilardi (vercel/next.js#99114).
 *
 *  `NEXT_FONT_GOOGLE_MOCKED_RESPONSES` ham yaramaydi: u faqat webpack
 *  yuklagichida ishlaydi, Turbopack'da esa resolverni boshqa joyda
 *  buzadi — o'lchandi, 2026-09-24:
 *
 *      Module not found:
 *      '@vercel/turbopack-next/internal/font/google/cssmodule.module.css'
 *
 *  Shuning uchun fayllar BIR MARTA `tools/vendor_fonts.py` bilan
 *  yuklanib, repoga qo'yildi (`src/fonts/`). Endi build diskdan o'qiydi:
 *  deterministik, tarmoqsiz, Google'ga bog'liq emas.
 *
 *  Yuklamasi o'zgarmaydi: `next/font` baribir xuddi shu fayllarni build
 *  vaqtida olib, `/_next/static/media/` ga chiqarardi.
 *
 *  ⚠️ `localFont` — kompilyatsiya vaqtidagi transform, oddiy funksiya
 *  emas. Shuning uchun har bir oila shu faylda `const X = localFont({...})`
 *  ko'rinishida, modul darajasida va inline obyekt bilan yozilishi SHART:
 *
 *      Error: Font loaders must be called and assigned to a const
 *             in the module scope
 *
 *  ya'ni uni tsikl yoki yordamchi funksiya ichida chaqirib bo'lmaydi.
 *  O'lchandi, 2026-09-24. `src` ro'yxatini `tools/vendor_fonts.py`
 *  `src/fonts/manifest.json` asosida chiqaradi.
 *
 *  ⚠️ Yozuv soni fayl soniga TENG EMAS. Google beshta oilaga *variable*
 *  shrift beradi: har weight AYNI faylga ishora qiladi, weight'ni
 *  renderer qo'llaydi. O'lchandi, 2026-09-24 — 110 yozuv, 60 fayl.
 *
 *  ⚠️ Bu faylni qo'lda tahrirlagandan keyin `python3 tools/check_fonts.py`
 *  ni ishga tushiring: u ro'yxatni manifest bilan solishtiradi.
 */

import localFont from "next/font/local";

/** IBM Plex Mono — statik, 15 yozuv / 15 fayl. */
export const plexMono = localFont({
  src: [
    { path: "../fonts/ibm-plex-mono/ibm-plex-mono-0.woff2", weight: "400", style: "normal" },
    { path: "../fonts/ibm-plex-mono/ibm-plex-mono-1.woff2", weight: "400", style: "normal" },
    { path: "../fonts/ibm-plex-mono/ibm-plex-mono-2.woff2", weight: "400", style: "normal" },
    { path: "../fonts/ibm-plex-mono/ibm-plex-mono-3.woff2", weight: "400", style: "normal" },
    { path: "../fonts/ibm-plex-mono/ibm-plex-mono-4.woff2", weight: "400", style: "normal" },
    { path: "../fonts/ibm-plex-mono/ibm-plex-mono-5.woff2", weight: "500", style: "normal" },
    { path: "../fonts/ibm-plex-mono/ibm-plex-mono-6.woff2", weight: "500", style: "normal" },
    { path: "../fonts/ibm-plex-mono/ibm-plex-mono-7.woff2", weight: "500", style: "normal" },
    { path: "../fonts/ibm-plex-mono/ibm-plex-mono-8.woff2", weight: "500", style: "normal" },
    { path: "../fonts/ibm-plex-mono/ibm-plex-mono-9.woff2", weight: "500", style: "normal" },
    { path: "../fonts/ibm-plex-mono/ibm-plex-mono-10.woff2", weight: "600", style: "normal" },
    { path: "../fonts/ibm-plex-mono/ibm-plex-mono-11.woff2", weight: "600", style: "normal" },
    { path: "../fonts/ibm-plex-mono/ibm-plex-mono-12.woff2", weight: "600", style: "normal" },
    { path: "../fonts/ibm-plex-mono/ibm-plex-mono-13.woff2", weight: "600", style: "normal" },
    { path: "../fonts/ibm-plex-mono/ibm-plex-mono-14.woff2", weight: "600", style: "normal" },
  ],
  variable: "--rw-ibm-plex-mono",
  display: "swap",
  preload: false,
});

/** IBM Plex Serif — statik, 20 yozuv / 20 fayl. */
export const plexSerif = localFont({
  src: [
    { path: "../fonts/ibm-plex-serif/ibm-plex-serif-0.woff2", weight: "400", style: "italic" },
    { path: "../fonts/ibm-plex-serif/ibm-plex-serif-1.woff2", weight: "400", style: "italic" },
    { path: "../fonts/ibm-plex-serif/ibm-plex-serif-2.woff2", weight: "400", style: "italic" },
    { path: "../fonts/ibm-plex-serif/ibm-plex-serif-3.woff2", weight: "400", style: "italic" },
    { path: "../fonts/ibm-plex-serif/ibm-plex-serif-4.woff2", weight: "400", style: "italic" },
    { path: "../fonts/ibm-plex-serif/ibm-plex-serif-5.woff2", weight: "600", style: "italic" },
    { path: "../fonts/ibm-plex-serif/ibm-plex-serif-6.woff2", weight: "600", style: "italic" },
    { path: "../fonts/ibm-plex-serif/ibm-plex-serif-7.woff2", weight: "600", style: "italic" },
    { path: "../fonts/ibm-plex-serif/ibm-plex-serif-8.woff2", weight: "600", style: "italic" },
    { path: "../fonts/ibm-plex-serif/ibm-plex-serif-9.woff2", weight: "600", style: "italic" },
    { path: "../fonts/ibm-plex-serif/ibm-plex-serif-10.woff2", weight: "400", style: "normal" },
    { path: "../fonts/ibm-plex-serif/ibm-plex-serif-11.woff2", weight: "400", style: "normal" },
    { path: "../fonts/ibm-plex-serif/ibm-plex-serif-12.woff2", weight: "400", style: "normal" },
    { path: "../fonts/ibm-plex-serif/ibm-plex-serif-13.woff2", weight: "400", style: "normal" },
    { path: "../fonts/ibm-plex-serif/ibm-plex-serif-14.woff2", weight: "400", style: "normal" },
    { path: "../fonts/ibm-plex-serif/ibm-plex-serif-15.woff2", weight: "600", style: "normal" },
    { path: "../fonts/ibm-plex-serif/ibm-plex-serif-16.woff2", weight: "600", style: "normal" },
    { path: "../fonts/ibm-plex-serif/ibm-plex-serif-17.woff2", weight: "600", style: "normal" },
    { path: "../fonts/ibm-plex-serif/ibm-plex-serif-18.woff2", weight: "600", style: "normal" },
    { path: "../fonts/ibm-plex-serif/ibm-plex-serif-19.woff2", weight: "600", style: "normal" },
  ],
  variable: "--rw-ibm-plex-serif",
  display: "swap",
  preload: false,
});

/** Inter — variable, 21 yozuv / 7 fayl. */
export const inter = localFont({
  src: [
    { path: "../fonts/inter/inter-0.woff2", weight: "400", style: "normal" },
    { path: "../fonts/inter/inter-1.woff2", weight: "400", style: "normal" },
    { path: "../fonts/inter/inter-2.woff2", weight: "400", style: "normal" },
    { path: "../fonts/inter/inter-3.woff2", weight: "400", style: "normal" },
    { path: "../fonts/inter/inter-4.woff2", weight: "400", style: "normal" },
    { path: "../fonts/inter/inter-5.woff2", weight: "400", style: "normal" },
    { path: "../fonts/inter/inter-6.woff2", weight: "400", style: "normal" },
    { path: "../fonts/inter/inter-0.woff2", weight: "500", style: "normal" },
    { path: "../fonts/inter/inter-1.woff2", weight: "500", style: "normal" },
    { path: "../fonts/inter/inter-2.woff2", weight: "500", style: "normal" },
    { path: "../fonts/inter/inter-3.woff2", weight: "500", style: "normal" },
    { path: "../fonts/inter/inter-4.woff2", weight: "500", style: "normal" },
    { path: "../fonts/inter/inter-5.woff2", weight: "500", style: "normal" },
    { path: "../fonts/inter/inter-6.woff2", weight: "500", style: "normal" },
    { path: "../fonts/inter/inter-0.woff2", weight: "600", style: "normal" },
    { path: "../fonts/inter/inter-1.woff2", weight: "600", style: "normal" },
    { path: "../fonts/inter/inter-2.woff2", weight: "600", style: "normal" },
    { path: "../fonts/inter/inter-3.woff2", weight: "600", style: "normal" },
    { path: "../fonts/inter/inter-4.woff2", weight: "600", style: "normal" },
    { path: "../fonts/inter/inter-5.woff2", weight: "600", style: "normal" },
    { path: "../fonts/inter/inter-6.woff2", weight: "600", style: "normal" },
  ],
  variable: "--rw-inter",
  display: "swap",
  preload: false,
});

/** Plus Jakarta Sans — variable, 12 yozuv / 4 fayl. */
export const jakarta = localFont({
  src: [
    { path: "../fonts/plus-jakarta-sans/plus-jakarta-sans-0.woff2", weight: "400", style: "normal" },
    { path: "../fonts/plus-jakarta-sans/plus-jakarta-sans-1.woff2", weight: "400", style: "normal" },
    { path: "../fonts/plus-jakarta-sans/plus-jakarta-sans-2.woff2", weight: "400", style: "normal" },
    { path: "../fonts/plus-jakarta-sans/plus-jakarta-sans-3.woff2", weight: "400", style: "normal" },
    { path: "../fonts/plus-jakarta-sans/plus-jakarta-sans-0.woff2", weight: "500", style: "normal" },
    { path: "../fonts/plus-jakarta-sans/plus-jakarta-sans-1.woff2", weight: "500", style: "normal" },
    { path: "../fonts/plus-jakarta-sans/plus-jakarta-sans-2.woff2", weight: "500", style: "normal" },
    { path: "../fonts/plus-jakarta-sans/plus-jakarta-sans-3.woff2", weight: "500", style: "normal" },
    { path: "../fonts/plus-jakarta-sans/plus-jakarta-sans-0.woff2", weight: "600", style: "normal" },
    { path: "../fonts/plus-jakarta-sans/plus-jakarta-sans-1.woff2", weight: "600", style: "normal" },
    { path: "../fonts/plus-jakarta-sans/plus-jakarta-sans-2.woff2", weight: "600", style: "normal" },
    { path: "../fonts/plus-jakarta-sans/plus-jakarta-sans-3.woff2", weight: "600", style: "normal" },
  ],
  variable: "--rw-plus-jakarta-sans",
  display: "swap",
  preload: false,
});

/** Roboto — variable, 27 yozuv / 9 fayl. */
export const roboto = localFont({
  src: [
    { path: "../fonts/roboto/roboto-0.woff2", weight: "400", style: "normal" },
    { path: "../fonts/roboto/roboto-1.woff2", weight: "400", style: "normal" },
    { path: "../fonts/roboto/roboto-2.woff2", weight: "400", style: "normal" },
    { path: "../fonts/roboto/roboto-3.woff2", weight: "400", style: "normal" },
    { path: "../fonts/roboto/roboto-4.woff2", weight: "400", style: "normal" },
    { path: "../fonts/roboto/roboto-5.woff2", weight: "400", style: "normal" },
    { path: "../fonts/roboto/roboto-6.woff2", weight: "400", style: "normal" },
    { path: "../fonts/roboto/roboto-7.woff2", weight: "400", style: "normal" },
    { path: "../fonts/roboto/roboto-8.woff2", weight: "400", style: "normal" },
    { path: "../fonts/roboto/roboto-0.woff2", weight: "500", style: "normal" },
    { path: "../fonts/roboto/roboto-1.woff2", weight: "500", style: "normal" },
    { path: "../fonts/roboto/roboto-2.woff2", weight: "500", style: "normal" },
    { path: "../fonts/roboto/roboto-3.woff2", weight: "500", style: "normal" },
    { path: "../fonts/roboto/roboto-4.woff2", weight: "500", style: "normal" },
    { path: "../fonts/roboto/roboto-5.woff2", weight: "500", style: "normal" },
    { path: "../fonts/roboto/roboto-6.woff2", weight: "500", style: "normal" },
    { path: "../fonts/roboto/roboto-7.woff2", weight: "500", style: "normal" },
    { path: "../fonts/roboto/roboto-8.woff2", weight: "500", style: "normal" },
    { path: "../fonts/roboto/roboto-0.woff2", weight: "700", style: "normal" },
    { path: "../fonts/roboto/roboto-1.woff2", weight: "700", style: "normal" },
    { path: "../fonts/roboto/roboto-2.woff2", weight: "700", style: "normal" },
    { path: "../fonts/roboto/roboto-3.woff2", weight: "700", style: "normal" },
    { path: "../fonts/roboto/roboto-4.woff2", weight: "700", style: "normal" },
    { path: "../fonts/roboto/roboto-5.woff2", weight: "700", style: "normal" },
    { path: "../fonts/roboto/roboto-6.woff2", weight: "700", style: "normal" },
    { path: "../fonts/roboto/roboto-7.woff2", weight: "700", style: "normal" },
    { path: "../fonts/roboto/roboto-8.woff2", weight: "700", style: "normal" },
  ],
  variable: "--rw-roboto",
  display: "swap",
  preload: false,
});

/** DM Sans — variable, 6 yozuv / 2 fayl. */
export const dmSans = localFont({
  src: [
    { path: "../fonts/dm-sans/dm-sans-0.woff2", weight: "400", style: "normal" },
    { path: "../fonts/dm-sans/dm-sans-1.woff2", weight: "400", style: "normal" },
    { path: "../fonts/dm-sans/dm-sans-0.woff2", weight: "500", style: "normal" },
    { path: "../fonts/dm-sans/dm-sans-1.woff2", weight: "500", style: "normal" },
    { path: "../fonts/dm-sans/dm-sans-0.woff2", weight: "600", style: "normal" },
    { path: "../fonts/dm-sans/dm-sans-1.woff2", weight: "600", style: "normal" },
  ],
  variable: "--rw-dm-sans",
  display: "swap",
  preload: false,
});

/** Lexend — variable, 9 yozuv / 3 fayl. */
export const lexend = localFont({
  src: [
    { path: "../fonts/lexend/lexend-0.woff2", weight: "400", style: "normal" },
    { path: "../fonts/lexend/lexend-1.woff2", weight: "400", style: "normal" },
    { path: "../fonts/lexend/lexend-2.woff2", weight: "400", style: "normal" },
    { path: "../fonts/lexend/lexend-0.woff2", weight: "500", style: "normal" },
    { path: "../fonts/lexend/lexend-1.woff2", weight: "500", style: "normal" },
    { path: "../fonts/lexend/lexend-2.woff2", weight: "500", style: "normal" },
    { path: "../fonts/lexend/lexend-0.woff2", weight: "600", style: "normal" },
    { path: "../fonts/lexend/lexend-1.woff2", weight: "600", style: "normal" },
    { path: "../fonts/lexend/lexend-2.woff2", weight: "600", style: "normal" },
  ],
  variable: "--rw-lexend",
  display: "swap",
  preload: false,
});

