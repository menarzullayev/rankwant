/** Yuklanish ko'rinishlari — o'nta animatsiya (D62).
 *
 *  ⚠️ Hammasi **sof CSS/SVG**: hech qanday kutubxona qo'shilmaydi
 *  (Motion, Lottie, Rive kerak emas). Sabab — og'irlik va barqarorlik:
 *  Lottie bitta animatsiya uchun ~250 KB va dizayner ishi talab qiladi,
 *  bu yerda esa har biri ~10 satr CSS.
 *
 *  ⚠️ **Harakat o'chirilganda ham ko'rinib turishi shart.** `motion` =
 *  `off`/`reduce`/`mild` bo'lsa animatsiya to'xtaydi, lekin element
 *  qoladi: spinner yoyi, skeleton ustunlari, shimmer gradienti. Sabab:
 *  yuklanish — **holat**, dekoratsiya emas. Uni yashirish foydalanuvchini
 *  «sahifa qotib qoldi» degan xulosaga olib keladi.
 *
 *  Shuning uchun bu klasslar ataylab `rw-pulse`/`animate-` prefiksidan
 *  **foydalanmaydi**: `[data-motion="mild"]` o'sha prefikslarni butunlay
 *  o'chiradi (globals.css ga qarang), ya'ni yuklanish indikatori yo'q
 *  bo'lib qolardi.
 */

export type LoadingVariant =
  | "spinner"
  | "ring"
  | "skeleton"
  | "shimmer"
  | "dotsBounce"
  | "dotsFade"
  | "bars"
  | "iconSpin"
  | "pulseIcon"
  | "progress";

/** Standart — aylanuvchi yoy. Eng tushunarli va eng arzon. */
export const DEFAULT_LOADING_VARIANT: LoadingVariant = "spinner";

export const LOADING_VARIANTS: { id: LoadingVariant; labelKey: string; hintKey: string }[] = [
  { id: "spinner", labelKey: "loading.style.spinner", hintKey: "loading.style.spinnerHint" },
  { id: "ring", labelKey: "loading.style.ring", hintKey: "loading.style.ringHint" },
  { id: "skeleton", labelKey: "loading.style.skeleton", hintKey: "loading.style.skeletonHint" },
  { id: "shimmer", labelKey: "loading.style.shimmer", hintKey: "loading.style.shimmerHint" },
  { id: "dotsBounce", labelKey: "loading.style.dotsBounce", hintKey: "loading.style.dotsBounceHint" },
  { id: "dotsFade", labelKey: "loading.style.dotsFade", hintKey: "loading.style.dotsFadeHint" },
  { id: "bars", labelKey: "loading.style.bars", hintKey: "loading.style.barsHint" },
  { id: "iconSpin", labelKey: "loading.style.iconSpin", hintKey: "loading.style.iconSpinHint" },
  { id: "pulseIcon", labelKey: "loading.style.pulseIcon", hintKey: "loading.style.pulseIconHint" },
  { id: "progress", labelKey: "loading.style.progress", hintKey: "loading.style.progressHint" },
];

export function clampLoadingVariant(value: unknown): LoadingVariant {
  return LOADING_VARIANTS.some((v) => v.id === value)
    ? (value as LoadingVariant)
    : DEFAULT_LOADING_VARIANT;
}

/** `skeleton` va `shimmer` — **joy egallovchi** ko'rinishlar: ular
 *  kontent kelguncha o'sha kontentning o'lchamini ushlab turadi.
 *  Qolganlari — **belgi** ko'rinishlar: kichik, o'rtada turadi.
 *
 *  Bu farq muhim: skeleton'ni tugma ichiga qo'yib bo'lmaydi, spinner'ni
 *  esa butun kartaga cho'zib bo'lmaydi. Ya'ni tanlov kontekstga bog'liq,
 *  shuning uchun `Loading` ham `block` propini oladi. */
export const PLACEHOLDER_VARIANTS: LoadingVariant[] = ["skeleton", "shimmer"];

export function isPlaceholder(variant: LoadingVariant): boolean {
  return PLACEHOLDER_VARIANTS.includes(variant);
}
