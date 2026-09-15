/** Tabler ikonkalari (MIT), 24×24 to'r.
 *
 *  Generatsiya qilingan — `tools/gen-icon-packs.mjs` bilan qayta yasash mumkin.
 *  Qo'lda tahrirlanmaydi.
 *
 *  ⚠️ Manba CDN'dan **bir marta** olinadi va shu faylga yoziladi: ilova
 *  ishga tushganda tarmoqqa chiqmaydi, ya'ni yangi dependency ham,
 *  kutubxona yangilanishini kuzatish ham kerak emas.
 *
 *  39 ta ikonka.
 */

type IconProps = { className?: string };

const base = { viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 2, strokeLinecap: "round" as const, strokeLinejoin: "round" as const, xmlns: "http://www.w3.org/2000/svg" };

/** Tabler `chevron-left` (MIT). */
export const TbChevronLeft = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M15 6l-6 6l6 6" />
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

/** Tabler `check` (MIT). */
export const TbCheck = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M5 12l5 5l10 -10" />
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

/** Tabler `moon` (MIT). */
export const TbMoon = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 3c.132 0 .263 0 .393 0a7.5 7.5 0 0 0 7.92 12.446a9 9 0 1 1 -8.313 -12.454z" />
  </svg>
);

/** Tabler `chevron-down` (MIT). */
export const TbChevronDown = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M6 9l6 6l6 -6" />
  </svg>
);

/** Tabler `star` (MIT). */
export const TbStar = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 17.75l-6.172 3.245l1.179 -6.873l-5 -4.867l6.9 -1l3.086 -6.253l3.086 6.253l6.9 1l-5 4.867l1.179 6.873z" />
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

/** Tabler `loader` (MIT). */
export const TbLoader = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 6l0 -3" />
    <path d="M16.25 7.75l2.15 -2.15" />
    <path d="M18 12l3 0" />
    <path d="M16.25 16.25l2.15 2.15" />
    <path d="M12 18l0 3" />
    <path d="M7.75 16.25l-2.15 2.15" />
    <path d="M6 12l-3 0" />
    <path d="M7.75 7.75l-2.15 -2.15" />
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

/** Tabler `flag` (MIT). */
export const TbFlag = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M5 5a5 5 0 0 1 7 0a5 5 0 0 0 7 0v9a5 5 0 0 1 -7 0a5 5 0 0 0 -7 0v-9z" />
    <path d="M5 21v-7" />
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

/** Tabler `arrow-up` (MIT). */
export const TbArrowUp = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 5l0 14" />
    <path d="M18 11l-6 -6" />
    <path d="M6 11l6 -6" />
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

/** Tabler `history` (MIT). */
export const TbHistory = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 8l0 4l2 2" />
    <path d="M3.05 11a9 9 0 1 1 .5 4m-.5 5v-5h5" />
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

/** Tabler `function` (MIT). */
export const TbFunction = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M4 4m0 2.667a2.667 2.667 0 0 1 2.667 -2.667h10.666a2.667 2.667 0 0 1 2.667 2.667v10.666a2.667 2.667 0 0 1 -2.667 2.667h-10.666a2.667 2.667 0 0 1 -2.667 -2.667z" />
    <path d="M9 15.5v.25c0 .69 .56 1.25 1.25 1.25c.71 0 1.304 -.538 1.374 -1.244l.752 -7.512a1.381 1.381 0 0 1 1.374 -1.244c.69 0 1.25 .56 1.25 1.25v.25" />
    <path d="M9 12h6" />
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

/** Tabler `info-circle` (MIT). */
export const TbInfoCircle = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M3 12a9 9 0 1 0 18 0a9 9 0 0 0 -18 0" />
    <path d="M12 9h.01" />
    <path d="M11 12h1v4h1" />
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

/** Tabler `menu` (MIT). */
export const TbMenu = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M4 8l16 0" />
    <path d="M4 16l16 0" />
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

/** Tabler `help-circle` (MIT). */
export const TbHelpCircle = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M3 12a9 9 0 1 0 18 0a9 9 0 0 0 -18 0" />
    <path d="M12 16v.01" />
    <path d="M12 13a2 2 0 0 0 .914 -3.782a1.98 1.98 0 0 0 -2.414 .483" />
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

/** Tabler `map` (MIT). */
export const TbMap = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M3 7l6 -3l6 3l6 -3v13l-6 3l-6 -3l-6 3v-13" />
    <path d="M9 4v13" />
    <path d="M15 7v13" />
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

/** Tabler `shopping-bag` (MIT). */
export const TbShoppingBag = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M6.331 8h11.339a2 2 0 0 1 1.977 2.304l-1.255 8.152a3 3 0 0 1 -2.966 2.544h-6.852a3 3 0 0 1 -2.965 -2.544l-1.255 -8.152a2 2 0 0 1 1.977 -2.304z" />
    <path d="M9 11v-5a3 3 0 0 1 6 0v5" />
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

/** Tabler `circle-x` (MIT). */
export const TbCircleX = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0 -18 0" />
    <path d="M10 10l4 4m0 -4l-4 4" />
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

/** Tabler `alert-triangle` (MIT). */
export const TbAlertTriangle = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path stroke="none" d="M0 0h24v24H0z"/>
    <path d="M12 9v4" />
    <path d="M10.363 3.591l-8.106 13.534a1.914 1.914 0 0 0 1.636 2.871h16.214a1.914 1.914 0 0 0 1.636 -2.87l-8.106 -13.536a1.914 1.914 0 0 0 -3.274 0z" />
    <path d="M12 16h.01" />
  </svg>
);

/** Semantik kalit → Tabler ikonkasi (D18: `domen.ob'ekt.holat`). */
export const TABLER_ICONS: Record<string, (p: IconProps) => React.JSX.Element> = {
  "action.back": TbChevronLeft,
  "action.close": TbX,
  "action.confirm": TbCheck,
  "action.copy": TbCopy,
  "action.dark": TbMoon,
  "action.expand": TbChevronDown,
  "action.favourite": TbStar,
  "action.light": TbSun,
  "action.loading": TbLoader,
  "action.logout": TbLogout,
  "action.report": TbFlag,
  "action.search": TbSearch,
  "action.theme": TbPalette,
  "action.up": TbArrowUp,
  "nav.algorithm": TbRoute,
  "nav.arena": TbSwords,
  "nav.attempts": TbHistory,
  "nav.blog": TbNews,
  "nav.calendar": TbCalendar,
  "nav.classroom": TbPresentation,
  "nav.contest": TbTrophy,
  "nav.duel": TbUsers,
  "nav.formula": TbFunction,
  "nav.hackathon": TbCode,
  "nav.info": TbInfoCircle,
  "nav.language": TbGlobe,
  "nav.leaderboard": TbChartBar,
  "nav.learn": TbBook,
  "nav.menu": TbMenu,
  "nav.notifications": TbBell,
  "nav.problems": TbBook,
  "nav.quiz": TbHelpCircle,
  "nav.qvant": TbCoins,
  "nav.roadmap": TbMap,
  "nav.settings": TbSettings,
  "nav.shop": TbShoppingBag,
  "nav.team": TbUsers,
  "nav.tournament": TbTrophy,
  "nav.updates": TbBell,
  "nav.user": TbUser,
  "status.bad": TbCircleX,
  "status.info": TbInfoCircle,
  "status.ok": TbCircleCheck,
  "status.warning": TbAlertTriangle,
};
