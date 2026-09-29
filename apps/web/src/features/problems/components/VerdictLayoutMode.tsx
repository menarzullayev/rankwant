"use client";

import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

import {
  useVerdictLayoutMode,
  type VerdictLayoutMode,
} from "./problem-solve-context";

const MODES: VerdictLayoutMode[] = ["tab", "column", "toast", "modal"];

const LABEL: Record<
  VerdictLayoutMode,
  | "problem.verdictLayout.tab"
  | "problem.verdictLayout.column"
  | "problem.verdictLayout.toast"
  | "problem.verdictLayout.modal"
> = {
  tab: "problem.verdictLayout.tab",
  column: "problem.verdictLayout.column",
  toast: "problem.verdictLayout.toast",
  modal: "problem.verdictLayout.modal",
};

/** Prototip CHOICE 15 — natija qayerda ko‘rinsin. */
export function VerdictLayoutModeToggle() {
  const locale = useLocale();
  const [mode, setMode] = useVerdictLayoutMode();

  return (
    <span
      role="group"
      aria-label={t(locale, "problem.verdictLayout.label")}
      className="inline-flex gap-0.5 rw-radius-sm border rw-divider rw-panel-2 p-0.5"
    >
      {MODES.map((m) => (
        <button
          key={m}
          type="button"
          aria-pressed={mode === m}
          title={t(locale, LABEL[m])}
          onClick={() => setMode(m)}
          className={`min-h-[24px] rw-radius-sm px-2 text-theme-2xs font-semibold transition rw-focus-ring ${
            mode === m
              ? "rw-panel-bg rw-accent-ink shadow-sm"
              : "rw-faint rw-hover-bg"
          }`}
        >
          {t(locale, LABEL[m])}
        </button>
      ))}
    </span>
  );
}
