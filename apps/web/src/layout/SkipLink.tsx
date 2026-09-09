"use client";

import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

/** Menyuni chetlab o'tish havolasi — WCAG 2.4.1 «Bypass Blocks».
 *
 * O'lchandi: Tab bosib mazmunga yetish uchun 20 dan ortiq yon menyu
 * havolasini kesib o'tish kerak edi, va bu HAR sahifada takrorlanardi.
 * Sichqoncha bilan ko'rinmaydi, fokusga kelganda chiqadi.
 */
export function SkipLink() {
  const locale = useLocale();
  return (
    <a
      href="#main"
      className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-[100]
        focus:rw-radius-sm focus:border focus:rw-line focus:rw-chrome focus:px-4 focus:py-2
        focus:text-theme-sm focus:font-medium focus:rw-strong"
    >
      {t(locale, "nav.skipToContent")}
    </a>
  );
}
