/** Heroicons (outline) ikonkalari (MIT), 24×24 to'r.
 *
 *  Generatsiya qilingan — `tools/gen-icon-packs.mjs` bilan qayta yasash mumkin.
 *  Qo'lda tahrirlanmaydi.
 *
 *  ⚠️ Manba CDN'dan **bir marta** olinadi va shu faylga yoziladi: ilova
 *  ishga tushganda tarmoqqa chiqmaydi, ya'ni yangi dependency ham,
 *  kutubxona yangilanishini kuzatish ham kerak emas.
 *
 *  133 ta ikonka.
 */

type IconProps = { className?: string };

const base = { viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 1.5, strokeLinecap: "round" as const, strokeLinejoin: "round" as const, xmlns: "http://www.w3.org/2000/svg" };

/** Heroicons (outline) `plus` (MIT). */
export const HiPlus = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15"/>
  </svg>
);

/** Heroicons (outline) `bookmark` (MIT). */
export const HiBookmark = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M17.593 3.322c1.1.128 1.907 1.077 1.907 2.185V21L12 17.25 4.5 21V5.507c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0 1 11.186 0Z"/>
  </svg>
);

/** Heroicons (outline) `x-circle` (MIT). */
export const HiXCircle = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="m9.75 9.75 4.5 4.5m0-4.5-4.5 4.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/>
  </svg>
);

/** Heroicons (outline) `clipboard` (MIT). */
export const HiClipboard = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M15.666 3.888A2.25 2.25 0 0 0 13.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 0 1-.75.75H9a.75.75 0 0 1-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 0 1-2.25 2.25H6.75A2.25 2.25 0 0 1 4.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 0 1 1.927-.184"/>
  </svg>
);

/** Heroicons (outline) `document-duplicate` (MIT). */
export const HiDocumentDuplicate = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 0 1-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H6.75a9.06 9.06 0 0 1 1.5.124m7.5 10.376h3.375c.621 0 1.125-.504 1.125-1.125V11.25c0-4.46-3.243-8.161-7.5-8.876a9.06 9.06 0 0 0-1.5-.124H9.375c-.621 0-1.125.504-1.125 1.125v3.5m7.5 10.375H9.375a1.125 1.125 0 0 1-1.125-1.125v-9.25m12 6.625v-1.875a3.375 3.375 0 0 0-3.375-3.375h-1.5a1.125 1.125 0 0 1-1.125-1.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H9.75"/>
  </svg>
);

/** Heroicons (outline) `trash` (MIT). */
export const HiTrash = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0"/>
  </svg>
);

/** Heroicons (outline) `arrow-down-tray` (MIT). */
export const HiArrowDownTray = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3"/>
  </svg>
);

/** Heroicons (outline) `pencil` (MIT). */
export const HiPencil = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Zm0 0L19.5 7.125"/>
  </svg>
);

/** Heroicons (outline) `eye` (MIT). */
export const HiEye = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z"/>
    <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"/>
  </svg>
);

/** Heroicons (outline) `eye-slash` (MIT). */
export const HiEyeSlash = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88"/>
  </svg>
);

/** Heroicons (outline) `funnel` (MIT). */
export const HiFunnel = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 3c2.755 0 5.455.232 8.083.678.533.09.917.556.917 1.096v1.044a2.25 2.25 0 0 1-.659 1.591l-5.432 5.432a2.25 2.25 0 0 0-.659 1.591v2.927a2.25 2.25 0 0 1-1.244 2.013L9.75 21v-6.568a2.25 2.25 0 0 0-.659-1.591L3.659 7.409A2.25 2.25 0 0 1 3 5.818V4.774c0-.54.384-1.006.917-1.096A48.32 48.32 0 0 1 12 3Z"/>
  </svg>
);

/** Heroicons (outline) `sparkles` (MIT). */
export const HiSparkles = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z"/>
  </svg>
);

/** Heroicons (outline) `arrows-pointing-out` (MIT). */
export const HiArrowsPointingOut = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3.75v4.5m0-4.5h4.5m-4.5 0L9 9M3.75 20.25v-4.5m0 4.5h4.5m-4.5 0L9 15M20.25 3.75h-4.5m4.5 0v4.5m0-4.5L15 9m5.25 11.25h-4.5m4.5 0v-4.5m0 4.5L15 15"/>
  </svg>
);

/** Heroicons (outline) `question-mark-circle` (MIT). */
export const HiQuestionMarkCircle = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 5.25h.008v.008H12v-.008Z"/>
  </svg>
);

/** Heroicons (outline) `map-pin` (MIT). */
export const HiMapPin = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"/>
    <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1 1 15 0Z"/>
  </svg>
);

/** Heroicons (outline) `printer` (MIT). */
export const HiPrinter = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M6.72 13.829c-.24.03-.48.062-.72.096m.72-.096a42.415 42.415 0 0 1 10.56 0m-10.56 0L6.34 18m10.94-4.171c.24.03.48.062.72.096m-.72-.096L17.66 18m0 0 .229 2.523a1.125 1.125 0 0 1-1.12 1.227H7.231c-.662 0-1.18-.568-1.12-1.227L6.34 18m11.318 0h1.091A2.25 2.25 0 0 0 21 15.75V9.456c0-1.081-.768-2.015-1.837-2.175a48.055 48.055 0 0 0-1.913-.247M6.34 18H5.25A2.25 2.25 0 0 1 3 15.75V9.456c0-1.081.768-2.015 1.837-2.175a48.041 48.041 0 0 1 1.913-.247m10.5 0a48.536 48.536 0 0 0-10.5 0m10.5 0V3.375c0-.621-.504-1.125-1.125-1.125h-8.25c-.621 0-1.125.504-1.125 1.125v3.659M18 10.5h.008v.008H18V10.5Zm-3 0h.008v.008H15V10.5Z"/>
  </svg>
);

/** Heroicons (outline) `arrow-path` (MIT). */
export const HiArrowPath = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99"/>
  </svg>
);

/** Heroicons (outline) `bookmark-square` (MIT). */
export const HiBookmarkSquare = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 3.75V16.5L12 14.25 7.5 16.5V3.75m9 0H18A2.25 2.25 0 0 1 20.25 6v12A2.25 2.25 0 0 1 18 20.25H6A2.25 2.25 0 0 1 3.75 18V6A2.25 2.25 0 0 1 6 3.75h1.5m9 0h-9"/>
  </svg>
);

/** Heroicons (outline) `magnifying-glass` (MIT). */
export const HiMagnifyingGlass = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z"/>
  </svg>
);

/** Heroicons (outline) `share` (MIT). */
export const HiShare = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M7.217 10.907a2.25 2.25 0 1 0 0 2.186m0-2.186c.18.324.283.696.283 1.093s-.103.77-.283 1.093m0-2.186 9.566-5.314m-9.566 7.5 9.566 5.314m0 0a2.25 2.25 0 1 0 3.935 2.186 2.25 2.25 0 0 0-3.935-2.186Zm0-12.814a2.25 2.25 0 1 0 3.933-2.185 2.25 2.25 0 0 0-3.933 2.185Z"/>
  </svg>
);

/** Heroicons (outline) `adjustments-horizontal` (MIT). */
export const HiAdjustmentsHorizontal = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 6h9.75M10.5 6a1.5 1.5 0 1 1-3 0m3 0a1.5 1.5 0 1 0-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m-9.75 0h9.75"/>
  </svg>
);

/** Heroicons (outline) `bars-arrow-up` (MIT). */
export const HiBarsArrowUp = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M3 4.5h14.25M3 9h9.75M3 13.5h5.25m5.25-.75L17.25 9m0 0L21 12.75M17.25 9v12"/>
  </svg>
);

/** Heroicons (outline) `bars-arrow-down` (MIT). */
export const HiBarsArrowDown = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M3 4.5h14.25M3 9h9.75M3 13.5h9.75m4.5-4.5v12m0 0-3.75-3.75M17.25 21 21 17.25"/>
  </svg>
);

/** Heroicons (outline) `speaker-wave` (MIT). */
export const HiSpeakerWave = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M19.114 5.636a9 9 0 0 1 0 12.728M16.463 8.288a5.25 5.25 0 0 1 0 7.424M6.75 8.25l4.72-4.72a.75.75 0 0 1 1.28.53v15.88a.75.75 0 0 1-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.507-1.938-1.354A9.009 9.009 0 0 1 2.25 12c0-.83.112-1.633.322-2.396C2.806 8.756 3.63 8.25 4.51 8.25H6.75Z"/>
  </svg>
);

/** Heroicons (outline) `arrow-up-tray` (MIT). */
export const HiArrowUpTray = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5"/>
  </svg>
);

/** Heroicons (outline) `newspaper` (MIT). */
export const HiNewspaper = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 7.5h1.5m-1.5 3h1.5m-7.5 3h7.5m-7.5 3h7.5m3-9h3.375c.621 0 1.125.504 1.125 1.125V18a2.25 2.25 0 0 1-2.25 2.25M16.5 7.5V18a2.25 2.25 0 0 0 2.25 2.25M16.5 7.5V4.875c0-.621-.504-1.125-1.125-1.125H4.125C3.504 3.75 3 4.254 3 4.875V18a2.25 2.25 0 0 0 2.25 2.25h13.5M6 7.5h3v3H6v-3Z"/>
  </svg>
);

/** Heroicons (outline) `musical-note` (MIT). */
export const HiMusicalNote = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="m9 9 10.5-3m0 6.553v3.75a2.25 2.25 0 0 1-1.632 2.163l-1.32.377a1.803 1.803 0 1 1-.99-3.467l2.31-.66a2.25 2.25 0 0 0 1.632-2.163Zm0 0V2.25L9 5.25v10.303m0 0v3.75a2.25 2.25 0 0 1-1.632 2.163l-1.32.377a1.803 1.803 0 0 1-.99-3.467l2.31-.66A2.25 2.25 0 0 0 9 15.553Z"/>
  </svg>
);

/** Heroicons (outline) `folder` (MIT). */
export const HiFolder = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z"/>
  </svg>
);

/** Heroicons (outline) `code-bracket` (MIT). */
export const HiCodeBracket = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M17.25 6.75 22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3-4.5 16.5"/>
  </svg>
);

/** Heroicons (outline) `academic-cap` (MIT). */
export const HiAcademicCap = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M4.26 10.147a60.438 60.438 0 0 0-.491 6.347A48.62 48.62 0 0 1 12 20.904a48.62 48.62 0 0 1 8.232-4.41 60.46 60.46 0 0 0-.491-6.347m-15.482 0a50.636 50.636 0 0 0-2.658-.813A59.906 59.906 0 0 1 12 3.493a59.903 59.903 0 0 1 10.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.717 50.717 0 0 1 12 13.489a50.702 50.702 0 0 1 7.74-3.342M6.75 15a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm0 0v-3.675A55.378 55.378 0 0 1 12 8.443m-7.007 11.55A5.981 5.981 0 0 0 6.75 15.75v-1.5"/>
  </svg>
);

/** Heroicons (outline) `document` (MIT). */
export const HiDocument = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z"/>
  </svg>
);

/** Heroicons (outline) `photo` (MIT). */
export const HiPhoto = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="m2.25 15.75 5.159-5.159a2.25 2.25 0 0 1 3.182 0l5.159 5.159m-1.5-1.5 1.409-1.409a2.25 2.25 0 0 1 3.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 0 0 1.5-1.5V6a1.5 1.5 0 0 0-1.5-1.5H3.75A1.5 1.5 0 0 0 2.25 6v12a1.5 1.5 0 0 0 1.5 1.5Zm10.5-11.25h.008v.008h-.008V8.25Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z"/>
  </svg>
);

/** Heroicons (outline) `chart-bar` (MIT). */
export const HiChartBar = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z"/>
  </svg>
);

/** Heroicons (outline) `book-open` (MIT). */
export const HiBookOpen = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 0 0 6 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 0 1 6 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 0 1 6-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0 0 18 18a8.967 8.967 0 0 0-6 2.292m0-14.25v14.25"/>
  </svg>
);

/** Heroicons (outline) `map` (MIT). */
export const HiMap = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 6.75V15m6-6v8.25m.503 3.498 4.875-2.437c.381-.19.622-.58.622-1.006V4.82c0-.836-.88-1.38-1.628-1.006l-3.869 1.934c-.317.159-.69.159-1.006 0L9.503 3.252a1.125 1.125 0 0 0-1.006 0L3.622 5.689C3.24 5.88 3 6.27 3 6.695V19.18c0 .836.88 1.38 1.628 1.006l3.869-1.934c.317-.159.69-.159 1.006 0l4.994 2.497c.317.158.69.158 1.006 0Z"/>
  </svg>
);

/** Heroicons (outline) `numbered-list` (MIT). */
export const HiNumberedList = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M8.242 5.992h12m-12 6.003H20.24m-12 5.999h12M4.117 7.495v-3.75H2.99m1.125 3.75H2.99m1.125 0H5.24m-1.92 2.577a1.125 1.125 0 1 1 1.591 1.59l-1.83 1.83h2.16M2.99 15.745h1.125a1.125 1.125 0 0 1 0 2.25H3.74m0-.002h.375a1.125 1.125 0 0 1 0 2.25H2.99"/>
  </svg>
);

/** Heroicons (outline) `tag` (MIT). */
export const HiTag = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M9.568 3H5.25A2.25 2.25 0 0 0 3 5.25v4.318c0 .597.237 1.17.659 1.591l9.581 9.581c.699.699 1.78.872 2.607.33a18.095 18.095 0 0 0 5.223-5.223c.542-.827.369-1.908-.33-2.607L11.16 3.66A2.25 2.25 0 0 0 9.568 3Z"/>
    <path strokeLinecap="round" strokeLinejoin="round" d="M6 6h.008v.008H6V6Z"/>
  </svg>
);

/** Heroicons (outline) `command-line` (MIT). */
export const HiCommandLine = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="m6.75 7.5 3 2.25-3 2.25m4.5 0h3m-9 8.25h13.5A2.25 2.25 0 0 0 21 18V6a2.25 2.25 0 0 0-2.25-2.25H5.25A2.25 2.25 0 0 0 3 6v12a2.25 2.25 0 0 0 2.25 2.25Z"/>
  </svg>
);

/** Heroicons (outline) `beaker` (MIT). */
export const HiBeaker = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 0 1-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 0 1 4.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0 1 12 15a9.065 9.065 0 0 0-6.23-.693L5 14.5m14.8.8 1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0 1 12 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5"/>
  </svg>
);

/** Heroicons (outline) `play-circle` (MIT). */
export const HiPlayCircle = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/>
    <path strokeLinecap="round" strokeLinejoin="round" d="M15.91 11.672a.375.375 0 0 1 0 .656l-5.603 3.113a.375.375 0 0 1-.557-.328V8.887c0-.286.307-.466.557-.327l5.603 3.112Z"/>
  </svg>
);

/** Heroicons (outline) `bolt` (MIT). */
export const HiBolt = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="m3.75 13.5 10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75Z"/>
  </svg>
);

/** Heroicons (outline) `calendar` (MIT). */
export const HiCalendar = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 0 1 2.25-2.25h13.5A2.25 2.25 0 0 1 21 7.5v11.25m-18 0A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75m-18 0v-7.5A2.25 2.25 0 0 1 5.25 9h13.5A2.25 2.25 0 0 1 21 11.25v7.5"/>
  </svg>
);

/** Heroicons (outline) `clock` (MIT). */
export const HiClock = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/>
  </svg>
);

/** Heroicons (outline) `flag` (MIT). */
export const HiFlag = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M3 3v1.5M3 21v-6m0 0 2.77-.693a9 9 0 0 1 6.208.682l.108.054a9 9 0 0 0 6.086.71l3.114-.732a48.524 48.524 0 0 1-.005-10.499l-3.11.732a9 9 0 0 1-6.085-.711l-.108-.054a9 9 0 0 0-6.208-.682L3 4.5M3 15V4.5"/>
  </svg>
);

/** Heroicons (outline) `circle-stack` (MIT). */
export const HiCircleStack = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125"/>
  </svg>
);

/** Heroicons (outline) `signal` (MIT). */
export const HiSignal = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M9.348 14.652a3.75 3.75 0 0 1 0-5.304m5.304 0a3.75 3.75 0 0 1 0 5.304m-7.425 2.121a6.75 6.75 0 0 1 0-9.546m9.546 0a6.75 6.75 0 0 1 0 9.546M5.106 18.894c-3.808-3.807-3.808-9.98 0-13.788m13.788 0c3.808 3.807 3.808 9.98 0 13.788M12 12h.008v.008H12V12Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z"/>
  </svg>
);

/** Heroicons (outline) `lock-closed` (MIT). */
export const HiLockClosed = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z"/>
  </svg>
);

/** Heroicons (outline) `arrow-trending-up` (MIT). */
export const HiArrowTrendingUp = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18 9 11.25l4.306 4.306a11.95 11.95 0 0 1 5.814-5.518l2.74-1.22m0 0-5.94-2.281m5.94 2.28-2.28 5.941"/>
  </svg>
);

/** Heroicons (outline) `clipboard-document-check` (MIT). */
export const HiClipboardDocumentCheck = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M11.35 3.836c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75 2.25 2.25 0 0 0-.1-.664m-5.8 0A2.251 2.251 0 0 1 13.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m8.9-4.414c.376.023.75.05 1.124.08 1.131.094 1.976 1.057 1.976 2.192V16.5A2.25 2.25 0 0 1 18 18.75h-2.25m-7.5-10.5H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V18.75m-7.5-10.5h6.375c.621 0 1.125.504 1.125 1.125v9.375m-8.25-3 1.5 1.5 3-3.75"/>
  </svg>
);

/** Heroicons (outline) `table-cells` (MIT). */
export const HiTableCells = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 0 1-1.125-1.125M3.375 19.5h7.5c.621 0 1.125-.504 1.125-1.125m-9.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-7.5A1.125 1.125 0 0 1 12 18.375m9.75-12.75c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125m19.5 0v1.5c0 .621-.504 1.125-1.125 1.125M2.25 5.625v1.5c0 .621.504 1.125 1.125 1.125m0 0h17.25m-17.25 0h7.5c.621 0 1.125.504 1.125 1.125M3.375 8.25c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125m17.25-3.75h-7.5c-.621 0-1.125.504-1.125 1.125m8.625-1.125c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125m-17.25 0h7.5m-7.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125M12 10.875v-1.5m0 1.5c0 .621-.504 1.125-1.125 1.125M12 10.875c0 .621.504 1.125 1.125 1.125m-2.25 0c.621 0 1.125.504 1.125 1.125M13.125 12h7.5m-7.5 0c-.621 0-1.125.504-1.125 1.125M20.625 12c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125m-17.25 0h7.5M12 14.625v-1.5m0 1.5c0 .621-.504 1.125-1.125 1.125M12 14.625c0 .621.504 1.125 1.125 1.125m-2.25 0c.621 0 1.125.504 1.125 1.125m0 1.5v-1.5m0 0c0-.621.504-1.125 1.125-1.125m0 0h7.5"/>
  </svg>
);

/** Heroicons (outline) `users` (MIT). */
export const HiUsers = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 4.121-.952 4.125 4.125 0 0 0-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 0 1 8.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0 1 11.964-3.07M12 6.375a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0Zm8.25 2.25a2.625 2.625 0 1 1-5.25 0 2.625 2.625 0 0 1 5.25 0Z"/>
  </svg>
);

/** Heroicons (outline) `globe-alt` (MIT). */
export const HiGlobeAlt = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 21a9.004 9.004 0 0 0 8.716-6.747M12 21a9.004 9.004 0 0 1-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 0 1 7.843 4.582M12 3a8.997 8.997 0 0 0-7.843 4.582m15.686 0A11.953 11.953 0 0 1 12 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0 1 21 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0 1 12 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 0 1 3 12c0-1.605.42-3.113 1.157-4.418"/>
  </svg>
);

/** Heroicons (outline) `computer-desktop` (MIT). */
export const HiComputerDesktop = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 17.25v1.007a3 3 0 0 1-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0 1 15 18.257V17.25m6-12V15a2.25 2.25 0 0 1-2.25 2.25H5.25A2.25 2.25 0 0 1 3 15V5.25m18 0A2.25 2.25 0 0 0 18.75 3H5.25A2.25 2.25 0 0 0 3 5.25m18 0V12a2.25 2.25 0 0 1-2.25 2.25H5.25A2.25 2.25 0 0 1 3 12V5.25"/>
  </svg>
);

/** Heroicons (outline) `device-phone-mobile` (MIT). */
export const HiDevicePhoneMobile = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 1.5H8.25A2.25 2.25 0 0 0 6 3.75v16.5a2.25 2.25 0 0 0 2.25 2.25h7.5A2.25 2.25 0 0 0 18 20.25V3.75a2.25 2.25 0 0 0-2.25-2.25H13.5m-3 0V3h3V1.5m-3 0h3m-3 18.75h3"/>
  </svg>
);

/** Heroicons (outline) `qr-code` (MIT). */
export const HiQrCode = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 4.875c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5A1.125 1.125 0 0 1 3.75 9.375v-4.5ZM3.75 14.625c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5a1.125 1.125 0 0 1-1.125-1.125v-4.5ZM13.5 4.875c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5A1.125 1.125 0 0 1 13.5 9.375v-4.5Z"/>
    <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 6.75h.75v.75h-.75v-.75ZM6.75 16.5h.75v.75h-.75v-.75ZM16.5 6.75h.75v.75h-.75v-.75ZM13.5 13.5h.75v.75h-.75v-.75ZM13.5 19.5h.75v.75h-.75v-.75ZM19.5 13.5h.75v.75h-.75v-.75ZM19.5 19.5h.75v.75h-.75v-.75ZM16.5 16.5h.75v.75h-.75v-.75Z"/>
  </svg>
);

/** Heroicons (outline) `device-tablet` (MIT). */
export const HiDeviceTablet = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5h3m-6.75 2.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-15a2.25 2.25 0 0 0-2.25-2.25H6.75A2.25 2.25 0 0 0 4.5 4.5v15a2.25 2.25 0 0 0 2.25 2.25Z"/>
  </svg>
);

/** Heroicons (outline) `cursor-arrow-rays` (MIT). */
export const HiCursorArrowRays = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M15.042 21.672 13.684 16.6m0 0-2.51 2.225.569-9.47 5.227 7.917-3.286-.672ZM12 2.25V4.5m5.834.166-1.591 1.591M20.25 10.5H18M7.757 14.743l-1.59 1.59M6 10.5H3.75m4.007-4.243-1.59-1.59"/>
  </svg>
);

/** Heroicons (outline) `clipboard-document-list` (MIT). */
export const HiClipboardDocumentList = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 0 0 2.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 0 0-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75 2.25 2.25 0 0 0-.1-.664m-5.8 0A2.251 2.251 0 0 1 13.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25ZM6.75 12h.008v.008H6.75V12Zm0 3h.008v.008H6.75V15Zm0 3h.008v.008H6.75V18Z"/>
  </svg>
);

/** Heroicons (outline) `folder-open` (MIT). */
export const HiFolderOpen = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 9.776c.112-.017.227-.026.344-.026h15.812c.117 0 .232.009.344.026m-16.5 0a2.25 2.25 0 0 0-1.883 2.542l.857 6a2.25 2.25 0 0 0 2.227 1.932H19.05a2.25 2.25 0 0 0 2.227-1.932l.857-6a2.25 2.25 0 0 0-1.883-2.542m-16.5 0V6A2.25 2.25 0 0 1 6 3.75h3.879a1.5 1.5 0 0 1 1.06.44l2.122 2.12a1.5 1.5 0 0 0 1.06.44H18A2.25 2.25 0 0 1 20.25 9v.776"/>
  </svg>
);

/** Heroicons (outline) `chat-bubble-oval-left` (MIT). */
export const HiChatBubbleOvalLeft = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 20.25c4.97 0 9-3.694 9-8.25s-4.03-8.25-9-8.25S3 7.444 3 12c0 2.104.859 4.023 2.273 5.48.432.447.74 1.04.586 1.641a4.483 4.483 0 0 1-.923 1.785A5.969 5.969 0 0 0 6 21c1.282 0 2.47-.402 3.445-1.087.81.22 1.668.337 2.555.337Z"/>
  </svg>
);

/** Heroicons (outline) `bell-slash` (MIT). */
export const HiBellSlash = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M9.143 17.082a24.248 24.248 0 0 0 3.844.148m-3.844-.148a23.856 23.856 0 0 1-5.455-1.31 8.964 8.964 0 0 0 2.3-5.542m3.155 6.852a3 3 0 0 0 5.667 1.97m1.965-2.277L21 21m-4.225-4.225a23.81 23.81 0 0 0 3.536-1.003A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6.53 6.53m10.245 10.245L6.53 6.53M3 3l3.53 3.53"/>
  </svg>
);

/** Heroicons (outline) `wrench-screwdriver` (MIT). */
export const HiWrenchScrewdriver = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M11.42 15.17 17.25 21A2.652 2.652 0 0 0 21 17.25l-5.877-5.877M11.42 15.17l2.496-3.03c.317-.384.74-.626 1.208-.766M11.42 15.17l-4.655 5.653a2.548 2.548 0 1 1-3.586-3.586l6.837-5.63m5.108-.233c.55-.164 1.163-.188 1.743-.14a4.5 4.5 0 0 0 4.486-6.336l-3.276 3.277a3.004 3.004 0 0 1-2.25-2.25l3.276-3.276a4.5 4.5 0 0 0-6.336 4.486c.091 1.076-.071 2.264-.904 2.95l-.102.085m-1.745 1.437L5.909 7.5H4.5L2.25 3.75l1.5-1.5L7.5 4.5v1.409l4.26 4.26m-1.745 1.437 1.745-1.437m6.615 8.206L15.75 15.75M4.867 19.125h.008v.008h-.008v-.008Z"/>
  </svg>
);

/** Heroicons (outline) `slash` (MIT). */
export const HiSlash = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="m9 20.247 6-16.5"/>
  </svg>
);

/** Heroicons (outline) `exclamation-triangle` (MIT). */
export const HiExclamationTriangle = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z"/>
  </svg>
);

/** Heroicons (outline) `wifi` (MIT). */
export const HiWifi = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M8.288 15.038a5.25 5.25 0 0 1 7.424 0M5.106 11.856c3.807-3.808 9.98-3.808 13.788 0M1.924 8.674c5.565-5.565 14.587-5.565 20.152 0M12.53 18.22l-.53.53-.53-.53a.75.75 0 0 1 1.06 0Z"/>
  </svg>
);

/** Heroicons (outline) `fire` (MIT). */
export const HiFire = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M15.362 5.214A8.252 8.252 0 0 1 12 21 8.25 8.25 0 0 1 6.038 7.047 8.287 8.287 0 0 0 9 9.601a8.983 8.983 0 0 1 3.361-6.867 8.21 8.21 0 0 0 3 2.48Z"/>
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 18a3.75 3.75 0 0 0 .495-7.468 5.99 5.99 0 0 0-1.925 3.547 5.975 5.975 0 0 1-2.133-1.001A3.75 3.75 0 0 0 12 18Z"/>
  </svg>
);

/** Heroicons (outline) `language` (MIT). */
export const HiLanguage = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="m10.5 21 5.25-11.25L21 21m-9-3h7.5M3 5.621a48.474 48.474 0 0 1 6-.371m0 0c1.12 0 2.233.038 3.334.114M9 5.25V3m3.334 2.364C11.176 10.658 7.69 15.08 3 17.502m9.334-12.138c.896.061 1.785.147 2.666.257m-4.589 8.495a18.023 18.023 0 0 1-3.827-5.802"/>
  </svg>
);

/** Heroicons (outline) `bold` (MIT). */
export const HiBold = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinejoin="round" d="M6.75 3.744h-.753v8.25h7.125a4.125 4.125 0 0 0 0-8.25H6.75Zm0 0v.38m0 16.122h6.747a4.5 4.5 0 0 0 0-9.001h-7.5v9h.753Zm0 0v-.37m0-15.751h6a3.75 3.75 0 1 1 0 7.5h-6m0-7.5v7.5m0 0v8.25m0-8.25h6.375a4.125 4.125 0 0 1 0 8.25H6.75m.747-15.38h4.875a3.375 3.375 0 0 1 0 6.75H7.497v-6.75Zm0 7.5h5.25a3.75 3.75 0 0 1 0 7.5h-5.25v-7.5Z"/>
  </svg>
);

/** Heroicons (outline) `code-bracket-square` (MIT). */
export const HiCodeBracketSquare = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M14.25 9.75 16.5 12l-2.25 2.25m-4.5 0L7.5 12l2.25-2.25M6 20.25h12A2.25 2.25 0 0 0 20.25 18V6A2.25 2.25 0 0 0 18 3.75H6A2.25 2.25 0 0 0 3.75 6v12A2.25 2.25 0 0 0 6 20.25Z"/>
  </svg>
);

/** Heroicons (outline) `calculator` (MIT). */
export const HiCalculator = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 15.75V18m-7.5-6.75h.008v.008H8.25v-.008Zm0 2.25h.008v.008H8.25V13.5Zm0 2.25h.008v.008H8.25v-.008Zm0 2.25h.008v.008H8.25V18Zm2.498-6.75h.007v.008h-.007v-.008Zm0 2.25h.007v.008h-.007V13.5Zm0 2.25h.007v.008h-.007v-.008Zm0 2.25h.007v.008h-.007V18Zm2.504-6.75h.008v.008h-.008v-.008Zm0 2.25h.008v.008h-.008V13.5Zm0 2.25h.008v.008h-.008v-.008Zm0 2.25h.008v.008h-.008V18Zm2.498-6.75h.008v.008h-.008v-.008Zm0 2.25h.008v.008h-.008V13.5ZM8.25 6h7.5v2.25h-7.5V6ZM12 2.25c-1.892 0-3.758.11-5.593.322C5.307 2.7 4.5 3.65 4.5 4.757V19.5a2.25 2.25 0 0 0 2.25 2.25h10.5a2.25 2.25 0 0 0 2.25-2.25V4.757c0-1.108-.806-2.057-1.907-2.185A48.507 48.507 0 0 0 12 2.25Z"/>
  </svg>
);

/** Heroicons (outline) `document-text` (MIT). */
export const HiDocumentText = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z"/>
  </svg>
);

/** Heroicons (outline) `minus` (MIT). */
export const HiMinus = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14"/>
  </svg>
);

/** Heroicons (outline) `italic` (MIT). */
export const HiItalic = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M5.248 20.246H9.05m0 0h3.696m-3.696 0 5.893-16.502m0 0h-3.697m3.697 0h3.803"/>
  </svg>
);

/** Heroicons (outline) `link` (MIT). */
export const HiLink = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M13.19 8.688a4.5 4.5 0 0 1 1.242 7.244l-4.5 4.5a4.5 4.5 0 0 1-6.364-6.364l1.757-1.757m13.35-.622 1.757-1.757a4.5 4.5 0 0 0-6.364-6.364l-4.5 4.5a4.5 4.5 0 0 0 1.242 7.244"/>
  </svg>
);

/** Heroicons (outline) `list-bullet` (MIT). */
export const HiListBullet = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 6.75h12M8.25 12h12m-12 5.25h12M3.75 6.75h.007v.008H3.75V6.75Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0ZM3.75 12h.007v.008H3.75V12Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm-.375 5.25h.007v.008H3.75v-.008Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z"/>
  </svg>
);

/** Heroicons (outline) `chat-bubble-bottom-center-text` (MIT). */
export const HiChatBubbleBottomCenterText = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 0 1 .865-.501 48.172 48.172 0 0 0 3.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z"/>
  </svg>
);

/** Heroicons (outline) `paper-clip` (MIT). */
export const HiPaperClip = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="m18.375 12.739-7.693 7.693a4.5 4.5 0 0 1-6.364-6.364l10.94-10.94A3 3 0 1 1 19.5 7.372L8.552 18.32m.009-.01-.01.01m5.699-9.941-7.81 7.81a1.5 1.5 0 0 0 2.112 2.13"/>
  </svg>
);

/** Heroicons (outline) `scissors` (MIT). */
export const HiScissors = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="m7.848 8.25 1.536.887M7.848 8.25a3 3 0 1 1-5.196-3 3 3 0 0 1 5.196 3Zm1.536.887a2.165 2.165 0 0 1 1.083 1.839c.005.351.054.695.14 1.024M9.384 9.137l2.077 1.199M7.848 15.75l1.536-.887m-1.536.887a3 3 0 1 1-5.196 3 3 3 0 0 1 5.196-3Zm1.536-.887a2.165 2.165 0 0 0 1.083-1.838c.005-.352.054-.695.14-1.025m-1.223 2.863 2.077-1.199m0-3.328a4.323 4.323 0 0 1 2.068-1.379l5.325-1.628a4.5 4.5 0 0 1 2.48-.044l.803.215-7.794 4.5m-2.882-1.664A4.33 4.33 0 0 0 10.607 12m3.736 0 7.794 4.5-.802.215a4.5 4.5 0 0 1-2.48-.043l-5.326-1.629a4.324 4.324 0 0 1-2.068-1.379M14.343 12l-2.882 1.664"/>
  </svg>
);

/** Heroicons (outline) `chevron-right` (MIT). */
export const HiChevronRight = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5"/>
  </svg>
);

/** Heroicons (outline) `pause-circle` (MIT). */
export const HiPauseCircle = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M14.25 9v6m-4.5 0V9M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/>
  </svg>
);

/** Heroicons (outline) `chevron-left` (MIT). */
export const HiChevronLeft = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5"/>
  </svg>
);

/** Heroicons (outline) `magnifying-glass-plus` (MIT). */
export const HiMagnifyingGlassPlus = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607ZM10.5 7.5v6m3-3h-6"/>
  </svg>
);

/** Heroicons (outline) `magnifying-glass-minus` (MIT). */
export const HiMagnifyingGlassMinus = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607ZM13.5 10.5h-6"/>
  </svg>
);

/** Heroicons (outline) `arrow-left` (MIT). */
export const HiArrowLeft = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18"/>
  </svg>
);

/** Heroicons (outline) `x-mark` (MIT). */
export const HiXMark = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12"/>
  </svg>
);

/** Heroicons (outline) `chevron-double-left` (MIT). */
export const HiChevronDoubleLeft = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="m18.75 4.5-7.5 7.5 7.5 7.5m-6-15L5.25 12l7.5 7.5"/>
  </svg>
);

/** Heroicons (outline) `chevron-down` (MIT). */
export const HiChevronDown = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5"/>
  </svg>
);

/** Heroicons (outline) `chevron-up` (MIT). */
export const HiChevronUp = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 15.75 7.5-7.5 7.5 7.5"/>
  </svg>
);

/** Heroicons (outline) `arrow-top-right-on-square` (MIT). */
export const HiArrowTopRightOnSquare = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 0 0 3 8.25v10.5A2.25 2.25 0 0 0 5.25 21h10.5A2.25 2.25 0 0 0 18 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25"/>
  </svg>
);

/** Heroicons (outline) `arrow-right` (MIT). */
export const HiArrowRight = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3"/>
  </svg>
);

/** Heroicons (outline) `squares-2x2` (MIT). */
export const HiSquares2x2 = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6A2.25 2.25 0 0 1 6 3.75h2.25A2.25 2.25 0 0 1 10.5 6v2.25a2.25 2.25 0 0 1-2.25 2.25H6a2.25 2.25 0 0 1-2.25-2.25V6ZM3.75 15.75A2.25 2.25 0 0 1 6 13.5h2.25a2.25 2.25 0 0 1 2.25 2.25V18a2.25 2.25 0 0 1-2.25 2.25H6A2.25 2.25 0 0 1 3.75 18v-2.25ZM13.5 6a2.25 2.25 0 0 1 2.25-2.25H18A2.25 2.25 0 0 1 20.25 6v2.25A2.25 2.25 0 0 1 18 10.5h-2.25a2.25 2.25 0 0 1-2.25-2.25V6ZM13.5 15.75a2.25 2.25 0 0 1 2.25-2.25H18a2.25 2.25 0 0 1 2.25 2.25V18A2.25 2.25 0 0 1 18 20.25h-2.25A2.25 2.25 0 0 1 13.5 18v-2.25Z"/>
  </svg>
);

/** Heroicons (outline) `home` (MIT). */
export const HiHome = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25"/>
  </svg>
);

/** Heroicons (outline) `bars-3` (MIT). */
export const HiBars3 = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5"/>
  </svg>
);

/** Heroicons (outline) `ellipsis-horizontal` (MIT). */
export const HiEllipsisHorizontal = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 12a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM12.75 12a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM18.75 12a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0Z"/>
  </svg>
);

/** Heroicons (outline) `arrow-up` (MIT). */
export const HiArrowUp = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 10.5 12 3m0 0 7.5 7.5M12 3v18"/>
  </svg>
);

/** Heroicons (outline) `megaphone` (MIT). */
export const HiMegaphone = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M10.34 15.84c-.688-.06-1.386-.09-2.09-.09H7.5a4.5 4.5 0 1 1 0-9h.75c.704 0 1.402-.03 2.09-.09m0 9.18c.253.962.584 1.892.985 2.783.247.55.06 1.21-.463 1.511l-.657.38c-.551.318-1.26.117-1.527-.461a20.845 20.845 0 0 1-1.44-4.282m3.102.069a18.03 18.03 0 0 1-.59-4.59c0-1.586.205-3.124.59-4.59m0 9.18a23.848 23.848 0 0 1 8.835 2.535M10.34 6.66a23.847 23.847 0 0 0 8.835-2.535m0 0A23.74 23.74 0 0 0 18.795 3m.38 1.125a23.91 23.91 0 0 1 1.014 5.395m-1.014 8.855c-.118.38-.245.754-.38 1.125m.38-1.125a23.91 23.91 0 0 0 1.014-5.395m0-3.46c.495.413.811 1.035.811 1.73 0 .695-.316 1.317-.811 1.73m0-3.46a24.347 24.347 0 0 1 0 3.46"/>
  </svg>
);

/** Heroicons (outline) `bell` (MIT). */
export const HiBell = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0"/>
  </svg>
);

/** Heroicons (outline) `chat-bubble-left` (MIT). */
export const HiChatBubbleLeft = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 12.76c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.076-4.076a1.526 1.526 0 0 1 1.037-.443 48.282 48.282 0 0 0 5.68-.494c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z"/>
  </svg>
);

/** Heroicons (outline) `envelope` (MIT). */
export const HiEnvelope = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75"/>
  </svg>
);

/** Heroicons (outline) `check-badge` (MIT). */
export const HiCheckBadge = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12c0 1.268-.63 2.39-1.593 3.068a3.745 3.745 0 0 1-1.043 3.296 3.745 3.745 0 0 1-3.296 1.043A3.745 3.745 0 0 1 12 21c-1.268 0-2.39-.63-3.068-1.593a3.746 3.746 0 0 1-3.296-1.043 3.745 3.745 0 0 1-1.043-3.296A3.745 3.745 0 0 1 3 12c0-1.268.63-2.39 1.593-3.068a3.745 3.745 0 0 1 1.043-3.296 3.746 3.746 0 0 1 3.296-1.043A3.746 3.746 0 0 1 12 3c1.268 0 2.39.63 3.068 1.593a3.746 3.746 0 0 1 3.296 1.043 3.746 3.746 0 0 1 1.043 3.296A3.745 3.745 0 0 1 21 12Z"/>
  </svg>
);

/** Heroicons (outline) `chart-pie` (MIT). */
export const HiChartPie = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 6a7.5 7.5 0 1 0 7.5 7.5h-7.5V6Z"/>
    <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 10.5H21A7.5 7.5 0 0 0 13.5 3v7.5Z"/>
  </svg>
);

/** Heroicons (outline) `trophy` (MIT). */
export const HiTrophy = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 18.75h-9m9 0a3 3 0 0 1 3 3h-15a3 3 0 0 1 3-3m9 0v-3.375c0-.621-.503-1.125-1.125-1.125h-.871M7.5 18.75v-3.375c0-.621.504-1.125 1.125-1.125h.872m5.007 0H9.497m5.007 0a7.454 7.454 0 0 1-.982-3.172M9.497 14.25a7.454 7.454 0 0 0 .981-3.172M5.25 4.236c-.982.143-1.954.317-2.916.52A6.003 6.003 0 0 0 7.73 9.728M5.25 4.236V4.5c0 2.108.966 3.99 2.48 5.228M5.25 4.236V2.721C7.456 2.41 9.71 2.25 12 2.25c2.291 0 4.545.16 6.75.47v1.516M7.73 9.728a6.726 6.726 0 0 0 2.748 1.35m8.272-6.842V4.5c0 2.108-.966 3.99-2.48 5.228m2.48-5.492a46.32 46.32 0 0 1 2.916.52 6.003 6.003 0 0 1-5.395 4.972m0 0a6.726 6.726 0 0 1-2.749 1.35m0 0a6.772 6.772 0 0 1-3.044 0"/>
  </svg>
);

/** Heroicons (outline) `hashtag` (MIT). */
export const HiHashtag = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 8.25h15m-16.5 7.5h15m-1.8-13.5-3.9 19.5m-2.1-19.5-3.9 19.5"/>
  </svg>
);

/** Heroicons (outline) `shield-check` (MIT). */
export const HiShieldCheck = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285Z"/>
  </svg>
);

/** Heroicons (outline) `star` (MIT). */
export const HiStar = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M11.48 3.499a.562.562 0 0 1 1.04 0l2.125 5.111a.563.563 0 0 0 .475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 0 0-.182.557l1.285 5.385a.562.562 0 0 1-.84.61l-4.725-2.885a.562.562 0 0 0-.586 0L6.982 20.54a.562.562 0 0 1-.84-.61l1.285-5.386a.562.562 0 0 0-.182-.557l-4.204-3.602a.562.562 0 0 1 .321-.988l5.518-.442a.563.563 0 0 0 .475-.345L11.48 3.5Z"/>
  </svg>
);

/** Heroicons (outline) `hand-thumb-down` (MIT). */
export const HiHandThumbDown = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M7.498 15.25H4.372c-1.026 0-1.945-.694-2.054-1.715a12.137 12.137 0 0 1-.068-1.285c0-2.848.992-5.464 2.649-7.521C5.287 4.247 5.886 4 6.504 4h4.016a4.5 4.5 0 0 1 1.423.23l3.114 1.04a4.5 4.5 0 0 0 1.423.23h1.294M7.498 15.25c.618 0 .991.724.725 1.282A7.471 7.471 0 0 0 7.5 19.75 2.25 2.25 0 0 0 9.75 22a.75.75 0 0 0 .75-.75v-.633c0-.573.11-1.14.322-1.672.304-.76.93-1.33 1.653-1.715a9.04 9.04 0 0 0 2.86-2.4c.498-.634 1.226-1.08 2.032-1.08h.384m-10.253 1.5H9.7m8.075-9.75c.01.05.027.1.05.148.593 1.2.925 2.55.925 3.977 0 1.487-.36 2.89-.999 4.125m.023-8.25c-.076-.365.183-.75.575-.75h.908c.889 0 1.713.518 1.972 1.368.339 1.11.521 2.287.521 3.507 0 1.553-.295 3.036-.831 4.398-.306.774-1.086 1.227-1.918 1.227h-1.053c-.472 0-.745-.556-.5-.96a8.95 8.95 0 0 0 .303-.54"/>
  </svg>
);

/** Heroicons (outline) `hand-thumb-up` (MIT). */
export const HiHandThumbUp = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M6.633 10.25c.806 0 1.533-.446 2.031-1.08a9.041 9.041 0 0 1 2.861-2.4c.723-.384 1.35-.956 1.653-1.715a4.498 4.498 0 0 0 .322-1.672V2.75a.75.75 0 0 1 .75-.75 2.25 2.25 0 0 1 2.25 2.25c0 1.152-.26 2.243-.723 3.218-.266.558.107 1.282.725 1.282m0 0h3.126c1.026 0 1.945.694 2.054 1.715.045.422.068.85.068 1.285a11.95 11.95 0 0 1-2.649 7.521c-.388.482-.987.729-1.605.729H13.48c-.483 0-.964-.078-1.423-.23l-3.114-1.04a4.501 4.501 0 0 0-1.423-.23H5.904m10.598-9.75H14.25M5.904 18.5c.083.205.173.405.27.602.197.4-.078.898-.523.898h-.908c-.889 0-1.713-.518-1.972-1.368a12 12 0 0 1-.521-3.507c0-1.553.295-3.036.831-4.398C3.387 9.953 4.167 9.5 5 9.5h1.053c.472 0 .745.556.5.96a8.958 8.958 0 0 0-1.302 4.665c0 1.194.232 2.333.654 3.375Z"/>
  </svg>
);

/** Heroicons (outline) `arrow-trending-down` (MIT). */
export const HiArrowTrendingDown = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 6 9 12.75l4.286-4.286a11.948 11.948 0 0 1 4.306 6.43l.776 2.898m0 0 3.182-5.511m-3.182 5.51-5.511-3.181"/>
  </svg>
);

/** Heroicons (outline) `shopping-bag` (MIT). */
export const HiShoppingBag = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 10.5V6a3.75 3.75 0 1 0-7.5 0v4.5m11.356-1.993 1.263 12c.07.665-.45 1.243-1.119 1.243H4.25a1.125 1.125 0 0 1-1.12-1.243l1.264-12A1.125 1.125 0 0 1 5.513 7.5h12.974c.576 0 1.059.435 1.119 1.007ZM8.625 10.5a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm7.5 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z"/>
  </svg>
);

/** Heroicons (outline) `credit-card` (MIT). */
export const HiCreditCard = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 8.25h19.5M2.25 9h19.5m-16.5 5.25h6m-6 2.25h3m-3.75 3h15a2.25 2.25 0 0 0 2.25-2.25V6.75A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25v10.5A2.25 2.25 0 0 0 4.5 19.5Z"/>
  </svg>
);

/** Heroicons (outline) `shopping-cart` (MIT). */
export const HiShoppingCart = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 3h1.386c.51 0 .955.343 1.087.835l.383 1.437M7.5 14.25a3 3 0 0 0-3 3h15.75m-12.75-3h11.218c1.121-2.3 2.1-4.684 2.924-7.138a60.114 60.114 0 0 0-16.536-1.84M7.5 14.25 5.106 5.272M6 20.25a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0Zm12.75 0a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0Z"/>
  </svg>
);

/** Heroicons (outline) `wallet` (MIT). */
export const HiWallet = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M21 12a2.25 2.25 0 0 0-2.25-2.25H15a3 3 0 1 1-6 0H5.25A2.25 2.25 0 0 0 3 12m18 0v6a2.25 2.25 0 0 1-2.25 2.25H5.25A2.25 2.25 0 0 1 3 18v-6m18 0V9M3 12V9m18 0a2.25 2.25 0 0 0-2.25-2.25H5.25A2.25 2.25 0 0 0 3 9m18 0V6a2.25 2.25 0 0 0-2.25-2.25H5.25A2.25 2.25 0 0 0 3 6v3"/>
  </svg>
);

/** Heroicons (outline) `receipt-percent` (MIT). */
export const HiReceiptPercent = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="m9 14.25 6-6m4.5-3.493V21.75l-3.75-1.5-3.75 1.5-3.75-1.5-3.75 1.5V4.757c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0 1 11.186 0c1.1.128 1.907 1.077 1.907 2.185ZM9.75 9h.008v.008H9.75V9Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm4.125 4.5h.008v.008h-.008V13.5Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z"/>
  </svg>
);

/** Heroicons (outline) `gift` (MIT). */
export const HiGift = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M21 11.25v8.25a1.5 1.5 0 0 1-1.5 1.5H5.25a1.5 1.5 0 0 1-1.5-1.5v-8.25M12 4.875A2.625 2.625 0 1 0 9.375 7.5H12m0-2.625V7.5m0-2.625A2.625 2.625 0 1 1 14.625 7.5H12m0 0V21m-8.625-9.75h18c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125h-18c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125Z"/>
  </svg>
);

/** Heroicons (outline) `cpu-chip` (MIT). */
export const HiCpuChip = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 3v1.5M4.5 8.25H3m18 0h-1.5M4.5 12H3m18 0h-1.5m-15 3.75H3m18 0h-1.5M8.25 19.5V21M12 3v1.5m0 15V21m3.75-18v1.5m0 15V21m-9-1.5h10.5a2.25 2.25 0 0 0 2.25-2.25V6.75a2.25 2.25 0 0 0-2.25-2.25H6.75A2.25 2.25 0 0 0 4.5 6.75v10.5a2.25 2.25 0 0 0 2.25 2.25Zm.75-12h9v9h-9v-9Z"/>
  </svg>
);

/** Heroicons (outline) `percent-badge` (MIT). */
export const HiPercentBadge = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="m8.99 14.993 6-6m6 3.001c0 1.268-.63 2.39-1.593 3.069a3.746 3.746 0 0 1-1.043 3.296 3.745 3.745 0 0 1-3.296 1.043 3.745 3.745 0 0 1-3.068 1.593c-1.268 0-2.39-.63-3.068-1.593a3.745 3.745 0 0 1-3.296-1.043 3.746 3.746 0 0 1-1.043-3.297 3.746 3.746 0 0 1-1.593-3.068c0-1.268.63-2.39 1.593-3.068a3.746 3.746 0 0 1 1.043-3.297 3.745 3.745 0 0 1 3.296-1.042 3.745 3.745 0 0 1 3.068-1.594c1.268 0 2.39.63 3.068 1.593a3.745 3.745 0 0 1 3.296 1.043 3.746 3.746 0 0 1 1.043 3.297 3.746 3.746 0 0 1 1.593 3.068ZM9.74 9.743h.008v.007H9.74v-.007Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm4.125 4.5h.008v.008h-.008v-.008Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z"/>
  </svg>
);

/** Heroicons (outline) `server-stack` (MIT). */
export const HiServerStack = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 14.25h13.5m-13.5 0a3 3 0 0 1-3-3m3 3a3 3 0 1 0 0 6h13.5a3 3 0 1 0 0-6m-16.5-3a3 3 0 0 1 3-3h13.5a3 3 0 0 1 3 3m-19.5 0a4.5 4.5 0 0 1 .9-2.7L5.737 5.1a3.375 3.375 0 0 1 2.7-1.35h7.126c1.062 0 2.062.5 2.7 1.35l2.587 3.45a4.5 4.5 0 0 1 .9 2.7m0 0a3 3 0 0 1-3 3m0 3h.008v.008h-.008v-.008Zm0-6h.008v.008h-.008v-.008Zm-3 6h.008v.008h-.008v-.008Zm0-6h.008v.008h-.008v-.008Z"/>
  </svg>
);

/** Heroicons (outline) `check-circle` (MIT). */
export const HiCheckCircle = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/>
  </svg>
);

/** Heroicons (outline) `information-circle` (MIT). */
export const HiInformationCircle = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z"/>
  </svg>
);

/** Heroicons (outline) `stop-circle` (MIT). */
export const HiStopCircle = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/>
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 9.563C9 9.252 9.252 9 9.563 9h4.874c.311 0 .563.252.563.563v4.874c0 .311-.252.563-.563.563H9.564A.562.562 0 0 1 9 14.437V9.564Z"/>
  </svg>
);

/** Heroicons (outline) `lock-open` (MIT). */
export const HiLockOpen = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 10.5V6.75a4.5 4.5 0 1 1 9 0v3.75M3.75 21.75h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H3.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z"/>
  </svg>
);

/** Heroicons (outline) `archive-box` (MIT). */
export const HiArchiveBox = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="m20.25 7.5-.625 10.632a2.25 2.25 0 0 1-2.247 2.118H6.622a2.25 2.25 0 0 1-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125Z"/>
  </svg>
);

/** Heroicons (outline) `moon` (MIT). */
export const HiMoon = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M21.752 15.002A9.72 9.72 0 0 1 18 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 0 0 3 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 0 0 9.002-5.998Z"/>
  </svg>
);

/** Heroicons (outline) `key` (MIT). */
export const HiKey = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 5.25a3 3 0 0 1 3 3m3 0a6 6 0 0 1-7.029 5.912c-.563-.097-1.159.026-1.563.43L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1 1 21.75 8.25Z"/>
  </svg>
);

/** Heroicons (outline) `sun` (MIT). */
export const HiSun = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v2.25m6.364.386-1.591 1.591M21 12h-2.25m-.386 6.364-1.591-1.591M12 18.75V21m-4.773-4.227-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0Z"/>
  </svg>
);

/** Heroicons (outline) `swatch` (MIT). */
export const HiSwatch = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M4.098 19.902a3.75 3.75 0 0 0 5.304 0l6.401-6.402M6.75 21A3.75 3.75 0 0 1 3 17.25V4.125C3 3.504 3.504 3 4.125 3h5.25c.621 0 1.125.504 1.125 1.125v4.072M6.75 21a3.75 3.75 0 0 0 3.75-3.75V8.197M6.75 21h13.125c.621 0 1.125-.504 1.125-1.125v-5.25c0-.621-.504-1.125-1.125-1.125h-4.072M10.5 8.197l2.88-2.88c.438-.439 1.15-.439 1.59 0l3.712 3.713c.44.44.44 1.152 0 1.59l-2.879 2.88M6.75 17.25h.008v.008H6.75v-.008Z"/>
  </svg>
);

/** Heroicons (outline) `queue-list` (MIT). */
export const HiQueueList = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 12h16.5m-16.5 3.75h16.5M3.75 19.5h16.5M5.625 4.5h12.75a1.875 1.875 0 0 1 0 3.75H5.625a1.875 1.875 0 0 1 0-3.75Z"/>
  </svg>
);

/** Heroicons (outline) `cog` (MIT). */
export const HiCog = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12a7.5 7.5 0 0 0 15 0m-15 0a7.5 7.5 0 1 1 15 0m-15 0H3m16.5 0H21m-1.5 0H12m-8.457 3.077 1.41-.513m14.095-5.13 1.41-.513M5.106 17.785l1.15-.964m11.49-9.642 1.149-.964M7.501 19.795l.75-1.3m7.5-12.99.75-1.3m-6.063 16.658.26-1.477m2.605-14.772.26-1.477m0 17.726-.26-1.477M10.698 4.614l-.26-1.477M16.5 19.794l-.75-1.299M7.5 4.205 12 12m6.894 5.785-1.149-.964M6.256 7.178l-1.15-.964m15.352 8.864-1.41-.513M4.954 9.435l-1.41-.514M12.002 12l-3.75 6.495"/>
  </svg>
);

/** Heroicons (outline) `user` (MIT). */
export const HiUser = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z"/>
  </svg>
);

/** Heroicons (outline) `user-minus` (MIT). */
export const HiUserMinus = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M22 10.5h-6m-2.25-4.125a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0ZM4 19.235v-.11a6.375 6.375 0 0 1 12.75 0v.109A12.318 12.318 0 0 1 10.374 21c-2.331 0-4.512-.645-6.374-1.766Z"/>
  </svg>
);

/** Heroicons (outline) `user-plus` (MIT). */
export const HiUserPlus = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M18 7.5v3m0 0v3m0-3h3m-3 0h-3m-2.25-4.125a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0ZM3 19.235v-.11a6.375 6.375 0 0 1 12.75 0v.109A12.318 12.318 0 0 1 9.374 21c-2.331 0-4.512-.645-6.374-1.766Z"/>
  </svg>
);

/** Heroicons (outline) `arrow-right-on-rectangle` (MIT). */
export const HiArrowRightOnRectangle = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0 0 13.5 3h-6a2.25 2.25 0 0 0-2.25 2.25v13.5A2.25 2.25 0 0 0 7.5 21h6a2.25 2.25 0 0 0 2.25-2.25V15m3 0 3-3m0 0-3-3m3 3H9"/>
  </svg>
);

/** Heroicons (outline) `briefcase` (MIT). */
export const HiBriefcase = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 14.15v4.25c0 1.094-.787 2.036-1.872 2.18-2.087.277-4.216.42-6.378.42s-4.291-.143-6.378-.42c-1.085-.144-1.872-1.086-1.872-2.18v-4.25m16.5 0a2.18 2.18 0 0 0 .75-1.661V8.706c0-1.081-.768-2.015-1.837-2.175a48.114 48.114 0 0 0-3.413-.387m4.5 8.006c-.194.165-.42.295-.673.38A23.978 23.978 0 0 1 12 15.75c-2.648 0-5.195-.429-7.577-1.22a2.016 2.016 0 0 1-.673-.38m0 0A2.18 2.18 0 0 1 3 12.489V8.706c0-1.081.768-2.015 1.837-2.175a48.111 48.111 0 0 1 3.413-.387m7.5 0V5.25A2.25 2.25 0 0 0 13.5 3h-3a2.25 2.25 0 0 0-2.25 2.25v.894m7.5 0a48.667 48.667 0 0 0-7.5 0M12 12.75h.008v.008H12v-.008Z"/>
  </svg>
);

/** Semantik kalit → Heroicons (outline) ikonkasi (D18: `domen.ob'ekt.holat`). */
export const HEROICONS_ICONS: Record<string, (p: IconProps) => React.JSX.Element> = {
  "action.add": HiPlus,
  "action.bookmark": HiBookmark,
  "action.cancel": HiXCircle,
  "action.clear": HiXCircle,
  "action.clipboard": HiClipboard,
  "action.copy": HiDocumentDuplicate,
  "action.delete": HiTrash,
  "action.download": HiArrowDownTray,
  "action.edit": HiPencil,
  "action.eye": HiEye,
  "action.eyeOff": HiEyeSlash,
  "action.filter": HiFunnel,
  "action.format": HiSparkles,
  "action.fullscreen": HiArrowsPointingOut,
  "action.help": HiQuestionMarkCircle,
  "action.pin": HiMapPin,
  "action.print": HiPrinter,
  "action.retry": HiArrowPath,
  "action.save": HiBookmarkSquare,
  "action.search": HiMagnifyingGlass,
  "action.share": HiShare,
  "action.sliders": HiAdjustmentsHorizontal,
  "action.sortAsc": HiBarsArrowUp,
  "action.sortDesc": HiBarsArrowDown,
  "action.sound": HiSpeakerWave,
  "action.upload": HiArrowUpTray,
  "content.algorithm": HiShare,
  "content.article": HiNewspaper,
  "content.audio": HiMusicalNote,
  "content.category": HiFolder,
  "content.code": HiCodeBracket,
  "content.course": HiAcademicCap,
  "content.file": HiDocument,
  "content.image": HiPhoto,
  "content.level": HiChartBar,
  "content.pdf": HiDocument,
  "content.problem": HiBookOpen,
  "content.quiz": HiQuestionMarkCircle,
  "content.roadmap": HiMap,
  "content.step": HiNumberedList,
  "content.tag": HiTag,
  "content.terminal": HiCommandLine,
  "content.test": HiBeaker,
  "content.video": HiPlayCircle,
  "contest.arena": HiBolt,
  "contest.calendar": HiCalendar,
  "contest.clock": HiClock,
  "contest.duel": HiBolt,
  "contest.flag": HiFlag,
  "contest.formatAcm": HiCircleStack,
  "contest.formatIoi": HiChartBar,
  "contest.hackathon": HiCodeBracket,
  "contest.live": HiSignal,
  "contest.lock": HiLockClosed,
  "contest.rated": HiArrowTrendingUp,
  "contest.register": HiClipboardDocumentCheck,
  "contest.standings": HiTableCells,
  "contest.team": HiUsers,
  "device.appStore": HiArrowDownTray,
  "device.browser": HiGlobeAlt,
  "device.desktop": HiComputerDesktop,
  "device.laptop": HiComputerDesktop,
  "device.phone": HiDevicePhoneMobile,
  "device.qr": HiQrCode,
  "device.tablet": HiDeviceTablet,
  "device.touch": HiCursorArrowRays,
  "empty.attempts": HiClipboardDocumentList,
  "empty.files": HiFolderOpen,
  "empty.messages": HiChatBubbleOvalLeft,
  "empty.notFound": HiMagnifyingGlass,
  "empty.notifications": HiBellSlash,
  "empty.search": HiMagnifyingGlass,
  "empty.serverError": HiWrenchScrewdriver,
  "empty.team": HiUsers,
  "error.forbidden": HiSlash,
  "error.invalid": HiExclamationTriangle,
  "error.network": HiWifi,
  "error.notFound": HiMagnifyingGlass,
  "error.server": HiFire,
  "error.timeout": HiClock,
  "locale.flag": HiFlag,
  "locale.globe": HiLanguage,
  "locale.region": HiMap,
  "locale.switch": HiLanguage,
  "locale.timezone": HiGlobeAlt,
  "locale.translate": HiLanguage,
  "markdown.bold": HiBold,
  "markdown.code": HiCodeBracket,
  "markdown.codeBlock": HiCodeBracketSquare,
  "markdown.formula": HiCalculator,
  "markdown.heading": HiDocumentText,
  "markdown.hr": HiMinus,
  "markdown.image": HiPhoto,
  "markdown.italic": HiItalic,
  "markdown.link": HiLink,
  "markdown.list": HiListBullet,
  "markdown.orderedList": HiNumberedList,
  "markdown.preview": HiEye,
  "markdown.quote": HiChatBubbleBottomCenterText,
  "markdown.table": HiTableCells,
  "media.clip": HiPaperClip,
  "media.crop": HiScissors,
  "media.folder": HiFolder,
  "media.fullscreen": HiArrowsPointingOut,
  "media.next": HiChevronRight,
  "media.pause": HiPauseCircle,
  "media.play": HiPlayCircle,
  "media.prev": HiChevronLeft,
  "media.rotate": HiArrowPath,
  "media.volume": HiSpeakerWave,
  "media.zoomIn": HiMagnifyingGlassPlus,
  "media.zoomOut": HiMagnifyingGlassMinus,
  "nav.back": HiArrowLeft,
  "nav.close": HiXMark,
  "nav.collapse": HiChevronDoubleLeft,
  "nav.expandDown": HiChevronDown,
  "nav.expandUp": HiChevronUp,
  "nav.external": HiArrowTopRightOnSquare,
  "nav.filterPanel": HiAdjustmentsHorizontal,
  "nav.forward": HiArrowRight,
  "nav.grid": HiSquares2x2,
  "nav.home": HiHome,
  "nav.leaderboard": HiChartBar,
  "nav.list": HiListBullet,
  "nav.menu": HiBars3,
  "nav.more": HiEllipsisHorizontal,
  "nav.problems": HiBookOpen,
  "nav.quiz": HiQuestionMarkCircle,
  "nav.separator": HiChevronRight,
  "nav.up": HiArrowUp,
  "notification.announce": HiMegaphone,
  "notification.badgeNew": HiSparkles,
  "notification.bell": HiBell,
  "notification.bellRead": HiBell,
  "notification.changelog": HiSparkles,
  "notification.chat": HiChatBubbleOvalLeft,
  "notification.comment": HiChatBubbleLeft,
  "notification.email": HiEnvelope,
  "notification.muted": HiBellSlash,
  "notification.reply": HiArrowLeft,
  "ranking.badge": HiCheckBadge,
  "ranking.certificate": HiCheckBadge,
  "ranking.chartBar": HiChartBar,
  "ranking.chartLine": HiChartBar,
  "ranking.chartPie": HiChartPie,
  "ranking.crown": HiSparkles,
  "ranking.diamond": HiSparkles,
  "ranking.medalBronze": HiTrophy,
  "ranking.medalGold": HiTrophy,
  "ranking.medalSilver": HiTrophy,
  "ranking.podium": HiChartBar,
  "ranking.rank": HiHashtag,
  "ranking.shield": HiShieldCheck,
  "ranking.star": HiStar,
  "ranking.streak": HiFire,
  "ranking.thumbDown": HiHandThumbDown,
  "ranking.thumbUp": HiHandThumbUp,
  "ranking.trendDown": HiArrowTrendingDown,
  "ranking.trendUp": HiArrowTrendingUp,
  "ranking.trophy": HiTrophy,
  "shop.buy": HiShoppingBag,
  "shop.card": HiCreditCard,
  "shop.cart": HiShoppingCart,
  "shop.coin": HiWallet,
  "shop.discount": HiReceiptPercent,
  "shop.gift": HiGift,
  "shop.history": HiReceiptPercent,
  "shop.price": HiTag,
  "shop.store": HiShoppingBag,
  "shop.wallet": HiCreditCard,
  "stats.calculator": HiCalculator,
  "stats.chartBar": HiChartBar,
  "stats.chartLine": HiChartBar,
  "stats.chartPie": HiChartPie,
  "stats.database": HiCircleStack,
  "stats.funnel": HiFunnel,
  "stats.load": HiCpuChip,
  "stats.memory": HiCpuChip,
  "stats.percent": HiPercentBadge,
  "stats.server": HiServerStack,
  "stats.speed": HiChartBar,
  "stats.table": HiTableCells,
  "status.bad": HiXCircle,
  "status.blocked": HiSlash,
  "status.clock": HiClock,
  "status.finished": HiCheckCircle,
  "status.info": HiInformationCircle,
  "status.live": HiSignal,
  "status.locked": HiLockClosed,
  "status.offline": HiStopCircle,
  "status.ok": HiCheckCircle,
  "status.online": HiStopCircle,
  "status.pending": HiClock,
  "status.timer": HiClock,
  "status.unlocked": HiLockOpen,
  "status.verified": HiCheckBadge,
  "status.warning": HiExclamationTriangle,
  "status.watching": HiEye,
  "system.apiKey": HiCodeBracket,
  "system.backup": HiArchiveBox,
  "system.dark": HiMoon,
  "system.device": HiCpuChip,
  "system.key": HiKey,
  "system.light": HiSun,
  "system.log": HiClipboardDocumentList,
  "system.monitor": HiComputerDesktop,
  "system.palette": HiSwatch,
  "system.security": HiShieldCheck,
  "system.sessions": HiQueueList,
  "system.settings": HiCog,
  "user.avatar": HiUser,
  "user.block": HiUserMinus,
  "user.education": HiAcademicCap,
  "user.follow": HiUserPlus,
  "user.followers": HiUsers,
  "user.group": HiUsers,
  "user.invite": HiUserPlus,
  "user.link": HiLink,
  "user.location": HiMapPin,
  "user.logout": HiArrowRightOnRectangle,
  "user.profile": HiUser,
  "user.roleAdmin": HiShieldCheck,
  "user.roleStudent": HiAcademicCap,
  "user.roleTeacher": HiAcademicCap,
  "user.unfollow": HiUserMinus,
  "user.work": HiBriefcase,
};
