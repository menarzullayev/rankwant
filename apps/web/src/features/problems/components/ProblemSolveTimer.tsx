"use client";

import { useEffect, useState } from "react";

import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";

/** Stopwatch and timer beside the statement (decision 2026-11-11 ①).
 *
 *  - The stopwatch counts the time on this problem; pause, resume, reset. It
 *    lives in the tab's session per problem, so a reload does not lose it.
 *  - The timer counts down from minutes the reader picks and says when the
 *    time is up.
 *  - In a running contest, the real time left until the contest ends (it
 *    replaced a 45-minute demo countdown that had no contest behind it).
 */

type Watch = { since: number | null; kept: number };

const PRESETS = [15, 30, 45, 60] as const;
const CHIP =
  "inline-flex min-h-9 items-center gap-1.5 rw-radius-full border rw-line rw-panel-bg px-3 text-theme-xs font-medium rw-strong shadow-sm";
const BUTTON =
  "min-h-8 [@media(pointer:coarse)]:min-h-11 rw-radius-sm px-2 text-theme-xs font-medium rw-dim rw-hover-bg rw-focus-ring";

export function formatElapsed(ms: number): string {
  const s = Math.max(0, Math.floor(ms / 1000));
  const m = Math.floor(s / 60);
  const h = Math.floor(m / 60);
  if (h > 0) return `${h}:${String(m % 60).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;
  return `${m}:${String(s % 60).padStart(2, "0")}`;
}

function readWatch(key: string): Watch {
  try {
    const raw = window.sessionStorage.getItem(key);
    if (raw) return JSON.parse(raw) as Watch;
  } catch {
    // Storage may be off (private mode): the watch simply starts afresh.
  }
  return { since: Date.now(), kept: 0 };
}

function writeWatch(key: string, watch: Watch) {
  try {
    window.sessionStorage.setItem(key, JSON.stringify(watch));
  } catch {
    // Nothing to keep it in; the watch still runs for this page.
  }
}

export function ProblemSolveTimer({ slug, contestEndsAt }: { slug: string; contestEndsAt?: string }) {
  const locale = useLocale();
  const key = `rw:stopwatch:${slug}`;
  const [watch, setWatch] = useState<Watch | null>(null);
  const [now, setNow] = useState(() => Date.now());
  const [deadline, setDeadline] = useState<number | null>(null);
  const [picking, setPicking] = useState(false);

  // The stored watch is read after mount: the server has no session storage.
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- one read of browser storage after mount
    setWatch(readWatch(key));
  }, [key]);

  useEffect(() => {
    const id = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(id);
  }, []);

  // `now` ticks once a second, so a press reads the clock itself: pausing on
  // the stale tick would drop up to a second, resuming would step back one.
  const update = (next: Watch) => {
    setWatch(next);
    setNow(Date.now());
    writeWatch(key, next);
  };
  const toggle = () => {
    if (!watch) return;
    const at = Date.now();
    update(watch.since !== null ? { since: null, kept: watch.kept + (at - watch.since) } : { since: at, kept: watch.kept });
  };

  const elapsed = watch ? watch.kept + (watch.since !== null ? now - watch.since : 0) : 0;
  const running = watch?.since !== null && watch !== null;
  const left = deadline !== null ? deadline - now : null;
  const contestLeft = contestEndsAt ? new Date(contestEndsAt).getTime() - now : null;

  return (
    <div className="sticky top-20 z-10 mb-4 flex flex-wrap justify-end gap-2">
      <span className={CHIP}>
        <span aria-hidden>⏱</span>
        <span className="rw-faint">{t(locale, "problem.solveTimer")}</span>
        <span className="font-mono tabular-nums">{formatElapsed(elapsed)}</span>
        <button type="button" className={BUTTON} onClick={toggle}>
          {t(locale, running ? "timer.pause" : "timer.resume")}
        </button>
        <button type="button" className={BUTTON} onClick={() => update({ since: Date.now(), kept: 0 })}>
          {t(locale, "timer.reset")}
        </button>
      </span>

      {left === null ? (
        <span className={CHIP}>
          <span aria-hidden>⏳</span>
          {picking ? (
            <span className="flex flex-wrap items-center gap-1" role="group" aria-label={t(locale, "timer.set")}>
              {PRESETS.map((minutes) => (
                <button
                  key={minutes}
                  type="button"
                  className={BUTTON}
                  onClick={() => {
                    const at = Date.now();
                    setNow(at);
                    setDeadline(at + minutes * 60_000);
                    setPicking(false);
                  }}
                >
                  {fill(t(locale, "timer.minutes"), { count: minutes })}
                </button>
              ))}
            </span>
          ) : (
            <button type="button" className={BUTTON} onClick={() => setPicking(true)}>
              {t(locale, "timer.set")}
            </button>
          )}
        </span>
      ) : (
        <span className={CHIP} role="timer">
          <span aria-hidden>⏳</span>
          {left > 0 ? (
            <span className="font-mono tabular-nums">{formatElapsed(left)}</span>
          ) : (
            <span role="alert" className="rw-bad-ink">
              {t(locale, "timer.done")}
            </span>
          )}
          <button type="button" className={BUTTON} onClick={() => setDeadline(null)}>
            {t(locale, "timer.stop")}
          </button>
        </span>
      )}

      {contestLeft !== null && contestLeft > 0 && (
        <span className={CHIP}>
          <span className="rw-faint">{t(locale, "problem.roundTimer")}</span>
          <span className="font-mono tabular-nums">{formatElapsed(contestLeft)}</span>
        </span>
      )}
    </div>
  );
}
