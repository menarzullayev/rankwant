"use client";

import { useSyncExternalStore } from "react";

import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

const SIZES = [14, 16, 18, 20] as const;
const DEFAULT_SIZE = 16;
const SIZE_KEY = "rw:statement-size";

const sizeListeners = new Set<() => void>();

function readSize(): number {
  try {
    const saved = Number(localStorage.getItem(SIZE_KEY));
    if (SIZES.includes(saved as (typeof SIZES)[number])) return saved;
  } catch {
    // private mode
  }
  return DEFAULT_SIZE;
}

function subscribeSize(callback: () => void) {
  sizeListeners.add(callback);
  return () => sizeListeners.delete(callback);
}

function writeSize(next: number) {
  try {
    localStorage.setItem(SIZE_KEY, String(next));
  } catch {
    // ignore
  }
  sizeListeners.forEach((l) => l());
}

function useStatementSizePx(): [number, (next: number) => void] {
  const size = useSyncExternalStore(subscribeSize, readSize, () => DEFAULT_SIZE);
  return [size, writeSize];
}

/** Prototip sarlavha qatoridagi A± boshqaruvi. */
export function StatementTextSizeControls() {
  const locale = useLocale();
  const [size, pick] = useStatementSizePx();

  const index = SIZES.indexOf(size as (typeof SIZES)[number]);
  const button =
    "size-8 min-w-8 rw-radius-sm text-theme-sm font-medium rw-dim transition rw-hover-bg disabled:opacity-40 rw-focus-ring";

  return (
    <span
      className="inline-flex items-center gap-1"
      title={t(locale, "problem.statementSizeHint")}
    >
      <span className="text-theme-2xs rw-faint tracking-wide">
        {t(locale, "problem.statementSizeLabel")}
      </span>
      <button
        type="button"
        aria-label={t(locale, "problem.statementSizeDown")}
        onClick={() => pick(SIZES[index - 1])}
        disabled={index <= 0}
        className={button}
      >
        A−
      </button>
      <span className="w-9 text-center text-theme-xs rw-faint tabular-nums">
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
    </span>
  );
}

/** Masala matni uzoq o'qiladi va ekranlar har xil — RoboContest ham
 * shrift kattaligini beradi. Faqat shu qurilmada, qoralamalar kabi. */
export function StatementSize({ children }: { children: React.ReactNode }) {
  const [size] = useStatementSizePx();

  return (
    <div style={{ fontSize: `${size}px` }} className="problem-statement-measure rw-md">
      {children}
    </div>
  );
}
