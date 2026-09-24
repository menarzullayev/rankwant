"use client";

import { useState } from "react";

import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

const SIZES = [14, 16, 18, 20] as const;
const DEFAULT_SIZE = 16;

/** Masala matni uzoq o'qiladi va ekranlar har xil — RoboContest ham
 * shrift kattaligini beradi. Faqat shu qurilmada, qoralamalar kabi. */
export function StatementSize({ children }: { children: React.ReactNode }) {
  const locale = useLocale();
  const [size, setSize] = useState<number>(() => {
    try {
      const saved = Number(localStorage.getItem("rw:statement-size"));
      return SIZES.includes(saved as (typeof SIZES)[number])
        ? saved
        : DEFAULT_SIZE;
    } catch {
      return DEFAULT_SIZE;
    }
  });

  function pick(next: number) {
    setSize(next);
    try {
      localStorage.setItem("rw:statement-size", String(next));
    } catch {
      // Private rejim — o'lcham sessiya davomida ishlaydi.
    }
  }

  const index = SIZES.indexOf(size as (typeof SIZES)[number]);
  const button =
    "size-7 rw-radius-sm text-theme-sm font-medium rw-dim transition rw-hover-bg disabled:opacity-40";

  return (
    <div>
      <div className="mb-2 flex items-center justify-end gap-1">
        <button
          type="button"
          aria-label={t(locale, "problem.statementSizeDown")}
          onClick={() => pick(SIZES[index - 1])}
          disabled={index <= 0}
          className={button}
        >
          A−
        </button>
        <span className="w-10 text-center text-theme-xs rw-faint">
          {size}px
        </span>
        <button
          type="button"
          aria-label={t(locale, "problem.statementSizeUp")}
          onClick={() => pick(SIZES[index + 1])}
          disabled={index < 0 || index >= SIZES.length - 1}
          className={button}
        >
          A+
        </button>
      </div>
      <div style={{ fontSize: `${size}px` }}>{children}</div>
    </div>
  );
}
