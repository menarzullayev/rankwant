"use client";

import { useCallback, useEffect, useRef, useState, useSyncExternalStore, type ReactNode } from "react";

/** How long each slide stays (ms). Long enough to read a headline and a
 *  line of copy; the dots and the arrows move it on at once. */
const SLIDE_MS = 8000;

/** `aria-live` values: silent while the carousel plays itself. */
const QUIET = "off";
const POLITE = "polite";

/** `matchMedia` / `visibilitychange` as external stores: the server render
 *  assumes "motion allowed, tab visible" and the client corrects it without
 *  a state-setting effect. */
function useReducedMotion(): boolean {
  return useSyncExternalStore(
    (notify) => {
      const query = window.matchMedia("(prefers-reduced-motion: reduce)");
      query.addEventListener("change", notify);
      return () => query.removeEventListener("change", notify);
    },
    () => window.matchMedia("(prefers-reduced-motion: reduce)").matches,
    () => false,
  );
}

function useTabHidden(): boolean {
  return useSyncExternalStore(
    (notify) => {
      document.addEventListener("visibilitychange", notify);
      return () => document.removeEventListener("visibilitychange", notify);
    },
    () => document.hidden,
    () => false,
  );
}

export type CarouselLabels = {
  region: string;
  prev: string;
  next: string;
  pause: string;
  play: string;
  /** `{n}` is the 1-based slide number. */
  go: string;
};

/** Ten slides, one at a time (HITL 2026-10-25).
 *
 *  The slides arrive as server-rendered children, so this component holds
 *  only the position and the timer. All of them are in the document; the
 *  inactive ones are `inert` and `aria-hidden`, so a screen reader and the
 *  Tab key meet one slide at a time.
 *
 *  Auto-advance follows the usual carousel rules (WCAG 2.2.2): it never
 *  starts under `prefers-reduced-motion`, a pause button is always there,
 *  and it stops while the pointer or focus is inside and while the tab is
 *  hidden. The live region is silent while it plays itself and polite once
 *  the visitor moves it by hand. */
export function AuthCarousel({
  slides,
  labels,
}: {
  slides: ReactNode[];
  labels: CarouselLabels;
}) {
  const [index, setIndex] = useState(0);
  // `null` = the visitor has not touched the button: follow the system.
  const [manual, setManual] = useState<boolean | null>(null);
  const [held, setHeld] = useState(false);
  const reduced = useReducedMotion();
  const hidden = useTabHidden();
  const playing = manual ?? !reduced;
  const root = useRef<HTMLDivElement>(null);
  const count = slides.length;

  const go = useCallback(
    (to: number) => setIndex(((to % count) + count) % count),
    [count],
  );

  useEffect(() => {
    if (!playing || held || hidden) return;
    const timer = setTimeout(() => go(index + 1), SLIDE_MS);
    return () => clearTimeout(timer);
  }, [playing, held, hidden, index, go]);

  return (
    <div
      ref={root}
      className="ap-carousel"
      role="region"
      aria-roledescription="carousel"
      aria-label={labels.region}
      onMouseEnter={() => setHeld(true)}
      onMouseLeave={() => setHeld(false)}
      onFocus={() => setHeld(true)}
      onBlur={(event) => {
        if (!root.current?.contains(event.relatedTarget)) setHeld(false);
      }}
      onKeyDown={(event) => {
        if (event.key === "ArrowRight") go(index + 1);
        else if (event.key === "ArrowLeft") go(index - 1);
      }}
    >
      <div className="ap-stage" aria-live={playing && !held ? QUIET : POLITE}>
        {slides.map((slide, i) => (
          <div
            // The slides never reorder.
            key={i}
            className={`ap-slide ap-s${i + 1}${i === index ? " is-active" : ""}`}
            role="group"
            aria-roledescription="slide"
            aria-hidden={i === index ? undefined : true}
            inert={i === index ? undefined : true}
          >
            {slide}
          </div>
        ))}
      </div>
      <div className="ap-controls">
        <button type="button" className="ap-btn" aria-label={labels.prev} onClick={() => go(index - 1)}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M15 18l-6-6 6-6" />
          </svg>
        </button>
        <div className="ap-dots">
          {slides.map((_, i) => (
            <button
              key={i}
              type="button"
              className="ap-dot"
              aria-label={labels.go.replace("{n}", String(i + 1))}
              aria-current={i === index ? "true" : undefined}
              onClick={() => go(i)}
            />
          ))}
        </div>
        <button
          type="button"
          className="ap-btn"
          aria-label={playing ? labels.pause : labels.play}
          aria-pressed={!playing}
          onClick={() => setManual(!playing)}
        >
          {playing ? (
            <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <rect x="6" y="5" width="4" height="14" rx="1" />
              <rect x="14" y="5" width="4" height="14" rx="1" />
            </svg>
          ) : (
            <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M8 5.5v13a1 1 0 0 0 1.5.86l10.5-6.5a1 1 0 0 0 0-1.72L9.5 4.64A1 1 0 0 0 8 5.5z" />
            </svg>
          )}
        </button>
        <button type="button" className="ap-btn" aria-label={labels.next} onClick={() => go(index + 1)}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M9 18l6-6-6-6" />
          </svg>
        </button>
      </div>
    </div>
  );
}
