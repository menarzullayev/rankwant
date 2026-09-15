"use client";

import { useCustomizer } from "@/context/CustomizerContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { LOADING_ICONS } from "@/icons/phosphor";
import {
  DEFAULT_LOADING_VARIANT,
  isPlaceholder,
  type LoadingVariant,
} from "@/lib/theme/loading";

/** Yuklanish ko'rsatkichi — o'nta shakl (D62).
 *
 *  **Bitta komponent, o'nta variant.** Hammasi sof CSS/SVG — hech qanday
 *  kutubxona yo'q (Motion, Lottie kerak emas). Tanlov foydalanuvchi
 *  sozlamasi: `Customizer → «Yuklanish»`.
 *
 *  | Variant      | Ko'rinish                | Qayerda                     |
 *  |--------------|--------------------------|-----------------------------|
 *  | `spinner`    | aylanuvchi yoy           | tugma ichida, kichik kutish |
 *  | `ring`       | SVG uzuk                 | karta ichida, bo'lim        |
 *  | `skeleton`   | pulsatsiyalanuvchi ustun | jadval, ro'yxat o'rni       |
 *  | `shimmer`    | yorug'lik o'tishi        | karta, rasm o'rni           |
 *  | `dotsBounce` | sakrayotgan nuqtalar     | «yozmoqda…», chat           |
 *  | `dotsFade`   | so'nayotgan nuqtalar     | fon amali, avtomatik saqlash|
 *  | `bars`       | ekvalayzer ustunlari     | media, real vaqt oqimi      |
 *  | `iconSpin`   | aylanuvchi ikonka        | «yangilash» tugmasi         |
 *  | `pulseIcon`  | pulsatsiyalanuvchi ikonka| live indikator              |
 *  | `progress`   | aniqlanmagan chiziq      | sahifa yuqorisi, uzoq amal  |
 *
 *  ⚠️ **`block`** — `skeleton`/`shimmer` uchun: ular kontent **o'rnini**
 *  egallaydi (`display: block`, kenglik 100%), qolganlari esa **belgi**
 *  (`inline-flex`, o'rtada). Tugma ichiga skeleton qo'yib bo'lmaydi.
 *
 *  ⚠️ **Harakat o'chirilganda ham ko'rinadi.** `motion` = `off`/`reduce`/
 *  `mild` bo'lsa animatsiya to'xtaydi, lekin shakl qoladi — yuklanish
 *  holat, dekoratsiya emas. Klasslar ataylab `rw-pulse`/`animate-`
 *  prefiksisiz (sabab `lib/theme/loading.ts` da).
 *
 *  ⚠️ `role="status"` + `aria-live="polite"`: ekran o'quvchi kutish
 *  boshlanganini e'lon qiladi. Ko'rinadigan matn yo'q, ya'ni nom
 *  `sr-only` dan keladi.
 */
export function Loading({
  variant,
  label,
  lines = 3,
  block = false,
  className = "",
}: {
  /** Ko'rinishni majburan tanlash. Berilmasa — foydalanuvchi sozlamasi. */
  variant?: LoadingVariant;
  /** Ekran o'quvchi uchun nom. Berilmasa — umumiy «Yuklanmoqda». */
  label?: string;
  /** `skeleton` uchun ustunlar soni. */
  lines?: number;
  /** Joy egallovchi ko'rinish (kenglik 100%). */
  block?: boolean;
  className?: string;
}) {
  const locale = useLocale();
  const { appearance } = useCustomizer();
  const shape = variant ?? appearance.loadingStyle ?? DEFAULT_LOADING_VARIANT;
  const text = label ?? t(locale, "loading.label");
  const full = block || isPlaceholder(shape);

  const wrap = (inner: React.ReactNode) => (
    <span
      role="status"
      aria-live="polite"
      className={`rw-load rw-load-${shape}${full ? " rw-load-block" : ""} ${className}`}
    >
      {inner}
      <span className="sr-only">{text}</span>
    </span>
  );

  if (shape === "ring") {
    return wrap(
      <svg className="rw-load-ring" viewBox="0 0 40 40" aria-hidden="true">
        <circle cx="20" cy="20" r="16" fill="none" stroke="currentColor" strokeWidth="4" opacity=".2" />
        <circle
          className="rw-load-ring-arc"
          cx="20"
          cy="20"
          r="16"
          fill="none"
          stroke="currentColor"
          strokeWidth="4"
          strokeLinecap="round"
          strokeDasharray="25 100"
        />
      </svg>
    );
  }

  if (shape === "skeleton") {
    return wrap(
      <span className="rw-load-skel" aria-hidden="true">
        {Array.from({ length: lines }, (_, i) => (
          // Oxirgi ustun qisqaroq — matn blokiga o'xshasin.
          <i key={i} style={{ width: i === lines - 1 ? "62%" : "100%" }} />
        ))}
      </span>
    );
  }

  if (shape === "shimmer") {
    return wrap(<span className="rw-load-shimmer" aria-hidden="true" />);
  }

  if (shape === "dotsBounce" || shape === "dotsFade") {
    return wrap(
      <span className="rw-load-dots" aria-hidden="true">
        <i />
        <i />
        <i />
      </span>
    );
  }

  if (shape === "bars") {
    return wrap(
      <span className="rw-load-bars" aria-hidden="true">
        <i />
        <i />
        <i />
        <i />
      </span>
    );
  }

  if (shape === "iconSpin") {
    const Icon = LOADING_ICONS.spin;
    return wrap(<Icon className="size-6 rw-load-iconspin" />);
  }

  if (shape === "pulseIcon") {
    const Icon = LOADING_ICONS.pulse;
    return wrap(<Icon className="size-6 rw-load-pulse" />);
  }

  if (shape === "progress") {
    return wrap(<span className="rw-load-progress" aria-hidden="true" />);
  }

  // `spinner` — standart. SVG emas, chegara: masshtabda chiziq qalinligi
  // bir xil qoladi va ikonka import qilinmaydi.
  return wrap(<span className="rw-load-arc" aria-hidden="true" />);
}
