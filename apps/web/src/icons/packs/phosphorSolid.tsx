/** Phosphor Solid ikonkalari (MIT), 256×256 to'r.
 *
 *  Generatsiya qilingan — `tools/gen-icon-packs.mjs` bilan qayta yasash mumkin.
 *  Qo'lda tahrirlanmaydi.
 *
 *  ⚠️ Manba CDN'dan **bir marta** olinadi va shu faylga yoziladi: ilova
 *  ishga tushganda tarmoqqa chiqmaydi, ya'ni yangi dependency ham,
 *  kutubxona yangilanishini kuzatish ham kerak emas.
 *
 *  155 ta ikonka.
 */

type IconProps = { className?: string };

const base = { viewBox: "0 0 256 256", fill: "currentColor", xmlns: "http://www.w3.org/2000/svg" };

/** Phosphor Solid `plus-fill` (MIT). */
export const PhFPlusFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M208,32H48A16,16,0,0,0,32,48V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V48A16,16,0,0,0,208,32ZM184,136H136v48a8,8,0,0,1-16,0V136H72a8,8,0,0,1,0-16h48V72a8,8,0,0,1,16,0v48h48a8,8,0,0,1,0,16Z"/>
  </svg>
);

/** Phosphor Solid `bookmark-fill` (MIT). */
export const PhFBookmarkFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M184,32H72A16,16,0,0,0,56,48V224a8,8,0,0,0,12.24,6.78L128,193.43l59.77,37.35A8,8,0,0,0,200,224V48A16,16,0,0,0,184,32ZM132.23,177.22a8,8,0,0,0-8.48,0L72,209.57V180.43l56-35,56,35v29.14Z"/>
  </svg>
);

/** Phosphor Solid `prohibit-fill` (MIT). */
export const PhFProhibitFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M200,128a71.69,71.69,0,0,1-15.78,44.91L83.09,71.78A71.95,71.95,0,0,1,200,128ZM56,128a71.95,71.95,0,0,0,116.91,56.22L71.78,83.09A71.69,71.69,0,0,0,56,128Zm180,0A108,108,0,1,1,128,20,108.12,108.12,0,0,1,236,128Zm-20,0a88,88,0,1,0-88,88A88.1,88.1,0,0,0,216,128Z"/>
  </svg>
);

/** Phosphor Solid `x-circle-fill` (MIT). */
export const PhFXCircleFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm37.66,130.34a8,8,0,0,1-11.32,11.32L128,139.31l-26.34,26.35a8,8,0,0,1-11.32-11.32L116.69,128,90.34,101.66a8,8,0,0,1,11.32-11.32L128,116.69l26.34-26.35a8,8,0,0,1,11.32,11.32L139.31,128Z"/>
  </svg>
);

/** Phosphor Solid `clipboard-fill` (MIT). */
export const PhFClipboardFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M200,32H163.74a47.92,47.92,0,0,0-71.48,0H56A16,16,0,0,0,40,48V216a16,16,0,0,0,16,16H200a16,16,0,0,0,16-16V48A16,16,0,0,0,200,32Zm-72,0a32,32,0,0,1,32,32H96A32,32,0,0,1,128,32Z"/>
  </svg>
);

/** Phosphor Solid `copy-fill` (MIT). */
export const PhFCopyFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M216,32H88a8,8,0,0,0-8,8V80H40a8,8,0,0,0-8,8V216a8,8,0,0,0,8,8H168a8,8,0,0,0,8-8V176h40a8,8,0,0,0,8-8V40A8,8,0,0,0,216,32Zm-8,128H176V88a8,8,0,0,0-8-8H96V48H208Z"/>
  </svg>
);

/** Phosphor Solid `trash-fill` (MIT). */
export const PhFTrashFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M216,48H176V40a24,24,0,0,0-24-24H104A24,24,0,0,0,80,40v8H40a8,8,0,0,0,0,16h8V208a16,16,0,0,0,16,16H192a16,16,0,0,0,16-16V64h8a8,8,0,0,0,0-16ZM112,168a8,8,0,0,1-16,0V104a8,8,0,0,1,16,0Zm48,0a8,8,0,0,1-16,0V104a8,8,0,0,1,16,0Zm0-120H96V40a8,8,0,0,1,8-8h48a8,8,0,0,1,8,8Z"/>
  </svg>
);

/** Phosphor Solid `download-fill` (MIT). */
export const PhFDownloadFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M74.34,85.66A8,8,0,0,1,85.66,74.34L120,108.69V24a8,8,0,0,1,16,0v84.69l34.34-34.35a8,8,0,0,1,11.32,11.32l-48,48a8,8,0,0,1-11.32,0ZM240,136v64a16,16,0,0,1-16,16H32a16,16,0,0,1-16-16V136a16,16,0,0,1,16-16H84.4a4,4,0,0,1,2.83,1.17L111,145A24,24,0,0,0,145,145l23.8-23.8A4,4,0,0,1,171.6,120H224A16,16,0,0,1,240,136Zm-40,32a12,12,0,1,0-12,12A12,12,0,0,0,200,168Z"/>
  </svg>
);

/** Phosphor Solid `pencil-fill` (MIT). */
export const PhFPencilFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M227.31,73.37,182.63,28.68a16,16,0,0,0-22.63,0L36.69,152A15.86,15.86,0,0,0,32,163.31V208a16,16,0,0,0,16,16H92.69A15.86,15.86,0,0,0,104,219.31L227.31,96a16,16,0,0,0,0-22.63ZM51.31,160l90.35-90.35,16.68,16.69L68,176.68ZM48,179.31,76.69,208H48Zm48,25.38L79.31,188l90.35-90.35h0l16.68,16.69Z"/>
  </svg>
);

/** Phosphor Solid `eye-fill` (MIT). */
export const PhFEyeFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M247.31,124.76c-.35-.79-8.82-19.58-27.65-38.41C194.57,61.26,162.88,48,128,48S61.43,61.26,36.34,86.35C17.51,105.18,9,124,8.69,124.76a8,8,0,0,0,0,6.5c.35.79,8.82,19.57,27.65,38.4C61.43,194.74,93.12,208,128,208s66.57-13.26,91.66-38.34c18.83-18.83,27.3-37.61,27.65-38.4A8,8,0,0,0,247.31,124.76ZM128,168a40,40,0,1,1,40-40A40,40,0,0,1,128,168Z"/>
  </svg>
);

/** Phosphor Solid `eye-closed-fill` (MIT). */
export const PhFEyeClosedFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M230.94,164A8,8,0,1,1,217.05,172l-19-33.2A123.23,123.23,0,0,1,162,155.46l5.87,35.22a8,8,0,0,1-6.58,9.21A8.4,8.4,0,0,1,160,200a8,8,0,0,1-7.88-6.69l-5.77-34.58a133.06,133.06,0,0,1-36.68,0l-5.77,34.58A8,8,0,0,1,96,200a8.4,8.4,0,0,1-1.32-.11,8,8,0,0,1-6.58-9.21L94,155.46a123.23,123.23,0,0,1-36.06-16.69L39,172A8,8,0,1,1,25.06,164l20-35a152.8,152.8,0,0,1-19.3-20,8,8,0,0,1,0-10.06C44.56,75.72,77.55,48,128,48s83.44,27.72,102.22,51a8,8,0,0,1,0,10.06,152.8,152.8,0,0,1-19.3,20Z"/>
  </svg>
);

/** Phosphor Solid `funnel-fill` (MIT). */
export const PhFFunnelFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M227.81,66.76l-.08.09L160,139.17v55.49A16,16,0,0,1,152.87,208l-32,21.34A16,16,0,0,1,96,216V139.17L28.27,66.85l-.08-.09A16,16,0,0,1,40,40H216a16,16,0,0,1,11.84,26.76Z"/>
  </svg>
);

/** Phosphor Solid `magic-wand-fill` (MIT). */
export const PhFMagicWandFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M248,152a8,8,0,0,1-8,8H224v16a8,8,0,0,1-16,0V160H192a8,8,0,0,1,0-16h16V128a8,8,0,0,1,16,0v16h16A8,8,0,0,1,248,152ZM56,72H72V88a8,8,0,0,0,16,0V72h16a8,8,0,0,0,0-16H88V40a8,8,0,0,0-16,0V56H56a8,8,0,0,0,0,16ZM184,192h-8v-8a8,8,0,0,0-16,0v8h-8a8,8,0,0,0,0,16h8v8a8,8,0,0,0,16,0v-8h8a8,8,0,0,0,0-16ZM219.31,80,80,219.31a16,16,0,0,1-22.62,0L36.68,198.63a16,16,0,0,1,0-22.63L176,36.69a16,16,0,0,1,22.63,0l20.68,20.68A16,16,0,0,1,219.31,80ZM208,68.69,187.31,48l-32,32L176,100.69Z"/>
  </svg>
);

/** Phosphor Solid `arrows-out-fill` (MIT). */
export const PhFArrowsOutFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M109.66,146.34a8,8,0,0,1,0,11.32L83.31,184l18.35,18.34A8,8,0,0,1,96,216H48a8,8,0,0,1-8-8V160a8,8,0,0,1,13.66-5.66L72,172.69l26.34-26.35A8,8,0,0,1,109.66,146.34ZM83.31,72l18.35-18.34A8,8,0,0,0,96,40H48a8,8,0,0,0-8,8V96a8,8,0,0,0,13.66,5.66L72,83.31l26.34,26.35a8,8,0,0,0,11.32-11.32ZM208,40H160a8,8,0,0,0-5.66,13.66L172.69,72,146.34,98.34a8,8,0,0,0,11.32,11.32L184,83.31l18.34,18.35A8,8,0,0,0,216,96V48A8,8,0,0,0,208,40Zm3.06,112.61a8,8,0,0,0-8.72,1.73L184,172.69l-26.34-26.35a8,8,0,0,0-11.32,11.32L172.69,184l-18.35,18.34A8,8,0,0,0,160,216h48a8,8,0,0,0,8-8V160A8,8,0,0,0,211.06,152.61Z"/>
  </svg>
);

/** Phosphor Solid `question-fill` (MIT). */
export const PhFQuestionFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm0,168a12,12,0,1,1,12-12A12,12,0,0,1,128,192Zm8-48.72V144a8,8,0,0,1-16,0v-8a8,8,0,0,1,8-8c13.23,0,24-9,24-20s-10.77-20-24-20-24,9-24,20v4a8,8,0,0,1-16,0v-4c0-19.85,17.94-36,40-36s40,16.15,40,36C168,125.38,154.24,139.93,136,143.28Z"/>
  </svg>
);

/** Phosphor Solid `map-pin-fill` (MIT). */
export const PhFMapPinFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M128,16a88.1,88.1,0,0,0-88,88c0,75.3,80,132.17,83.41,134.55a8,8,0,0,0,9.18,0C136,236.17,216,179.3,216,104A88.1,88.1,0,0,0,128,16Zm0,56a32,32,0,1,1-32,32A32,32,0,0,1,128,72Z"/>
  </svg>
);

/** Phosphor Solid `printer-fill` (MIT). */
export const PhFPrinterFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M240,96v80a8,8,0,0,1-8,8H200v32a8,8,0,0,1-8,8H64a8,8,0,0,1-8-8V184H24a8,8,0,0,1-8-8V96c0-13.23,11.36-24,25.33-24H56V40a8,8,0,0,1,8-8H192a8,8,0,0,1,8,8V72h14.67C228.64,72,240,82.77,240,96ZM72,72H184V48H72Zm112,88H72v48H184Zm16-44a12,12,0,1,0-12,12A12,12,0,0,0,200,116Z"/>
  </svg>
);

/** Phosphor Solid `arrow-clockwise-fill` (MIT). */
export const PhFArrowClockwiseFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M240,56v48a8,8,0,0,1-8,8H184a8,8,0,0,1-5.66-13.66l17-17-10.55-9.65-.25-.24a80,80,0,1,0-1.67,114.78,8,8,0,1,1,11,11.63A95.44,95.44,0,0,1,128,224h-1.32A96,96,0,1,1,195.75,60l10.93,10L226.34,50.3A8,8,0,0,1,240,56Z"/>
  </svg>
);

/** Phosphor Solid `floppy-disk-fill` (MIT). */
export const PhFFloppyDiskFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M219.31,72,184,36.69A15.86,15.86,0,0,0,172.69,32H48A16,16,0,0,0,32,48V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V83.31A15.86,15.86,0,0,0,219.31,72ZM208,208H184V152a16,16,0,0,0-16-16H88a16,16,0,0,0-16,16v56H48V48H172.69L208,83.31ZM160,72a8,8,0,0,1-8,8H96a8,8,0,0,1,0-16h56A8,8,0,0,1,160,72Z"/>
  </svg>
);

/** Phosphor Solid `magnifying-glass-fill` (MIT). */
export const PhFMagnifyingGlassFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M168,112a56,56,0,1,1-56-56A56,56,0,0,1,168,112Zm61.66,117.66a8,8,0,0,1-11.32,0l-50.06-50.07a88,88,0,1,1,11.32-11.31l50.06,50.06A8,8,0,0,1,229.66,229.66ZM112,184a72,72,0,1,0-72-72A72.08,72.08,0,0,0,112,184Z"/>
  </svg>
);

/** Phosphor Solid `share-fill` (MIT). */
export const PhFShareFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M229.66,109.66l-48,48A8,8,0,0,1,168,152V112h-3a88,88,0,0,0-85.23,66,8,8,0,0,1-15.5-4A103.94,103.94,0,0,1,165,96h3V56a8,8,0,0,1,13.66-5.66l48,48A8,8,0,0,1,229.66,109.66ZM192,208H40V88a8,8,0,0,0-16,0V216a8,8,0,0,0,8,8H192a8,8,0,0,0,0-16Z"/>
  </svg>
);

/** Phosphor Solid `sliders-horizontal-fill` (MIT). */
export const PhFSlidersHorizontalFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M32,80a8,8,0,0,1,8-8H77.17a28,28,0,0,1,53.66,0H216a8,8,0,0,1,0,16H130.83a28,28,0,0,1-53.66,0H40A8,8,0,0,1,32,80Zm184,88H194.83a28,28,0,0,0-53.66,0H40a8,8,0,0,0,0,16H141.17a28,28,0,0,0,53.66,0H216a8,8,0,0,0,0-16Z"/>
  </svg>
);

/** Phosphor Solid `sort-ascending-fill` (MIT). */
export const PhFSortAscendingFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M208,32H48A16,16,0,0,0,32,48V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V48A16,16,0,0,0,208,32ZM72,72h96a8,8,0,0,1,0,16H72a8,8,0,0,1,0-16Zm40,112H72a8,8,0,0,1,0-16h40a8,8,0,0,1,0,16Zm8-48H72a8,8,0,0,1,0-16h48a8,8,0,0,1,0,16Zm77.66,29.66-24,24a8,8,0,0,1-11.32,0l-24-24a8,8,0,0,1,11.32-11.32L160,164.69V120a8,8,0,0,1,16,0v44.69l10.34-10.35a8,8,0,0,1,11.32,11.32Z"/>
  </svg>
);

/** Phosphor Solid `sort-descending-fill` (MIT). */
export const PhFSortDescendingFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M208,32H48A16,16,0,0,0,32,48V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V48A16,16,0,0,0,208,32ZM72,72h40a8,8,0,0,1,0,16H72a8,8,0,0,1,0-16Zm0,48h48a8,8,0,0,1,0,16H72a8,8,0,0,1,0-16Zm96,64H72a8,8,0,0,1,0-16h96a8,8,0,0,1,0,16Zm29.66-82.34a8,8,0,0,1-11.32,0L176,91.31V136a8,8,0,0,1-16,0V91.31l-10.34,10.35a8,8,0,0,1-11.32-11.32l24-24a8,8,0,0,1,11.32,0l24,24A8,8,0,0,1,197.66,101.66Z"/>
  </svg>
);

/** Phosphor Solid `speaker-high-fill` (MIT). */
export const PhFSpeakerHighFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M160,32.25V223.69a8.29,8.29,0,0,1-3.91,7.18,8,8,0,0,1-9-.56l-65.57-51A4,4,0,0,1,80,176.16V79.84a4,4,0,0,1,1.55-3.15l65.57-51a8,8,0,0,1,10,.16A8.27,8.27,0,0,1,160,32.25ZM60,80H32A16,16,0,0,0,16,96v64a16,16,0,0,0,16,16H60a4,4,0,0,0,4-4V84A4,4,0,0,0,60,80Zm126.77,20.84a8,8,0,0,0-.72,11.3,24,24,0,0,1,0,31.72,8,8,0,1,0,12,10.58,40,40,0,0,0,0-52.88A8,8,0,0,0,186.74,100.84Zm40.89-26.17a8,8,0,1,0-11.92,10.66,64,64,0,0,1,0,85.34,8,8,0,1,0,11.92,10.66,80,80,0,0,0,0-106.66Z"/>
  </svg>
);

/** Phosphor Solid `upload-fill` (MIT). */
export const PhFUploadFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M74.34,77.66a8,8,0,0,1,0-11.32l48-48a8,8,0,0,1,11.32,0l48,48a8,8,0,0,1-11.32,11.32L136,43.31V128a8,8,0,0,1-16,0V43.31L85.66,77.66A8,8,0,0,1,74.34,77.66ZM240,136v64a16,16,0,0,1-16,16H32a16,16,0,0,1-16-16V136a16,16,0,0,1,16-16h68a4,4,0,0,1,4,4v3.46c0,13.45,11,24.79,24.46,24.54A24,24,0,0,0,152,128v-4a4,4,0,0,1,4-4h68A16,16,0,0,1,240,136Zm-40,32a12,12,0,1,0-12,12A12,12,0,0,0,200,168Z"/>
  </svg>
);

/** Phosphor Solid `git-branch-fill` (MIT). */
export const PhFGitBranchFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M232,64a32,32,0,1,0-40,31v17a8,8,0,0,1-8,8H96a23.84,23.84,0,0,0-8,1.38V95a32,32,0,1,0-16,0v66a32,32,0,1,0,16,0V144a8,8,0,0,1,8-8h88a24,24,0,0,0,24-24V95A32.06,32.06,0,0,0,232,64ZM64,64A16,16,0,1,1,80,80,16,16,0,0,1,64,64ZM96,192a16,16,0,1,1-16-16A16,16,0,0,1,96,192Z"/>
  </svg>
);

/** Phosphor Solid `newspaper-fill` (MIT). */
export const PhFNewspaperFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M216,48H56A16,16,0,0,0,40,64V184a8,8,0,0,1-16,0V88A8,8,0,0,0,8,88v96.11A24,24,0,0,0,32,208H208a24,24,0,0,0,24-24V64A16,16,0,0,0,216,48ZM176,152H96a8,8,0,0,1,0-16h80a8,8,0,0,1,0,16Zm0-32H96a8,8,0,0,1,0-16h80a8,8,0,0,1,0,16Z"/>
  </svg>
);

/** Phosphor Solid `headphones-fill` (MIT). */
export const PhFHeadphonesFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M232,128v56a24,24,0,0,1-24,24H192a24,24,0,0,1-24-24V144a24,24,0,0,1,24-24h23.65a87.71,87.71,0,0,0-87-80H128a88,88,0,0,0-87.64,80H64a24,24,0,0,1,24,24v40a24,24,0,0,1-24,24H48a24,24,0,0,1-24-24V128A104.11,104.11,0,0,1,201.89,54.66,103.41,103.41,0,0,1,232,128Z"/>
  </svg>
);

/** Phosphor Solid `folder-fill` (MIT). */
export const PhFFolderFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M216,72H131.31L104,44.69A15.88,15.88,0,0,0,92.69,40H40A16,16,0,0,0,24,56V200.62A15.41,15.41,0,0,0,39.39,216h177.5A15.13,15.13,0,0,0,232,200.89V88A16,16,0,0,0,216,72ZM40,56H92.69l16,16H40Z"/>
  </svg>
);

/** Phosphor Solid `code-fill` (MIT). */
export const PhFCodeFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M216,40H40A16,16,0,0,0,24,56V200a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A16,16,0,0,0,216,40ZM92.8,145.6a8,8,0,1,1-9.6,12.8l-32-24a8,8,0,0,1,0-12.8l32-24a8,8,0,0,1,9.6,12.8L69.33,128Zm58.89-71.4-32,112a8,8,0,1,1-15.38-4.4l32-112a8,8,0,0,1,15.38,4.4Zm53.11,60.2-32,24a8,8,0,0,1-9.6-12.8L186.67,128,163.2,110.4a8,8,0,1,1,9.6-12.8l32,24a8,8,0,0,1,0,12.8Z"/>
  </svg>
);

/** Phosphor Solid `graduation-cap-fill` (MIT). */
export const PhFGraduationCapFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M176,207.24a119,119,0,0,0,16-7.73V240a8,8,0,0,1-16,0Zm11.76-88.43-56-29.87a8,8,0,0,0-7.52,14.12L171,128l17-9.06Zm64-29.87-120-64a8,8,0,0,0-7.52,0l-120,64a8,8,0,0,0,0,14.12L32,117.87v48.42a15.91,15.91,0,0,0,4.06,10.65C49.16,191.53,78.51,216,128,216a130,130,0,0,0,48-8.76V130.67L171,128l-43,22.93L43.83,106l0,0L25,96,128,41.07,231,96l-18.78,10-.06,0L188,118.94a8,8,0,0,1,4,6.93v73.64a115.63,115.63,0,0,0,27.94-22.57A15.91,15.91,0,0,0,224,166.29V117.87l27.76-14.81a8,8,0,0,0,0-14.12Z"/>
  </svg>
);

/** Phosphor Solid `file-fill` (MIT). */
export const PhFFileFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M213.66,82.34l-56-56A8,8,0,0,0,152,24H56A16,16,0,0,0,40,40V216a16,16,0,0,0,16,16H200a16,16,0,0,0,16-16V88A8,8,0,0,0,213.66,82.34ZM152,88V44l44,44Z"/>
  </svg>
);

/** Phosphor Solid `image-fill` (MIT). */
export const PhFImageFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M216,40H40A16,16,0,0,0,24,56V200a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A16,16,0,0,0,216,40ZM156,88a12,12,0,1,1-12,12A12,12,0,0,1,156,88Zm60,112H40V160.69l46.34-46.35a8,8,0,0,1,11.32,0h0L165,181.66a8,8,0,0,0,11.32-11.32l-17.66-17.65L173,138.34a8,8,0,0,1,11.31,0L216,170.07V200Z"/>
  </svg>
);

/** Phosphor Solid `stack-fill` (MIT). */
export const PhFStackFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M220,169.09l-92,53.65L36,169.09A8,8,0,0,0,28,182.91l96,56a8,8,0,0,0,8.06,0l96-56A8,8,0,1,0,220,169.09Z"/><path d="M220,121.09l-92,53.65L36,121.09A8,8,0,0,0,28,134.91l96,56a8,8,0,0,0,8.06,0l96-56A8,8,0,1,0,220,121.09Z"/><path d="M28,86.91l96,56a8,8,0,0,0,8.06,0l96-56a8,8,0,0,0,0-13.82l-96-56a8,8,0,0,0-8.06,0l-96,56a8,8,0,0,0,0,13.82Z"/>
  </svg>
);

/** Phosphor Solid `file-text-fill` (MIT). */
export const PhFFileTextFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M213.66,82.34l-56-56A8,8,0,0,0,152,24H56A16,16,0,0,0,40,40V216a16,16,0,0,0,16,16H200a16,16,0,0,0,16-16V88A8,8,0,0,0,213.66,82.34ZM160,176H96a8,8,0,0,1,0-16h64a8,8,0,0,1,0,16Zm0-32H96a8,8,0,0,1,0-16h64a8,8,0,0,1,0,16Zm-8-56V44l44,44Z"/>
  </svg>
);

/** Phosphor Solid `book-open-fill` (MIT). */
export const PhFBookOpenFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M240,56V200a8,8,0,0,1-8,8H160a24,24,0,0,0-24,23.94,7.9,7.9,0,0,1-5.12,7.55A8,8,0,0,1,120,232a24,24,0,0,0-24-24H24a8,8,0,0,1-8-8V56a8,8,0,0,1,8-8H88a32,32,0,0,1,32,32v87.73a8.17,8.17,0,0,0,7.47,8.25,8,8,0,0,0,8.53-8V80a32,32,0,0,1,32-32h64A8,8,0,0,1,240,56Z"/>
  </svg>
);

/** Phosphor Solid `signpost-fill` (MIT). */
export const PhFSignpostFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M246,117.35,212.33,154.7a16,16,0,0,1-11.89,5.3H136v64a8,8,0,0,1-16,0V160H40a16,16,0,0,1-16-16V80A16,16,0,0,1,40,64h80V32a8,8,0,0,1,16,0V64h64.44a16,16,0,0,1,11.89,5.3L246,106.65A8,8,0,0,1,246,117.35Z"/>
  </svg>
);

/** Phosphor Solid `footprints-fill` (MIT). */
export const PhFFootprintsFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M216.06,192v12A36,36,0,0,1,144,204V192a8,8,0,0,1,8-8h56A8,8,0,0,1,216.06,192ZM104,160h-56a8,8,0,0,0-8,8v12A36,36,0,0,0,112,180V168A8,8,0,0,0,104,160ZM76,16C64.36,16,53.07,26.31,44.2,45c-13.93,29.38-18.56,73,.29,96a8,8,0,0,0,6.2,2.93h50.55a8,8,0,0,0,6.2-2.93c18.85-23,14.22-66.65.29-96C98.85,26.31,87.57,16,76,16Zm78.8,152h50.55a8,8,0,0,0,6.2-2.93c18.85-23,14.22-66.65.29-96C202.93,50.31,191.64,40,180,40s-22.89,10.31-31.77,29c-13.93,29.38-18.56,73,.29,96A8,8,0,0,0,154.76,168Z"/>
  </svg>
);

/** Phosphor Solid `tag-fill` (MIT). */
export const PhFTagFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M243.31,136,144,36.69A15.86,15.86,0,0,0,132.69,32H40a8,8,0,0,0-8,8v92.69A15.86,15.86,0,0,0,36.69,144L136,243.31a16,16,0,0,0,22.63,0l84.68-84.68a16,16,0,0,0,0-22.63ZM84,96A12,12,0,1,1,96,84,12,12,0,0,1,84,96Z"/>
  </svg>
);

/** Phosphor Solid `terminal-fill` (MIT). */
export const PhFTerminalFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M216,40H40A16,16,0,0,0,24,56V200a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A16,16,0,0,0,216,40ZM77.66,173.66a8,8,0,0,1-11.32-11.32L100.69,128,66.34,93.66A8,8,0,0,1,77.66,82.34l40,40a8,8,0,0,1,0,11.32ZM192,176H128a8,8,0,0,1,0-16h64a8,8,0,0,1,0,16Z"/>
  </svg>
);

/** Phosphor Solid `flask-fill` (MIT). */
export const PhFFlaskFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M221.69,199.77,160,96.92V40h8a8,8,0,0,0,0-16H88a8,8,0,0,0,0,16h8V96.92L34.31,199.77A16,16,0,0,0,48,224H208a16,16,0,0,0,13.72-24.23Zm-90.08-42.91c-15.91-8.05-31.05-12.32-45.22-12.81l24.47-40.8A7.93,7.93,0,0,0,112,99.14V40h32V99.14a7.93,7.93,0,0,0,1.14,4.11L183.36,167C171.4,169.34,154.29,168.34,131.61,156.86Z"/>
  </svg>
);

/** Phosphor Solid `video-fill` (MIT). */
export const PhFVideoFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M232,208a8,8,0,0,1-8,8H32a8,8,0,0,1,0-16H224A8,8,0,0,1,232,208Zm0-152V168a16,16,0,0,1-16,16H40a16,16,0,0,1-16-16V56A16,16,0,0,1,40,40H216A16,16,0,0,1,232,56Zm-68,56a8,8,0,0,0-3.41-6.55l-40-28A8,8,0,0,0,108,84v56a8,8,0,0,0,12.59,6.55l40-28A8,8,0,0,0,164,112Z"/>
  </svg>
);

/** Phosphor Solid `target-fill` (MIT). */
export const PhFTargetFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M221.87,83.16A104.1,104.1,0,1,1,195.67,49l22.67-22.68a8,8,0,0,1,11.32,11.32L167.6,99.71h0l-37.71,37.71-23.95,23.95a40,40,0,0,0,62-35.67,8,8,0,1,1,16-.9,56,56,0,0,1-95.5,42.79h0a56,56,0,0,1,73.13-84.43L184.3,60.39a87.88,87.88,0,1,0,23.13,29.67,8,8,0,0,1,14.44-6.9Z"/>
  </svg>
);

/** Phosphor Solid `calendar-fill` (MIT). */
export const PhFCalendarFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M208,32H184V24a8,8,0,0,0-16,0v8H88V24a8,8,0,0,0-16,0v8H48A16,16,0,0,0,32,48V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V48A16,16,0,0,0,208,32ZM112,184a8,8,0,0,1-16,0V132.94l-4.42,2.22a8,8,0,0,1-7.16-14.32l16-8A8,8,0,0,1,112,120Zm56-8a8,8,0,0,1,0,16H136a8,8,0,0,1-6.4-12.8l28.78-38.37A8,8,0,1,0,145.07,132a8,8,0,1,1-13.85-8A24,24,0,0,1,176,136a23.76,23.76,0,0,1-4.84,14.45L152,176ZM48,80V48H72v8a8,8,0,0,0,16,0V48h80v8a8,8,0,0,0,16,0V48h24V80Z"/>
  </svg>
);

/** Phosphor Solid `clock-fill` (MIT). */
export const PhFClockFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm56,112H128a8,8,0,0,1-8-8V72a8,8,0,0,1,16,0v48h48a8,8,0,0,1,0,16Z"/>
  </svg>
);

/** Phosphor Solid `sword-fill` (MIT). */
export const PhFSwordFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M216,32H152a8,8,0,0,0-6.34,3.12l-64,83.21L72,108.69a16,16,0,0,0-22.64,0l-8.69,8.7a16,16,0,0,0,0,22.63l22,22-32,32a16,16,0,0,0,0,22.63l8.69,8.68a16,16,0,0,0,22.62,0l32-32,22,22a16,16,0,0,0,22.64,0l8.69-8.7a16,16,0,0,0,0-22.63l-9.64-9.64,83.21-64A8,8,0,0,0,224,104V40A8,8,0,0,0,216,32Zm-8,68.06-81.74,62.88L115.32,152l50.34-50.34a8,8,0,0,0-11.32-11.31L104,140.68,93.07,129.74,155.94,48H208Z"/>
  </svg>
);

/** Phosphor Solid `flag-fill` (MIT). */
export const PhFFlagFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M232,56V176a8,8,0,0,1-2.76,6c-15.28,13.23-29.89,18-43.82,18-18.91,0-36.57-8.74-53-16.85C105.87,170,82.79,158.61,56,179.77V224a8,8,0,0,1-16,0V56a8,8,0,0,1,2.77-6h0c36-31.18,68.31-15.21,96.79-1.12C167,62.46,190.79,74.2,218.76,50A8,8,0,0,1,232,56Z"/>
  </svg>
);

/** Phosphor Solid `trophy-fill` (MIT). */
export const PhFTrophyFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M232,64H208V48a8,8,0,0,0-8-8H56a8,8,0,0,0-8,8V64H24A16,16,0,0,0,8,80V96a40,40,0,0,0,40,40h3.65A80.13,80.13,0,0,0,120,191.61V216H96a8,8,0,0,0,0,16h64a8,8,0,0,0,0-16H136V191.58c31.94-3.23,58.44-25.64,68.08-55.58H208a40,40,0,0,0,40-40V80A16,16,0,0,0,232,64ZM48,120A24,24,0,0,1,24,96V80H48v32q0,4,.39,8ZM232,96a24,24,0,0,1-24,24h-.5a81.81,81.81,0,0,0,.5-8.9V80h24Z"/>
  </svg>
);

/** Phosphor Solid `chart-bar-fill` (MIT). */
export const PhFChartBarFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M232,208a8,8,0,0,1-8,8H32a8,8,0,0,1,0-16h8V136a8,8,0,0,1,8-8H72a8,8,0,0,1,8,8v64H96V88a8,8,0,0,1,8-8h32a8,8,0,0,1,8,8V200h16V40a8,8,0,0,1,8-8h40a8,8,0,0,1,8,8V200h8A8,8,0,0,1,232,208Z"/>
  </svg>
);

/** Phosphor Solid `radio-fill` (MIT). */
export const PhFRadioFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M216,64H86.51L194.3,31.67a8,8,0,0,0-4.6-15.33l-160,48h0A8,8,0,0,0,24,72V192a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V80A16,16,0,0,0,216,64ZM104,176H64a8,8,0,0,1,0-16h40a8,8,0,0,1,0,16Zm0-32H64a8,8,0,0,1,0-16h40a8,8,0,0,1,0,16Zm0-32H64a8,8,0,0,1,0-16h40a8,8,0,0,1,0,16Zm64,56a32,32,0,1,1,32-32A32,32,0,0,1,168,168Z"/>
  </svg>
);

/** Phosphor Solid `lock-fill` (MIT). */
export const PhFLockFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M208,80H176V56a48,48,0,0,0-96,0V80H48A16,16,0,0,0,32,96V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V96A16,16,0,0,0,208,80Zm-80,84a12,12,0,1,1,12-12A12,12,0,0,1,128,164Zm32-84H96V56a32,32,0,0,1,64,0Z"/>
  </svg>
);

/** Phosphor Solid `star-fill` (MIT). */
export const PhFStarFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M234.29,114.85l-45,38.83L203,211.75a16.4,16.4,0,0,1-24.5,17.82L128,198.49,77.47,229.57A16.4,16.4,0,0,1,53,211.75l13.76-58.07-45-38.83A16.46,16.46,0,0,1,31.08,86l59-4.76,22.76-55.08a16.36,16.36,0,0,1,30.27,0l22.75,55.08,59,4.76a16.46,16.46,0,0,1,9.37,28.86Z"/>
  </svg>
);

/** Phosphor Solid `user-check-fill` (MIT). */
export const PhFUserCheckFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M253.66,133.66l-32,32a8,8,0,0,1-11.32,0l-16-16a8,8,0,0,1,11.32-11.32L216,148.69l26.34-26.35a8,8,0,0,1,11.32,11.32ZM144,157.68a68,68,0,1,0-71.9,0c-20.65,6.76-39.23,19.39-54.17,37.17A8,8,0,0,0,24,208H192a8,8,0,0,0,6.13-13.15C183.18,177.07,164.6,164.44,144,157.68Z"/>
  </svg>
);

/** Phosphor Solid `table-fill` (MIT). */
export const PhFTableFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M224,48H32a8,8,0,0,0-8,8V192a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A8,8,0,0,0,224,48ZM40,112H80v32H40Zm56,0H216v32H96ZM40,160H80v32H40Zm176,32H96V160H216v32Z"/>
  </svg>
);

/** Phosphor Solid `users-fill` (MIT). */
export const PhFUsersFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M164.47,195.63a8,8,0,0,1-6.7,12.37H10.23a8,8,0,0,1-6.7-12.37,95.83,95.83,0,0,1,47.22-37.71,60,60,0,1,1,66.5,0A95.83,95.83,0,0,1,164.47,195.63Zm87.91-.15a95.87,95.87,0,0,0-47.13-37.56A60,60,0,0,0,144.7,54.59a4,4,0,0,0-1.33,6A75.83,75.83,0,0,1,147,150.53a4,4,0,0,0,1.07,5.53,112.32,112.32,0,0,1,29.85,30.83,23.92,23.92,0,0,1,3.65,16.47,4,4,0,0,0,3.95,4.64h60.3a8,8,0,0,0,7.73-5.93A8.22,8.22,0,0,0,252.38,195.48Z"/>
  </svg>
);

/** Phosphor Solid `globe-fill` (MIT). */
export const PhFGlobeFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M128,24h0A104,104,0,1,0,232,128,104.12,104.12,0,0,0,128,24Zm78.36,64H170.71a135.28,135.28,0,0,0-22.3-45.6A88.29,88.29,0,0,1,206.37,88ZM216,128a87.61,87.61,0,0,1-3.33,24H174.16a157.44,157.44,0,0,0,0-48h38.51A87.61,87.61,0,0,1,216,128ZM128,43a115.27,115.27,0,0,1,26,45H102A115.11,115.11,0,0,1,128,43ZM102,168H154a115.11,115.11,0,0,1-26,45A115.27,115.27,0,0,1,102,168Zm-3.9-16a140.84,140.84,0,0,1,0-48h59.88a140.84,140.84,0,0,1,0,48Zm50.35,61.6a135.28,135.28,0,0,0,22.3-45.6h35.66A88.29,88.29,0,0,1,148.41,213.6Z"/>
  </svg>
);

/** Phosphor Solid `monitor-fill` (MIT). */
export const PhFMonitorFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M232,64V176a24,24,0,0,1-24,24H48a24,24,0,0,1-24-24V64A24,24,0,0,1,48,40H208A24,24,0,0,1,232,64ZM160,216H96a8,8,0,0,0,0,16h64a8,8,0,0,0,0-16Z"/>
  </svg>
);

/** Phosphor Solid `laptop-fill` (MIT). */
export const PhFLaptopFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M232,168h-8V72a24,24,0,0,0-24-24H56A24,24,0,0,0,32,72v96H24a8,8,0,0,0-8,8v16a24,24,0,0,0,24,24H216a24,24,0,0,0,24-24V176A8,8,0,0,0,232,168ZM112,72h32a8,8,0,0,1,0,16H112a8,8,0,0,1,0-16ZM224,192a8,8,0,0,1-8,8H40a8,8,0,0,1-8-8v-8H224Z"/>
  </svg>
);

/** Phosphor Solid `device-mobile-fill` (MIT). */
export const PhFDeviceMobileFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M176,16H80A24,24,0,0,0,56,40V216a24,24,0,0,0,24,24h96a24,24,0,0,0,24-24V40A24,24,0,0,0,176,16ZM80,32h96a8,8,0,0,1,8,8v8H72V40A8,8,0,0,1,80,32Zm96,192H80a8,8,0,0,1-8-8v-8H184v8A8,8,0,0,1,176,224Z"/>
  </svg>
);

/** Phosphor Solid `qr-code-fill` (MIT). */
export const PhFQrCodeFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M120,56v48a16,16,0,0,1-16,16H56a16,16,0,0,1-16-16V56A16,16,0,0,1,56,40h48A16,16,0,0,1,120,56Zm-16,80H56a16,16,0,0,0-16,16v48a16,16,0,0,0,16,16h48a16,16,0,0,0,16-16V152A16,16,0,0,0,104,136Zm96-96H152a16,16,0,0,0-16,16v48a16,16,0,0,0,16,16h48a16,16,0,0,0,16-16V56A16,16,0,0,0,200,40ZM144,184a8,8,0,0,0,8-8V144a8,8,0,0,0-16,0v32A8,8,0,0,0,144,184Zm64-32H184v-8a8,8,0,0,0-16,0v56H144a8,8,0,0,0,0,16h32a8,8,0,0,0,8-8V168h24a8,8,0,0,0,0-16Zm0,32a8,8,0,0,0-8,8v16a8,8,0,0,0,16,0V192A8,8,0,0,0,208,184Z"/>
  </svg>
);

/** Phosphor Solid `device-tablet-fill` (MIT). */
export const PhFDeviceTabletFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M192,24H64A24,24,0,0,0,40,48V208a24,24,0,0,0,24,24H192a24,24,0,0,0,24-24V48A24,24,0,0,0,192,24ZM64,40H192a8,8,0,0,1,8,8v8H56V48A8,8,0,0,1,64,40ZM192,216H64a8,8,0,0,1-8-8v-8H200v8A8,8,0,0,1,192,216Z"/>
  </svg>
);

/** Phosphor Solid `hand-fill` (MIT). */
export const PhFHandFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M216,64v90.93c0,46.2-36.85,84.55-83,85.06A83.71,83.71,0,0,1,72.6,215.4C50.79,192.33,26.15,136,26.15,136a16,16,0,0,1,6.53-22.23c7.66-4,17.1-.84,21.4,6.62l21,36.44a6.09,6.09,0,0,0,6,3.09l.12,0A8.19,8.19,0,0,0,88,151.74V48a16,16,0,0,1,16.77-16c8.61.4,15.23,7.82,15.23,16.43V112a8,8,0,0,0,8.53,8,8.17,8.17,0,0,0,7.47-8.25V32a16,16,0,0,1,16.77-16c8.61.4,15.23,7.82,15.23,16.43V120a8,8,0,0,0,8.53,8,8.17,8.17,0,0,0,7.47-8.25V64.45c0-8.61,6.62-16,15.23-16.43A16,16,0,0,1,216,64Z"/>
  </svg>
);

/** Phosphor Solid `list-fill` (MIT). */
export const PhFListFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M208,32H48A16,16,0,0,0,32,48V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V48A16,16,0,0,0,208,32ZM192,184H64a8,8,0,0,1,0-16H192a8,8,0,0,1,0,16Zm0-48H64a8,8,0,0,1,0-16H192a8,8,0,0,1,0,16Zm0-48H64a8,8,0,0,1,0-16H192a8,8,0,0,1,0,16Z"/>
  </svg>
);

/** Phosphor Solid `folder-open-fill` (MIT). */
export const PhFFolderOpenFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M245,110.64A16,16,0,0,0,232,104H216V88a16,16,0,0,0-16-16H130.67L102.94,51.2a16.14,16.14,0,0,0-9.6-3.2H40A16,16,0,0,0,24,64V208h0a8,8,0,0,0,8,8H211.1a8,8,0,0,0,7.59-5.47l28.49-85.47A16.05,16.05,0,0,0,245,110.64ZM93.34,64,123.2,86.4A8,8,0,0,0,128,88h72v16H69.77a16,16,0,0,0-15.18,10.94L40,158.7V64Z"/>
  </svg>
);

/** Phosphor Solid `chat-fill` (MIT). */
export const PhFChatFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M232,64V192a16,16,0,0,1-16,16H83l-32.6,28.16-.09.07A15.89,15.89,0,0,1,40,240a16.05,16.05,0,0,1-6.79-1.52A15.84,15.84,0,0,1,24,224V64A16,16,0,0,1,40,48H216A16,16,0,0,1,232,64Z"/>
  </svg>
);

/** Phosphor Solid `compass-fill` (MIT). */
export const PhFCompassFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm51.58,57.79-32,64a4.08,4.08,0,0,1-1.79,1.79l-64,32a4,4,0,0,1-5.37-5.37l32-64a4.08,4.08,0,0,1,1.79-1.79l64-32A4,4,0,0,1,179.58,81.79Z"/>
  </svg>
);

/** Phosphor Solid `bell-slash-fill` (MIT). */
export const PhFBellSlashFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M221.84,192v0a1.85,1.85,0,0,1-3,.28L83.27,43.19a4,4,0,0,1,.8-6A79.55,79.55,0,0,1,129.17,24C173,24.66,207.8,61.1,208,104.92c.14,34.88,8.31,61.54,13.82,71A15.89,15.89,0,0,1,221.84,192Zm-7.92,18.62a8,8,0,0,1-11.85,10.76L182.62,200H167.16a40,40,0,0,1-78.41,0H47.91a15.78,15.78,0,0,1-13.59-7.59,16.42,16.42,0,0,1-.09-16.68c5.55-9.73,13.7-36.64,13.7-71.73A79.42,79.42,0,0,1,58.79,63.85L42,45.38A8,8,0,1,1,53.84,34.62ZM150.59,200H105.32a24,24,0,0,0,45.27,0Z"/>
  </svg>
);

/** Phosphor Solid `gear-fill` (MIT). */
export const PhFGearFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M216,130.16q.06-2.16,0-4.32l14.92-18.64a8,8,0,0,0,1.48-7.06,107.6,107.6,0,0,0-10.88-26.25,8,8,0,0,0-6-3.93l-23.72-2.64q-1.48-1.56-3-3L186,40.54a8,8,0,0,0-3.94-6,107.29,107.29,0,0,0-26.25-10.86,8,8,0,0,0-7.06,1.48L130.16,40Q128,40,125.84,40L107.2,25.11a8,8,0,0,0-7.06-1.48A107.6,107.6,0,0,0,73.89,34.51a8,8,0,0,0-3.93,6L67.32,64.27q-1.56,1.49-3,3L40.54,70a8,8,0,0,0-6,3.94,107.71,107.71,0,0,0-10.87,26.25,8,8,0,0,0,1.49,7.06L40,125.84Q40,128,40,130.16L25.11,148.8a8,8,0,0,0-1.48,7.06,107.6,107.6,0,0,0,10.88,26.25,8,8,0,0,0,6,3.93l23.72,2.64q1.49,1.56,3,3L70,215.46a8,8,0,0,0,3.94,6,107.71,107.71,0,0,0,26.25,10.87,8,8,0,0,0,7.06-1.49L125.84,216q2.16.06,4.32,0l18.64,14.92a8,8,0,0,0,7.06,1.48,107.21,107.21,0,0,0,26.25-10.88,8,8,0,0,0,3.93-6l2.64-23.72q1.56-1.48,3-3L215.46,186a8,8,0,0,0,6-3.94,107.71,107.71,0,0,0,10.87-26.25,8,8,0,0,0-1.49-7.06ZM128,168a40,40,0,1,1,40-40A40,40,0,0,1,128,168Z"/>
  </svg>
);

/** Phosphor Solid `warning-fill` (MIT). */
export const PhFWarningFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M236.8,188.09,149.35,36.22h0a24.76,24.76,0,0,0-42.7,0L19.2,188.09a23.51,23.51,0,0,0,0,23.72A24.35,24.35,0,0,0,40.55,224h174.9a24.35,24.35,0,0,0,21.33-12.19A23.51,23.51,0,0,0,236.8,188.09ZM120,104a8,8,0,0,1,16,0v40a8,8,0,0,1-16,0Zm8,88a12,12,0,1,1,12-12A12,12,0,0,1,128,192Z"/>
  </svg>
);

/** Phosphor Solid `plug-fill` (MIT). */
export const PhFPlugFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M237.66,77.66,203.31,112l26.35,26.34a8,8,0,0,1-11.32,11.32L212,143.31l-53,53a40,40,0,0,1-56.57,0L86.75,180.57,37.66,229.66a8,8,0,0,1-11.32-11.32l49.09-49.09L59.72,153.54a40,40,0,0,1,0-56.57l53-53-6.35-6.34a8,8,0,0,1,11.32-11.32L144,52.69l34.34-34.35a8,8,0,1,1,11.32,11.32L155.31,64,192,100.69l34.34-34.35a8,8,0,0,1,11.32,11.32Z"/>
  </svg>
);

/** Phosphor Solid `flame-fill` (MIT). */
export const PhFFlameFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M173.79,51.48a221.25,221.25,0,0,0-41.67-34.34,8,8,0,0,0-8.24,0A221.25,221.25,0,0,0,82.21,51.48C54.59,80.48,40,112.47,40,144a88,88,0,0,0,176,0C216,112.47,201.41,80.48,173.79,51.48ZM96,184c0-27.67,22.53-47.28,32-54.3,9.48,7,32,26.63,32,54.3a32,32,0,0,1-64,0Z"/>
  </svg>
);

/** Phosphor Solid `timer-fill` (MIT). */
export const PhFTimerFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M128,40a96,96,0,1,0,96,96A96.11,96.11,0,0,0,128,40Zm45.66,61.66-40,40a8,8,0,0,1-11.32-11.32l40-40a8,8,0,0,1,11.32,11.32ZM96,16a8,8,0,0,1,8-8h48a8,8,0,0,1,0,16H104A8,8,0,0,1,96,16Z"/>
  </svg>
);

/** Phosphor Solid `translate-fill` (MIT). */
export const PhFTranslateFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M160,129.89,175.06,160H144.94l6.36-12.7v0ZM224,48V208a16,16,0,0,1-16,16H48a16,16,0,0,1-16-16V48A16,16,0,0,1,48,32H208A16,16,0,0,1,224,48ZM207.16,188.42l-40-80a8,8,0,0,0-14.32,0L139.66,134.8a62.31,62.31,0,0,1-23.61-10A79.61,79.61,0,0,0,135.6,80H152a8,8,0,0,0,0-16H112V56a8,8,0,0,0-16,0v8H56a8,8,0,0,0,0,16h63.48a63.73,63.73,0,0,1-15.3,34.05,65.93,65.93,0,0,1-9-13.61,8,8,0,0,0-14.32,7.12,81.75,81.75,0,0,0,11.4,17.15A63.62,63.62,0,0,1,56,136a8,8,0,0,0,0,16,79.56,79.56,0,0,0,48.11-16.13,78.33,78.33,0,0,0,28.18,13.66l-19.45,38.89a8,8,0,0,0,14.32,7.16L136.94,176h46.12l9.78,19.58a8,8,0,1,0,14.32-7.16Z"/>
  </svg>
);

/** Phosphor Solid `text-b-fill` (MIT). */
export const PhFTextBFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M168,156a20,20,0,0,1-20,20H96V136h52A20,20,0,0,1,168,156ZM224,48V208a16,16,0,0,1-16,16H48a16,16,0,0,1-16-16V48A16,16,0,0,1,48,32H208A16,16,0,0,1,224,48ZM184,156a36,36,0,0,0-18-31.15A36,36,0,0,0,140,64H88a8,8,0,0,0-8,8V184a8,8,0,0,0,8,8h60A36,36,0,0,0,184,156Zm-24-56a20,20,0,0,0-20-20H96v40h44A20,20,0,0,0,160,100Z"/>
  </svg>
);

/** Phosphor Solid `code-simple-fill` (MIT). */
export const PhFCodeSimpleFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M216,40H40A16,16,0,0,0,24,56V200a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A16,16,0,0,0,216,40ZM101.66,162.34a8,8,0,0,1-11.32,11.32l-40-40a8,8,0,0,1,0-11.32l40-40a8,8,0,0,1,11.32,11.32L67.31,128Zm104-28.68-40,40a8,8,0,0,1-11.32-11.32L188.69,128,154.34,93.66a8,8,0,0,1,11.32-11.32l40,40A8,8,0,0,1,205.66,133.66Z"/>
  </svg>
);

/** Phosphor Solid `code-block-fill` (MIT). */
export const PhFCodeBlockFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M200,40H168a16,16,0,0,0-16-16H32A16,16,0,0,0,16,40v80a16,16,0,0,0,16,16h8v64a16,16,0,0,0,16,16H200a16,16,0,0,0,16-16V56A16,16,0,0,0,200,40ZM106.34,61.66a8,8,0,0,1,11.32-11.32l24,24a8,8,0,0,1,0,11.32l-24,24a8,8,0,0,1-11.32-11.32L124.69,80Zm-64,24a8,8,0,0,1,0-11.32l24-24A8,8,0,0,1,77.66,61.66L59.31,80,77.66,98.34a8,8,0,0,1-11.32,11.32ZM200,200H56V136h96a16,16,0,0,0,16-16V56h32Z"/>
  </svg>
);

/** Phosphor Solid `function-fill` (MIT). */
export const PhFFunctionFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M208,32H48A16,16,0,0,0,32,48V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V48A16,16,0,0,0,208,32ZM176,72H159.92a16,16,0,0,0-15.73,13l-6.55,35H168a8,8,0,0,1,0,16H134.64l-7.11,37.9A32,32,0,0,1,96.08,200H80a8,8,0,0,1,0-16H96.08A16,16,0,0,0,111.81,171L118.36,136H88a8,8,0,0,1,0-16h33.36l7.11-37.9A32,32,0,0,1,159.92,56H176a8,8,0,0,1,0,16Z"/>
  </svg>
);

/** Phosphor Solid `text-h-one-fill` (MIT). */
export const PhFTextHOneFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M208,32H48A16,16,0,0,0,32,48V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V48A16,16,0,0,0,208,32ZM144,160a8,8,0,0,1-16,0V128H72v32a8,8,0,0,1-16,0V80a8,8,0,0,1,16,0v32h56V80a8,8,0,0,1,16,0Zm56,16a8,8,0,0,1-16,0V111l-11.56,7.71a8,8,0,1,1-8.88-13.32l24-16A8,8,0,0,1,200,96Z"/>
  </svg>
);

/** Phosphor Solid `minus-fill` (MIT). */
export const PhFMinusFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M208,32H48A16,16,0,0,0,32,48V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V48A16,16,0,0,0,208,32ZM184,136H72a8,8,0,0,1,0-16H184a8,8,0,0,1,0,16Z"/>
  </svg>
);

/** Phosphor Solid `text-italic-fill` (MIT). */
export const PhFTextItalicFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M208,32H48A16,16,0,0,0,32,48V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V48A16,16,0,0,0,208,32ZM176,80H153.64l-34.29,96H136a8,8,0,0,1,0,16H80a8,8,0,0,1,0-16h22.36l34.29-96H120a8,8,0,0,1,0-16h56a8,8,0,0,1,0,16Z"/>
  </svg>
);

/** Phosphor Solid `link-fill` (MIT). */
export const PhFLinkFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M208,32H48A16,16,0,0,0,32,48V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V48A16,16,0,0,0,208,32ZM115.7,192.49a43.31,43.31,0,0,1-55-66.43l25.37-25.37a43.35,43.35,0,0,1,61.25,0,42.9,42.9,0,0,1,9.95,15.43,8,8,0,1,1-15,5.6A27.33,27.33,0,0,0,97.37,112L72,137.37a27.32,27.32,0,0,0,34.68,41.91,8,8,0,1,1,9,13.21Zm79.61-62.55-25.37,25.37A43,43,0,0,1,139.32,168h0a43.35,43.35,0,0,1-40.53-28.12,8,8,0,1,1,15-5.6A27.35,27.35,0,0,0,139.28,152h0a27.14,27.14,0,0,0,19.32-8L184,118.63a27.32,27.32,0,0,0-34.68-41.91,8,8,0,1,1-9-13.21,43.32,43.32,0,0,1,55,66.43Z"/>
  </svg>
);

/** Phosphor Solid `list-plus-fill` (MIT). */
export const PhFListPlusFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M208,32H48A16,16,0,0,0,32,48V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V48A16,16,0,0,0,208,32ZM64,72H192a8,8,0,0,1,0,16H64a8,8,0,0,1,0-16Zm56,112H64a8,8,0,0,1,0-16h56a8,8,0,0,1,0,16Zm16-48H64a8,8,0,0,1,0-16h72a8,8,0,0,1,0,16Zm64,32H184v16a8,8,0,0,1-16,0V168H152a8,8,0,0,1,0-16h16V136a8,8,0,0,1,16,0v16h16a8,8,0,0,1,0,16Z"/>
  </svg>
);

/** Phosphor Solid `list-numbers-fill` (MIT). */
export const PhFListNumbersFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M208,32H48A16,16,0,0,0,32,48V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V48A16,16,0,0,0,208,32ZM56.84,75.58a8,8,0,0,1,3.58-10.74l16-8A8,8,0,0,1,88,64v48a8,8,0,0,1-16,0V76.94l-4.42,2.22A8,8,0,0,1,56.84,75.58ZM92,180a8,8,0,0,1,0,16H68a8,8,0,0,1-6.4-12.8l21.67-28.89A3.92,3.92,0,0,0,84,152a4,4,0,0,0-7.77-1.33,8,8,0,0,1-15.09-5.34,20,20,0,1,1,35,18.53L84,180Zm100,4H120a8,8,0,0,1,0-16h72a8,8,0,0,1,0,16Zm0-48H120a8,8,0,0,1,0-16h72a8,8,0,0,1,0,16Zm0-48H120a8,8,0,0,1,0-16h72a8,8,0,0,1,0,16Z"/>
  </svg>
);

/** Phosphor Solid `quotes-fill` (MIT). */
export const PhFQuotesFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M116,72v88a48.05,48.05,0,0,1-48,48,8,8,0,0,1,0-16,32,32,0,0,0,32-32v-8H40a16,16,0,0,1-16-16V72A16,16,0,0,1,40,56h60A16,16,0,0,1,116,72ZM216,56H156a16,16,0,0,0-16,16v64a16,16,0,0,0,16,16h60v8a32,32,0,0,1-32,32,8,8,0,0,0,0,16,48.05,48.05,0,0,0,48-48V72A16,16,0,0,0,216,56Z"/>
  </svg>
);

/** Phosphor Solid `paperclip-fill` (MIT). */
export const PhFPaperclipFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm37.66,50.34a8,8,0,0,0-11.32,0L87.09,143A24,24,0,1,0,121,177l49.32-50.32a8,8,0,1,1,11.42,11.2l-49.37,50.38a40,40,0,1,1-56.62-56.51L143,63.09A24,24,0,1,1,177,97L109.71,165.6a8,8,0,1,1-11.42-11.2L165.6,85.71a8,8,0,0,0,.06-11.37Z"/>
  </svg>
);

/** Phosphor Solid `crop-fill` (MIT). */
export const PhFCropFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M208,32H48A16,16,0,0,0,32,48V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V48A16,16,0,0,0,208,32ZM120,80h48a8,8,0,0,1,8,8v48a8,8,0,0,1-16,0V96H120a8,8,0,0,1,0-16Zm72,96H176v16a8,8,0,0,1-16,0V176H88a8,8,0,0,1-8-8V96H64a8,8,0,0,1,0-16H80V64a8,8,0,0,1,16,0v96h96a8,8,0,0,1,0,16Z"/>
  </svg>
);

/** Phosphor Solid `skip-forward-fill` (MIT). */
export const PhFSkipForwardFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M208,40V216a8,8,0,0,1-16,0V146.77L72.43,221.55A15.95,15.95,0,0,1,48,208.12V47.88A15.95,15.95,0,0,1,72.43,34.45L192,109.23V40a8,8,0,0,1,16,0Z"/>
  </svg>
);

/** Phosphor Solid `pause-fill` (MIT). */
export const PhFPauseFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M216,48V208a16,16,0,0,1-16,16H160a16,16,0,0,1-16-16V48a16,16,0,0,1,16-16h40A16,16,0,0,1,216,48ZM96,32H56A16,16,0,0,0,40,48V208a16,16,0,0,0,16,16H96a16,16,0,0,0,16-16V48A16,16,0,0,0,96,32Z"/>
  </svg>
);

/** Phosphor Solid `play-fill` (MIT). */
export const PhFPlayFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M240,128a15.74,15.74,0,0,1-7.6,13.51L88.32,229.65a16,16,0,0,1-16.2.3A15.86,15.86,0,0,1,64,216.13V39.87a15.86,15.86,0,0,1,8.12-13.82,16,16,0,0,1,16.2.3L232.4,114.49A15.74,15.74,0,0,1,240,128Z"/>
  </svg>
);

/** Phosphor Solid `skip-back-fill` (MIT). */
export const PhFSkipBackFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M208,47.88V208.12a16,16,0,0,1-24.43,13.43L64,146.77V216a8,8,0,0,1-16,0V40a8,8,0,0,1,16,0v69.23L183.57,34.45A15.95,15.95,0,0,1,208,47.88Z"/>
  </svg>
);

/** Phosphor Solid `magnifying-glass-plus-fill` (MIT). */
export const PhFMagnifyingGlassPlusFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M229.66,218.34,179.6,168.28a88.21,88.21,0,1,0-11.32,11.31l50.06,50.07a8,8,0,0,0,11.32-11.32ZM144,120H120v24a8,8,0,0,1-16,0V120H80a8,8,0,0,1,0-16h24V80a8,8,0,0,1,16,0v24h24a8,8,0,0,1,0,16Z"/>
  </svg>
);

/** Phosphor Solid `magnifying-glass-minus-fill` (MIT). */
export const PhFMagnifyingGlassMinusFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M229.66,218.34,179.6,168.28a88.21,88.21,0,1,0-11.32,11.31l50.06,50.07a8,8,0,0,0,11.32-11.32ZM144,120H80a8,8,0,0,1,0-16h64a8,8,0,0,1,0,16Z"/>
  </svg>
);

/** Phosphor Solid `arrow-left-fill` (MIT). */
export const PhFArrowLeftFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M224,128a8,8,0,0,1-8,8H120v64a8,8,0,0,1-13.66,5.66l-72-72a8,8,0,0,1,0-11.32l72-72A8,8,0,0,1,120,56v64h96A8,8,0,0,1,224,128Z"/>
  </svg>
);

/** Phosphor Solid `x-fill` (MIT). */
export const PhFXFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M208,32H48A16,16,0,0,0,32,48V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V48A16,16,0,0,0,208,32ZM181.66,170.34a8,8,0,0,1-11.32,11.32L128,139.31,85.66,181.66a8,8,0,0,1-11.32-11.32L116.69,128,74.34,85.66A8,8,0,0,1,85.66,74.34L128,116.69l42.34-42.35a8,8,0,0,1,11.32,11.32L139.31,128Z"/>
  </svg>
);

/** Phosphor Solid `sidebar-simple-fill` (MIT). */
export const PhFSidebarSimpleFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M216,40H40A16,16,0,0,0,24,56V200a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A16,16,0,0,0,216,40Zm0,160H88V56H216V200Z"/>
  </svg>
);

/** Phosphor Solid `caret-down-fill` (MIT). */
export const PhFCaretDownFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M213.66,101.66l-80,80a8,8,0,0,1-11.32,0l-80-80A8,8,0,0,1,48,88H208a8,8,0,0,1,5.66,13.66Z"/>
  </svg>
);

/** Phosphor Solid `caret-up-fill` (MIT). */
export const PhFCaretUpFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M215.39,163.06A8,8,0,0,1,208,168H48a8,8,0,0,1-5.66-13.66l80-80a8,8,0,0,1,11.32,0l80,80A8,8,0,0,1,215.39,163.06Z"/>
  </svg>
);

/** Phosphor Solid `arrow-square-out-fill` (MIT). */
export const PhFArrowSquareOutFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M192,136v72a16,16,0,0,1-16,16H48a16,16,0,0,1-16-16V80A16,16,0,0,1,48,64h72a8,8,0,0,1,0,16H48V208H176V136a8,8,0,0,1,16,0Zm32-96a8,8,0,0,0-8-8H152a8,8,0,0,0-5.66,13.66L172.69,72l-42.35,42.34a8,8,0,0,0,11.32,11.32L184,83.31l26.34,26.35A8,8,0,0,0,224,104Z"/>
  </svg>
);

/** Phosphor Solid `arrow-right-fill` (MIT). */
export const PhFArrowRightFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M221.66,133.66l-72,72A8,8,0,0,1,136,200V136H40a8,8,0,0,1,0-16h96V56a8,8,0,0,1,13.66-5.66l72,72A8,8,0,0,1,221.66,133.66Z"/>
  </svg>
);

/** Phosphor Solid `squares-four-fill` (MIT). */
export const PhFSquaresFourFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M120,56v48a16,16,0,0,1-16,16H56a16,16,0,0,1-16-16V56A16,16,0,0,1,56,40h48A16,16,0,0,1,120,56Zm80-16H152a16,16,0,0,0-16,16v48a16,16,0,0,0,16,16h48a16,16,0,0,0,16-16V56A16,16,0,0,0,200,40Zm-96,96H56a16,16,0,0,0-16,16v48a16,16,0,0,0,16,16h48a16,16,0,0,0,16-16V152A16,16,0,0,0,104,136Zm96,0H152a16,16,0,0,0-16,16v48a16,16,0,0,0,16,16h48a16,16,0,0,0,16-16V152A16,16,0,0,0,200,136Z"/>
  </svg>
);

/** Phosphor Solid `house-fill` (MIT). */
export const PhFHouseFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M224,120v96a8,8,0,0,1-8,8H160a8,8,0,0,1-8-8V164a4,4,0,0,0-4-4H108a4,4,0,0,0-4,4v52a8,8,0,0,1-8,8H40a8,8,0,0,1-8-8V120a16,16,0,0,1,4.69-11.31l80-80a16,16,0,0,1,22.62,0l80,80A16,16,0,0,1,224,120Z"/>
  </svg>
);

/** Phosphor Solid `dots-three-fill` (MIT). */
export const PhFDotsThreeFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M224,80H32A16,16,0,0,0,16,96v64a16,16,0,0,0,16,16H224a16,16,0,0,0,16-16V96A16,16,0,0,0,224,80ZM60,140a12,12,0,1,1,12-12A12,12,0,0,1,60,140Zm68,0a12,12,0,1,1,12-12A12,12,0,0,1,128,140Zm68,0a12,12,0,1,1,12-12A12,12,0,0,1,196,140Z"/>
  </svg>
);

/** Phosphor Solid `caret-right-fill` (MIT). */
export const PhFCaretRightFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M181.66,133.66l-80,80A8,8,0,0,1,88,208V48a8,8,0,0,1,13.66-5.66l80,80A8,8,0,0,1,181.66,133.66Z"/>
  </svg>
);

/** Phosphor Solid `arrow-up-fill` (MIT). */
export const PhFArrowUpFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M207.39,115.06A8,8,0,0,1,200,120H136v96a8,8,0,0,1-16,0V120H56a8,8,0,0,1-5.66-13.66l72-72a8,8,0,0,1,11.32,0l72,72A8,8,0,0,1,207.39,115.06Z"/>
  </svg>
);

/** Phosphor Solid `megaphone-fill` (MIT). */
export const PhFMegaphoneFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M200,72H160.2c-2.91-.17-53.62-3.74-101.91-44.24A16,16,0,0,0,32,40V200a16,16,0,0,0,26.29,12.25c37.77-31.68,77-40.76,93.71-43.3v31.72A16,16,0,0,0,159.12,214l11,7.33A16,16,0,0,0,194.5,212l11.77-44.36A48,48,0,0,0,200,72ZM179,207.89l0,.11-11-7.33V168h21.6ZM200,152H168V88h32a32,32,0,1,1,0,64Z"/>
  </svg>
);

/** Phosphor Solid `circle-fill` (MIT). */
export const PhFCircleFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M232,128A104,104,0,1,1,128,24,104.13,104.13,0,0,1,232,128Z"/>
  </svg>
);

/** Phosphor Solid `bell-fill` (MIT). */
export const PhFBellFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M221.8,175.94C216.25,166.38,208,139.33,208,104a80,80,0,1,0-160,0c0,35.34-8.26,62.38-13.81,71.94A16,16,0,0,0,48,200H88.81a40,40,0,0,0,78.38,0H208a16,16,0,0,0,13.8-24.06ZM128,216a24,24,0,0,1-22.62-16h45.24A24,24,0,0,1,128,216Z"/>
  </svg>
);

/** Phosphor Solid `envelope-fill` (MIT). */
export const PhFEnvelopeFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M224,48H32a8,8,0,0,0-8,8V192a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A8,8,0,0,0,224,48ZM98.71,128,40,181.81V74.19Zm11.84,10.85,12,11.05a8,8,0,0,0,10.82,0l12-11.05,58,53.15H52.57ZM157.29,128,216,74.18V181.82Z"/>
  </svg>
);

/** Phosphor Solid `medal-fill` (MIT). */
export const PhFMedalFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M216,96A88,88,0,1,0,72,163.83V240a8,8,0,0,0,11.58,7.16L128,225l44.43,22.21A8.07,8.07,0,0,0,176,248a8,8,0,0,0,8-8V163.83A87.85,87.85,0,0,0,216,96ZM56,96a72,72,0,1,1,72,72A72.08,72.08,0,0,1,56,96Zm16,0a56,56,0,1,1,56,56A56.06,56.06,0,0,1,72,96Z"/>
  </svg>
);

/** Phosphor Solid `scroll-fill` (MIT). */
export const PhFScrollFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M220.8,169.6A8,8,0,0,0,216,168h-8V64a32,32,0,0,0-32-32H40A32,32,0,0,0,8,64C8,77.61,18.05,85.54,19.2,86.4h0A7.89,7.89,0,0,0,24,88a8,8,0,0,0,4.87-14.33h0C28.83,73.62,24,69.74,24,64a16,16,0,0,1,32,0V192a32,32,0,0,0,32,32H200a32,32,0,0,0,32-32C232,178.39,222,170.46,220.8,169.6ZM104,96h64a8,8,0,0,1,0,16H104a8,8,0,0,1,0-16Zm-8,40a8,8,0,0,1,8-8h64a8,8,0,0,1,0,16H104A8,8,0,0,1,96,136Zm104,72H107.71A31.82,31.82,0,0,0,112,192a26.92,26.92,0,0,0-1.21-8h102a12.58,12.58,0,0,1,3.23,8A16,16,0,0,1,200,208Z"/>
  </svg>
);

/** Phosphor Solid `chart-line-up-fill` (MIT). */
export const PhFChartLineUpFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M216,40H40A16,16,0,0,0,24,56V200a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A16,16,0,0,0,216,40ZM200,192H56a8,8,0,0,1-8-8V72a8,8,0,0,1,16,0v76.69l34.34-34.35a8,8,0,0,1,11.32,0L128,132.69,172.69,88H144a8,8,0,0,1,0-16h48a8,8,0,0,1,8,8v48a8,8,0,0,1-16,0V99.31l-50.34,50.35a8,8,0,0,1-11.32,0L104,131.31l-40,40V176H200a8,8,0,0,1,0,16Z"/>
  </svg>
);

/** Phosphor Solid `chart-pie-fill` (MIT). */
export const PhFChartPieFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm0,16a88,88,0,0,1,71.87,37.27L128,118.76Zm0,176a88,88,0,0,1-71.87-37.27L207.89,91.12A88,88,0,0,1,128,216Z"/>
  </svg>
);

/** Phosphor Solid `crown-simple-fill` (MIT). */
export const PhFCrownSimpleFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M239.75,90.81c0,.11,0,.21-.07.32L217,195a16,16,0,0,1-15.72,13H54.71A16,16,0,0,1,39,195L16.32,91.13c0-.11-.05-.21-.07-.32A16,16,0,0,1,44,77.39l33.67,36.29,35.8-80.29a1,1,0,0,0,0-.1,16,16,0,0,1,29.06,0,1,1,0,0,0,0,.1l35.8,80.29L212,77.39a16,16,0,0,1,27.71,13.42Z"/>
  </svg>
);

/** Phosphor Solid `diamond-fill` (MIT). */
export const PhFDiamondFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M240,128a15.85,15.85,0,0,1-4.67,11.28l-96.05,96.06a16,16,0,0,1-22.56,0h0l-96-96.06a16,16,0,0,1,0-22.56l96.05-96.06a16,16,0,0,1,22.56,0l96.05,96.06A15.85,15.85,0,0,1,240,128Z"/>
  </svg>
);

/** Phosphor Solid `ranking-fill` (MIT). */
export const PhFRankingFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M240,200h-8V144a16,16,0,0,0-16-16H176V56a16,16,0,0,0-16-16H96A16,16,0,0,0,80,56V88H40a16,16,0,0,0-16,16v96H16a8,8,0,0,0,0,16H240a8,8,0,0,0,0-16ZM80,200H40V104H80Zm60-64a8,8,0,0,1-16,0V107.1l-1.47.49a8,8,0,0,1-5.06-15.18l12-4A8,8,0,0,1,140,96Zm76,64H176V144h40Z"/>
  </svg>
);

/** Phosphor Solid `number-circle-one-fill` (MIT). */
export const PhFNumberCircleOneFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm12,152a8,8,0,0,1-16,0V95l-11.56,7.71a8,8,0,1,1-8.88-13.32l24-16A8,8,0,0,1,140,80Z"/>
  </svg>
);

/** Phosphor Solid `shield-fill` (MIT). */
export const PhFShieldFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M224,56v56c0,52.72-25.52,84.67-46.93,102.19-23.06,18.86-46,25.27-47,25.53a8,8,0,0,1-4.2,0c-1-.26-23.91-6.67-47-25.53C57.52,196.67,32,164.72,32,112V56A16,16,0,0,1,48,40H208A16,16,0,0,1,224,56Z"/>
  </svg>
);

/** Phosphor Solid `thumbs-down-fill` (MIT). */
export const PhFThumbsDownFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M239.82,157l-12-96A24,24,0,0,0,204,40H32A16,16,0,0,0,16,56v88a16,16,0,0,0,16,16H75.06l37.78,75.58A8,8,0,0,0,120,240a40,40,0,0,0,40-40V184h56a24,24,0,0,0,23.82-27ZM72,144H32V56H72Z"/>
  </svg>
);

/** Phosphor Solid `thumbs-up-fill` (MIT). */
export const PhFThumbsUpFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M234,80.12A24,24,0,0,0,216,72H160V56a40,40,0,0,0-40-40,8,8,0,0,0-7.16,4.42L75.06,96H32a16,16,0,0,0-16,16v88a16,16,0,0,0,16,16H204a24,24,0,0,0,23.82-21l12-96A24,24,0,0,0,234,80.12ZM32,112H72v88H32Z"/>
  </svg>
);

/** Phosphor Solid `trend-down-fill` (MIT). */
export const PhFTrendDownFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M240,128v64a8,8,0,0,1-8,8H168a8,8,0,0,1-5.66-13.66L188.69,160,136,107.31l-34.34,34.35a8,8,0,0,1-11.32,0l-72-72A8,8,0,0,1,29.66,58.34L96,124.69l34.34-34.35a8,8,0,0,1,11.32,0L200,148.69l26.34-26.35A8,8,0,0,1,240,128Z"/>
  </svg>
);

/** Phosphor Solid `trend-up-fill` (MIT). */
export const PhFTrendUpFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M240,56v64a8,8,0,0,1-13.66,5.66L200,99.31l-58.34,58.35a8,8,0,0,1-11.32,0L96,123.31,29.66,189.66a8,8,0,0,1-11.32-11.32l72-72a8,8,0,0,1,11.32,0L136,140.69,188.69,88,162.34,61.66A8,8,0,0,1,168,48h64A8,8,0,0,1,240,56Z"/>
  </svg>
);

/** Phosphor Solid `shopping-bag-fill` (MIT). */
export const PhFShoppingBagFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M216,40H40A16,16,0,0,0,24,56V200a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A16,16,0,0,0,216,40Zm-88,96A48.05,48.05,0,0,1,80,88a8,8,0,0,1,16,0,32,32,0,0,0,64,0,8,8,0,0,1,16,0A48.05,48.05,0,0,1,128,136Z"/>
  </svg>
);

/** Phosphor Solid `credit-card-fill` (MIT). */
export const PhFCreditCardFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M224,48H32A16,16,0,0,0,16,64V192a16,16,0,0,0,16,16H224a16,16,0,0,0,16-16V64A16,16,0,0,0,224,48ZM136,176H120a8,8,0,0,1,0-16h16a8,8,0,0,1,0,16Zm64,0H168a8,8,0,0,1,0-16h32a8,8,0,0,1,0,16ZM32,88V64H224V88Z"/>
  </svg>
);

/** Phosphor Solid `shopping-cart-fill` (MIT). */
export const PhFShoppingCartFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M230.14,58.87A8,8,0,0,0,224,56H62.68L56.6,22.57A8,8,0,0,0,48.73,16H24a8,8,0,0,0,0,16h18L67.56,172.29a24,24,0,0,0,5.33,11.27,28,28,0,1,0,44.4,8.44h45.42A27.75,27.75,0,0,0,160,204a28,28,0,1,0,28-28H91.17a8,8,0,0,1-7.87-6.57L80.13,152h116a24,24,0,0,0,23.61-19.71l12.16-66.86A8,8,0,0,0,230.14,58.87ZM104,204a12,12,0,1,1-12-12A12,12,0,0,1,104,204Zm96,0a12,12,0,1,1-12-12A12,12,0,0,1,200,204Z"/>
  </svg>
);

/** Phosphor Solid `coins-fill` (MIT). */
export const PhFCoinsFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M184,89.57V84c0-25.08-37.83-44-88-44S8,58.92,8,84v40c0,20.89,26.25,37.49,64,42.46V172c0,25.08,37.83,44,88,44s88-18.92,88-44V132C248,111.3,222.58,94.68,184,89.57ZM56,146.87C36.41,141.4,24,132.39,24,124V109.93c8.16,5.78,19.09,10.44,32,13.57Zm80-23.37c12.91-3.13,23.84-7.79,32-13.57V124c0,8.39-12.41,17.4-32,22.87Zm-16,71.37C100.41,189.4,88,180.39,88,172v-4.17c2.63.1,5.29.17,8,.17,3.88,0,7.67-.13,11.39-.35A121.92,121.92,0,0,0,120,171.41Zm0-44.62A163,163,0,0,1,96,152a163,163,0,0,1-24-1.75V126.46A183.74,183.74,0,0,0,96,128a183.74,183.74,0,0,0,24-1.54Zm64,48a165.45,165.45,0,0,1-48,0V174.4a179.48,179.48,0,0,0,24,1.6,183.74,183.74,0,0,0,24-1.54ZM232,172c0,8.39-12.41,17.4-32,22.87V171.5c12.91-3.13,23.84-7.79,32-13.57Z"/>
  </svg>
);

/** Phosphor Solid `percent-fill` (MIT). */
export const PhFPercentFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M176,172a12,12,0,1,1-12-12A12,12,0,0,1,176,172ZM92,96A12,12,0,1,0,80,84,12,12,0,0,0,92,96ZM224,48V208a16,16,0,0,1-16,16H48a16,16,0,0,1-16-16V48A16,16,0,0,1,48,32H208A16,16,0,0,1,224,48ZM64,84A28,28,0,1,0,92,56,28,28,0,0,0,64,84Zm128,88a28,28,0,1,0-28,28A28,28,0,0,0,192,172ZM189.66,66.34a8,8,0,0,0-11.32,0l-112,112a8,8,0,0,0,11.32,11.32l112-112A8,8,0,0,0,189.66,66.34Z"/>
  </svg>
);

/** Phosphor Solid `gift-fill` (MIT). */
export const PhFGiftFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M216,72H180.92c.39-.33.79-.65,1.17-1A29.53,29.53,0,0,0,192,49.57,32.62,32.62,0,0,0,158.44,16,29.53,29.53,0,0,0,137,25.91a54.94,54.94,0,0,0-9,14.48,54.94,54.94,0,0,0-9-14.48A29.53,29.53,0,0,0,97.56,16,32.62,32.62,0,0,0,64,49.57,29.53,29.53,0,0,0,73.91,71c.38.33.78.65,1.17,1H40A16,16,0,0,0,24,88v32a16,16,0,0,0,16,16v64a16,16,0,0,0,16,16h60a4,4,0,0,0,4-4V120H40V88h80v32h16V88h80v32H136v92a4,4,0,0,0,4,4h60a16,16,0,0,0,16-16V136a16,16,0,0,0,16-16V88A16,16,0,0,0,216,72ZM84.51,59a13.69,13.69,0,0,1-4.5-10A16.62,16.62,0,0,1,96.59,32h.49a13.69,13.69,0,0,1,10,4.5c8.39,9.48,11.35,25.2,12.39,34.92C109.71,70.39,94,67.43,84.51,59Zm87,0c-9.49,8.4-25.24,11.36-35,12.4C137.7,60.89,141,45.5,149,36.51a13.69,13.69,0,0,1,10-4.5h.49A16.62,16.62,0,0,1,176,49.08,13.69,13.69,0,0,1,171.49,59Z"/>
  </svg>
);

/** Phosphor Solid `receipt-fill` (MIT). */
export const PhFReceiptFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M216,40H40A16,16,0,0,0,24,56V208a8,8,0,0,0,11.58,7.15L64,200.94l28.42,14.21a8,8,0,0,0,7.16,0L128,200.94l28.42,14.21a8,8,0,0,0,7.16,0L192,200.94l28.42,14.21A8,8,0,0,0,232,208V56A16,16,0,0,0,216,40ZM176,144H80a8,8,0,0,1,0-16h96a8,8,0,0,1,0,16Zm0-32H80a8,8,0,0,1,0-16h96a8,8,0,0,1,0,16Z"/>
  </svg>
);

/** Phosphor Solid `wallet-fill` (MIT). */
export const PhFWalletFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M216,64H56a8,8,0,0,1,0-16H192a8,8,0,0,0,0-16H56A24,24,0,0,0,32,56V184a24,24,0,0,0,24,24H216a16,16,0,0,0,16-16V80A16,16,0,0,0,216,64Zm-36,80a12,12,0,1,1,12-12A12,12,0,0,1,180,144Z"/>
  </svg>
);

/** Phosphor Solid `calculator-fill` (MIT). */
export const PhFCalculatorFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M200,24H56A16,16,0,0,0,40,40V216a16,16,0,0,0,16,16H200a16,16,0,0,0,16-16V40A16,16,0,0,0,200,24ZM88,200a12,12,0,1,1,12-12A12,12,0,0,1,88,200Zm0-40a12,12,0,1,1,12-12A12,12,0,0,1,88,160Zm40,40a12,12,0,1,1,12-12A12,12,0,0,1,128,200Zm0-40a12,12,0,1,1,12-12A12,12,0,0,1,128,160Zm40,40a12,12,0,1,1,12-12A12,12,0,0,1,168,200Zm0-40a12,12,0,1,1,12-12A12,12,0,0,1,168,160Zm16-56a8,8,0,0,1-8,8H80a8,8,0,0,1-8-8V64a8,8,0,0,1,8-8h96a8,8,0,0,1,8,8Z"/>
  </svg>
);

/** Phosphor Solid `database-fill` (MIT). */
export const PhFDatabaseFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M128,24C74.17,24,32,48.6,32,80v96c0,31.4,42.17,56,96,56s96-24.6,96-56V80C224,48.6,181.83,24,128,24Zm80,104c0,9.62-7.88,19.43-21.61,26.92C170.93,163.35,150.19,168,128,168s-42.93-4.65-58.39-13.08C55.88,147.43,48,137.62,48,128V111.36c17.06,15,46.23,24.64,80,24.64s62.94-9.68,80-24.64Zm-21.61,74.92C170.93,211.35,150.19,216,128,216s-42.93-4.65-58.39-13.08C55.88,195.43,48,185.62,48,176V159.36c17.06,15,46.23,24.64,80,24.64s62.94-9.68,80-24.64V176C208,185.62,200.12,195.43,186.39,202.92Z"/>
  </svg>
);

/** Phosphor Solid `pulse-fill` (MIT). */
export const PhFPulseFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M216,40H40A16,16,0,0,0,24,56V200a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A16,16,0,0,0,216,40Zm-8,96H188.64L159,188a8,8,0,0,1-6.95,4h-.46a8,8,0,0,1-6.89-4.84L103,89.92,79,132a8,8,0,0,1-7,4H48a8,8,0,0,1,0-16H67.36L97.05,68a8,8,0,0,1,14.3.82L153,166.08l24-42.05a8,8,0,0,1,6.95-4h24a8,8,0,0,1,0,16Z"/>
  </svg>
);

/** Phosphor Solid `cpu-fill` (MIT). */
export const PhFCpuFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M104,104h48v48H104Zm136,48a8,8,0,0,1-8,8H216v40a16,16,0,0,1-16,16H160v16a8,8,0,0,1-16,0V216H112v16a8,8,0,0,1-16,0V216H56a16,16,0,0,1-16-16V160H24a8,8,0,0,1,0-16H40V112H24a8,8,0,0,1,0-16H40V56A16,16,0,0,1,56,40H96V24a8,8,0,0,1,16,0V40h32V24a8,8,0,0,1,16,0V40h40a16,16,0,0,1,16,16V96h16a8,8,0,0,1,0,16H216v32h16A8,8,0,0,1,240,152ZM168,96a8,8,0,0,0-8-8H96a8,8,0,0,0-8,8v64a8,8,0,0,0,8,8h64a8,8,0,0,0,8-8Z"/>
  </svg>
);

/** Phosphor Solid `hard-drives-fill` (MIT). */
export const PhFHardDrivesFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M208,40H48A16,16,0,0,0,32,56v48a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V56A16,16,0,0,0,208,40ZM180,92a12,12,0,1,1,12-12A12,12,0,0,1,180,92Z"/><path d="M208,136H48a16,16,0,0,0-16,16v48a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V152A16,16,0,0,0,208,136Zm-28,52a12,12,0,1,1,12-12A12,12,0,0,1,180,188Z"/>
  </svg>
);

/** Phosphor Solid `gauge-fill` (MIT). */
export const PhFGaugeFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M240,152v24a16,16,0,0,1-16,16H115.93a4,4,0,0,1-3.24-6.35L174.27,101a8.21,8.21,0,0,0-1.37-11.3,8,8,0,0,0-11.37,1.61l-72,99.06A4,4,0,0,1,86.25,192H32a16,16,0,0,1-16-16V153.13c0-1.79,0-3.57.13-5.33a4,4,0,0,1,4-3.8H48a8,8,0,0,0,8-8.53A8.17,8.17,0,0,0,47.73,128H23.92a4,4,0,0,1-3.87-5c12-43.84,49.66-77.13,95.52-82.28a4,4,0,0,1,4.43,4V72a8,8,0,0,0,8.53,8A8.17,8.17,0,0,0,136,71.73V44.67a4,4,0,0,1,4.43-4A112.18,112.18,0,0,1,236.23,123a4,4,0,0,1-3.88,5H208.27a8.17,8.17,0,0,0-8.25,7.47,8,8,0,0,0,8,8.53h27.92a4,4,0,0,1,4,3.86C240,149.23,240,150.61,240,152Z"/>
  </svg>
);

/** Phosphor Solid `flag-checkered-fill` (MIT). */
export const PhFFlagCheckeredFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M227.32,48.75A8,8,0,0,0,218.76,50c-28,24.22-51.72,12.48-79.21-1.13C111.07,34.76,78.78,18.79,42.76,50h0A8,8,0,0,0,40,56V224a8,8,0,0,0,16,0V179.77c26.79-21.16,49.87-9.75,76.45,3.41,16.4,8.11,34.06,16.85,53,16.85,13.93,0,28.54-4.75,43.82-18a8,8,0,0,0,2.76-6V56A8,8,0,0,0,227.32,48.75ZM56,160.44V109.88c16.85-11.28,32.64-11.59,48-7.34v51.74C88.87,150.47,72.87,150.71,56,160.44ZM104,50.87c9.25,2.83,18.61,7.45,28.45,12.32,11.26,5.57,23.11,11.43,35.55,14.56v51.74c15.35,4.25,31.14,3.94,48-7.35v50.11c-16.87,13.32-32.27,13.72-48,8.91V129.49c-21.62-6-42.38-21-64-26.95Z"/>
  </svg>
);

/** Phosphor Solid `info-fill` (MIT). */
export const PhFInfoFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm-4,48a12,12,0,1,1-12,12A12,12,0,0,1,124,72Zm12,112a16,16,0,0,1-16-16V128a8,8,0,0,1,0-16,16,16,0,0,1,16,16v40a8,8,0,0,1,0,16Z"/>
  </svg>
);

/** Phosphor Solid `check-circle-fill` (MIT). */
export const PhFCheckCircleFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm45.66,85.66-56,56a8,8,0,0,1-11.32,0l-24-24a8,8,0,0,1,11.32-11.32L112,148.69l50.34-50.35a8,8,0,0,1,11.32,11.32Z"/>
  </svg>
);

/** Phosphor Solid `hourglass-fill` (MIT). */
export const PhFHourglassFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M200,75.64V40a16,16,0,0,0-16-16H72A16,16,0,0,0,56,40V76a16.08,16.08,0,0,0,6.41,12.8L114.67,128,62.4,167.2A16.07,16.07,0,0,0,56,180v36a16,16,0,0,0,16,16H184a16,16,0,0,0,16-16V180.36a16,16,0,0,0-6.36-12.77L141.26,128l52.38-39.59A16.05,16.05,0,0,0,200,75.64Z"/>
  </svg>
);

/** Phosphor Solid `lock-open-fill` (MIT). */
export const PhFLockOpenFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M208,80H96V56a32,32,0,0,1,32-32c15.37,0,29.2,11,32.16,25.59a8,8,0,0,0,15.68-3.18C171.32,24.15,151.2,8,128,8A48.05,48.05,0,0,0,80,56V80H48A16,16,0,0,0,32,96V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V96A16,16,0,0,0,208,80Zm-80,84a12,12,0,1,1,12-12A12,12,0,0,1,128,164Z"/>
  </svg>
);

/** Phosphor Solid `seal-check-fill` (MIT). */
export const PhFSealCheckFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M225.86,102.82c-3.77-3.94-7.67-8-9.14-11.57-1.36-3.27-1.44-8.69-1.52-13.94-.15-9.76-.31-20.82-8-28.51s-18.75-7.85-28.51-8c-5.25-.08-10.67-.16-13.94-1.52-3.56-1.47-7.63-5.37-11.57-9.14C146.28,23.51,138.44,16,128,16s-18.27,7.51-25.18,14.14c-3.94,3.77-8,7.67-11.57,9.14C88,40.64,82.56,40.72,77.31,40.8c-9.76.15-20.82.31-28.51,8S41,67.55,40.8,77.31c-.08,5.25-.16,10.67-1.52,13.94-1.47,3.56-5.37,7.63-9.14,11.57C23.51,109.72,16,117.56,16,128s7.51,18.27,14.14,25.18c3.77,3.94,7.67,8,9.14,11.57,1.36,3.27,1.44,8.69,1.52,13.94.15,9.76.31,20.82,8,28.51s18.75,7.85,28.51,8c5.25.08,10.67.16,13.94,1.52,3.56,1.47,7.63,5.37,11.57,9.14C109.72,232.49,117.56,240,128,240s18.27-7.51,25.18-14.14c3.94-3.77,8-7.67,11.57-9.14,3.27-1.36,8.69-1.44,13.94-1.52,9.76-.15,20.82-.31,28.51-8s7.85-18.75,8-28.51c.08-5.25.16-10.67,1.52-13.94,1.47-3.56,5.37-7.63,9.14-11.57C232.49,146.28,240,138.44,240,128S232.49,109.73,225.86,102.82Zm-52.2,6.84-56,56a8,8,0,0,1-11.32,0l-24-24a8,8,0,0,1,11.32-11.32L112,148.69l50.34-50.35a8,8,0,0,1,11.32,11.32Z"/>
  </svg>
);

/** Phosphor Solid `key-fill` (MIT). */
export const PhFKeyFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M216.57,39.43A80,80,0,0,0,83.91,120.78L28.69,176A15.86,15.86,0,0,0,24,187.31V216a16,16,0,0,0,16,16H72a8,8,0,0,0,8-8V208H96a8,8,0,0,0,8-8V184h16a8,8,0,0,0,5.66-2.34l9.56-9.57A79.73,79.73,0,0,0,160,176h.1A80,80,0,0,0,216.57,39.43ZM180,92a16,16,0,1,1,16-16A16,16,0,0,1,180,92Z"/>
  </svg>
);

/** Phosphor Solid `cloud-arrow-up-fill` (MIT). */
export const PhFCloudArrowUpFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M247.93,124.52C246.11,77.54,207.07,40,160.06,40A88.1,88.1,0,0,0,81.29,88.67h0A87.48,87.48,0,0,0,72,127.73,8.18,8.18,0,0,1,64.57,136,8,8,0,0,1,56,128a103.66,103.66,0,0,1,5.34-32.92,4,4,0,0,0-4.75-5.18A64.09,64.09,0,0,0,8,152c0,35.19,29.75,64,65,64H160A88.09,88.09,0,0,0,247.93,124.52Zm-50.27,9.14a8,8,0,0,1-11.32,0L168,115.31V176a8,8,0,0,1-16,0V115.31l-18.34,18.35a8,8,0,0,1-11.32-11.32l32-32a8,8,0,0,1,11.32,0l32,32A8,8,0,0,1,197.66,133.66Z"/>
  </svg>
);

/** Phosphor Solid `moon-fill` (MIT). */
export const PhFMoonFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M235.54,150.21a104.84,104.84,0,0,1-37,52.91A104,104,0,0,1,32,120,103.09,103.09,0,0,1,52.88,57.48a104.84,104.84,0,0,1,52.91-37,8,8,0,0,1,10,10,88.08,88.08,0,0,0,109.8,109.8,8,8,0,0,1,10,10Z"/>
  </svg>
);

/** Phosphor Solid `sun-fill` (MIT). */
export const PhFSunFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M120,40V16a8,8,0,0,1,16,0V40a8,8,0,0,1-16,0Zm8,24a64,64,0,1,0,64,64A64.07,64.07,0,0,0,128,64ZM58.34,69.66A8,8,0,0,0,69.66,58.34l-16-16A8,8,0,0,0,42.34,53.66Zm0,116.68-16,16a8,8,0,0,0,11.32,11.32l16-16a8,8,0,0,0-11.32-11.32ZM192,72a8,8,0,0,0,5.66-2.34l16-16a8,8,0,0,0-11.32-11.32l-16,16A8,8,0,0,0,192,72Zm5.66,114.34a8,8,0,0,0-11.32,11.32l16,16a8,8,0,0,0,11.32-11.32ZM48,128a8,8,0,0,0-8-8H16a8,8,0,0,0,0,16H40A8,8,0,0,0,48,128Zm80,80a8,8,0,0,0-8,8v24a8,8,0,0,0,16,0V216A8,8,0,0,0,128,208Zm112-88H216a8,8,0,0,0,0,16h24a8,8,0,0,0,0-16Z"/>
  </svg>
);

/** Phosphor Solid `palette-fill` (MIT). */
export const PhFPaletteFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M200.77,53.89A103.27,103.27,0,0,0,128,24h-1.07A104,104,0,0,0,24,128c0,43,26.58,79.06,69.36,94.17A32,32,0,0,0,136,192a16,16,0,0,1,16-16h46.21a31.81,31.81,0,0,0,31.2-24.88,104.43,104.43,0,0,0,2.59-24A103.28,103.28,0,0,0,200.77,53.89ZM84,168a12,12,0,1,1,12-12A12,12,0,0,1,84,168Zm0-56a12,12,0,1,1,12-12A12,12,0,0,1,84,112Zm44-24a12,12,0,1,1,12-12A12,12,0,0,1,128,88Zm44,24a12,12,0,1,1,12-12A12,12,0,0,1,172,112Z"/>
  </svg>
);

/** Phosphor Solid `devices-fill` (MIT). */
export const PhFDevicesFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M224,72H208V64a24,24,0,0,0-24-24H40A24,24,0,0,0,16,64v96a24,24,0,0,0,24,24H152v8a24,24,0,0,0,24,24h48a24,24,0,0,0,24-24V96A24,24,0,0,0,224,72Zm8,120a8,8,0,0,1-8,8H176a8,8,0,0,1-8-8V96a8,8,0,0,1,8-8h48a8,8,0,0,1,8,8Zm-96,16a8,8,0,0,1-8,8H88a8,8,0,0,1,0-16h40A8,8,0,0,1,136,208Zm80-96a8,8,0,0,1-8,8H192a8,8,0,0,1,0-16h16A8,8,0,0,1,216,112Z"/>
  </svg>
);

/** Phosphor Solid `user-fill` (MIT). */
export const PhFUserFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M230.93,220a8,8,0,0,1-6.93,4H32a8,8,0,0,1-6.92-12c15.23-26.33,38.7-45.21,66.09-54.16a72,72,0,1,1,73.66,0c27.39,8.95,50.86,27.83,66.09,54.16A8,8,0,0,1,230.93,220Z"/>
  </svg>
);

/** Phosphor Solid `user-minus-fill` (MIT). */
export const PhFUserMinusFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M198.13,194.85A8,8,0,0,1,192,208H24a8,8,0,0,1-6.12-13.15c14.94-17.78,33.52-30.41,54.17-37.17a68,68,0,1,1,71.9,0C164.6,164.44,183.18,177.07,198.13,194.85ZM248,128H200a8,8,0,0,0,0,16h48a8,8,0,0,0,0-16Z"/>
  </svg>
);

/** Phosphor Solid `user-plus-fill` (MIT). */
export const PhFUserPlusFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M256,136a8,8,0,0,1-8,8H232v16a8,8,0,0,1-16,0V144H200a8,8,0,0,1,0-16h16V112a8,8,0,0,1,16,0v16h16A8,8,0,0,1,256,136ZM144,157.68a68,68,0,1,0-71.9,0c-20.65,6.76-39.23,19.39-54.17,37.17A8,8,0,0,0,24,208H192a8,8,0,0,0,6.13-13.15C183.18,177.07,164.6,164.44,144,157.68Z"/>
  </svg>
);

/** Phosphor Solid `sign-out-fill` (MIT). */
export const PhFSignOutFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M120,216a8,8,0,0,1-8,8H48a8,8,0,0,1-8-8V40a8,8,0,0,1,8-8h64a8,8,0,0,1,0,16H56V208h56A8,8,0,0,1,120,216Zm109.66-93.66-40-40A8,8,0,0,0,176,88v32H112a8,8,0,0,0,0,16h64v32a8,8,0,0,0,13.66,5.66l40-40A8,8,0,0,0,229.66,122.34Z"/>
  </svg>
);

/** Phosphor Solid `shield-check-fill` (MIT). */
export const PhFShieldCheckFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M208,40H48A16,16,0,0,0,32,56v56c0,52.72,25.52,84.67,46.93,102.19,23.06,18.86,46,25.26,47,25.53a8,8,0,0,0,4.2,0c1-.27,23.91-6.67,47-25.53C198.48,196.67,224,164.72,224,112V56A16,16,0,0,0,208,40Zm-34.32,69.66-56,56a8,8,0,0,1-11.32,0l-24-24a8,8,0,0,1,11.32-11.32L112,148.69l50.34-50.35a8,8,0,0,1,11.32,11.32Z"/>
  </svg>
);

/** Phosphor Solid `presentation-fill` (MIT). */
export const PhFPresentationFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M216,40H136V24a8,8,0,0,0-16,0V40H40A16,16,0,0,0,24,56V176a16,16,0,0,0,16,16H79.36L57.75,219a8,8,0,0,0,12.5,10l29.59-37h56.32l29.59,37a8,8,0,1,0,12.5-10l-21.61-27H216a16,16,0,0,0,16-16V56A16,16,0,0,0,216,40Z"/>
  </svg>
);

/** Phosphor Solid `briefcase-fill` (MIT). */
export const PhFBriefcaseFill = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    <path d="M152,112a8,8,0,0,1-8,8H112a8,8,0,0,1,0-16h32A8,8,0,0,1,152,112Zm80-40V200a16,16,0,0,1-16,16H40a16,16,0,0,1-16-16V72A16,16,0,0,1,40,56H80V48a24,24,0,0,1,24-24h48a24,24,0,0,1,24,24v8h40A16,16,0,0,1,232,72ZM96,56h64V48a8,8,0,0,0-8-8H104a8,8,0,0,0-8,8Zm120,57.61V72H40v41.61A184,184,0,0,0,128,136,184,184,0,0,0,216,113.61Z"/>
  </svg>
);

/** Semantik kalit → Phosphor Solid ikonkasi (D18: `domen.ob'ekt.holat`). */
export const PHOSPHORSOLID_ICONS: Record<string, (p: IconProps) => React.JSX.Element> = {
  "action.add": PhFPlusFill,
  "action.bookmark": PhFBookmarkFill,
  "action.cancel": PhFProhibitFill,
  "action.clear": PhFXCircleFill,
  "action.clipboard": PhFClipboardFill,
  "action.copy": PhFCopyFill,
  "action.delete": PhFTrashFill,
  "action.download": PhFDownloadFill,
  "action.edit": PhFPencilFill,
  "action.eye": PhFEyeFill,
  "action.eyeOff": PhFEyeClosedFill,
  "action.filter": PhFFunnelFill,
  "action.format": PhFMagicWandFill,
  "action.fullscreen": PhFArrowsOutFill,
  "action.help": PhFQuestionFill,
  "action.pin": PhFMapPinFill,
  "action.print": PhFPrinterFill,
  "action.retry": PhFArrowClockwiseFill,
  "action.save": PhFFloppyDiskFill,
  "action.search": PhFMagnifyingGlassFill,
  "action.share": PhFShareFill,
  "action.sliders": PhFSlidersHorizontalFill,
  "action.sortAsc": PhFSortAscendingFill,
  "action.sortDesc": PhFSortDescendingFill,
  "action.sound": PhFSpeakerHighFill,
  "action.upload": PhFUploadFill,
  "content.algorithm": PhFGitBranchFill,
  "content.article": PhFNewspaperFill,
  "content.audio": PhFHeadphonesFill,
  "content.category": PhFFolderFill,
  "content.code": PhFCodeFill,
  "content.course": PhFGraduationCapFill,
  "content.file": PhFFileFill,
  "content.image": PhFImageFill,
  "content.level": PhFStackFill,
  "content.pdf": PhFFileTextFill,
  "content.problem": PhFBookOpenFill,
  "content.quiz": PhFQuestionFill,
  "content.roadmap": PhFSignpostFill,
  "content.step": PhFFootprintsFill,
  "content.tag": PhFTagFill,
  "content.terminal": PhFTerminalFill,
  "content.test": PhFFlaskFill,
  "content.video": PhFVideoFill,
  "contest.arena": PhFTargetFill,
  "contest.calendar": PhFCalendarFill,
  "contest.clock": PhFClockFill,
  "contest.duel": PhFSwordFill,
  "contest.flag": PhFFlagFill,
  "contest.formatAcm": PhFTrophyFill,
  "contest.formatIoi": PhFChartBarFill,
  "contest.hackathon": PhFCodeFill,
  "contest.live": PhFRadioFill,
  "contest.lock": PhFLockFill,
  "contest.rated": PhFStarFill,
  "contest.register": PhFUserCheckFill,
  "contest.standings": PhFTableFill,
  "contest.team": PhFUsersFill,
  "device.appStore": PhFDownloadFill,
  "device.browser": PhFGlobeFill,
  "device.desktop": PhFMonitorFill,
  "device.laptop": PhFLaptopFill,
  "device.phone": PhFDeviceMobileFill,
  "device.qr": PhFQrCodeFill,
  "device.tablet": PhFDeviceTabletFill,
  "device.touch": PhFHandFill,
  "empty.attempts": PhFListFill,
  "empty.files": PhFFolderOpenFill,
  "empty.messages": PhFChatFill,
  "empty.notFound": PhFCompassFill,
  "empty.notifications": PhFBellSlashFill,
  "empty.search": PhFMagnifyingGlassFill,
  "empty.serverError": PhFGearFill,
  "empty.team": PhFUsersFill,
  "error.forbidden": PhFLockFill,
  "error.invalid": PhFWarningFill,
  "error.network": PhFPlugFill,
  "error.notFound": PhFMagnifyingGlassFill,
  "error.server": PhFFlameFill,
  "error.timeout": PhFTimerFill,
  "locale.flag": PhFFlagFill,
  "locale.globe": PhFGlobeFill,
  "locale.region": PhFMapPinFill,
  "locale.switch": PhFTranslateFill,
  "locale.timezone": PhFClockFill,
  "locale.translate": PhFTranslateFill,
  "markdown.bold": PhFTextBFill,
  "markdown.code": PhFCodeSimpleFill,
  "markdown.codeBlock": PhFCodeBlockFill,
  "markdown.formula": PhFFunctionFill,
  "markdown.heading": PhFTextHOneFill,
  "markdown.hr": PhFMinusFill,
  "markdown.image": PhFImageFill,
  "markdown.italic": PhFTextItalicFill,
  "markdown.link": PhFLinkFill,
  "markdown.list": PhFListPlusFill,
  "markdown.orderedList": PhFListNumbersFill,
  "markdown.preview": PhFEyeFill,
  "markdown.quote": PhFQuotesFill,
  "markdown.table": PhFTableFill,
  "media.clip": PhFPaperclipFill,
  "media.crop": PhFCropFill,
  "media.folder": PhFFolderFill,
  "media.fullscreen": PhFArrowsOutFill,
  "media.next": PhFSkipForwardFill,
  "media.pause": PhFPauseFill,
  "media.play": PhFPlayFill,
  "media.prev": PhFSkipBackFill,
  "media.rotate": PhFArrowClockwiseFill,
  "media.volume": PhFSpeakerHighFill,
  "media.zoomIn": PhFMagnifyingGlassPlusFill,
  "media.zoomOut": PhFMagnifyingGlassMinusFill,
  "nav.back": PhFArrowLeftFill,
  "nav.close": PhFXFill,
  "nav.collapse": PhFSidebarSimpleFill,
  "nav.expandDown": PhFCaretDownFill,
  "nav.expandUp": PhFCaretUpFill,
  "nav.external": PhFArrowSquareOutFill,
  "nav.filterPanel": PhFSlidersHorizontalFill,
  "nav.forward": PhFArrowRightFill,
  "nav.grid": PhFSquaresFourFill,
  "nav.home": PhFHouseFill,
  "nav.leaderboard": PhFChartBarFill,
  "nav.list": PhFListFill,
  "nav.menu": PhFListFill,
  "nav.more": PhFDotsThreeFill,
  "nav.problems": PhFBookOpenFill,
  "nav.quiz": PhFQuestionFill,
  "nav.separator": PhFCaretRightFill,
  "nav.up": PhFArrowUpFill,
  "notification.announce": PhFMegaphoneFill,
  "notification.badgeNew": PhFCircleFill,
  "notification.bell": PhFBellFill,
  "notification.bellRead": PhFBellFill,
  "notification.changelog": PhFMegaphoneFill,
  "notification.chat": PhFChatFill,
  "notification.comment": PhFChatFill,
  "notification.email": PhFEnvelopeFill,
  "notification.muted": PhFBellSlashFill,
  "notification.reply": PhFArrowLeftFill,
  "ranking.badge": PhFMedalFill,
  "ranking.certificate": PhFScrollFill,
  "ranking.chartBar": PhFChartBarFill,
  "ranking.chartLine": PhFChartLineUpFill,
  "ranking.chartPie": PhFChartPieFill,
  "ranking.crown": PhFCrownSimpleFill,
  "ranking.diamond": PhFDiamondFill,
  "ranking.medalBronze": PhFMedalFill,
  "ranking.medalGold": PhFMedalFill,
  "ranking.medalSilver": PhFMedalFill,
  "ranking.podium": PhFRankingFill,
  "ranking.rank": PhFNumberCircleOneFill,
  "ranking.shield": PhFShieldFill,
  "ranking.star": PhFStarFill,
  "ranking.streak": PhFFlameFill,
  "ranking.thumbDown": PhFThumbsDownFill,
  "ranking.thumbUp": PhFThumbsUpFill,
  "ranking.trendDown": PhFTrendDownFill,
  "ranking.trendUp": PhFTrendUpFill,
  "ranking.trophy": PhFTrophyFill,
  "shop.buy": PhFShoppingBagFill,
  "shop.card": PhFCreditCardFill,
  "shop.cart": PhFShoppingCartFill,
  "shop.coin": PhFCoinsFill,
  "shop.discount": PhFPercentFill,
  "shop.gift": PhFGiftFill,
  "shop.history": PhFReceiptFill,
  "shop.price": PhFStarFill,
  "shop.store": PhFShoppingBagFill,
  "shop.wallet": PhFWalletFill,
  "stats.calculator": PhFCalculatorFill,
  "stats.chartBar": PhFChartBarFill,
  "stats.chartLine": PhFChartLineUpFill,
  "stats.chartPie": PhFChartPieFill,
  "stats.database": PhFDatabaseFill,
  "stats.funnel": PhFFunnelFill,
  "stats.load": PhFPulseFill,
  "stats.memory": PhFCpuFill,
  "stats.percent": PhFPercentFill,
  "stats.server": PhFHardDrivesFill,
  "stats.speed": PhFGaugeFill,
  "stats.table": PhFTableFill,
  "status.bad": PhFXCircleFill,
  "status.blocked": PhFProhibitFill,
  "status.clock": PhFClockFill,
  "status.finished": PhFFlagCheckeredFill,
  "status.info": PhFInfoFill,
  "status.live": PhFRadioFill,
  "status.locked": PhFLockFill,
  "status.offline": PhFCircleFill,
  "status.ok": PhFCheckCircleFill,
  "status.online": PhFCircleFill,
  "status.pending": PhFHourglassFill,
  "status.timer": PhFTimerFill,
  "status.unlocked": PhFLockOpenFill,
  "status.verified": PhFSealCheckFill,
  "status.warning": PhFWarningFill,
  "status.watching": PhFEyeFill,
  "system.apiKey": PhFKeyFill,
  "system.backup": PhFCloudArrowUpFill,
  "system.dark": PhFMoonFill,
  "system.device": PhFCpuFill,
  "system.key": PhFKeyFill,
  "system.light": PhFSunFill,
  "system.log": PhFFileTextFill,
  "system.monitor": PhFMonitorFill,
  "system.palette": PhFPaletteFill,
  "system.security": PhFShieldFill,
  "system.sessions": PhFDevicesFill,
  "system.settings": PhFGearFill,
  "user.avatar": PhFUserFill,
  "user.block": PhFUserMinusFill,
  "user.education": PhFGraduationCapFill,
  "user.follow": PhFUserPlusFill,
  "user.followers": PhFUsersFill,
  "user.group": PhFUsersFill,
  "user.invite": PhFUserPlusFill,
  "user.link": PhFLinkFill,
  "user.location": PhFMapPinFill,
  "user.logout": PhFSignOutFill,
  "user.profile": PhFUserFill,
  "user.roleAdmin": PhFShieldCheckFill,
  "user.roleStudent": PhFGraduationCapFill,
  "user.roleTeacher": PhFPresentationFill,
  "user.unfollow": PhFUserMinusFill,
  "user.work": PhFBriefcaseFill,
};
