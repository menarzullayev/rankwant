/** Lucide ikonkalari (ISC), 24×24 to'r.
 *
 *  Generatsiya qilingan — `tools/gen-icon-packs.mjs` bilan qayta yasash mumkin.
 *  Qo'lda tahrirlanmaydi.
 *
 *  ⚠️ Manba CDN'dan **bir marta** olinadi va shu faylga yoziladi: ilova
 *  ishga tushganda tarmoqqa chiqmaydi, ya'ni yangi dependency ham,
 *  kutubxona yangilanishini kuzatish ham kerak emas.
 *
 *  165 ta ikonka.
 */

type IconProps = { className?: string };

const base = { viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 2, strokeLinecap: "round" as const, strokeLinejoin: "round" as const, xmlns: "http://www.w3.org/2000/svg" };

/** Lucide `plus` (ISC). */
export const LuPlus = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M5 12h14" />
    <path d="M12 5v14" />
  </svg>
);

/** Lucide `bookmark` (ISC). */
export const LuBookmark = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z" />
  </svg>
);

/** Lucide `ban` (ISC). */
export const LuBan = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M4.929 4.929 19.07 19.071" />
    <circle cx="12" cy="12" r="10" />
  </svg>
);

/** Lucide `x-circle` (ISC). */
export const LuXCircle = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <circle cx="12" cy="12" r="10" />
    <path d="m15 9-6 6" />
    <path d="m9 9 6 6" />
  </svg>
);

/** Lucide `clipboard` (ISC). */
export const LuClipboard = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <rect x="8" y="2" rx="1" ry="1" />
    <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
  </svg>
);

/** Lucide `copy` (ISC). */
export const LuCopy = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <rect x="8" y="8" rx="2" ry="2" />
    <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2" />
  </svg>
);

/** Lucide `trash-2` (ISC). */
export const LuTrash2 = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M10 11v6" />
    <path d="M14 11v6" />
    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6" />
    <path d="M3 6h18" />
    <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
  </svg>
);

/** Lucide `download` (ISC). */
export const LuDownload = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M12 15V3" />
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <path d="m7 10 5 5 5-5" />
  </svg>
);

/** Lucide `pencil-line` (ISC). */
export const LuPencilLine = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M13 21h8" />
    <path d="m15 5 4 4" />
    <path d="M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497z" />
  </svg>
);

/** Lucide `eye` (ISC). */
export const LuEye = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0" />
    <circle cx="12" cy="12" r="3" />
  </svg>
);

/** Lucide `eye-off` (ISC). */
export const LuEyeOff = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0 .696 10.747 10.747 0 0 1-1.444 2.49" />
    <path d="M14.084 14.158a3 3 0 0 1-4.242-4.242" />
    <path d="M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-.696 10.75 10.75 0 0 1 4.446-5.143" />
    <path d="m2 2 20 20" />
  </svg>
);

/** Lucide `funnel` (ISC). */
export const LuFunnel = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M10 20a1 1 0 0 0 .553.895l2 1A1 1 0 0 0 14 21v-7a2 2 0 0 1 .517-1.341L21.74 4.67A1 1 0 0 0 21 3H3a1 1 0 0 0-.742 1.67l7.225 7.989A2 2 0 0 1 10 14z" />
  </svg>
);

/** Lucide `wand-2` (ISC). */
export const LuWand2 = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="m21.64 3.64-1.28-1.28a1.21 1.21 0 0 0-1.72 0L2.36 18.64a1.21 1.21 0 0 0 0 1.72l1.28 1.28a1.2 1.2 0 0 0 1.72 0L21.64 5.36a1.2 1.2 0 0 0 0-1.72" />
    <path d="m14 7 3 3" />
    <path d="M5 6v4" />
    <path d="M19 14v4" />
    <path d="M10 2v2" />
    <path d="M7 8H3" />
    <path d="M21 16h-4" />
    <path d="M11 3H9" />
  </svg>
);

/** Lucide `maximize` (ISC). */
export const LuMaximize = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M8 3H5a2 2 0 0 0-2 2v3" />
    <path d="M21 8V5a2 2 0 0 0-2-2h-3" />
    <path d="M3 16v3a2 2 0 0 0 2 2h3" />
    <path d="M16 21h3a2 2 0 0 0 2-2v-3" />
  </svg>
);

/** Lucide `circle-help` (ISC). */
export const LuCircleHelp = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <circle cx="12" cy="12" r="10" />
    <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
    <path d="M12 17h.01" />
  </svg>
);

/** Lucide `pin` (ISC). */
export const LuPin = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M12 17v5" />
    <path d="M9 10.76a2 2 0 0 1-1.11 1.79l-1.78.9A2 2 0 0 0 5 15.24V16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-.76a2 2 0 0 0-1.11-1.79l-1.78-.9A2 2 0 0 1 15 10.76V7a1 1 0 0 1 1-1 2 2 0 0 0 0-4H8a2 2 0 0 0 0 4 1 1 0 0 1 1 1z" />
  </svg>
);

/** Lucide `printer` (ISC). */
export const LuPrinter = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2" />
    <path d="M6 9V3a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v6" />
    <rect x="6" y="14" rx="1" />
  </svg>
);

/** Lucide `refresh-cw` (ISC). */
export const LuRefreshCw = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" />
    <path d="M21 3v5h-5" />
    <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" />
    <path d="M8 16H3v5" />
  </svg>
);

/** Lucide `save` (ISC). */
export const LuSave = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M15.2 3a2 2 0 0 1 1.4.6l3.8 3.8a2 2 0 0 1 .6 1.4V19a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z" />
    <path d="M17 21v-7a1 1 0 0 0-1-1H8a1 1 0 0 0-1 1v7" />
    <path d="M7 3v4a1 1 0 0 0 1 1h7" />
  </svg>
);

/** Lucide `search` (ISC). */
export const LuSearch = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="m21 21-4.34-4.34" />
    <circle cx="11" cy="11" r="8" />
  </svg>
);

/** Lucide `share-2` (ISC). */
export const LuShare2 = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <circle cx="18" cy="5" r="3" />
    <circle cx="6" cy="12" r="3" />
    <circle cx="18" cy="19" r="3" />
    <line x1="8.59" x2="15.42" y1="13.51" y2="17.49" />
    <line x1="15.41" x2="8.59" y1="6.51" y2="10.49" />
  </svg>
);

/** Lucide `sliders-horizontal` (ISC). */
export const LuSlidersHorizontal = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M10 5H3" />
    <path d="M12 19H3" />
    <path d="M14 3v4" />
    <path d="M16 17v4" />
    <path d="M21 12h-9" />
    <path d="M21 19h-5" />
    <path d="M21 5h-7" />
    <path d="M8 10v4" />
    <path d="M8 12H3" />
  </svg>
);

/** Lucide `arrow-up-narrow-wide` (ISC). */
export const LuArrowUpNarrowWide = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="m3 8 4-4 4 4" />
    <path d="M7 4v16" />
    <path d="M11 12h4" />
    <path d="M11 16h7" />
    <path d="M11 20h10" />
  </svg>
);

/** Lucide `arrow-down-wide-narrow` (ISC). */
export const LuArrowDownWideNarrow = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="m3 16 4 4 4-4" />
    <path d="M7 20V4" />
    <path d="M11 4h10" />
    <path d="M11 8h7" />
    <path d="M11 12h4" />
  </svg>
);

/** Lucide `volume-2` (ISC). */
export const LuVolume2 = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M11 4.702a.705.705 0 0 0-1.203-.498L6.413 7.587A1.4 1.4 0 0 1 5.416 8H3a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h2.416a1.4 1.4 0 0 1 .997.413l3.383 3.384A.705.705 0 0 0 11 19.298z" />
    <path d="M16 9a5 5 0 0 1 0 6" />
    <path d="M19.364 18.364a9 9 0 0 0 0-12.728" />
  </svg>
);

/** Lucide `upload` (ISC). */
export const LuUpload = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M12 3v12" />
    <path d="m17 8-5-5-5 5" />
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
  </svg>
);

/** Lucide `route` (ISC). */
export const LuRoute = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <circle cx="6" cy="19" r="3" />
    <path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15" />
    <circle cx="18" cy="5" r="3" />
  </svg>
);

/** Lucide `newspaper` (ISC). */
export const LuNewspaper = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M15 18h-5" />
    <path d="M18 14h-8" />
    <path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-4 0v-9a2 2 0 0 1 2-2h2" />
    <rect x="10" y="6" rx="1" />
  </svg>
);

/** Lucide `headphones` (ISC). */
export const LuHeadphones = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M3 14h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7a9 9 0 0 1 18 0v7a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3" />
  </svg>
);

/** Lucide `folder` (ISC). */
export const LuFolder = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z" />
  </svg>
);

/** Lucide `code` (ISC). */
export const LuCode = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="m16 18 6-6-6-6" />
    <path d="m8 6-6 6 6 6" />
  </svg>
);

/** Lucide `graduation-cap` (ISC). */
export const LuGraduationCap = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z" />
    <path d="M22 10v6" />
    <path d="M6 12.5V16a6 3 0 0 0 12 0v-3.5" />
  </svg>
);

/** Lucide `file` (ISC). */
export const LuFile = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" />
    <path d="M14 2v4a2 2 0 0 0 2 2h4" />
  </svg>
);

/** Lucide `image` (ISC). */
export const LuImage = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <rect x="3" y="3" rx="2" ry="2" />
    <circle cx="9" cy="9" r="2" />
    <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21" />
  </svg>
);

/** Lucide `layers` (ISC). */
export const LuLayers = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83z" />
    <path d="M2 12a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 12" />
    <path d="M2 17a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 17" />
  </svg>
);

/** Lucide `file-text` (ISC). */
export const LuFileText = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" />
    <path d="M14 2v4a2 2 0 0 0 2 2h4" />
    <path d="M10 9H8" />
    <path d="M16 13H8" />
    <path d="M16 17H8" />
  </svg>
);

/** Lucide `book-open` (ISC). */
export const LuBookOpen = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M12 7v14" />
    <path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z" />
  </svg>
);

/** Lucide `map` (ISC). */
export const LuMap = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M14.106 5.553a2 2 0 0 0 1.788 0l3.659-1.83A1 1 0 0 1 21 4.619v12.764a1 1 0 0 1-.553.894l-4.553 2.277a2 2 0 0 1-1.788 0l-4.212-2.106a2 2 0 0 0-1.788 0l-3.659 1.83A1 1 0 0 1 3 19.381V6.618a1 1 0 0 1 .553-.894l4.553-2.277a2 2 0 0 1 1.788 0z" />
    <path d="M15 5.764v15" />
    <path d="M9 3.236v15" />
  </svg>
);

/** Lucide `footprints` (ISC). */
export const LuFootprints = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M4 16v-2.38C4 11.5 2.97 10.5 3 8c.03-2.72 1.49-6 4.5-6C9.37 2 10 3.8 10 5.5c0 3.11-2 5.66-2 8.68V16a2 2 0 1 1-4 0Z" />
    <path d="M20 20v-2.38c0-2.12 1.03-3.12 1-5.62-.03-2.72-1.49-6-4.5-6C14.63 6 14 7.8 14 9.5c0 3.11 2 5.66 2 8.68V20a2 2 0 1 0 4 0Z" />
    <path d="M16 17h4" />
    <path d="M4 13h4" />
  </svg>
);

/** Lucide `tag` (ISC). */
export const LuTag = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M12.586 2.586A2 2 0 0 0 11.172 2H4a2 2 0 0 0-2 2v7.172a2 2 0 0 0 .586 1.414l8.704 8.704a2.426 2.426 0 0 0 3.42 0l6.58-6.58a2.426 2.426 0 0 0 0-3.42z" />
    <circle cx="7.5" cy="7.5" r=".5" />
  </svg>
);

/** Lucide `terminal` (ISC). */
export const LuTerminal = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M12 19h8" />
    <path d="m4 17 6-6-6-6" />
  </svg>
);

/** Lucide `beaker` (ISC). */
export const LuBeaker = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M4.5 3h15" />
    <path d="M6 3v16a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V3" />
    <path d="M6 14h12" />
  </svg>
);

/** Lucide `video` (ISC). */
export const LuVideo = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.87a.5.5 0 0 0-.752-.432L16 10.5" />
    <rect x="2" y="6" rx="2" />
  </svg>
);

/** Lucide `target` (ISC). */
export const LuTarget = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <circle cx="12" cy="12" r="10" />
    <circle cx="12" cy="12" r="6" />
    <circle cx="12" cy="12" r="2" />
  </svg>
);

/** Lucide `calendar` (ISC). */
export const LuCalendar = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M8 2v4" />
    <path d="M16 2v4" />
    <rect x="3" y="4" rx="2" />
    <path d="M3 10h18" />
  </svg>
);

/** Lucide `clock` (ISC). */
export const LuClock = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M12 6v6l4 2" />
    <circle cx="12" cy="12" r="10" />
  </svg>
);

/** Lucide `swords` (ISC). */
export const LuSwords = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <polyline points="14.5 17.5 3 6 3 3 6 3 17.5 14.5" />
    <line x1="13" x2="19" y1="19" y2="13" />
    <line x1="16" x2="20" y1="16" y2="20" />
    <line x1="19" x2="21" y1="21" y2="19" />
    <polyline points="14.5 6.5 18 3 21 3 21 6 17.5 9.5" />
    <line x1="5" x2="9" y1="14" y2="18" />
    <line x1="7" x2="4" y1="17" y2="20" />
    <line x1="3" x2="5" y1="19" y2="21" />
  </svg>
);

/** Lucide `flag` (ISC). */
export const LuFlag = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M4 22V4a1 1 0 0 1 .4-.8A6 6 0 0 1 8 2c3 0 5 2 7.333 2q2 0 3.067-.8A1 1 0 0 1 20 4v10a1 1 0 0 1-.4.8A6 6 0 0 1 16 16c-3 0-5-2-8-2a6 6 0 0 0-4 1.528" />
  </svg>
);

/** Lucide `circle-x` (ISC). */
export const LuCircleX = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <circle cx="12" cy="12" r="10" />
    <path d="m15 9-6 6" />
    <path d="m9 9 6 6" />
  </svg>
);

/** Lucide `chart-bar` (ISC). */
export const LuChartBar = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M3 3v16a2 2 0 0 0 2 2h16" />
    <path d="M7 16h8" />
    <path d="M7 11h12" />
    <path d="M7 6h3" />
  </svg>
);

/** Lucide `radio` (ISC). */
export const LuRadio = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M16.247 7.761a6 6 0 0 1 0 8.478" />
    <path d="M19.075 4.933a10 10 0 0 1 0 14.134" />
    <path d="M4.925 19.067a10 10 0 0 1 0-14.134" />
    <path d="M7.753 16.239a6 6 0 0 1 0-8.478" />
    <circle cx="12" cy="12" r="2" />
  </svg>
);

/** Lucide `lock` (ISC). */
export const LuLock = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <rect x="3" y="11" rx="2" ry="2" />
    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
  </svg>
);

/** Lucide `trending-up` (ISC). */
export const LuTrendingUp = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M16 7h6v6" />
    <path d="m22 7-8.5 8.5-5-5L2 17" />
  </svg>
);

/** Lucide `clipboard-check` (ISC). */
export const LuClipboardCheck = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <rect x="8" y="2" rx="1" ry="1" />
    <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
    <path d="m9 14 2 2 4-4" />
  </svg>
);

/** Lucide `list-ordered` (ISC). */
export const LuListOrdered = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M11 5h10" />
    <path d="M11 12h10" />
    <path d="M11 19h10" />
    <path d="M4 4h1v5" />
    <path d="M4 9h2" />
    <path d="M6.5 20H3.4c0-1 2.6-1.925 2.6-3.5a1.5 1.5 0 0 0-2.6-1.02" />
  </svg>
);

/** Lucide `users` (ISC). */
export const LuUsers = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
    <path d="M16 3.128a4 4 0 0 1 0 7.744" />
    <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
    <circle cx="9" cy="7" r="4" />
  </svg>
);

/** Lucide `globe` (ISC). */
export const LuGlobe = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <circle cx="12" cy="12" r="10" />
    <path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20" />
    <path d="M2 12h20" />
  </svg>
);

/** Lucide `monitor` (ISC). */
export const LuMonitor = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <rect x="2" y="3" rx="2" />
    <line x1="8" x2="16" y1="21" y2="21" />
    <line x1="12" x2="12" y1="17" y2="21" />
  </svg>
);

/** Lucide `laptop` (ISC). */
export const LuLaptop = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M18 5a2 2 0 0 1 2 2v8.526a2 2 0 0 0 .212.897l1.068 2.127a1 1 0 0 1-.9 1.45H3.62a1 1 0 0 1-.9-1.45l1.068-2.127A2 2 0 0 0 4 15.526V7a2 2 0 0 1 2-2z" />
    <path d="M20.054 15.987H3.946" />
  </svg>
);

/** Lucide `smartphone` (ISC). */
export const LuSmartphone = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <rect x="5" y="2" rx="2" ry="2" />
    <path d="M12 18h.01" />
  </svg>
);

/** Lucide `qr-code` (ISC). */
export const LuQrCode = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <rect x="3" y="3" rx="1" />
    <rect x="16" y="3" rx="1" />
    <rect x="3" y="16" rx="1" />
    <path d="M21 16h-3a2 2 0 0 0-2 2v3" />
    <path d="M21 21v.01" />
    <path d="M12 7v3a2 2 0 0 1-2 2H7" />
    <path d="M3 12h.01" />
    <path d="M12 3h.01" />
    <path d="M12 16v.01" />
    <path d="M16 12h1" />
    <path d="M21 12v.01" />
    <path d="M12 21v-1" />
  </svg>
);

/** Lucide `tablet` (ISC). */
export const LuTablet = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <rect x="4" y="2" rx="2" ry="2" />
    <line x1="12" x2="12.01" y1="18" y2="18" />
  </svg>
);

/** Lucide `pointer` (ISC). */
export const LuPointer = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M22 14a8 8 0 0 1-8 8" />
    <path d="M18 11v-1a2 2 0 0 0-2-2a2 2 0 0 0-2 2" />
    <path d="M14 10V9a2 2 0 0 0-2-2a2 2 0 0 0-2 2v1" />
    <path d="M10 9.5V4a2 2 0 0 0-2-2a2 2 0 0 0-2 2v10" />
    <path d="M18 11a2 2 0 1 1 4 0v3a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-5.99-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15" />
  </svg>
);

/** Lucide `clipboard-list` (ISC). */
export const LuClipboardList = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <rect x="8" y="2" rx="1" ry="1" />
    <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
    <path d="M12 11h4" />
    <path d="M12 16h4" />
    <path d="M8 11h.01" />
    <path d="M8 16h.01" />
  </svg>
);

/** Lucide `folder-open` (ISC). */
export const LuFolderOpen = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="m6 14 1.5-2.9A2 2 0 0 1 9.24 10H20a2 2 0 0 1 1.94 2.5l-1.54 6a2 2 0 0 1-1.95 1.5H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h3.9a2 2 0 0 1 1.69.9l.81 1.2a2 2 0 0 0 1.67.9H18a2 2 0 0 1 2 2v2" />
  </svg>
);

/** Lucide `message-circle` (ISC). */
export const LuMessageCircle = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M2.992 16.342a2 2 0 0 1 .094 1.167l-1.065 3.29a1 1 0 0 0 1.236 1.168l3.413-.998a2 2 0 0 1 1.099.092 10 10 0 1 0-4.777-4.719" />
  </svg>
);

/** Lucide `compass` (ISC). */
export const LuCompass = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="m16.24 7.76-1.804 5.411a2 2 0 0 1-1.265 1.265L7.76 16.24l1.804-5.411a2 2 0 0 1 1.265-1.265z" />
    <circle cx="12" cy="12" r="10" />
  </svg>
);

/** Lucide `bell-off` (ISC). */
export const LuBellOff = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M10.268 21a2 2 0 0 0 3.464 0" />
    <path d="M17 17H4a1 1 0 0 1-.74-1.673C4.59 13.956 6 12.499 6 8a6 6 0 0 1 .258-1.742" />
    <path d="m2 2 20 20" />
    <path d="M8.668 3.01A6 6 0 0 1 18 8c0 2.687.77 4.653 1.707 6.05" />
  </svg>
);

/** Lucide `search-x` (ISC). */
export const LuSearchX = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="m13.5 8.5-5 5" />
    <path d="m8.5 8.5 5 5" />
    <circle cx="11" cy="11" r="8" />
    <path d="m21 21-4.3-4.3" />
  </svg>
);

/** Lucide `settings` (ISC). */
export const LuSettings = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915" />
    <circle cx="12" cy="12" r="3" />
  </svg>
);

/** Lucide `triangle-alert` (ISC). */
export const LuTriangleAlert = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3" />
    <path d="M12 9v4" />
    <path d="M12 17h.01" />
  </svg>
);

/** Lucide `wifi-off` (ISC). */
export const LuWifiOff = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M12 20h.01" />
    <path d="M8.5 16.429a5 5 0 0 1 7 0" />
    <path d="M5 12.859a10 10 0 0 1 5.17-2.69" />
    <path d="M19 12.859a10 10 0 0 0-2.007-1.523" />
    <path d="M2 8.82a15 15 0 0 1 4.177-2.643" />
    <path d="M22 8.82a15 15 0 0 0-11.288-3.764" />
    <path d="m2 2 20 20" />
  </svg>
);

/** Lucide `flame` (ISC). */
export const LuFlame = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z" />
  </svg>
);

/** Lucide `timer-off` (ISC). */
export const LuTimerOff = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M10 2h4" />
    <path d="M4.6 11a8 8 0 0 0 1.7 8.7 8 8 0 0 0 8.7 1.7" />
    <path d="M7.4 7.4a8 8 0 0 1 10.3 1 8 8 0 0 1 .9 10.2" />
    <path d="m2 2 20 20" />
    <path d="M12 12v-2" />
  </svg>
);

/** Lucide `languages` (ISC). */
export const LuLanguages = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="m5 8 6 6" />
    <path d="m4 14 6-6 2-3" />
    <path d="M2 5h12" />
    <path d="M7 2h1" />
    <path d="m22 22-5-10-5 10" />
    <path d="M14 18h6" />
  </svg>
);

/** Lucide `bold` (ISC). */
export const LuBold = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M6 12h9a4 4 0 0 1 0 8H7a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1h7a4 4 0 0 1 0 8" />
  </svg>
);

/** Lucide `code-square` (ISC). */
export const LuCodeSquare = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="m10 9-3 3 3 3" />
    <path d="m14 15 3-3-3-3" />
    <rect x="3" y="3" rx="2" />
  </svg>
);

/** Lucide `sigma` (ISC). */
export const LuSigma = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M18 7V5a1 1 0 0 0-1-1H6.5a.5.5 0 0 0-.4.8l4.5 6a2 2 0 0 1 0 2.4l-4.5 6a.5.5 0 0 0 .4.8H17a1 1 0 0 0 1-1v-2" />
  </svg>
);

/** Lucide `heading` (ISC). */
export const LuHeading = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M6 12h12" />
    <path d="M6 20V4" />
    <path d="M18 20V4" />
  </svg>
);

/** Lucide `minus` (ISC). */
export const LuMinus = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M5 12h14" />
  </svg>
);

/** Lucide `italic` (ISC). */
export const LuItalic = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <line x1="19" x2="10" y1="4" y2="4" />
    <line x1="14" x2="5" y1="20" y2="20" />
    <line x1="15" x2="9" y1="4" y2="20" />
  </svg>
);

/** Lucide `link` (ISC). */
export const LuLink = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
  </svg>
);

/** Lucide `list` (ISC). */
export const LuList = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M3 5h.01" />
    <path d="M3 12h.01" />
    <path d="M3 19h.01" />
    <path d="M8 5h13" />
    <path d="M8 12h13" />
    <path d="M8 19h13" />
  </svg>
);

/** Lucide `quote` (ISC). */
export const LuQuote = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M16 3a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2 1 1 0 0 1 1 1v1a2 2 0 0 1-2 2 1 1 0 0 0-1 1v2a1 1 0 0 0 1 1 6 6 0 0 0 6-6V5a2 2 0 0 0-2-2z" />
    <path d="M5 3a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2 1 1 0 0 1 1 1v1a2 2 0 0 1-2 2 1 1 0 0 0-1 1v2a1 1 0 0 0 1 1 6 6 0 0 0 6-6V5a2 2 0 0 0-2-2z" />
  </svg>
);

/** Lucide `table` (ISC). */
export const LuTable = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M12 3v18" />
    <rect x="3" y="3" rx="2" />
    <path d="M3 9h18" />
    <path d="M3 15h18" />
  </svg>
);

/** Lucide `paperclip` (ISC). */
export const LuPaperclip = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="m16 6-8.414 8.586a2 2 0 0 0 2.829 2.829l8.414-8.586a4 4 0 1 0-5.657-5.657l-8.379 8.551a6 6 0 1 0 8.485 8.485l8.379-8.551" />
  </svg>
);

/** Lucide `crop` (ISC). */
export const LuCrop = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M6 2v14a2 2 0 0 0 2 2h14" />
    <path d="M18 22V8a2 2 0 0 0-2-2H2" />
  </svg>
);

/** Lucide `skip-forward` (ISC). */
export const LuSkipForward = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M21 4v16" />
    <path d="M6.029 4.285A2 2 0 0 0 3 6v12a2 2 0 0 0 3.029 1.715l9.997-5.998a2 2 0 0 0 .003-3.432z" />
  </svg>
);

/** Lucide `pause` (ISC). */
export const LuPause = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <rect x="14" y="3" rx="1" />
    <rect x="5" y="3" rx="1" />
  </svg>
);

/** Lucide `play` (ISC). */
export const LuPlay = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M5 5a2 2 0 0 1 3.008-1.728l11.997 6.998a2 2 0 0 1 .003 3.458l-12 7A2 2 0 0 1 5 19z" />
  </svg>
);

/** Lucide `skip-back` (ISC). */
export const LuSkipBack = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M17.971 4.285A2 2 0 0 1 21 6v12a2 2 0 0 1-3.029 1.715l-9.997-5.998a2 2 0 0 1-.003-3.432z" />
    <path d="M3 20V4" />
  </svg>
);

/** Lucide `rotate-cw` (ISC). */
export const LuRotateCw = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8" />
    <path d="M21 3v5h-5" />
  </svg>
);

/** Lucide `zoom-in` (ISC). */
export const LuZoomIn = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <circle cx="11" cy="11" r="8" />
    <line x1="21" x2="16.65" y1="21" y2="16.65" />
    <line x1="11" x2="11" y1="8" y2="14" />
    <line x1="8" x2="14" y1="11" y2="11" />
  </svg>
);

/** Lucide `zoom-out` (ISC). */
export const LuZoomOut = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <circle cx="11" cy="11" r="8" />
    <line x1="21" x2="16.65" y1="21" y2="16.65" />
    <line x1="8" x2="14" y1="11" y2="11" />
  </svg>
);

/** Lucide `arrow-left` (ISC). */
export const LuArrowLeft = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="m12 19-7-7 7-7" />
    <path d="M19 12H5" />
  </svg>
);

/** Lucide `x` (ISC). */
export const LuX = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M18 6 6 18" />
    <path d="m6 6 12 12" />
  </svg>
);

/** Lucide `panel-left-close` (ISC). */
export const LuPanelLeftClose = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <rect x="3" y="3" rx="2" />
    <path d="M9 3v18" />
    <path d="m16 15-3-3 3-3" />
  </svg>
);

/** Lucide `chevron-down` (ISC). */
export const LuChevronDown = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="m6 9 6 6 6-6" />
  </svg>
);

/** Lucide `chevron-up` (ISC). */
export const LuChevronUp = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="m18 15-6-6-6 6" />
  </svg>
);

/** Lucide `external-link` (ISC). */
export const LuExternalLink = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M15 3h6v6" />
    <path d="M10 14 21 3" />
    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
  </svg>
);

/** Lucide `arrow-right` (ISC). */
export const LuArrowRight = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M5 12h14" />
    <path d="m12 5 7 7-7 7" />
  </svg>
);

/** Lucide `layout-grid` (ISC). */
export const LuLayoutGrid = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <rect x="3" y="3" rx="1" />
    <rect x="14" y="3" rx="1" />
    <rect x="14" y="14" rx="1" />
    <rect x="3" y="14" rx="1" />
  </svg>
);

/** Lucide `house` (ISC). */
export const LuHouse = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8" />
    <path d="M3 10a2 2 0 0 1 .709-1.528l7-6a2 2 0 0 1 2.582 0l7 6A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
  </svg>
);

/** Lucide `chart-no-axes-column` (ISC). */
export const LuChartNoAxesColumn = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M5 21v-6" />
    <path d="M12 21V3" />
    <path d="M19 21V9" />
  </svg>
);

/** Lucide `menu` (ISC). */
export const LuMenu = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M4 5h16" />
    <path d="M4 12h16" />
    <path d="M4 19h16" />
  </svg>
);

/** Lucide `ellipsis` (ISC). */
export const LuEllipsis = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <circle cx="12" cy="12" r="1" />
    <circle cx="19" cy="12" r="1" />
    <circle cx="5" cy="12" r="1" />
  </svg>
);

/** Lucide `chevron-right` (ISC). */
export const LuChevronRight = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="m9 18 6-6-6-6" />
  </svg>
);

/** Lucide `arrow-up` (ISC). */
export const LuArrowUp = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="m5 12 7-7 7 7" />
    <path d="M12 19V5" />
  </svg>
);

/** Lucide `megaphone` (ISC). */
export const LuMegaphone = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M11 6a13 13 0 0 0 8.4-2.8A1 1 0 0 1 21 4v12a1 1 0 0 1-1.6.8A13 13 0 0 0 11 14H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2z" />
    <path d="M6 14a12 12 0 0 0 2.4 7.2 2 2 0 0 0 3.2-2.4A8 8 0 0 1 10 14" />
    <path d="M8 6v8" />
  </svg>
);

/** Lucide `badge` (ISC). */
export const LuBadge = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78 4 4 0 0 1 0 6.74 4 4 0 0 1-4.77 4.78 4 4 0 0 1-6.75 0 4 4 0 0 1-4.78-4.77 4 4 0 0 1 0-6.76Z" />
  </svg>
);

/** Lucide `bell` (ISC). */
export const LuBell = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M10.268 21a2 2 0 0 0 3.464 0" />
    <path d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326" />
  </svg>
);

/** Lucide `message-square` (ISC). */
export const LuMessageSquare = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M22 17a2 2 0 0 1-2 2H6.828a2 2 0 0 0-1.414.586l-2.202 2.202A.71.71 0 0 1 2 21.286V5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2z" />
  </svg>
);

/** Lucide `mail` (ISC). */
export const LuMail = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="m22 7-8.991 5.727a2 2 0 0 1-2.009 0L2 7" />
    <rect x="2" y="4" rx="2" />
  </svg>
);

/** Lucide `reply` (ISC). */
export const LuReply = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M20 18v-2a4 4 0 0 0-4-4H4" />
    <path d="m9 17-5-5 5-5" />
  </svg>
);

/** Lucide `scroll` (ISC). */
export const LuScroll = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M19 17V5a2 2 0 0 0-2-2H4" />
    <path d="M8 21h12a2 2 0 0 0 2-2v-1a1 1 0 0 0-1-1H11a1 1 0 0 0-1 1v1a2 2 0 1 1-4 0V5a2 2 0 1 0-4 0v2a1 1 0 0 0 1 1h3" />
  </svg>
);

/** Lucide `chart-spline` (ISC). */
export const LuChartSpline = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M3 3v16a2 2 0 0 0 2 2h16" />
    <path d="M7 16c.5-2 1.5-7 4-7 2 0 2 3 4 3 2.5 0 4.5-5 5-7" />
  </svg>
);

/** Lucide `chart-pie` (ISC). */
export const LuChartPie = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M21 12c.552 0 1.005-.449.95-.998a10 10 0 0 0-8.953-8.951c-.55-.055-.998.398-.998.95v8a1 1 0 0 0 1 1z" />
    <path d="M21.21 15.89A10 10 0 1 1 8 2.83" />
  </svg>
);

/** Lucide `crown` (ISC). */
export const LuCrown = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M11.562 3.266a.5.5 0 0 1 .876 0L15.39 8.87a1 1 0 0 0 1.516.294L21.183 5.5a.5.5 0 0 1 .798.519l-2.834 10.246a1 1 0 0 1-.956.734H5.81a1 1 0 0 1-.957-.734L2.02 6.02a.5.5 0 0 1 .798-.519l4.276 3.664a1 1 0 0 0 1.516-.294z" />
    <path d="M5 21h14" />
  </svg>
);

/** Lucide `gem` (ISC). */
export const LuGem = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M10.5 3 8 9l4 13 4-13-2.5-6" />
    <path d="M17 3a2 2 0 0 1 1.6.8l3 4a2 2 0 0 1 .013 2.382l-7.99 10.986a2 2 0 0 1-3.247 0l-7.99-10.986A2 2 0 0 1 2.4 7.8l2.998-3.997A2 2 0 0 1 7 3z" />
    <path d="M2 9h20" />
  </svg>
);

/** Lucide `medal` (ISC). */
export const LuMedal = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M7.21 15 2.66 7.14a2 2 0 0 1 .13-2.2L4.4 2.8A2 2 0 0 1 6 2h12a2 2 0 0 1 1.6.8l1.6 2.14a2 2 0 0 1 .14 2.2L16.79 15" />
    <path d="M11 12 5.12 2.2" />
    <path d="m13 12 5.88-9.8" />
    <path d="M8 7h8" />
    <circle cx="12" cy="17" r="5" />
    <path d="M12 18v-2h-.5" />
  </svg>
);

/** Lucide `hash` (ISC). */
export const LuHash = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <line x1="4" x2="20" y1="9" y2="9" />
    <line x1="4" x2="20" y1="15" y2="15" />
    <line x1="10" x2="8" y1="3" y2="21" />
    <line x1="16" x2="14" y1="3" y2="21" />
  </svg>
);

/** Lucide `shield` (ISC). */
export const LuShield = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z" />
  </svg>
);

/** Lucide `star` (ISC). */
export const LuStar = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z" />
  </svg>
);

/** Lucide `thumbs-down` (ISC). */
export const LuThumbsDown = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M17 14V2" />
    <path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22a3.13 3.13 0 0 1-3-3.88Z" />
  </svg>
);

/** Lucide `thumbs-up` (ISC). */
export const LuThumbsUp = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M7 10v12" />
    <path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2a3.13 3.13 0 0 1 3 3.88Z" />
  </svg>
);

/** Lucide `trending-down` (ISC). */
export const LuTrendingDown = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M16 17h6v-6" />
    <path d="m22 17-8.5-8.5-5 5L2 7" />
  </svg>
);

/** Lucide `trophy` (ISC). */
export const LuTrophy = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M10 14.66v1.626a2 2 0 0 1-.976 1.696A5 5 0 0 0 7 21.978" />
    <path d="M14 14.66v1.626a2 2 0 0 0 .976 1.696A5 5 0 0 1 17 21.978" />
    <path d="M18 9h1.5a1 1 0 0 0 0-5H18" />
    <path d="M4 22h16" />
    <path d="M6 9a6 6 0 0 0 12 0V3a1 1 0 0 0-1-1H7a1 1 0 0 0-1 1z" />
    <path d="M6 9H4.5a1 1 0 0 1 0-5H6" />
  </svg>
);

/** Lucide `shopping-bag` (ISC). */
export const LuShoppingBag = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M16 10a4 4 0 0 1-8 0" />
    <path d="M3.103 6.034h17.794" />
    <path d="M3.4 5.467a2 2 0 0 0-.4 1.2V20a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6.667a2 2 0 0 0-.4-1.2l-2-2.667A2 2 0 0 0 17 2H7a2 2 0 0 0-1.6.8z" />
  </svg>
);

/** Lucide `credit-card` (ISC). */
export const LuCreditCard = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <rect x="2" y="5" rx="2" />
    <line x1="2" x2="22" y1="10" y2="10" />
  </svg>
);

/** Lucide `shopping-cart` (ISC). */
export const LuShoppingCart = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <circle cx="8" cy="21" r="1" />
    <circle cx="19" cy="21" r="1" />
    <path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12" />
  </svg>
);

/** Lucide `coins` (ISC). */
export const LuCoins = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <circle cx="8" cy="8" r="6" />
    <path d="M18.09 10.37A6 6 0 1 1 10.34 18" />
    <path d="M7 6h1v4" />
    <path d="m16.71 13.88.7.71-2.82 2.82" />
  </svg>
);

/** Lucide `percent` (ISC). */
export const LuPercent = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <line x1="19" x2="5" y1="5" y2="19" />
    <circle cx="6.5" cy="6.5" r="2.5" />
    <circle cx="17.5" cy="17.5" r="2.5" />
  </svg>
);

/** Lucide `gift` (ISC). */
export const LuGift = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <rect x="3" y="8" rx="1" />
    <path d="M12 8v13" />
    <path d="M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7" />
    <path d="M7.5 8a2.5 2.5 0 0 1 0-5A4.8 8 0 0 1 12 8a4.8 8 0 0 1 4.5-5 2.5 2.5 0 0 1 0 5" />
  </svg>
);

/** Lucide `history` (ISC). */
export const LuHistory = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
    <path d="M3 3v5h5" />
    <path d="M12 7v5l4 2" />
  </svg>
);

/** Lucide `store` (ISC). */
export const LuStore = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M15 21v-5a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v5" />
    <path d="M17.774 10.31a1.12 1.12 0 0 0-1.549 0 2.5 2.5 0 0 1-3.451 0 1.12 1.12 0 0 0-1.548 0 2.5 2.5 0 0 1-3.452 0 1.12 1.12 0 0 0-1.549 0 2.5 2.5 0 0 1-3.77-3.248l2.889-4.184A2 2 0 0 1 7 2h10a2 2 0 0 1 1.653.873l2.895 4.192a2.5 2.5 0 0 1-3.774 3.244" />
    <path d="M4 10.95V19a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8.05" />
  </svg>
);

/** Lucide `wallet` (ISC). */
export const LuWallet = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1" />
    <path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4" />
  </svg>
);

/** Lucide `calculator` (ISC). */
export const LuCalculator = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <rect x="4" y="2" rx="2" />
    <line x1="8" x2="16" y1="6" y2="6" />
    <line x1="16" x2="16" y1="14" y2="18" />
    <path d="M16 10h.01" />
    <path d="M12 10h.01" />
    <path d="M8 10h.01" />
    <path d="M12 14h.01" />
    <path d="M8 14h.01" />
    <path d="M12 18h.01" />
    <path d="M8 18h.01" />
  </svg>
);

/** Lucide `database` (ISC). */
export const LuDatabase = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <ellipse cx="12" cy="5" rx="9" ry="3" />
    <path d="M3 5V19A9 3 0 0 0 21 19V5" />
    <path d="M3 12A9 3 0 0 0 21 12" />
  </svg>
);

/** Lucide `activity` (ISC). */
export const LuActivity = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2" />
  </svg>
);

/** Lucide `cpu` (ISC). */
export const LuCpu = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M12 20v2" />
    <path d="M12 2v2" />
    <path d="M17 20v2" />
    <path d="M17 2v2" />
    <path d="M2 12h2" />
    <path d="M2 17h2" />
    <path d="M2 7h2" />
    <path d="M20 12h2" />
    <path d="M20 17h2" />
    <path d="M20 7h2" />
    <path d="M7 20v2" />
    <path d="M7 2v2" />
    <rect x="4" y="4" rx="2" />
    <rect x="8" y="8" rx="1" />
  </svg>
);

/** Lucide `server` (ISC). */
export const LuServer = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <rect x="2" y="2" rx="2" ry="2" />
    <rect x="2" y="14" rx="2" ry="2" />
    <line x1="6" x2="6.01" y1="6" y2="6" />
    <line x1="6" x2="6.01" y1="18" y2="18" />
  </svg>
);

/** Lucide `gauge` (ISC). */
export const LuGauge = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="m12 14 4-4" />
    <path d="M3.34 19a10 10 0 1 1 17.32 0" />
  </svg>
);

/** Lucide `circle-check-big` (ISC). */
export const LuCircleCheckBig = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M21.801 10A10 10 0 1 1 17 3.335" />
    <path d="m9 11 3 3L22 4" />
  </svg>
);

/** Lucide `info` (ISC). */
export const LuInfo = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <circle cx="12" cy="12" r="10" />
    <path d="M12 16v-4" />
    <path d="M12 8h.01" />
  </svg>
);

/** Lucide `circle` (ISC). */
export const LuCircle = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <circle cx="12" cy="12" r="10" />
  </svg>
);

/** Lucide `circle-check` (ISC). */
export const LuCircleCheck = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <circle cx="12" cy="12" r="10" />
    <path d="m9 12 2 2 4-4" />
  </svg>
);

/** Lucide `hourglass` (ISC). */
export const LuHourglass = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M5 22h14" />
    <path d="M5 2h14" />
    <path d="M17 22v-4.172a2 2 0 0 0-.586-1.414L12 12l-4.414 4.414A2 2 0 0 0 7 17.828V22" />
    <path d="M7 2v4.172a2 2 0 0 0 .586 1.414L12 12l4.414-4.414A2 2 0 0 0 17 6.172V2" />
  </svg>
);

/** Lucide `timer` (ISC). */
export const LuTimer = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <line x1="10" x2="14" y1="2" y2="2" />
    <line x1="12" x2="15" y1="14" y2="11" />
    <circle cx="12" cy="14" r="8" />
  </svg>
);

/** Lucide `lock-open` (ISC). */
export const LuLockOpen = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <rect x="3" y="11" rx="2" ry="2" />
    <path d="M7 11V7a5 5 0 0 1 9.9-1" />
  </svg>
);

/** Lucide `badge-check` (ISC). */
export const LuBadgeCheck = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78 4 4 0 0 1 0 6.74 4 4 0 0 1-4.77 4.78 4 4 0 0 1-6.75 0 4 4 0 0 1-4.78-4.77 4 4 0 0 1 0-6.76Z" />
    <path d="m9 12 2 2 4-4" />
  </svg>
);

/** Lucide `key` (ISC). */
export const LuKey = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="m15.5 7.5 2.3 2.3a1 1 0 0 0 1.4 0l2.1-2.1a1 1 0 0 0 0-1.4L19 4" />
    <path d="m21 2-9.6 9.6" />
    <circle cx="7.5" cy="15.5" r="5.5" />
  </svg>
);

/** Lucide `database-backup` (ISC). */
export const LuDatabaseBackup = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <ellipse cx="12" cy="5" rx="9" ry="3" />
    <path d="M3 12a9 3 0 0 0 5 2.69" />
    <path d="M21 9.3V5" />
    <path d="M3 5v14a9 3 0 0 0 6.47 2.88" />
    <path d="M12 12v4h4" />
    <path d="M13 20a5 5 0 0 0 9-3 4.5 4.5 0 0 0-4.5-4.5c-1.33 0-2.54.54-3.41 1.41L12 16" />
  </svg>
);

/** Lucide `moon` (ISC). */
export const LuMoon = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M20.985 12.486a9 9 0 1 1-9.473-9.472c.405-.022.617.46.402.803a6 6 0 0 0 8.268 8.268c.344-.215.825-.004.803.401" />
  </svg>
);

/** Lucide `sun` (ISC). */
export const LuSun = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <circle cx="12" cy="12" r="4" />
    <path d="M12 2v2" />
    <path d="M12 20v2" />
    <path d="m4.93 4.93 1.41 1.41" />
    <path d="m17.66 17.66 1.41 1.41" />
    <path d="M2 12h2" />
    <path d="M20 12h2" />
    <path d="m6.34 17.66-1.41 1.41" />
    <path d="m19.07 4.93-1.41 1.41" />
  </svg>
);

/** Lucide `palette` (ISC). */
export const LuPalette = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M12 22a1 1 0 0 1 0-20 10 9 0 0 1 10 9 5 5 0 0 1-5 5h-2.25a1.75 1.75 0 0 0-1.4 2.8l.3.4a1.75 1.75 0 0 1-1.4 2.8z" />
    <circle cx="13.5" cy="6.5" r=".5" />
    <circle cx="17.5" cy="10.5" r=".5" />
    <circle cx="6.5" cy="12.5" r=".5" />
    <circle cx="8.5" cy="7.5" r=".5" />
  </svg>
);

/** Lucide `monitor-smartphone` (ISC). */
export const LuMonitorSmartphone = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M18 8V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h8" />
    <path d="M10 19v-3.96 3.15" />
    <path d="M7 19h5" />
    <rect x="16" y="12" rx="2" />
  </svg>
);

/** Lucide `user` (ISC). */
export const LuUser = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
    <circle cx="12" cy="7" r="4" />
  </svg>
);

/** Lucide `user-x` (ISC). */
export const LuUserX = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
    <circle cx="9" cy="7" r="4" />
    <line x1="17" x2="22" y1="8" y2="13" />
    <line x1="22" x2="17" y1="8" y2="13" />
  </svg>
);

/** Lucide `user-plus` (ISC). */
export const LuUserPlus = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
    <circle cx="9" cy="7" r="4" />
    <line x1="19" x2="19" y1="8" y2="14" />
    <line x1="22" x2="16" y1="11" y2="11" />
  </svg>
);

/** Lucide `map-pin` (ISC). */
export const LuMapPin = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0" />
    <circle cx="12" cy="10" r="3" />
  </svg>
);

/** Lucide `log-out` (ISC). */
export const LuLogOut = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="m16 17 5-5-5-5" />
    <path d="M21 12H9" />
    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
  </svg>
);

/** Lucide `shield-check` (ISC). */
export const LuShieldCheck = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z" />
    <path d="m9 12 2 2 4-4" />
  </svg>
);

/** Lucide `presentation` (ISC). */
export const LuPresentation = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M2 3h20" />
    <path d="M21 3v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V3" />
    <path d="m7 21 5-5 5 5" />
  </svg>
);

/** Lucide `user-minus` (ISC). */
export const LuUserMinus = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
    <circle cx="9" cy="7" r="4" />
    <line x1="22" x2="16" y1="11" y2="11" />
  </svg>
);

/** Lucide `briefcase` (ISC). */
export const LuBriefcase = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
    <rect x="2" y="6" rx="2" />
  </svg>
);

/** Semantik kalit → Lucide ikonkasi (D18: `domen.ob'ekt.holat`). */
export const LUCIDE_ICONS: Record<string, (p: IconProps) => React.JSX.Element> = {
  "action.add": LuPlus,
  "action.bookmark": LuBookmark,
  "action.cancel": LuBan,
  "action.clear": LuXCircle,
  "action.clipboard": LuClipboard,
  "action.copy": LuCopy,
  "action.delete": LuTrash2,
  "action.download": LuDownload,
  "action.edit": LuPencilLine,
  "action.eye": LuEye,
  "action.eyeOff": LuEyeOff,
  "action.filter": LuFunnel,
  "action.format": LuWand2,
  "action.fullscreen": LuMaximize,
  "action.help": LuCircleHelp,
  "action.pin": LuPin,
  "action.print": LuPrinter,
  "action.retry": LuRefreshCw,
  "action.save": LuSave,
  "action.search": LuSearch,
  "action.share": LuShare2,
  "action.sliders": LuSlidersHorizontal,
  "action.sortAsc": LuArrowUpNarrowWide,
  "action.sortDesc": LuArrowDownWideNarrow,
  "action.sound": LuVolume2,
  "action.upload": LuUpload,
  "content.algorithm": LuRoute,
  "content.article": LuNewspaper,
  "content.audio": LuHeadphones,
  "content.category": LuFolder,
  "content.code": LuCode,
  "content.course": LuGraduationCap,
  "content.file": LuFile,
  "content.image": LuImage,
  "content.level": LuLayers,
  "content.pdf": LuFileText,
  "content.problem": LuBookOpen,
  "content.quiz": LuCircleHelp,
  "content.roadmap": LuMap,
  "content.step": LuFootprints,
  "content.tag": LuTag,
  "content.terminal": LuTerminal,
  "content.test": LuBeaker,
  "content.video": LuVideo,
  "contest.arena": LuTarget,
  "contest.calendar": LuCalendar,
  "contest.clock": LuClock,
  "contest.duel": LuSwords,
  "contest.flag": LuFlag,
  "contest.formatAcm": LuCircleX,
  "contest.formatIoi": LuChartBar,
  "contest.hackathon": LuCode,
  "contest.live": LuRadio,
  "contest.lock": LuLock,
  "contest.rated": LuTrendingUp,
  "contest.register": LuClipboardCheck,
  "contest.standings": LuListOrdered,
  "contest.team": LuUsers,
  "device.appStore": LuDownload,
  "device.browser": LuGlobe,
  "device.desktop": LuMonitor,
  "device.laptop": LuLaptop,
  "device.phone": LuSmartphone,
  "device.qr": LuQrCode,
  "device.tablet": LuTablet,
  "device.touch": LuPointer,
  "empty.attempts": LuClipboardList,
  "empty.files": LuFolderOpen,
  "empty.messages": LuMessageCircle,
  "empty.notFound": LuCompass,
  "empty.notifications": LuBellOff,
  "empty.search": LuSearchX,
  "empty.serverError": LuSettings,
  "empty.team": LuUsers,
  "error.forbidden": LuBan,
  "error.invalid": LuTriangleAlert,
  "error.network": LuWifiOff,
  "error.notFound": LuSearchX,
  "error.server": LuFlame,
  "error.timeout": LuTimerOff,
  "locale.flag": LuFlag,
  "locale.globe": LuGlobe,
  "locale.region": LuMap,
  "locale.switch": LuLanguages,
  "locale.timezone": LuClock,
  "locale.translate": LuLanguages,
  "markdown.bold": LuBold,
  "markdown.code": LuCode,
  "markdown.codeBlock": LuCodeSquare,
  "markdown.formula": LuSigma,
  "markdown.heading": LuHeading,
  "markdown.hr": LuMinus,
  "markdown.image": LuImage,
  "markdown.italic": LuItalic,
  "markdown.link": LuLink,
  "markdown.list": LuList,
  "markdown.orderedList": LuListOrdered,
  "markdown.preview": LuEye,
  "markdown.quote": LuQuote,
  "markdown.table": LuTable,
  "media.clip": LuPaperclip,
  "media.crop": LuCrop,
  "media.folder": LuFolder,
  "media.fullscreen": LuMaximize,
  "media.next": LuSkipForward,
  "media.pause": LuPause,
  "media.play": LuPlay,
  "media.prev": LuSkipBack,
  "media.rotate": LuRotateCw,
  "media.volume": LuVolume2,
  "media.zoomIn": LuZoomIn,
  "media.zoomOut": LuZoomOut,
  "nav.back": LuArrowLeft,
  "nav.close": LuX,
  "nav.collapse": LuPanelLeftClose,
  "nav.expandDown": LuChevronDown,
  "nav.expandUp": LuChevronUp,
  "nav.external": LuExternalLink,
  "nav.filterPanel": LuSlidersHorizontal,
  "nav.forward": LuArrowRight,
  "nav.grid": LuLayoutGrid,
  "nav.home": LuHouse,
  "nav.leaderboard": LuChartNoAxesColumn,
  "nav.list": LuList,
  "nav.menu": LuMenu,
  "nav.more": LuEllipsis,
  "nav.problems": LuBookOpen,
  "nav.quiz": LuCircleHelp,
  "nav.separator": LuChevronRight,
  "nav.up": LuArrowUp,
  "notification.announce": LuMegaphone,
  "notification.badgeNew": LuBadge,
  "notification.bell": LuBell,
  "notification.bellRead": LuBell,
  "notification.changelog": LuMegaphone,
  "notification.chat": LuMessageCircle,
  "notification.comment": LuMessageSquare,
  "notification.email": LuMail,
  "notification.muted": LuBellOff,
  "notification.reply": LuReply,
  "ranking.badge": LuBadge,
  "ranking.certificate": LuScroll,
  "ranking.chartBar": LuChartNoAxesColumn,
  "ranking.chartLine": LuChartSpline,
  "ranking.chartPie": LuChartPie,
  "ranking.crown": LuCrown,
  "ranking.diamond": LuGem,
  "ranking.medalBronze": LuMedal,
  "ranking.medalGold": LuMedal,
  "ranking.medalSilver": LuMedal,
  "ranking.podium": LuChartNoAxesColumn,
  "ranking.rank": LuHash,
  "ranking.shield": LuShield,
  "ranking.star": LuStar,
  "ranking.streak": LuFlame,
  "ranking.thumbDown": LuThumbsDown,
  "ranking.thumbUp": LuThumbsUp,
  "ranking.trendDown": LuTrendingDown,
  "ranking.trendUp": LuTrendingUp,
  "ranking.trophy": LuTrophy,
  "shop.buy": LuShoppingBag,
  "shop.card": LuCreditCard,
  "shop.cart": LuShoppingCart,
  "shop.coin": LuCoins,
  "shop.discount": LuPercent,
  "shop.gift": LuGift,
  "shop.history": LuHistory,
  "shop.price": LuStar,
  "shop.store": LuStore,
  "shop.wallet": LuWallet,
  "stats.calculator": LuCalculator,
  "stats.chartBar": LuChartNoAxesColumn,
  "stats.chartLine": LuChartSpline,
  "stats.chartPie": LuChartPie,
  "stats.database": LuDatabase,
  "stats.funnel": LuFunnel,
  "stats.load": LuActivity,
  "stats.memory": LuCpu,
  "stats.percent": LuPercent,
  "stats.server": LuServer,
  "stats.speed": LuGauge,
  "stats.table": LuTable,
  "status.bad": LuCircleX,
  "status.blocked": LuBan,
  "status.clock": LuClock,
  "status.finished": LuCircleCheckBig,
  "status.info": LuInfo,
  "status.live": LuRadio,
  "status.locked": LuLock,
  "status.offline": LuCircle,
  "status.ok": LuCircleCheck,
  "status.online": LuCircle,
  "status.pending": LuHourglass,
  "status.timer": LuTimer,
  "status.unlocked": LuLockOpen,
  "status.verified": LuBadgeCheck,
  "status.warning": LuTriangleAlert,
  "status.watching": LuEye,
  "system.apiKey": LuKey,
  "system.backup": LuDatabaseBackup,
  "system.dark": LuMoon,
  "system.device": LuCpu,
  "system.key": LuKey,
  "system.light": LuSun,
  "system.log": LuFileText,
  "system.monitor": LuMonitor,
  "system.palette": LuPalette,
  "system.security": LuShield,
  "system.sessions": LuMonitorSmartphone,
  "system.settings": LuSettings,
  "user.avatar": LuUser,
  "user.block": LuUserX,
  "user.education": LuGraduationCap,
  "user.follow": LuUserPlus,
  "user.followers": LuUsers,
  "user.group": LuUsers,
  "user.invite": LuUserPlus,
  "user.link": LuLink,
  "user.location": LuMapPin,
  "user.logout": LuLogOut,
  "user.profile": LuUser,
  "user.roleAdmin": LuShieldCheck,
  "user.roleStudent": LuGraduationCap,
  "user.roleTeacher": LuPresentation,
  "user.unfollow": LuUserMinus,
  "user.work": LuBriefcase,
};
