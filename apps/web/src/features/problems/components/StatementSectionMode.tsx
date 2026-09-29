"use client";

import { useSyncExternalStore } from "react";

import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

export type StatementSectionMode = "space" | "line" | "card";

const KEY = "rw:statement-sec";
const MODES: StatementSectionMode[] = ["space", "line", "card"];

const LABEL: Record<StatementSectionMode, "problem.sectionMode.space" | "problem.sectionMode.line" | "problem.sectionMode.card"> = {
  space: "problem.sectionMode.space",
  line: "problem.sectionMode.line",
  card: "problem.sectionMode.card",
};

function readMode(): StatementSectionMode {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw === "line" || raw === "card" || raw === "space") return raw;
  } catch {
    // private mode
  }
  return "space";
}

function writeMode(mode: StatementSectionMode) {
  try {
    localStorage.setItem(KEY, mode);
  } catch {
    // ignore
  }
}

let listeners = new Set<() => void>();

function subscribe(callback: () => void) {
  listeners.add(callback);
  return () => listeners.delete(callback);
}

function emit() {
  listeners.forEach((l) => l());
}

export function useStatementSectionMode(): [
  StatementSectionMode,
  (mode: StatementSectionMode) => void,
] {
  const mode = useSyncExternalStore(subscribe, readMode, () => "space" as StatementSectionMode);
  const setMode = (next: StatementSectionMode) => {
    writeMode(next);
    emit();
  };
  return [mode, setMode];
}

/** Prototip CHOICE 11 — bo‘limlar orasidagi ajratish rejimi. */
export function StatementSectionModeToggle() {
  const locale = useLocale();
  const [mode, setMode] = useStatementSectionMode();

  return (
    <span
      role="group"
      aria-label={t(locale, "problem.sectionMode.label")}
      className="inline-flex gap-0.5 rw-radius-sm border rw-divider rw-panel-2 p-0.5"
    >
      {MODES.map((m) => (
        <button
          key={m}
          type="button"
          aria-pressed={mode === m}
          onClick={() => setMode(m)}
          className={`min-h-[26px] rw-radius-sm px-2.5 text-theme-xs font-semibold transition rw-focus-ring ${
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

/** Matn kartasiga `data-sec` qo‘yadi — CSS ajratish rejimlari uchun. */
export function StatementSectionBody({
  mode,
  children,
  className = "",
}: {
  mode: StatementSectionMode;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      data-sec={mode}
      className={`problem-statement-body ${className}`}
    >
      {children}
    </div>
  );
}
