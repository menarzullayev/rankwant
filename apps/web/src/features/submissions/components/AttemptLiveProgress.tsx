"use client";

import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import { Loading } from "@/components/ui/Loading";
import { Verdict } from "@/components/ui/Verdict";
import type { AttemptLiveState } from "@/features/submissions/attemptLiveState";
import { completedTestCount } from "@/features/submissions/attemptLiveState";
import { isPendingVerdict } from "@/lib/theme/verdict";

/** Jonli testlar ro'yxati — prototipdagi karta (maxfiy I/O yo'q). */
export function AttemptLiveProgress({
  attemptId,
  state,
  compact = false,
}: {
  attemptId: number;
  state: AttemptLiveState;
  compact?: boolean;
}) {
  const locale = useLocale();
  const pending = state.verdict ? isPendingVerdict(state.verdict) : true;
  const total = state.totalTests;
  const done = completedTestCount(state);
  const indices = Object.keys(state.tests)
    .map(Number)
    .sort((a, b) => a - b);

  if (!pending && indices.length === 0) return null;

  const phaseLabel =
    state.phase === "compiling"
      ? t(locale, "submit.compiling")
      : state.runningIndex != null
        ? fill(t(locale, "submit.runningTest"), { n: state.runningIndex })
        : t(locale, "submit.running");

  return (
    <div
      className={`rw-radius-md rw-field-bg border rw-border space-y-2 ${compact ? "p-2 text-theme-xs" : "p-3 text-theme-sm"}`}
      aria-live="polite"
    >
      <div className="flex flex-wrap items-center gap-2">
        <span className="font-mono rw-dim-2">#{attemptId}</span>
        {state.verdict && <Verdict verdict={state.verdict} />}
        {pending && (
          <span className="inline-flex items-center gap-1 rw-dim">
            <Loading className="scale-75" />
            {phaseLabel}
          </span>
        )}
        {total != null && total > 0 && (
          <span className="rw-faint text-theme-xs">
            {fill(t(locale, "attempts.liveTestsProgress"), { done, total })}
          </span>
        )}
      </div>
      {indices.length > 0 && (
        <ul className={`grid gap-1 ${compact ? "max-h-32 overflow-y-auto" : "max-h-48 overflow-y-auto"}`}>
          {indices.map((index) => {
            const row = state.tests[index];
            return (
              <li
                key={index}
                className="flex items-center justify-between gap-2 rw-radius-sm px-2 py-0.5 rw-hover-bg"
              >
                <span className="rw-dim-2">
                  {fill(t(locale, "attempts.liveTestLabel"), { index })}
                </span>
                <span className="inline-flex items-center gap-2">
                  {row.status === "running" && row.verdict === "RUNNING" ? (
                    <span className="rw-dim text-theme-xs">{t(locale, "submit.running")}</span>
                  ) : (
                    <Verdict verdict={row.verdict} />
                  )}
                  {row.time_ms != null && row.status === "done" && (
                    <span className="rw-faint tabular-nums text-theme-xs">{row.time_ms} ms</span>
                  )}
                </span>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
