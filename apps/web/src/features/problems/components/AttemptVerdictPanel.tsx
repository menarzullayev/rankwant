"use client";

import { useLocale } from "@/i18n/LocaleProvider";
import { fill, type Locale, t } from "@/i18n/messages";
import { Loading } from "@/components/ui/Loading";
import { Verdict } from "@/components/ui/Verdict";
import { isPendingVerdict } from "@/lib/theme/verdict";
import type { AttemptDetail } from "@/lib/api";

/** Prototip CHOICE 16–17 — yuborish natijasi kartasi (barcha rejimlar uchun). */
export function AttemptVerdictPanel({
  attempt,
  pending,
  locale,
  compact = false,
}: {
  attempt: AttemptDetail | null;
  /** Yuborish yoki navbat — hali `attempt` bo‘lmasa ham spinner. */
  pending: boolean;
  locale: Locale;
  compact?: boolean;
}) {
  const runningLabel = (a: AttemptDetail) => {
    if (a.verdict === "RUNNING" && a.running_test_index != null) {
      return fill(t(locale, "submit.runningTest"), { n: a.running_test_index });
    }
    return t(locale, "submit.running");
  };

  if (pending && (!attempt || isPendingVerdict(attempt.verdict))) {
    return (
      <div className="flex items-center justify-center gap-2 py-4 text-theme-sm rw-dim">
        <Loading />
        <span>{attempt ? runningLabel(attempt) : t(locale, "submit.running")}</span>
      </div>
    );
  }

  if (!attempt) {
    return (
      <p className="py-3 text-center text-theme-sm rw-faint">
        {t(locale, "submit.nothingSubmitted")}
      </p>
    );
  }

  if (isPendingVerdict(attempt.verdict)) {
    return (
      <div className="flex items-center justify-center gap-2 py-4 text-theme-sm rw-dim">
        <Loading />
        <span>{runningLabel(attempt)}</span>
      </div>
    );
  }

  return (
    <div className={`space-y-3 ${compact ? "text-theme-sm" : ""}`}>
      <div className="flex flex-wrap items-center gap-3">
        <Verdict verdict={attempt.verdict} />
        <span className="text-theme-sm rw-dim">
          {attempt.time_ms} ms · {Math.round(attempt.memory_kb / 1024)} MB
          {attempt.score > 0 && ` · ${attempt.score} ball`}
        </span>
        {attempt.failed_test_index !== null && (
          <span className="text-theme-sm rw-bad-ink">
            {attempt.failed_test_index}-testda to&apos;xtadi
          </span>
        )}
      </div>

      {attempt.compile_output && (
        <pre tabIndex={0} className="max-h-56 rw-scroll rw-radius-sm rw-field-bg p-3 text-theme-xs rw-dim-2">
          {attempt.compile_output}
        </pre>
      )}

      {attempt.test_results.length > 0 && !compact && (
        <div className="rw-scroll-x">
          <table className="w-full min-w-[20rem] table-fixed text-left text-theme-xs">
            <thead>
              <tr className="border-b rw-divider rw-faint">
                <th className="w-10 py-1.5">#</th>
                <th className="py-1.5">{t(locale, "attempts.verdict")}</th>
                <th className="py-1.5">{t(locale, "attempts.col.runTime")}</th>
              </tr>
            </thead>
            <tbody>
              {attempt.test_results.map((test) => (
                <tr key={test.index} className="border-t rw-divider font-mono">
                  <td className="py-1 tabular-nums">{test.index}</td>
                  <td
                    className={
                      test.verdict === "AC" ? "rw-ok-ink" : "rw-bad-ink"
                    }
                  >
                    {test.verdict}
                  </td>
                  <td className="tabular-nums">{test.time_ms} ms</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
