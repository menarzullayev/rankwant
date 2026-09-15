/** Judge verdiktlari ikonkalari.
 *
 *  Manba: **Phosphor** (MIT), 256×256 to'r, `fill="currentColor"`.
 *  Generatsiya qilingan — `tools/gen-verdict-icons.mjs` bilan qayta yasash mumkin.
 *
 *  ⚠️ Nega alohida fayl: bu ikonkalar **verdikt kalitiga** bog'langan
 *  (`lib/theme/verdict.ts`), ya'ni ular birgalikda o'zgaradi. Umumiy
 *  `icons/index.tsx` ga aralashtirilsa, aloqa ko'rinmay qolardi.
 *
 *  Nega 256×256: Phosphor shu to'rda chizilgan — boshqa o'lchamga
 *  masshtablashda chiziq qalinligi buziladi.
 */

type IconProps = { className?: string };

const base = {
  viewBox: "0 0 256 256",
  fill: "currentColor",
  xmlns: "http://www.w3.org/2000/svg",
};

/** Phosphor `check-circle` (MIT). Verdikt ikonkasi — VerdictAcceptedIcon. */
export const VerdictAcceptedIcon = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path fill="currentColor" d="M173.66 98.34a8 8 0 0 1 0 11.32l-56 56a8 8 0 0 1-11.32 0l-24-24a8 8 0 0 1 11.32-11.32L112 148.69l50.34-50.35a8 8 0 0 1 11.32 0M232 128A104 104 0 1 1 128 24a104.11 104.11 0 0 1 104 104m-16 0a88 88 0 1 0-88 88a88.1 88.1 0 0 0 88-88"/>
  </svg>
);

/** Phosphor `x-circle` (MIT). Verdikt ikonkasi — VerdictWrongIcon. */
export const VerdictWrongIcon = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path fill="currentColor" d="M165.66 101.66L139.31 128l26.35 26.34a8 8 0 0 1-11.32 11.32L128 139.31l-26.34 26.35a8 8 0 0 1-11.32-11.32L116.69 128l-26.35-26.34a8 8 0 0 1 11.32-11.32L128 116.69l26.34-26.35a8 8 0 0 1 11.32 11.32M232 128A104 104 0 1 1 128 24a104.11 104.11 0 0 1 104 104m-16 0a88 88 0 1 0-88 88a88.1 88.1 0 0 0 88-88"/>
  </svg>
);

/** Phosphor `timer` (MIT). Verdikt ikonkasi — VerdictTimeIcon. */
export const VerdictTimeIcon = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path fill="currentColor" d="M128 40a96 96 0 1 0 96 96a96.11 96.11 0 0 0-96-96m0 176a80 80 0 1 1 80-80a80.09 80.09 0 0 1-80 80m45.66-125.66a8 8 0 0 1 0 11.32l-40 40a8 8 0 0 1-11.32-11.32l40-40a8 8 0 0 1 11.32 0M96 16a8 8 0 0 1 8-8h48a8 8 0 0 1 0 16h-48a8 8 0 0 1-8-8"/>
  </svg>
);

/** Phosphor `cpu` (MIT). Verdikt ikonkasi — VerdictMemoryIcon. */
export const VerdictMemoryIcon = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path fill="currentColor" d="M152 96h-48a8 8 0 0 0-8 8v48a8 8 0 0 0 8 8h48a8 8 0 0 0 8-8v-48a8 8 0 0 0-8-8m-8 48h-32v-32h32Zm88 0h-16v-32h16a8 8 0 0 0 0-16h-16V56a16 16 0 0 0-16-16h-40V24a8 8 0 0 0-16 0v16h-32V24a8 8 0 0 0-16 0v16H56a16 16 0 0 0-16 16v40H24a8 8 0 0 0 0 16h16v32H24a8 8 0 0 0 0 16h16v40a16 16 0 0 0 16 16h40v16a8 8 0 0 0 16 0v-16h32v16a8 8 0 0 0 16 0v-16h40a16 16 0 0 0 16-16v-40h16a8 8 0 0 0 0-16m-32 56H56V56h144z"/>
  </svg>
);

/** Phosphor `warning-octagon` (MIT). Verdikt ikonkasi — VerdictRuntimeIcon. */
export const VerdictRuntimeIcon = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path fill="currentColor" d="M120 136V80a8 8 0 0 1 16 0v56a8 8 0 0 1-16 0m112-44.45v72.9a15.86 15.86 0 0 1-4.69 11.31l-51.55 51.55a15.86 15.86 0 0 1-11.31 4.69h-72.9a15.86 15.86 0 0 1-11.31-4.69l-51.55-51.55A15.86 15.86 0 0 1 24 164.45v-72.9a15.86 15.86 0 0 1 4.69-11.31l51.55-51.55A15.86 15.86 0 0 1 91.55 24h72.9a15.86 15.86 0 0 1 11.31 4.69l51.55 51.55A15.86 15.86 0 0 1 232 91.55m-16 0L164.45 40h-72.9L40 91.55v72.9L91.55 216h72.9L216 164.45ZM128 160a12 12 0 1 0 12 12a12 12 0 0 0-12-12"/>
  </svg>
);

/** Phosphor `wrench` (MIT). Verdikt ikonkasi — VerdictCompileIcon. */
export const VerdictCompileIcon = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path fill="currentColor" d="M226.76 69a8 8 0 0 0-12.84-2.88l-40.3 37.19l-17.23-3.7l-3.7-17.23l37.19-40.3A8 8 0 0 0 187 29.24A72 72 0 0 0 88 96a72.3 72.3 0 0 0 6 28.94L33.79 177c-.15.12-.29.26-.43.39a32 32 0 0 0 45.26 45.26c.13-.13.27-.28.39-.42L131.06 162A72 72 0 0 0 232 96a71.6 71.6 0 0 0-5.24-27M160 152a56.14 56.14 0 0 1-27.07-7a8 8 0 0 0-9.92 1.77l-55.9 64.74a16 16 0 0 1-22.62-22.62L109.18 133a8 8 0 0 0 1.77-9.93a56 56 0 0 1 58.36-82.31l-31.2 33.81a8 8 0 0 0-1.94 7.1l5.66 26.33a8 8 0 0 0 6.14 6.14l26.35 5.66a8 8 0 0 0 7.1-1.94l33.81-31.2A56.06 56.06 0 0 1 160 152"/>
  </svg>
);

/** Phosphor `ruler` (MIT). Verdikt ikonkasi — VerdictFormatIcon. */
export const VerdictFormatIcon = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path fill="currentColor" d="m235.32 73.37l-52.69-52.68a16 16 0 0 0-22.63 0L20.68 160a16 16 0 0 0 0 22.63l52.69 52.68a16 16 0 0 0 22.63 0L235.32 96a16 16 0 0 0 0-22.63M84.68 224L32 171.31l32-32l26.34 26.35a8 8 0 0 0 11.32-11.32L75.31 128L96 107.31l26.34 26.35a8 8 0 0 0 11.32-11.32L107.31 96L128 75.31l26.34 26.35a8 8 0 0 0 11.32-11.32L139.31 64l32-32L224 84.69Z"/>
  </svg>
);

/** Phosphor `upload-simple` (MIT). Verdikt ikonkasi — VerdictOutputIcon. */
export const VerdictOutputIcon = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path fill="currentColor" d="M224 144v64a8 8 0 0 1-8 8H40a8 8 0 0 1-8-8v-64a8 8 0 0 1 16 0v56h160v-56a8 8 0 0 1 16 0M93.66 77.66L120 51.31V144a8 8 0 0 0 16 0V51.31l26.34 26.35a8 8 0 0 0 11.32-11.32l-40-40a8 8 0 0 0-11.32 0l-40 40a8 8 0 0 0 11.32 11.32"/>
  </svg>
);

/** Phosphor `gear` (MIT). Verdikt ikonkasi — VerdictInternalIcon. */
export const VerdictInternalIcon = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path fill="currentColor" d="M128 80a48 48 0 1 0 48 48a48.05 48.05 0 0 0-48-48m0 80a32 32 0 1 1 32-32a32 32 0 0 1-32 32m88-29.84q.06-2.16 0-4.32l14.92-18.64a8 8 0 0 0 1.48-7.06a107.2 107.2 0 0 0-10.88-26.25a8 8 0 0 0-6-3.93l-23.72-2.64q-1.48-1.56-3-3L186 40.54a8 8 0 0 0-3.94-6a107.7 107.7 0 0 0-26.25-10.87a8 8 0 0 0-7.06 1.49L130.16 40h-4.32L107.2 25.11a8 8 0 0 0-7.06-1.48a107.6 107.6 0 0 0-26.25 10.88a8 8 0 0 0-3.93 6l-2.64 23.76q-1.56 1.49-3 3L40.54 70a8 8 0 0 0-6 3.94a107.7 107.7 0 0 0-10.87 26.25a8 8 0 0 0 1.49 7.06L40 125.84v4.32L25.11 148.8a8 8 0 0 0-1.48 7.06a107.2 107.2 0 0 0 10.88 26.25a8 8 0 0 0 6 3.93l23.72 2.64q1.49 1.56 3 3L70 215.46a8 8 0 0 0 3.94 6a107.7 107.7 0 0 0 26.25 10.87a8 8 0 0 0 7.06-1.49L125.84 216q2.16.06 4.32 0l18.64 14.92a8 8 0 0 0 7.06 1.48a107.2 107.2 0 0 0 26.25-10.88a8 8 0 0 0 3.93-6l2.64-23.72q1.56-1.48 3-3l23.78-2.8a8 8 0 0 0 6-3.94a107.7 107.7 0 0 0 10.87-26.25a8 8 0 0 0-1.49-7.06Zm-16.1-6.5a74 74 0 0 1 0 8.68a8 8 0 0 0 1.74 5.48l14.19 17.73a91.6 91.6 0 0 1-6.23 15l-22.6 2.56a8 8 0 0 0-5.1 2.64a74 74 0 0 1-6.14 6.14a8 8 0 0 0-2.64 5.1l-2.51 22.58a91.3 91.3 0 0 1-15 6.23l-17.74-14.19a8 8 0 0 0-5-1.75h-.48a74 74 0 0 1-8.68 0a8 8 0 0 0-5.48 1.74l-17.78 14.2a91.6 91.6 0 0 1-15-6.23L82.89 187a8 8 0 0 0-2.64-5.1a74 74 0 0 1-6.14-6.14a8 8 0 0 0-5.1-2.64l-22.58-2.52a91.3 91.3 0 0 1-6.23-15l14.19-17.74a8 8 0 0 0 1.74-5.48a74 74 0 0 1 0-8.68a8 8 0 0 0-1.74-5.48L40.2 100.45a91.6 91.6 0 0 1 6.23-15L69 82.89a8 8 0 0 0 5.1-2.64a74 74 0 0 1 6.14-6.14A8 8 0 0 0 82.89 69l2.51-22.57a91.3 91.3 0 0 1 15-6.23l17.74 14.19a8 8 0 0 0 5.48 1.74a74 74 0 0 1 8.68 0a8 8 0 0 0 5.48-1.74l17.77-14.19a91.6 91.6 0 0 1 15 6.23L173.11 69a8 8 0 0 0 2.64 5.1a74 74 0 0 1 6.14 6.14a8 8 0 0 0 5.1 2.64l22.58 2.51a91.3 91.3 0 0 1 6.23 15l-14.19 17.74a8 8 0 0 0-1.74 5.53Z"/>
  </svg>
);

/** Phosphor `hourglass` (MIT). Verdikt ikonkasi — VerdictPendingIcon. */
export const VerdictPendingIcon = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path fill="currentColor" d="M200 75.64V40a16 16 0 0 0-16-16H72a16 16 0 0 0-16 16v36a16.07 16.07 0 0 0 6.4 12.8l52.27 39.2l-52.27 39.2A16.07 16.07 0 0 0 56 180v36a16 16 0 0 0 16 16h112a16 16 0 0 0 16-16v-35.64a16.09 16.09 0 0 0-6.35-12.77L141.27 128l52.38-39.6A16.05 16.05 0 0 0 200 75.64M184 216H72v-36l56-42l56 42.35Zm0-140.36L128 118L72 76V40h112Z"/>
  </svg>
);

/** Verdikt kaliti → ikonka komponenti. */
export const VERDICT_ICONS: Record<string, (p: IconProps) => React.JSX.Element> = {
  AC: VerdictAcceptedIcon,
  WA: VerdictWrongIcon,
  TLE: VerdictTimeIcon,
  MLE: VerdictMemoryIcon,
  RE: VerdictRuntimeIcon,
  CE: VerdictCompileIcon,
  PE: VerdictFormatIcon,
  OLE: VerdictOutputIcon,
  IE: VerdictInternalIcon,
  PD: VerdictPendingIcon,
};
