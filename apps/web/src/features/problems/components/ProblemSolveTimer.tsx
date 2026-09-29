"use client";

import { useEffect, useState } from "react";

import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

function formatElapsed(ms: number) {
  const s = Math.floor(ms / 1000);
  const m = Math.floor(s / 60);
  const h = Math.floor(m / 60);
  if (h > 0)
    return `${h}:${String(m % 60).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;
  return `${m}:${String(s % 60).padStart(2, "0")}`;
}

/** Yechish vaqti + musobaqa teskari sanog'i (prototip timer #6, demo round). */
export function ProblemSolveTimer({ contest }: { contest?: string }) {
  const locale = useLocale();
  const [started] = useState(() => Date.now());
  const [now, setNow] = useState(started);

  useEffect(() => {
    const id = window.setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, []);

  const elapsed = formatElapsed(now - started);
  // Demo: 45 daqiqalik raund qoldig'i (haqiqiy contest API keyinroq)
  const demoRoundMs = 45 * 60 * 1000 - ((now - started) % (45 * 60 * 1000));
  const roundLeft = formatElapsed(demoRoundMs);

  return (
    <div
      className="sticky top-20 z-10 mb-4 flex flex-wrap justify-end gap-2"
      aria-live="polite"
    >
      <span className="inline-flex items-center gap-1.5 rw-radius-full border rw-line rw-panel-bg px-3 py-1.5 text-theme-xs font-medium rw-strong shadow-sm">
        <span aria-hidden>⏱</span>
        <span className="rw-faint">{t(locale, "problem.solveTimer")}</span>
        <span className="font-mono tabular-nums">{elapsed}</span>
      </span>
      {contest && (
        <span className="inline-flex items-center gap-1.5 rw-radius-full border rw-line rw-panel-bg px-3 py-1.5 text-theme-xs font-medium rw-strong shadow-sm">
          <span aria-hidden>⏳</span>
          <span className="rw-faint">{t(locale, "problem.roundTimer")}</span>
          <span className="font-mono tabular-nums">{roundLeft}</span>
        </span>
      )}
    </div>
  );
}
