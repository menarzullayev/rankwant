"use client";

import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";

import type { CourseProgress } from "../api/courses";

/** Required lessons only: optional ones never hold a course back. */
export function ProgressBar({ progress }: { progress: CourseProgress }) {
  const locale = useLocale();
  const label = fill(t(locale, "course.progress"), { percent: progress.percent });
  return (
    <div className="space-y-1.5">
      <div className="flex items-baseline justify-between gap-3 text-theme-sm">
        <span className="font-medium rw-strong">{label}</span>
        <span className="text-theme-xs rw-dim">
          {fill(t(locale, "course.progressDetail"), {
            done: progress.done,
            total: progress.total,
          })}
        </span>
      </div>
      <div
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={progress.percent}
        aria-label={label}
        className="h-2 overflow-hidden rounded-full rw-chip"
      >
        <div
          className={`h-full rounded-full ${progress.completed ? "bg-[var(--rw-ok-ink)]" : "rw-accent-bg"}`}
          style={{ width: `${progress.percent}%` }}
        />
      </div>
    </div>
  );
}
