"use client";

import type { Route } from "next";
import { useState } from "react";

import { IntentLink } from "@/components/ui/IntentLink";

export type NewsSlide = {
  slug: string;
  title: string;
  summary: string;
  /** Already formatted on the server, in the reader's locale. */
  date: string;
  cover: string;
};

const ARROW =
  "flex size-11 items-center justify-center rounded-full border rw-line rw-strong rw-hover-bg";

/** One post at a time, with previous / next.
 *
 *  It does not advance on its own: text that moves while somebody reads it
 *  is a WCAG 2.2.2 failure unless it can be paused, and a control that only
 *  exists to stop the page from moving is worse than not moving. */
export function NewsCarousel({
  slides,
  labels,
}: {
  slides: NewsSlide[];
  labels: { read: string; previous: string; next: string };
}) {
  const [index, setIndex] = useState(0);
  const slide = slides[index] ?? slides[0];
  if (!slide) return null;
  const step = (delta: number) => setIndex((i) => (i + delta + slides.length) % slides.length);

  return (
    <div className="space-y-4">
      <div
        className={`grid items-center gap-5 ${slide.cover ? "sm:grid-cols-2" : ""}`}
        aria-live="polite"
      >
        <div className="min-w-0">
          <p className="text-theme-xs rw-faint">{slide.date}</p>
          <p className="mt-1 text-theme-xl font-bold rw-strong">{slide.title}</p>
          {slide.summary && (
            <p className="mt-2 line-clamp-3 text-theme-sm rw-dim">{slide.summary}</p>
          )}
          <IntentLink
            href={`/blog/${slide.slug}` as Route}
            className="mt-3 inline-block text-theme-sm rw-accent-ink hover:underline"
          >
            {labels.read}
          </IntentLink>
        </div>
        {slide.cover && (
          // eslint-disable-next-line @next/next/no-img-element -- a staff-supplied URL on any host; the optimizer would need every host allow-listed
          <img
            src={slide.cover}
            alt=""
            loading="lazy"
            className="h-44 w-full rw-radius-sm object-cover"
          />
        )}
      </div>

      {slides.length > 1 && (
        <div className="flex items-center justify-between gap-3">
          <div className="flex gap-2" aria-hidden="true">
            {slides.map((s, i) => (
              <span
                key={s.slug}
                className={`h-1.5 rounded-full ${i === index ? "w-6 rw-accent-bg" : "w-1.5 rw-accent-soft"}`}
              />
            ))}
          </div>
          <div className="flex gap-2">
            <button type="button" className={ARROW} aria-label={labels.previous} onClick={() => step(-1)}>
              <span aria-hidden="true">‹</span>
            </button>
            <button type="button" className={ARROW} aria-label={labels.next} onClick={() => step(1)}>
              <span aria-hidden="true">›</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
