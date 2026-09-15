/** Tabler ikonkalari (MIT), 24×24 to'r.
 *
 *  Generatsiya qilingan — `tools/gen-icon-packs.mjs` bilan qayta yasash mumkin.
 *  Qo'lda tahrirlanmaydi.
 *
 *  ⚠️ Manba CDN'dan **bir marta** olinadi va shu faylga yoziladi: ilova
 *  ishga tushganda tarmoqqa chiqmaydi, ya'ni yangi dependency ham,
 *  kutubxona yangilanishini kuzatish ham kerak emas.
 *
 *  164 ta ikonka.
 */

type IconProps = { className?: string };

const base = { viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 2, strokeLinecap: "round" as const, strokeLinejoin: "round" as const, xmlns: "http://www.w3.org/2000/svg" };

/** Tabler `plus` (MIT). */
export const TbPlus = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 5l0 14" />
    <path d="M5 12l14 0" />
  </svg>
);

/** Tabler `bookmark` (MIT). */
export const TbBookmark = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M18 7v14l-6 -4l-6 4v-14a4 4 0 0 1 4 -4h4a4 4 0 0 1 4 4z" />
  </svg>
);

/** Tabler `ban` (MIT). */
export const TbBan = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0 -18 0" />
    <path d="M5.7 5.7l12.6 12.6" />
  </svg>
);

/** Tabler `circle-x` (MIT). */
export const TbCircleX = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0 -18 0" />
    <path d="M10 10l4 4m0 -4l-4 4" />
  </svg>
);

/** Tabler `clipboard` (MIT). */
export const TbClipboard = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M9 5h-2a2 2 0 0 0 -2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2 -2v-12a2 2 0 0 0 -2 -2h-2" />
    <path d="M9 3m0 2a2 2 0 0 1 2 -2h2a2 2 0 0 1 2 2v0a2 2 0 0 1 -2 2h-2a2 2 0 0 1 -2 -2z" />
  </svg>
);

/** Tabler `copy` (MIT). */
export const TbCopy = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M7 7m0 2.667a2.667 2.667 0 0 1 2.667 -2.667h8.666a2.667 2.667 0 0 1 2.667 2.667v8.666a2.667 2.667 0 0 1 -2.667 2.667h-8.666a2.667 2.667 0 0 1 -2.667 -2.667z" />
    <path d="M4.012 16.737a2.005 2.005 0 0 1 -1.012 -1.737v-10c0 -1.1 .9 -2 2 -2h10c.75 0 1.158 .385 1.5 1" />
  </svg>
);

/** Tabler `trash` (MIT). */
export const TbTrash = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M4 7l16 0" />
    <path d="M10 11l0 6" />
    <path d="M14 11l0 6" />
    <path d="M5 7l1 12a2 2 0 0 0 2 2h8a2 2 0 0 0 2 -2l1 -12" />
    <path d="M9 7v-3a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v3" />
  </svg>
);

/** Tabler `download` (MIT). */
export const TbDownload = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2 -2v-2" />
    <path d="M7 11l5 5l5 -5" />
    <path d="M12 4l0 12" />
  </svg>
);

/** Tabler `pencil` (MIT). */
export const TbPencil = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M4 20h4l10.5 -10.5a2.828 2.828 0 1 0 -4 -4l-10.5 10.5v4" />
    <path d="M13.5 6.5l4 4" />
  </svg>
);

/** Tabler `eye` (MIT). */
export const TbEye = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M10 12a2 2 0 1 0 4 0a2 2 0 0 0 -4 0" />
    <path d="M21 12c-2.4 4 -5.4 6 -9 6c-3.6 0 -6.6 -2 -9 -6c2.4 -4 5.4 -6 9 -6c3.6 0 6.6 2 9 6" />
  </svg>
);

/** Tabler `eye-off` (MIT). */
export const TbEyeOff = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M10.585 10.587a2 2 0 0 0 2.829 2.828" />
    <path d="M16.681 16.673a8.717 8.717 0 0 1 -4.681 1.327c-3.6 0 -6.6 -2 -9 -6c1.272 -2.12 2.712 -3.678 4.32 -4.674m2.86 -1.146a9.055 9.055 0 0 1 1.82 -.18c3.6 0 6.6 2 9 6c-.666 1.11 -1.379 2.067 -2.138 2.87" />
    <path d="M3 3l18 18" />
  </svg>
);

/** Tabler `filter` (MIT). */
export const TbFilter = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M4 4h16v2.172a2 2 0 0 1 -.586 1.414l-4.414 4.414v7l-6 2v-8.5l-4.48 -4.928a2 2 0 0 1 -.52 -1.345v-2.227z" />
  </svg>
);

/** Tabler `wand` (MIT). */
export const TbWand = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M6 21l15 -15l-3 -3l-15 15l3 3" />
    <path d="M15 6l3 3" />
    <path d="M9 3a2 2 0 0 0 2 2a2 2 0 0 0 -2 2a2 2 0 0 0 -2 -2a2 2 0 0 0 2 -2" />
    <path d="M19 13a2 2 0 0 0 2 2a2 2 0 0 0 -2 2a2 2 0 0 0 -2 -2a2 2 0 0 0 2 -2" />
  </svg>
);

/** Tabler `maximize` (MIT). */
export const TbMaximize = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M4 8v-2a2 2 0 0 1 2 -2h2" />
    <path d="M4 16v2a2 2 0 0 0 2 2h2" />
    <path d="M16 4h2a2 2 0 0 1 2 2v2" />
    <path d="M16 20h2a2 2 0 0 0 2 -2v-2" />
  </svg>
);

/** Tabler `help-circle` (MIT). */
export const TbHelpCircle = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M3 12a9 9 0 1 0 18 0a9 9 0 0 0 -18 0" />
    <path d="M12 16v.01" />
    <path d="M12 13a2 2 0 0 0 .914 -3.782a1.98 1.98 0 0 0 -2.414 .483" />
  </svg>
);

/** Tabler `pin` (MIT). */
export const TbPin = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M15 4.5l-4 4l-4 1.5l-1.5 1.5l7 7l1.5 -1.5l1.5 -4l4 -4" />
    <path d="M9 15l-4.5 4.5" />
    <path d="M14.5 4l5.5 5.5" />
  </svg>
);

/** Tabler `printer` (MIT). */
export const TbPrinter = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M17 17h2a2 2 0 0 0 2 -2v-4a2 2 0 0 0 -2 -2h-14a2 2 0 0 0 -2 2v4a2 2 0 0 0 2 2h2" />
    <path d="M17 9v-4a2 2 0 0 0 -2 -2h-6a2 2 0 0 0 -2 2v4" />
    <path d="M7 13m0 2a2 2 0 0 1 2 -2h6a2 2 0 0 1 2 2v4a2 2 0 0 1 -2 2h-6a2 2 0 0 1 -2 -2z" />
  </svg>
);

/** Tabler `refresh` (MIT). */
export const TbRefresh = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M20 11a8.1 8.1 0 0 0 -15.5 -2m-.5 -4v4h4" />
    <path d="M4 13a8.1 8.1 0 0 0 15.5 2m.5 4v-4h-4" />
  </svg>
);

/** Tabler `device-floppy` (MIT). */
export const TbDeviceFloppy = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M6 4h10l4 4v10a2 2 0 0 1 -2 2h-12a2 2 0 0 1 -2 -2v-12a2 2 0 0 1 2 -2" />
    <path d="M12 14m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0" />
    <path d="M14 4l0 4l-6 0l0 -4" />
  </svg>
);

/** Tabler `search` (MIT). */
export const TbSearch = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M10 10m-7 0a7 7 0 1 0 14 0a7 7 0 1 0 -14 0" />
    <path d="M21 21l-6 -6" />
  </svg>
);

/** Tabler `share-2` (MIT). */
export const TbShare2 = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M8 9h-1a2 2 0 0 0 -2 2v8a2 2 0 0 0 2 2h10a2 2 0 0 0 2 -2v-8a2 2 0 0 0 -2 -2h-1" />
    <path d="M12 14v-11" />
    <path d="M9 6l3 -3l3 3" />
  </svg>
);

/** Tabler `adjustments-horizontal` (MIT). */
export const TbAdjustmentsHorizontal = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M14 6m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0" />
    <path d="M4 6l8 0" />
    <path d="M16 6l4 0" />
    <path d="M8 12m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0" />
    <path d="M4 12l2 0" />
    <path d="M10 12l10 0" />
    <path d="M17 18m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0" />
    <path d="M4 18l11 0" />
    <path d="M19 18l1 0" />
  </svg>
);

/** Tabler `sort-ascending` (MIT). */
export const TbSortAscending = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M4 6l7 0" />
    <path d="M4 12l7 0" />
    <path d="M4 18l9 0" />
    <path d="M15 9l3 -3l3 3" />
    <path d="M18 6l0 12" />
  </svg>
);

/** Tabler `sort-descending` (MIT). */
export const TbSortDescending = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M4 6l9 0" />
    <path d="M4 12l7 0" />
    <path d="M4 18l7 0" />
    <path d="M15 15l3 3l3 -3" />
    <path d="M18 6l0 12" />
  </svg>
);

/** Tabler `volume-2` (MIT). */
export const TbVolume2 = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M15 8a5 5 0 0 1 0 8" />
    <path d="M6 15h-2a1 1 0 0 1 -1 -1v-4a1 1 0 0 1 1 -1h2l3.5 -4.5a.8 .8 0 0 1 1.5 .5v14a.8 .8 0 0 1 -1.5 .5l-3.5 -4.5" />
  </svg>
);

/** Tabler `upload` (MIT). */
export const TbUpload = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2 -2v-2" />
    <path d="M7 9l5 -5l5 5" />
    <path d="M12 4l0 12" />
  </svg>
);

/** Tabler `route` (MIT). */
export const TbRoute = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M3 19a2 2 0 1 0 4 0a2 2 0 0 0 -4 0" />
    <path d="M19 7a2 2 0 1 0 0 -4a2 2 0 0 0 0 4z" />
    <path d="M11 19h5.5a3.5 3.5 0 0 0 0 -7h-8a3.5 3.5 0 0 1 0 -7h4.5" />
  </svg>
);

/** Tabler `news` (MIT). */
export const TbNews = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M16 6h3a1 1 0 0 1 1 1v11a2 2 0 0 1 -4 0v-13a1 1 0 0 0 -1 -1h-10a1 1 0 0 0 -1 1v12a3 3 0 0 0 3 3h11" />
    <path d="M8 8l4 0" />
    <path d="M8 12l4 0" />
    <path d="M8 16l4 0" />
  </svg>
);

/** Tabler `headphones` (MIT). */
export const TbHeadphones = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M4 13m0 2a2 2 0 0 1 2 -2h1a2 2 0 0 1 2 2v3a2 2 0 0 1 -2 2h-1a2 2 0 0 1 -2 -2z" />
    <path d="M15 13m0 2a2 2 0 0 1 2 -2h1a2 2 0 0 1 2 2v3a2 2 0 0 1 -2 2h-1a2 2 0 0 1 -2 -2z" />
    <path d="M4 15v-3a8 8 0 0 1 16 0v3" />
  </svg>
);

/** Tabler `folder` (MIT). */
export const TbFolder = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M5 4h4l3 3h7a2 2 0 0 1 2 2v8a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2v-11a2 2 0 0 1 2 -2" />
  </svg>
);

/** Tabler `code` (MIT). */
export const TbCode = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M7 8l-4 4l4 4" />
    <path d="M17 8l4 4l-4 4" />
    <path d="M14 4l-4 16" />
  </svg>
);

/** Tabler `school` (MIT). */
export const TbSchool = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M22 9l-10 -4l-10 4l10 4l10 -4v6" />
    <path d="M6 10.6v5.4a6 3 0 0 0 12 0v-5.4" />
  </svg>
);

/** Tabler `file` (MIT). */
export const TbFile = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M14 3v4a1 1 0 0 0 1 1h4" />
    <path d="M17 21h-10a2 2 0 0 1 -2 -2v-14a2 2 0 0 1 2 -2h7l5 5v11a2 2 0 0 1 -2 2z" />
  </svg>
);

/** Tabler `photo` (MIT). */
export const TbPhoto = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M15 8h.01" />
    <path d="M3 6a3 3 0 0 1 3 -3h12a3 3 0 0 1 3 3v12a3 3 0 0 1 -3 3h-12a3 3 0 0 1 -3 -3v-12z" />
    <path d="M3 16l5 -5c.928 -.893 2.072 -.893 3 0l5 5" />
    <path d="M14 14l1 -1c.928 -.893 2.072 -.893 3 0l3 3" />
  </svg>
);

/** Tabler `stack` (MIT). */
export const TbStack = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 6l-8 4l8 4l8 -4l-8 -4" />
    <path d="M4 14l8 4l8 -4" />
  </svg>
);

/** Tabler `file-text` (MIT). */
export const TbFileText = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M14 3v4a1 1 0 0 0 1 1h4" />
    <path d="M17 21h-10a2 2 0 0 1 -2 -2v-14a2 2 0 0 1 2 -2h7l5 5v11a2 2 0 0 1 -2 2z" />
    <path d="M9 9l1 0" />
    <path d="M9 13l6 0" />
    <path d="M9 17l6 0" />
  </svg>
);

/** Tabler `book` (MIT). */
export const TbBook = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M3 19a9 9 0 0 1 9 0a9 9 0 0 1 9 0" />
    <path d="M3 6a9 9 0 0 1 9 0a9 9 0 0 1 9 0" />
    <path d="M3 6l0 13" />
    <path d="M12 6l0 13" />
    <path d="M21 6l0 13" />
  </svg>
);

/** Tabler `map` (MIT). */
export const TbMap = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M3 7l6 -3l6 3l6 -3v13l-6 3l-6 -3l-6 3v-13" />
    <path d="M9 4v13" />
    <path d="M15 7v13" />
  </svg>
);

/** Tabler `shoe` (MIT). */
export const TbShoe = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M4 6h5.426a1 1 0 0 1 .863 .496l1.064 1.823a3 3 0 0 0 1.896 1.407l4.677 1.114a4 4 0 0 1 3.074 3.89v2.27a1 1 0 0 1 -1 1h-16a1 1 0 0 1 -1 -1v-10a1 1 0 0 1 1 -1z" />
    <path d="M14 13l1 -2" />
    <path d="M8 18v-1a4 4 0 0 0 -4 -4h-1" />
    <path d="M10 12l1.5 -3" />
  </svg>
);

/** Tabler `tag` (MIT). */
export const TbTag = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M7.5 7.5m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0" />
    <path d="M3 6v5.172a2 2 0 0 0 .586 1.414l7.71 7.71a2.41 2.41 0 0 0 3.408 0l5.592 -5.592a2.41 2.41 0 0 0 0 -3.408l-7.71 -7.71a2 2 0 0 0 -1.414 -.586h-5.172a3 3 0 0 0 -3 3z" />
  </svg>
);

/** Tabler `terminal` (MIT). */
export const TbTerminal = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M5 7l5 5l-5 5" />
    <path d="M12 19l7 0" />
  </svg>
);

/** Tabler `flask` (MIT). */
export const TbFlask = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M9 3l6 0" />
    <path d="M10 9l4 0" />
    <path d="M10 3v6l-4 11a.7 .7 0 0 0 .5 1h11a.7 .7 0 0 0 .5 -1l-4 -11v-6" />
  </svg>
);

/** Tabler `video` (MIT). */
export const TbVideo = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M15 10l4.553 -2.276a1 1 0 0 1 1.447 .894v6.764a1 1 0 0 1 -1.447 .894l-4.553 -2.276v-4z" />
    <path d="M3 6m0 2a2 2 0 0 1 2 -2h8a2 2 0 0 1 2 2v8a2 2 0 0 1 -2 2h-8a2 2 0 0 1 -2 -2z" />
  </svg>
);

/** Tabler `target` (MIT). */
export const TbTarget = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 12m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0" />
    <path d="M12 12m-5 0a5 5 0 1 0 10 0a5 5 0 1 0 -10 0" />
    <path d="M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0 -18 0" />
  </svg>
);

/** Tabler `calendar` (MIT). */
export const TbCalendar = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M4 7a2 2 0 0 1 2 -2h12a2 2 0 0 1 2 2v12a2 2 0 0 1 -2 2h-12a2 2 0 0 1 -2 -2v-12z" />
    <path d="M16 3v4" />
    <path d="M8 3v4" />
    <path d="M4 11h16" />
    <path d="M11 15h1" />
    <path d="M12 15v3" />
  </svg>
);

/** Tabler `clock` (MIT). */
export const TbClock = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M3 12a9 9 0 1 0 18 0a9 9 0 0 0 -18 0" />
    <path d="M12 7v5l3 3" />
  </svg>
);

/** Tabler `swords` (MIT). */
export const TbSwords = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M21 3v5l-11 9l-4 4l-3 -3l4 -4l9 -11z" />
    <path d="M5 13l6 6" />
    <path d="M14.32 17.32l3.68 3.68l3 -3l-3.365 -3.365" />
    <path d="M10 5.5l-2 -2.5h-5v5l3 2.5" />
  </svg>
);

/** Tabler `flag` (MIT). */
export const TbFlag = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M5 5a5 5 0 0 1 7 0a5 5 0 0 0 7 0v9a5 5 0 0 1 -7 0a5 5 0 0 0 -7 0v-9z" />
    <path d="M5 21v-7" />
  </svg>
);

/** Tabler `chart-bar` (MIT). */
export const TbChartBar = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M3 13a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v6a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1z" />
    <path d="M15 9a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v10a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1z" />
    <path d="M9 5a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v14a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1z" />
    <path d="M4 20h14" />
  </svg>
);

/** Tabler `radio` (MIT). */
export const TbRadio = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M14 3l-9.371 3.749a1 1 0 0 0 -.629 .928v11.323a1 1 0 0 0 1 1h14a1 1 0 0 0 1 -1v-11a1 1 0 0 0 -1 -1h-14.5" />
    <path d="M4 12h16" />
    <path d="M7 12v-2" />
    <path d="M17 16v.01" />
    <path d="M13 16v.01" />
  </svg>
);

/** Tabler `lock` (MIT). */
export const TbLock = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M5 13a2 2 0 0 1 2 -2h10a2 2 0 0 1 2 2v6a2 2 0 0 1 -2 2h-10a2 2 0 0 1 -2 -2v-6z" />
    <path d="M11 16a1 1 0 1 0 2 0a1 1 0 0 0 -2 0" />
    <path d="M8 11v-4a4 4 0 1 1 8 0v4" />
  </svg>
);

/** Tabler `trending-up` (MIT). */
export const TbTrendingUp = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M3 17l6 -6l4 4l8 -8" />
    <path d="M14 7l7 0l0 7" />
  </svg>
);

/** Tabler `clipboard-check` (MIT). */
export const TbClipboardCheck = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M9 5h-2a2 2 0 0 0 -2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2 -2v-12a2 2 0 0 0 -2 -2h-2" />
    <path d="M9 3m0 2a2 2 0 0 1 2 -2h2a2 2 0 0 1 2 2v0a2 2 0 0 1 -2 2h-2a2 2 0 0 1 -2 -2z" />
    <path d="M9 14l2 2l4 -4" />
  </svg>
);

/** Tabler `table` (MIT). */
export const TbTable = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M3 5a2 2 0 0 1 2 -2h14a2 2 0 0 1 2 2v14a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2v-14z" />
    <path d="M3 10h18" />
    <path d="M10 3v18" />
  </svg>
);

/** Tabler `users` (MIT). */
export const TbUsers = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M9 7m-4 0a4 4 0 1 0 8 0a4 4 0 1 0 -8 0" />
    <path d="M3 21v-2a4 4 0 0 1 4 -4h4a4 4 0 0 1 4 4v2" />
    <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    <path d="M21 21v-2a4 4 0 0 0 -3 -3.85" />
  </svg>
);

/** Tabler `globe` (MIT). */
export const TbGlobe = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M7 9a4 4 0 1 0 8 0a4 4 0 0 0 -8 0" />
    <path d="M5.75 15a8.015 8.015 0 1 0 9.25 -13" />
    <path d="M11 17v4" />
    <path d="M7 21h8" />
  </svg>
);

/** Tabler `device-desktop` (MIT). */
export const TbDeviceDesktop = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M3 5a1 1 0 0 1 1 -1h16a1 1 0 0 1 1 1v10a1 1 0 0 1 -1 1h-16a1 1 0 0 1 -1 -1v-10z" />
    <path d="M7 20h10" />
    <path d="M9 16v4" />
    <path d="M15 16v4" />
  </svg>
);

/** Tabler `device-laptop` (MIT). */
export const TbDeviceLaptop = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M3 19l18 0" />
    <path d="M5 6m0 1a1 1 0 0 1 1 -1h12a1 1 0 0 1 1 1v8a1 1 0 0 1 -1 1h-12a1 1 0 0 1 -1 -1z" />
  </svg>
);

/** Tabler `device-mobile` (MIT). */
export const TbDeviceMobile = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M6 5a2 2 0 0 1 2 -2h8a2 2 0 0 1 2 2v14a2 2 0 0 1 -2 2h-8a2 2 0 0 1 -2 -2v-14z" />
    <path d="M11 4h2" />
    <path d="M12 17v.01" />
  </svg>
);

/** Tabler `qrcode` (MIT). */
export const TbQrcode = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M4 4m0 1a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v4a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1z" />
    <path d="M7 17l0 .01" />
    <path d="M14 4m0 1a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v4a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1z" />
    <path d="M7 7l0 .01" />
    <path d="M4 14m0 1a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v4a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1z" />
    <path d="M17 7l0 .01" />
    <path d="M14 14l3 0" />
    <path d="M20 14l0 .01" />
    <path d="M14 14l0 3" />
    <path d="M14 20l3 0" />
    <path d="M17 17l3 0" />
    <path d="M20 17l0 3" />
  </svg>
);

/** Tabler `device-tablet` (MIT). */
export const TbDeviceTablet = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M5 4a1 1 0 0 1 1 -1h12a1 1 0 0 1 1 1v16a1 1 0 0 1 -1 1h-12a1 1 0 0 1 -1 -1v-16z" />
    <path d="M11 17a1 1 0 1 0 2 0a1 1 0 0 0 -2 0" />
  </svg>
);

/** Tabler `pointer` (MIT). */
export const TbPointer = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M7.904 17.563a1.2 1.2 0 0 0 2.228 .308l2.09 -3.093l4.907 4.907a1.067 1.067 0 0 0 1.509 0l1.047 -1.047a1.067 1.067 0 0 0 0 -1.509l-4.907 -4.907l3.113 -2.09a1.2 1.2 0 0 0 -.309 -2.228l-13.582 -3.904l3.904 13.563z" />
  </svg>
);

/** Tabler `clipboard-list` (MIT). */
export const TbClipboardList = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M9 5h-2a2 2 0 0 0 -2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2 -2v-12a2 2 0 0 0 -2 -2h-2" />
    <path d="M9 3m0 2a2 2 0 0 1 2 -2h2a2 2 0 0 1 2 2v0a2 2 0 0 1 -2 2h-2a2 2 0 0 1 -2 -2z" />
    <path d="M9 12l.01 0" />
    <path d="M13 12l2 0" />
    <path d="M9 16l.01 0" />
    <path d="M13 16l2 0" />
  </svg>
);

/** Tabler `folder-open` (MIT). */
export const TbFolderOpen = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M5 19l2.757 -7.351a1 1 0 0 1 .936 -.649h12.307a1 1 0 0 1 .986 1.164l-.996 5.211a2 2 0 0 1 -1.964 1.625h-14.026a2 2 0 0 1 -2 -2v-11a2 2 0 0 1 2 -2h4l3 3h7a2 2 0 0 1 2 2v2" />
  </svg>
);

/** Tabler `message-circle` (MIT). */
export const TbMessageCircle = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M3 20l1.3 -3.9c-2.324 -3.437 -1.426 -7.872 2.1 -10.374c3.526 -2.501 8.59 -2.296 11.845 .48c3.255 2.777 3.695 7.266 1.029 10.501c-2.666 3.235 -7.615 4.215 -11.574 2.293l-4.7 1" />
  </svg>
);

/** Tabler `compass` (MIT). */
export const TbCompass = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M8 16l2 -6l6 -2l-2 6l-6 2" />
    <path d="M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0 -18 0" />
    <path d="M12 3l0 2" />
    <path d="M12 19l0 2" />
    <path d="M3 12l2 0" />
    <path d="M19 12l2 0" />
  </svg>
);

/** Tabler `bell-off` (MIT). */
export const TbBellOff = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M9.346 5.353c.21 -.129 .428 -.246 .654 -.353a2 2 0 1 1 4 0a7 7 0 0 1 4 6v3m-1 3h-13a4 4 0 0 0 2 -3v-3a6.996 6.996 0 0 1 1.273 -3.707" />
    <path d="M9 17v1a3 3 0 0 0 6 0v-1" />
    <path d="M3 3l18 18" />
  </svg>
);

/** Tabler `settings` (MIT). */
export const TbSettings = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M10.325 4.317c.426 -1.756 2.924 -1.756 3.35 0a1.724 1.724 0 0 0 2.573 1.066c1.543 -.94 3.31 .826 2.37 2.37a1.724 1.724 0 0 0 1.065 2.572c1.756 .426 1.756 2.924 0 3.35a1.724 1.724 0 0 0 -1.066 2.573c.94 1.543 -.826 3.31 -2.37 2.37a1.724 1.724 0 0 0 -2.572 1.065c-.426 1.756 -2.924 1.756 -3.35 0a1.724 1.724 0 0 0 -2.573 -1.066c-1.543 .94 -3.31 -.826 -2.37 -2.37a1.724 1.724 0 0 0 -1.065 -2.572c-1.756 -.426 -1.756 -2.924 0 -3.35a1.724 1.724 0 0 0 1.066 -2.573c-.94 -1.543 .826 -3.31 2.37 -2.37c1 .608 2.296 .07 2.572 -1.065z" />
    <path d="M9 12a3 3 0 1 0 6 0a3 3 0 0 0 -6 0" />
  </svg>
);

/** Tabler `alert-triangle` (MIT). */
export const TbAlertTriangle = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 9v4" />
    <path d="M10.363 3.591l-8.106 13.534a1.914 1.914 0 0 0 1.636 2.871h16.214a1.914 1.914 0 0 0 1.636 -2.87l-8.106 -13.536a1.914 1.914 0 0 0 -3.274 0z" />
    <path d="M12 16h.01" />
  </svg>
);

/** Tabler `wifi-off` (MIT). */
export const TbWifiOff = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 18l.01 0" />
    <path d="M9.172 15.172a4 4 0 0 1 5.656 0" />
    <path d="M6.343 12.343a7.963 7.963 0 0 1 3.864 -2.14m4.163 .155a7.965 7.965 0 0 1 3.287 2" />
    <path d="M3.515 9.515a12 12 0 0 1 3.544 -2.455m3.101 -.92a12 12 0 0 1 10.325 3.374" />
    <path d="M3 3l18 18" />
  </svg>
);

/** Tabler `flame` (MIT). */
export const TbFlame = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 10.941c2.333 -3.308 .167 -7.823 -1 -8.941c0 3.395 -2.235 5.299 -3.667 6.706c-1.43 1.408 -2.333 3.621 -2.333 5.588c0 3.704 3.134 6.706 7 6.706s7 -3.002 7 -6.706c0 -1.712 -1.232 -4.403 -2.333 -5.588c-2.084 3.353 -3.257 3.353 -4.667 2.235" />
  </svg>
);

/** Tabler `clock-x` (MIT). */
export const TbClockX = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M20.926 13.15a9 9 0 1 0 -7.835 7.784" />
    <path d="M12 7v5l2 2" />
    <path d="M22 22l-5 -5" />
    <path d="M17 22l5 -5" />
  </svg>
);

/** Tabler `language` (MIT). */
export const TbLanguage = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M9 6.371c0 4.418 -2.239 6.629 -5 6.629" />
    <path d="M4 6.371h7" />
    <path d="M5 9c0 2.144 2.252 3.908 6 4" />
    <path d="M12 20l4 -9l4 9" />
    <path d="M19.1 18h-6.2" />
    <path d="M6.694 3l.793 .582" />
  </svg>
);

/** Tabler `bold` (MIT). */
export const TbBold = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M7 5h6a3.5 3.5 0 0 1 0 7h-6z" />
    <path d="M13 12h1a3.5 3.5 0 0 1 0 7h-7v-7" />
  </svg>
);

/** Tabler `file-code` (MIT). */
export const TbFileCode = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M14 3v4a1 1 0 0 0 1 1h4" />
    <path d="M17 21h-10a2 2 0 0 1 -2 -2v-14a2 2 0 0 1 2 -2h7l5 5v11a2 2 0 0 1 -2 2z" />
    <path d="M10 13l-1 2l1 2" />
    <path d="M14 13l1 2l-1 2" />
  </svg>
);

/** Tabler `function` (MIT). */
export const TbFunction = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M4 4m0 2.667a2.667 2.667 0 0 1 2.667 -2.667h10.666a2.667 2.667 0 0 1 2.667 2.667v10.666a2.667 2.667 0 0 1 -2.667 2.667h-10.666a2.667 2.667 0 0 1 -2.667 -2.667z" />
    <path d="M9 15.5v.25c0 .69 .56 1.25 1.25 1.25c.71 0 1.304 -.538 1.374 -1.244l.752 -7.512a1.381 1.381 0 0 1 1.374 -1.244c.69 0 1.25 .56 1.25 1.25v.25" />
    <path d="M9 12h6" />
  </svg>
);

/** Tabler `h-1` (MIT). */
export const TbH1 = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M19 18v-8l-2 2" />
    <path d="M4 6v12" />
    <path d="M12 6v12" />
    <path d="M11 18h2" />
    <path d="M3 18h2" />
    <path d="M4 12h8" />
    <path d="M3 6h2" />
    <path d="M11 6h2" />
  </svg>
);

/** Tabler `minus` (MIT). */
export const TbMinus = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M5 12l14 0" />
  </svg>
);

/** Tabler `italic` (MIT). */
export const TbItalic = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M11 5l6 0" />
    <path d="M7 19l6 0" />
    <path d="M14 5l-4 14" />
  </svg>
);

/** Tabler `link` (MIT). */
export const TbLink = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M9 15l6 -6" />
    <path d="M11 6l.463 -.536a5 5 0 0 1 7.071 7.072l-.534 .464" />
    <path d="M13 18l-.397 .534a5.068 5.068 0 0 1 -7.127 0a4.972 4.972 0 0 1 0 -7.071l.524 -.463" />
  </svg>
);

/** Tabler `list` (MIT). */
export const TbList = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M9 6l11 0" />
    <path d="M9 12l11 0" />
    <path d="M9 18l11 0" />
    <path d="M5 6l0 .01" />
    <path d="M5 12l0 .01" />
    <path d="M5 18l0 .01" />
  </svg>
);

/** Tabler `list-numbers` (MIT). */
export const TbListNumbers = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M11 6h9" />
    <path d="M11 12h9" />
    <path d="M12 18h8" />
    <path d="M4 16a2 2 0 1 1 4 0c0 .591 -.5 1 -1 1.5l-3 2.5h4" />
    <path d="M6 10v-6l-2 2" />
  </svg>
);

/** Tabler `quote` (MIT). */
export const TbQuote = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M10 11h-4a1 1 0 0 1 -1 -1v-3a1 1 0 0 1 1 -1h3a1 1 0 0 1 1 1v6c0 2.667 -1.333 4.333 -4 5" />
    <path d="M19 11h-4a1 1 0 0 1 -1 -1v-3a1 1 0 0 1 1 -1h3a1 1 0 0 1 1 1v6c0 2.667 -1.333 4.333 -4 5" />
  </svg>
);

/** Tabler `paperclip` (MIT). */
export const TbPaperclip = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M15 7l-6.5 6.5a1.5 1.5 0 0 0 3 3l6.5 -6.5a3 3 0 0 0 -6 -6l-6.5 6.5a4.5 4.5 0 0 0 9 9l6.5 -6.5" />
  </svg>
);

/** Tabler `crop` (MIT). */
export const TbCrop = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M8 5v10a1 1 0 0 0 1 1h10" />
    <path d="M5 8h10a1 1 0 0 1 1 1v10" />
  </svg>
);

/** Tabler `player-skip-forward` (MIT). */
export const TbPlayerSkipForward = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M4 5v14l12 -7z" />
    <path d="M20 5l0 14" />
  </svg>
);

/** Tabler `player-pause` (MIT). */
export const TbPlayerPause = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M6 5m0 1a1 1 0 0 1 1 -1h2a1 1 0 0 1 1 1v12a1 1 0 0 1 -1 1h-2a1 1 0 0 1 -1 -1z" />
    <path d="M14 5m0 1a1 1 0 0 1 1 -1h2a1 1 0 0 1 1 1v12a1 1 0 0 1 -1 1h-2a1 1 0 0 1 -1 -1z" />
  </svg>
);

/** Tabler `play-card` (MIT). */
export const TbPlayCard = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M19 5v14a2 2 0 0 1 -2 2h-10a2 2 0 0 1 -2 -2v-14a2 2 0 0 1 2 -2h10a2 2 0 0 1 2 2z" />
    <path d="M8 6h.01" />
    <path d="M16 18h.01" />
    <path d="M12 16l-3 -4l3 -4l3 4z" />
  </svg>
);

/** Tabler `player-skip-back` (MIT). */
export const TbPlayerSkipBack = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M20 5v14l-12 -7z" />
    <path d="M4 5l0 14" />
  </svg>
);

/** Tabler `zoom-in` (MIT). */
export const TbZoomIn = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M10 10m-7 0a7 7 0 1 0 14 0a7 7 0 1 0 -14 0" />
    <path d="M7 10l6 0" />
    <path d="M10 7l0 6" />
    <path d="M21 21l-6 -6" />
  </svg>
);

/** Tabler `zoom-out` (MIT). */
export const TbZoomOut = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M10 10m-7 0a7 7 0 1 0 14 0a7 7 0 1 0 -14 0" />
    <path d="M7 10l6 0" />
    <path d="M21 21l-6 -6" />
  </svg>
);

/** Tabler `arrow-left` (MIT). */
export const TbArrowLeft = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M5 12l14 0" />
    <path d="M5 12l6 6" />
    <path d="M5 12l6 -6" />
  </svg>
);

/** Tabler `x` (MIT). */
export const TbX = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M18 6l-12 12" />
    <path d="M6 6l12 12" />
  </svg>
);

/** Tabler `layout-sidebar-left-collapse` (MIT). */
export const TbLayoutSidebarLeftCollapse = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M4 4m0 2a2 2 0 0 1 2 -2h12a2 2 0 0 1 2 2v12a2 2 0 0 1 -2 2h-12a2 2 0 0 1 -2 -2z" />
    <path d="M9 4v16" />
    <path d="M15 10l-2 2l2 2" />
  </svg>
);

/** Tabler `chevron-down` (MIT). */
export const TbChevronDown = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M6 9l6 6l6 -6" />
  </svg>
);

/** Tabler `chevron-up` (MIT). */
export const TbChevronUp = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M6 15l6 -6l6 6" />
  </svg>
);

/** Tabler `external-link` (MIT). */
export const TbExternalLink = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 6h-6a2 2 0 0 0 -2 2v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2 -2v-6" />
    <path d="M11 13l9 -9" />
    <path d="M15 4h5v5" />
  </svg>
);

/** Tabler `arrow-right` (MIT). */
export const TbArrowRight = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M5 12l14 0" />
    <path d="M13 18l6 -6" />
    <path d="M13 6l6 6" />
  </svg>
);

/** Tabler `layout-grid` (MIT). */
export const TbLayoutGrid = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M4 4m0 1a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v4a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1z" />
    <path d="M14 4m0 1a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v4a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1z" />
    <path d="M4 14m0 1a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v4a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1z" />
    <path d="M14 14m0 1a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v4a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1z" />
  </svg>
);

/** Tabler `home` (MIT). */
export const TbHome = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M5 12l-2 0l9 -9l9 9l-2 0" />
    <path d="M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2 -2v-7" />
    <path d="M9 21v-6a2 2 0 0 1 2 -2h2a2 2 0 0 1 2 2v6" />
  </svg>
);

/** Tabler `menu` (MIT). */
export const TbMenu = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M4 8l16 0" />
    <path d="M4 16l16 0" />
  </svg>
);

/** Tabler `dots` (MIT). */
export const TbDots = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M5 12m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0" />
    <path d="M12 12m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0" />
    <path d="M19 12m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0" />
  </svg>
);

/** Tabler `chevron-right` (MIT). */
export const TbChevronRight = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M9 6l6 6l-6 6" />
  </svg>
);

/** Tabler `arrow-up` (MIT). */
export const TbArrowUp = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 5l0 14" />
    <path d="M18 11l-6 -6" />
    <path d="M6 11l6 -6" />
  </svg>
);

/** Tabler `speakerphone` (MIT). */
export const TbSpeakerphone = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M18 8a3 3 0 0 1 0 6" />
    <path d="M10 8v11a1 1 0 0 1 -1 1h-1a1 1 0 0 1 -1 -1v-5" />
    <path d="M12 8h0l4.524 -3.77a.9 .9 0 0 1 1.476 .692v12.156a.9 .9 0 0 1 -1.476 .692l-4.524 -3.77h-8a1 1 0 0 1 -1 -1v-4a1 1 0 0 1 1 -1h8" />
  </svg>
);

/** Tabler `badge` (MIT). */
export const TbBadge = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M17 17v-13l-5 3l-5 -3v13l5 3z" />
  </svg>
);

/** Tabler `bell` (MIT). */
export const TbBell = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M10 5a2 2 0 1 1 4 0a7 7 0 0 1 4 6v3a4 4 0 0 0 2 3h-16a4 4 0 0 0 2 -3v-3a7 7 0 0 1 4 -6" />
    <path d="M9 17v1a3 3 0 0 0 6 0v-1" />
  </svg>
);

/** Tabler `sparkles` (MIT). */
export const TbSparkles = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M16 18a2 2 0 0 1 2 2a2 2 0 0 1 2 -2a2 2 0 0 1 -2 -2a2 2 0 0 1 -2 2zm0 -12a2 2 0 0 1 2 2a2 2 0 0 1 2 -2a2 2 0 0 1 -2 -2a2 2 0 0 1 -2 2zm-7 12a6 6 0 0 1 6 -6a6 6 0 0 1 -6 -6a6 6 0 0 1 -6 6a6 6 0 0 1 6 6z" />
  </svg>
);

/** Tabler `message` (MIT). */
export const TbMessage = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M8 9h8" />
    <path d="M8 13h6" />
    <path d="M18 4a3 3 0 0 1 3 3v8a3 3 0 0 1 -3 3h-5l-5 3v-3h-2a3 3 0 0 1 -3 -3v-8a3 3 0 0 1 3 -3h12z" />
  </svg>
);

/** Tabler `mail` (MIT). */
export const TbMail = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M3 7a2 2 0 0 1 2 -2h14a2 2 0 0 1 2 2v10a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2v-10z" />
    <path d="M3 7l9 6l9 -6" />
  </svg>
);

/** Tabler `arrow-back-up` (MIT). */
export const TbArrowBackUp = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M9 14l-4 -4l4 -4" />
    <path d="M5 10h11a4 4 0 1 1 0 8h-1" />
  </svg>
);

/** Tabler `certificate` (MIT). */
export const TbCertificate = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M15 15m-3 0a3 3 0 1 0 6 0a3 3 0 1 0 -6 0" />
    <path d="M13 17.5v4.5l2 -1.5l2 1.5v-4.5" />
    <path d="M10 19h-5a2 2 0 0 1 -2 -2v-10c0 -1.1 .9 -2 2 -2h14a2 2 0 0 1 2 2v10a2 2 0 0 1 -1 1.73" />
    <path d="M6 9l12 0" />
    <path d="M6 12l3 0" />
    <path d="M6 15l2 0" />
  </svg>
);

/** Tabler `chart-ppf` (MIT). */
export const TbChartPpf = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M19 17c0 -6.075 -5.373 -11 -12 -11" />
    <path d="M3 3v18h18" />
  </svg>
);

/** Tabler `chart-pie` (MIT). */
export const TbChartPie = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M10 3.2a9 9 0 1 0 10.8 10.8a1 1 0 0 0 -1 -1h-6.8a2 2 0 0 1 -2 -2v-7a.9 .9 0 0 0 -1 -.8" />
    <path d="M15 3.5a9 9 0 0 1 5.5 5.5h-4.5a1 1 0 0 1 -1 -1v-4.5" />
  </svg>
);

/** Tabler `crown` (MIT). */
export const TbCrown = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 6l4 6l5 -4l-2 10h-14l-2 -10l5 4z" />
  </svg>
);

/** Tabler `diamond` (MIT). */
export const TbDiamond = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M6 5h12l3 5l-8.5 9.5a.7 .7 0 0 1 -1 0l-8.5 -9.5l3 -5" />
    <path d="M10 12l-2 -2.2l.6 -1" />
  </svg>
);

/** Tabler `medal` (MIT). */
export const TbMedal = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 4v3m-4 -3v6m8 -6v6" />
    <path d="M12 18.5l-3 1.5l.5 -3.5l-2 -2l3 -.5l1.5 -3l1.5 3l3 .5l-2 2l.5 3.5z" />
  </svg>
);

/** Tabler `podium` (MIT). */
export const TbPodium = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M5 8h14l-.621 2.485a2 2 0 0 1 -1.94 1.515h-8.878a2 2 0 0 1 -1.94 -1.515l-.621 -2.485z" />
    <path d="M7 8v-2a3 3 0 0 1 3 -3" />
    <path d="M8 12l1 9" />
    <path d="M16 12l-1 9" />
    <path d="M7 21h10" />
  </svg>
);

/** Tabler `hash` (MIT). */
export const TbHash = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M5 9l14 0" />
    <path d="M5 15l14 0" />
    <path d="M11 4l-4 16" />
    <path d="M17 4l-4 16" />
  </svg>
);

/** Tabler `shield` (MIT). */
export const TbShield = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 3a12 12 0 0 0 8.5 3a12 12 0 0 1 -8.5 15a12 12 0 0 1 -8.5 -15a12 12 0 0 0 8.5 -3" />
  </svg>
);

/** Tabler `star` (MIT). */
export const TbStar = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 17.75l-6.172 3.245l1.179 -6.873l-5 -4.867l6.9 -1l3.086 -6.253l3.086 6.253l6.9 1l-5 4.867l1.179 6.873z" />
  </svg>
);

/** Tabler `thumb-down` (MIT). */
export const TbThumbDown = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M7 13v-8a1 1 0 0 0 -1 -1h-2a1 1 0 0 0 -1 1v7a1 1 0 0 0 1 1h3a4 4 0 0 1 4 4v1a2 2 0 0 0 4 0v-5h3a2 2 0 0 0 2 -2l-1 -5a2 3 0 0 0 -2 -2h-7a3 3 0 0 0 -3 3" />
  </svg>
);

/** Tabler `thumb-up` (MIT). */
export const TbThumbUp = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M7 11v8a1 1 0 0 1 -1 1h-2a1 1 0 0 1 -1 -1v-7a1 1 0 0 1 1 -1h3a4 4 0 0 0 4 -4v-1a2 2 0 0 1 4 0v5h3a2 2 0 0 1 2 2l-1 5a2 3 0 0 1 -2 2h-7a3 3 0 0 1 -3 -3" />
  </svg>
);

/** Tabler `trending-down` (MIT). */
export const TbTrendingDown = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M3 7l6 6l4 -4l8 8" />
    <path d="M21 10l0 7l-7 0" />
  </svg>
);

/** Tabler `trophy` (MIT). */
export const TbTrophy = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M8 21l8 0" />
    <path d="M12 17l0 4" />
    <path d="M7 4l10 0" />
    <path d="M17 4v8a5 5 0 0 1 -10 0v-8" />
    <path d="M5 9m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0" />
    <path d="M19 9m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0" />
  </svg>
);

/** Tabler `shopping-bag` (MIT). */
export const TbShoppingBag = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M6.331 8h11.339a2 2 0 0 1 1.977 2.304l-1.255 8.152a3 3 0 0 1 -2.966 2.544h-6.852a3 3 0 0 1 -2.965 -2.544l-1.255 -8.152a2 2 0 0 1 1.977 -2.304z" />
    <path d="M9 11v-5a3 3 0 0 1 6 0v5" />
  </svg>
);

/** Tabler `credit-card` (MIT). */
export const TbCreditCard = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M3 5m0 3a3 3 0 0 1 3 -3h12a3 3 0 0 1 3 3v8a3 3 0 0 1 -3 3h-12a3 3 0 0 1 -3 -3z" />
    <path d="M3 10l18 0" />
    <path d="M7 15l.01 0" />
    <path d="M11 15l2 0" />
  </svg>
);

/** Tabler `shopping-cart` (MIT). */
export const TbShoppingCart = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M6 19m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0" />
    <path d="M17 19m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0" />
    <path d="M17 17h-11v-14h-2" />
    <path d="M6 5l14 1l-1 7h-13" />
  </svg>
);

/** Tabler `coins` (MIT). */
export const TbCoins = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M9 14c0 1.657 2.686 3 6 3s6 -1.343 6 -3s-2.686 -3 -6 -3s-6 1.343 -6 3z" />
    <path d="M9 14v4c0 1.656 2.686 3 6 3s6 -1.344 6 -3v-4" />
    <path d="M3 6c0 1.072 1.144 2.062 3 2.598s4.144 .536 6 0c1.856 -.536 3 -1.526 3 -2.598c0 -1.072 -1.144 -2.062 -3 -2.598s-4.144 -.536 -6 0c-1.856 .536 -3 1.526 -3 2.598z" />
    <path d="M3 6v10c0 .888 .772 1.45 2 2" />
    <path d="M3 11c0 .888 .772 1.45 2 2" />
  </svg>
);

/** Tabler `discount` (MIT). */
export const TbDiscount = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M9 15l6 -6" />
    <circle cx="9.5" cy="9.5" r=".5" />
    <circle cx="14.5" cy="14.5" r=".5" />
    <path d="M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0 -18 0" />
  </svg>
);

/** Tabler `gift` (MIT). */
export const TbGift = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M3 8m0 1a1 1 0 0 1 1 -1h16a1 1 0 0 1 1 1v2a1 1 0 0 1 -1 1h-16a1 1 0 0 1 -1 -1z" />
    <path d="M12 8l0 13" />
    <path d="M19 12v7a2 2 0 0 1 -2 2h-10a2 2 0 0 1 -2 -2v-7" />
    <path d="M7.5 8a2.5 2.5 0 0 1 0 -5a4.8 8 0 0 1 4.5 5a4.8 8 0 0 1 4.5 -5a2.5 2.5 0 0 1 0 5" />
  </svg>
);

/** Tabler `history` (MIT). */
export const TbHistory = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 8l0 4l2 2" />
    <path d="M3.05 11a9 9 0 1 1 .5 4m-.5 5v-5h5" />
  </svg>
);

/** Tabler `wallet` (MIT). */
export const TbWallet = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M17 8v-3a1 1 0 0 0 -1 -1h-10a2 2 0 0 0 0 4h12a1 1 0 0 1 1 1v3m0 4v3a1 1 0 0 1 -1 1h-12a2 2 0 0 1 -2 -2v-12" />
    <path d="M20 12v4h-4a2 2 0 0 1 0 -4h4" />
  </svg>
);

/** Tabler `calculator` (MIT). */
export const TbCalculator = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M4 3m0 2a2 2 0 0 1 2 -2h12a2 2 0 0 1 2 2v14a2 2 0 0 1 -2 2h-12a2 2 0 0 1 -2 -2z" />
    <path d="M8 7m0 1a1 1 0 0 1 1 -1h6a1 1 0 0 1 1 1v1a1 1 0 0 1 -1 1h-6a1 1 0 0 1 -1 -1z" />
    <path d="M8 14l0 .01" />
    <path d="M12 14l0 .01" />
    <path d="M16 14l0 .01" />
    <path d="M8 17l0 .01" />
    <path d="M12 17l0 .01" />
    <path d="M16 17l0 .01" />
  </svg>
);

/** Tabler `database` (MIT). */
export const TbDatabase = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 6m-8 0a8 3 0 1 0 16 0a8 3 0 1 0 -16 0" />
    <path d="M4 6v6a8 3 0 0 0 16 0v-6" />
    <path d="M4 12v6a8 3 0 0 0 16 0v-6" />
  </svg>
);

/** Tabler `activity` (MIT). */
export const TbActivity = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M3 12h4l3 8l4 -16l3 8h4" />
  </svg>
);

/** Tabler `cpu` (MIT). */
export const TbCpu = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M5 5m0 1a1 1 0 0 1 1 -1h12a1 1 0 0 1 1 1v12a1 1 0 0 1 -1 1h-12a1 1 0 0 1 -1 -1z" />
    <path d="M9 9h6v6h-6z" />
    <path d="M3 10h2" />
    <path d="M3 14h2" />
    <path d="M10 3v2" />
    <path d="M14 3v2" />
    <path d="M21 10h-2" />
    <path d="M21 14h-2" />
    <path d="M14 21v-2" />
    <path d="M10 21v-2" />
  </svg>
);

/** Tabler `percentage` (MIT). */
export const TbPercentage = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M17 17m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0" />
    <path d="M7 7m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0" />
    <path d="M6 18l12 -12" />
  </svg>
);

/** Tabler `server` (MIT). */
export const TbServer = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M3 4m0 3a3 3 0 0 1 3 -3h12a3 3 0 0 1 3 3v2a3 3 0 0 1 -3 3h-12a3 3 0 0 1 -3 -3z" />
    <path d="M3 12m0 3a3 3 0 0 1 3 -3h12a3 3 0 0 1 3 3v2a3 3 0 0 1 -3 3h-12a3 3 0 0 1 -3 -3z" />
    <path d="M7 8l0 .01" />
    <path d="M7 16l0 .01" />
  </svg>
);

/** Tabler `gauge` (MIT). */
export const TbGauge = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0 -18 0" />
    <path d="M12 12m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0" />
    <path d="M13.41 10.59l2.59 -2.59" />
    <path d="M7 12a5 5 0 0 1 5 -5" />
  </svg>
);

/** Tabler `circle-check` (MIT). */
export const TbCircleCheck = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0 -18 0" />
    <path d="M9 12l2 2l4 -4" />
  </svg>
);

/** Tabler `info-circle` (MIT). */
export const TbInfoCircle = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M3 12a9 9 0 1 0 18 0a9 9 0 0 0 -18 0" />
    <path d="M12 9h.01" />
    <path d="M11 12h1v4h1" />
  </svg>
);

/** Tabler `circle` (MIT). */
export const TbCircle = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0 -18 0" />
  </svg>
);

/** Tabler `hourglass` (MIT). */
export const TbHourglass = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M6.5 7h11" />
    <path d="M6.5 17h11" />
    <path d="M6 20v-2a6 6 0 1 1 12 0v2a1 1 0 0 1 -1 1h-10a1 1 0 0 1 -1 -1z" />
    <path d="M6 4v2a6 6 0 1 0 12 0v-2a1 1 0 0 0 -1 -1h-10a1 1 0 0 0 -1 1z" />
  </svg>
);

/** Tabler `stopwatch` (MIT). */
export const TbStopwatch = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M5 13a7 7 0 1 0 14 0a7 7 0 0 0 -14 0z" />
    <path d="M14.5 10.5l-2.5 2.5" />
    <path d="M17 8l1 -1" />
    <path d="M14 3h-4" />
  </svg>
);

/** Tabler `lock-open` (MIT). */
export const TbLockOpen = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M5 11m0 2a2 2 0 0 1 2 -2h10a2 2 0 0 1 2 2v6a2 2 0 0 1 -2 2h-10a2 2 0 0 1 -2 -2z" />
    <path d="M12 16m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0" />
    <path d="M8 11v-5a4 4 0 0 1 8 0" />
  </svg>
);

/** Tabler `rosette-discount-check` (MIT). */
export const TbRosetteDiscountCheck = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M5 7.2a2.2 2.2 0 0 1 2.2 -2.2h1a2.2 2.2 0 0 0 1.55 -.64l.7 -.7a2.2 2.2 0 0 1 3.12 0l.7 .7c.412 .41 .97 .64 1.55 .64h1a2.2 2.2 0 0 1 2.2 2.2v1c0 .58 .23 1.138 .64 1.55l.7 .7a2.2 2.2 0 0 1 0 3.12l-.7 .7a2.2 2.2 0 0 0 -.64 1.55v1a2.2 2.2 0 0 1 -2.2 2.2h-1a2.2 2.2 0 0 0 -1.55 .64l-.7 .7a2.2 2.2 0 0 1 -3.12 0l-.7 -.7a2.2 2.2 0 0 0 -1.55 -.64h-1a2.2 2.2 0 0 1 -2.2 -2.2v-1a2.2 2.2 0 0 0 -.64 -1.55l-.7 -.7a2.2 2.2 0 0 1 0 -3.12l.7 -.7a2.2 2.2 0 0 0 .64 -1.55v-1" />
    <path d="M9 12l2 2l4 -4" />
  </svg>
);

/** Tabler `key` (MIT). */
export const TbKey = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M16.555 3.843l3.602 3.602a2.877 2.877 0 0 1 0 4.069l-2.643 2.643a2.877 2.877 0 0 1 -4.069 0l-.301 -.301l-6.558 6.558a2 2 0 0 1 -1.239 .578l-.175 .008h-1.172a1 1 0 0 1 -.993 -.883l-.007 -.117v-1.172a2 2 0 0 1 .467 -1.284l.119 -.13l.414 -.414h2v-2h2v-2l2.144 -2.144l-.301 -.301a2.877 2.877 0 0 1 0 -4.069l2.643 -2.643a2.877 2.877 0 0 1 4.069 0z" />
    <path d="M15 9h.01" />
  </svg>
);

/** Tabler `archive` (MIT). */
export const TbArchive = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M3 4m0 2a2 2 0 0 1 2 -2h14a2 2 0 0 1 2 2v0a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2z" />
    <path d="M5 8v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2 -2v-10" />
    <path d="M10 12l4 0" />
  </svg>
);

/** Tabler `moon` (MIT). */
export const TbMoon = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 3c.132 0 .263 0 .393 0a7.5 7.5 0 0 0 7.92 12.446a9 9 0 1 1 -8.313 -12.454z" />
  </svg>
);

/** Tabler `sun` (MIT). */
export const TbSun = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 12m-4 0a4 4 0 1 0 8 0a4 4 0 1 0 -8 0" />
    <path d="M3 12h1m8 -9v1m8 8h1m-9 8v1m-6.4 -15.4l.7 .7m12.1 -.7l-.7 .7m0 11.4l.7 .7m-12.1 -.7l-.7 .7" />
  </svg>
);

/** Tabler `screen-share` (MIT). */
export const TbScreenShare = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M21 12v3a1 1 0 0 1 -1 1h-16a1 1 0 0 1 -1 -1v-10a1 1 0 0 1 1 -1h9" />
    <path d="M7 20l10 0" />
    <path d="M9 16l0 4" />
    <path d="M15 16l0 4" />
    <path d="M17 4h4v4" />
    <path d="M16 9l5 -5" />
  </svg>
);

/** Tabler `palette` (MIT). */
export const TbPalette = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 21a9 9 0 0 1 0 -18c4.97 0 9 3.582 9 8c0 1.06 -.474 2.078 -1.318 2.828c-.844 .75 -1.989 1.172 -3.182 1.172h-2.5a2 2 0 0 0 -1 3.75a1.3 1.3 0 0 1 -1 2.25" />
    <path d="M8.5 10.5m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0" />
    <path d="M12.5 7.5m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0" />
    <path d="M16.5 10.5m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0" />
  </svg>
);

/** Tabler `devices` (MIT). */
export const TbDevices = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M13 9a1 1 0 0 1 1 -1h6a1 1 0 0 1 1 1v10a1 1 0 0 1 -1 1h-6a1 1 0 0 1 -1 -1v-10z" />
    <path d="M18 8v-3a1 1 0 0 0 -1 -1h-13a1 1 0 0 0 -1 1v12a1 1 0 0 0 1 1h9" />
    <path d="M16 9h2" />
  </svg>
);

/** Tabler `user` (MIT). */
export const TbUser = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M8 7a4 4 0 1 0 8 0a4 4 0 0 0 -8 0" />
    <path d="M6 21v-2a4 4 0 0 1 4 -4h4a4 4 0 0 1 4 4v2" />
  </svg>
);

/** Tabler `user-x` (MIT). */
export const TbUserX = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M8 7a4 4 0 1 0 8 0a4 4 0 0 0 -8 0" />
    <path d="M6 21v-2a4 4 0 0 1 4 -4h3.5" />
    <path d="M22 22l-5 -5" />
    <path d="M17 22l5 -5" />
  </svg>
);

/** Tabler `user-plus` (MIT). */
export const TbUserPlus = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M8 7a4 4 0 1 0 8 0a4 4 0 0 0 -8 0" />
    <path d="M16 19h6" />
    <path d="M19 16v6" />
    <path d="M6 21v-2a4 4 0 0 1 4 -4h4" />
  </svg>
);

/** Tabler `map-pin` (MIT). */
export const TbMapPin = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M9 11a3 3 0 1 0 6 0a3 3 0 0 0 -6 0" />
    <path d="M17.657 16.657l-4.243 4.243a2 2 0 0 1 -2.827 0l-4.244 -4.243a8 8 0 1 1 11.314 0z" />
  </svg>
);

/** Tabler `logout` (MIT). */
export const TbLogout = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M14 8v-2a2 2 0 0 0 -2 -2h-7a2 2 0 0 0 -2 2v12a2 2 0 0 0 2 2h7a2 2 0 0 0 2 -2v-2" />
    <path d="M9 12h12l-3 -3" />
    <path d="M18 15l3 -3" />
  </svg>
);

/** Tabler `shield-check` (MIT). */
export const TbShieldCheck = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M11.46 20.846a12 12 0 0 1 -7.96 -14.846a12 12 0 0 0 8.5 -3a12 12 0 0 0 8.5 3a12 12 0 0 1 -.09 7.06" />
    <path d="M15 19l2 2l4 -4" />
  </svg>
);

/** Tabler `backpack` (MIT). */
export const TbBackpack = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M5 18v-6a6 6 0 0 1 6 -6h2a6 6 0 0 1 6 6v6a3 3 0 0 1 -3 3h-8a3 3 0 0 1 -3 -3z" />
    <path d="M10 6v-1a2 2 0 1 1 4 0v1" />
    <path d="M9 21v-4a2 2 0 0 1 2 -2h2a2 2 0 0 1 2 2v4" />
    <path d="M11 10h2" />
  </svg>
);

/** Tabler `presentation` (MIT). */
export const TbPresentation = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M3 4l18 0" />
    <path d="M4 4v10a2 2 0 0 0 2 2h12a2 2 0 0 0 2 -2v-10" />
    <path d="M12 16l0 4" />
    <path d="M9 20l6 0" />
    <path d="M8 12l3 -3l2 2l3 -3" />
  </svg>
);

/** Tabler `user-minus` (MIT). */
export const TbUserMinus = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M8 7a4 4 0 1 0 8 0a4 4 0 0 0 -8 0" />
    <path d="M6 21v-2a4 4 0 0 1 4 -4h4c.348 0 .686 .045 1.009 .128" />
    <path d="M16 19h6" />
  </svg>
);

/** Tabler `briefcase` (MIT). */
export const TbBriefcase = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M3 7m0 2a2 2 0 0 1 2 -2h14a2 2 0 0 1 2 2v9a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2z" />
    <path d="M8 7v-2a2 2 0 0 1 2 -2h4a2 2 0 0 1 2 2v2" />
    <path d="M12 12l0 .01" />
    <path d="M3 13a20 20 0 0 0 18 0" />
  </svg>
);

/** Semantik kalit → Tabler ikonkasi (D18: `domen.ob'ekt.holat`). */
export const TABLER_ICONS: Record<string, (p: IconProps) => React.JSX.Element> = {
  "action.add": TbPlus,
  "action.bookmark": TbBookmark,
  "action.cancel": TbBan,
  "action.clear": TbCircleX,
  "action.clipboard": TbClipboard,
  "action.copy": TbCopy,
  "action.delete": TbTrash,
  "action.download": TbDownload,
  "action.edit": TbPencil,
  "action.eye": TbEye,
  "action.eyeOff": TbEyeOff,
  "action.filter": TbFilter,
  "action.format": TbWand,
  "action.fullscreen": TbMaximize,
  "action.help": TbHelpCircle,
  "action.pin": TbPin,
  "action.print": TbPrinter,
  "action.retry": TbRefresh,
  "action.save": TbDeviceFloppy,
  "action.search": TbSearch,
  "action.share": TbShare2,
  "action.sliders": TbAdjustmentsHorizontal,
  "action.sortAsc": TbSortAscending,
  "action.sortDesc": TbSortDescending,
  "action.sound": TbVolume2,
  "action.upload": TbUpload,
  "content.algorithm": TbRoute,
  "content.article": TbNews,
  "content.audio": TbHeadphones,
  "content.category": TbFolder,
  "content.code": TbCode,
  "content.course": TbSchool,
  "content.file": TbFile,
  "content.image": TbPhoto,
  "content.level": TbStack,
  "content.pdf": TbFileText,
  "content.problem": TbBook,
  "content.quiz": TbHelpCircle,
  "content.roadmap": TbMap,
  "content.step": TbShoe,
  "content.tag": TbTag,
  "content.terminal": TbTerminal,
  "content.test": TbFlask,
  "content.video": TbVideo,
  "contest.arena": TbTarget,
  "contest.calendar": TbCalendar,
  "contest.clock": TbClock,
  "contest.duel": TbSwords,
  "contest.flag": TbFlag,
  "contest.formatAcm": TbCircleX,
  "contest.formatIoi": TbChartBar,
  "contest.hackathon": TbCode,
  "contest.live": TbRadio,
  "contest.lock": TbLock,
  "contest.rated": TbTrendingUp,
  "contest.register": TbClipboardCheck,
  "contest.standings": TbTable,
  "contest.team": TbUsers,
  "device.appStore": TbDownload,
  "device.browser": TbGlobe,
  "device.desktop": TbDeviceDesktop,
  "device.laptop": TbDeviceLaptop,
  "device.phone": TbDeviceMobile,
  "device.qr": TbQrcode,
  "device.tablet": TbDeviceTablet,
  "device.touch": TbPointer,
  "empty.attempts": TbClipboardList,
  "empty.files": TbFolderOpen,
  "empty.messages": TbMessageCircle,
  "empty.notFound": TbCompass,
  "empty.notifications": TbBellOff,
  "empty.search": TbSearch,
  "empty.serverError": TbSettings,
  "empty.team": TbUsers,
  "error.forbidden": TbBan,
  "error.invalid": TbAlertTriangle,
  "error.network": TbWifiOff,
  "error.notFound": TbSearch,
  "error.server": TbFlame,
  "error.timeout": TbClockX,
  "locale.flag": TbFlag,
  "locale.globe": TbGlobe,
  "locale.region": TbMap,
  "locale.switch": TbLanguage,
  "locale.timezone": TbClock,
  "locale.translate": TbLanguage,
  "markdown.bold": TbBold,
  "markdown.code": TbCode,
  "markdown.codeBlock": TbFileCode,
  "markdown.formula": TbFunction,
  "markdown.heading": TbH1,
  "markdown.hr": TbMinus,
  "markdown.image": TbPhoto,
  "markdown.italic": TbItalic,
  "markdown.link": TbLink,
  "markdown.list": TbList,
  "markdown.orderedList": TbListNumbers,
  "markdown.preview": TbEye,
  "markdown.quote": TbQuote,
  "markdown.table": TbTable,
  "media.clip": TbPaperclip,
  "media.crop": TbCrop,
  "media.folder": TbFolder,
  "media.fullscreen": TbMaximize,
  "media.next": TbPlayerSkipForward,
  "media.pause": TbPlayerPause,
  "media.play": TbPlayCard,
  "media.prev": TbPlayerSkipBack,
  "media.rotate": TbRefresh,
  "media.volume": TbVolume2,
  "media.zoomIn": TbZoomIn,
  "media.zoomOut": TbZoomOut,
  "nav.back": TbArrowLeft,
  "nav.close": TbX,
  "nav.collapse": TbLayoutSidebarLeftCollapse,
  "nav.expandDown": TbChevronDown,
  "nav.expandUp": TbChevronUp,
  "nav.external": TbExternalLink,
  "nav.filterPanel": TbFilter,
  "nav.forward": TbArrowRight,
  "nav.grid": TbLayoutGrid,
  "nav.home": TbHome,
  "nav.leaderboard": TbChartBar,
  "nav.list": TbList,
  "nav.menu": TbMenu,
  "nav.more": TbDots,
  "nav.problems": TbBook,
  "nav.quiz": TbHelpCircle,
  "nav.separator": TbChevronRight,
  "nav.up": TbArrowUp,
  "notification.announce": TbSpeakerphone,
  "notification.badgeNew": TbBadge,
  "notification.bell": TbBell,
  "notification.bellRead": TbBell,
  "notification.changelog": TbSparkles,
  "notification.chat": TbMessageCircle,
  "notification.comment": TbMessage,
  "notification.email": TbMail,
  "notification.muted": TbBellOff,
  "notification.reply": TbArrowBackUp,
  "ranking.badge": TbBadge,
  "ranking.certificate": TbCertificate,
  "ranking.chartBar": TbChartBar,
  "ranking.chartLine": TbChartPpf,
  "ranking.chartPie": TbChartPie,
  "ranking.crown": TbCrown,
  "ranking.diamond": TbDiamond,
  "ranking.medalBronze": TbMedal,
  "ranking.medalGold": TbMedal,
  "ranking.medalSilver": TbMedal,
  "ranking.podium": TbPodium,
  "ranking.rank": TbHash,
  "ranking.shield": TbShield,
  "ranking.star": TbStar,
  "ranking.streak": TbFlame,
  "ranking.thumbDown": TbThumbDown,
  "ranking.thumbUp": TbThumbUp,
  "ranking.trendDown": TbTrendingDown,
  "ranking.trendUp": TbTrendingUp,
  "ranking.trophy": TbTrophy,
  "shop.buy": TbShoppingBag,
  "shop.card": TbCreditCard,
  "shop.cart": TbShoppingCart,
  "shop.coin": TbCoins,
  "shop.discount": TbDiscount,
  "shop.gift": TbGift,
  "shop.history": TbHistory,
  "shop.price": TbStar,
  "shop.store": TbShoppingBag,
  "shop.wallet": TbWallet,
  "stats.calculator": TbCalculator,
  "stats.chartBar": TbChartBar,
  "stats.chartLine": TbChartPpf,
  "stats.chartPie": TbChartPie,
  "stats.database": TbDatabase,
  "stats.funnel": TbFilter,
  "stats.load": TbActivity,
  "stats.memory": TbCpu,
  "stats.percent": TbPercentage,
  "stats.server": TbServer,
  "stats.speed": TbGauge,
  "stats.table": TbTable,
  "status.bad": TbCircleX,
  "status.blocked": TbBan,
  "status.clock": TbClock,
  "status.finished": TbCircleCheck,
  "status.info": TbInfoCircle,
  "status.live": TbRadio,
  "status.locked": TbLock,
  "status.offline": TbCircle,
  "status.ok": TbCircleCheck,
  "status.online": TbCircle,
  "status.pending": TbHourglass,
  "status.timer": TbStopwatch,
  "status.unlocked": TbLockOpen,
  "status.verified": TbRosetteDiscountCheck,
  "status.warning": TbAlertTriangle,
  "status.watching": TbEye,
  "system.apiKey": TbKey,
  "system.backup": TbArchive,
  "system.dark": TbMoon,
  "system.device": TbCpu,
  "system.key": TbKey,
  "system.light": TbSun,
  "system.log": TbFileText,
  "system.monitor": TbScreenShare,
  "system.palette": TbPalette,
  "system.security": TbShield,
  "system.sessions": TbDevices,
  "system.settings": TbSettings,
  "user.avatar": TbUser,
  "user.block": TbUserX,
  "user.education": TbSchool,
  "user.follow": TbUserPlus,
  "user.followers": TbUsers,
  "user.group": TbUsers,
  "user.invite": TbUserPlus,
  "user.link": TbLink,
  "user.location": TbMapPin,
  "user.logout": TbLogout,
  "user.profile": TbUser,
  "user.roleAdmin": TbShieldCheck,
  "user.roleStudent": TbBackpack,
  "user.roleTeacher": TbPresentation,
  "user.unfollow": TbUserMinus,
  "user.work": TbBriefcase,
};
