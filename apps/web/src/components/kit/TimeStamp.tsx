"use client";

import { useEffect, useState } from "react";

import { fill, t, type Locale } from "@/i18n/messages";
import {
  formatDate,
  formatDuration,
  formatRelative,
  isoDay,
  type DateKit,
} from "@/lib/format";
import type { TimeTone } from "@/lib/theme/kit";

const HOUR = 3600_000;
const DAY = 86_400_000;

export function dayBucket(
  value: string | Date,
  now = Date.now(),
): "today" | "yesterday" | "other" {
  const stamp = isoDay(value);
  const today = isoDay(new Date(now));
  if (stamp === today) return "today";
  const yest = isoDay(new Date(now - DAY));
  if (stamp === yest) return "yesterday";
  return "other";
}

export function freshnessOf(
  value: string | Date,
  now = Date.now(),
): "fresh" | "warm" | "stale" {
  const age = now - new Date(value).getTime();
  if (age < 6 * HOUR) return "fresh";
  if (age < 2 * DAY) return "warm";
  return "stale";
}

export function formatIsoStamp(value: string | Date): string {
  return new Date(value).toISOString().replace(/\.\d{3}Z$/, "Z");
}

export function TimeStamp({
  value,
  locale,
  tone = "relative",
  durationMin,
}: {
  value: string | Date;
  locale: Locale;
  tone?: Exclude<TimeTone, "countdown" | "timeline" | "cal">;
  durationMin?: number;
}) {
  const iso = new Date(value).toISOString();
  const exact = formatDate(value, locale, {
    dateStyle: "medium",
    timeStyle: "short",
  });
  const rel = formatRelative(value, locale);
  const bucket = dayBucket(value);
  const fresh = freshnessOf(value);

  if (tone === "duration") {
    return (
      <time dateTime={iso} className="rw-kit-time" data-kit-time="duration">
        {formatDuration(durationMin ?? 0)}
      </time>
    );
  }

  if (tone === "iso") {
    return (
      <time
        dateTime={iso}
        className="rw-kit-time"
        data-kit-time="iso"
        data-tip={exact}
        data-tip-kind="balloon"
      >
        {formatIsoStamp(value)}
      </time>
    );
  }

  if (tone === "badge") {
    const label =
      bucket === "today"
        ? t(locale, "kit.today")
        : bucket === "yesterday"
          ? t(locale, "kit.yesterday")
          : exact;
    return (
      <time dateTime={iso} className="rw-kit-time" data-kit-time="badge">
        <span className={bucket === "other" ? undefined : "rw-kit-badge"}>
          {label}
        </span>
      </time>
    );
  }

  if (tone === "dual") {
    return (
      <time
        dateTime={iso}
        className="rw-kit-time"
        data-kit-time="dual"
        data-tip={formatIsoStamp(value)}
        data-tip-kind="soft"
      >
        <span>{rel}</span>
        <span className="abs">{exact}</span>
      </time>
    );
  }

  if (tone === "fresh") {
    return (
      <time
        dateTime={iso}
        className="rw-kit-time"
        data-kit-time="fresh"
        data-fresh={fresh}
        data-tip={exact}
        data-tip-kind="theme"
      >
        {rel}
      </time>
    );
  }

  if (tone === "locale") {
    return (
      <time
        dateTime={iso}
        className="rw-kit-time"
        data-kit-time="locale"
        data-tip={formatIsoStamp(value)}
        data-tip-kind="rich"
        data-tip-title={t(locale, "kit.iso")}
      >
        {exact}
      </time>
    );
  }

  return (
    <time
      dateTime={iso}
      className="rw-kit-time"
      data-kit-time="relative"
      data-tip={exact}
      data-tip-kind="balloon"
    >
      {rel}
    </time>
  );
}

export function TimeLine({
  locale,
  events,
}: {
  locale: Locale;
  events: { at: string; label: string }[];
}) {
  return (
    <ol className="rw-kit-tl">
      {events.map((event) => (
        <li key={`${event.at}-${event.label}`}>
          <TimeStamp value={event.at} locale={locale} tone="dual" />
          <p className="text-theme-sm rw-strong">{event.label}</p>
        </li>
      ))}
    </ol>
  );
}

export function Countdown({
  until,
  locale,
}: {
  until: string | Date;
  locale: Locale;
}) {
  const target = new Date(until).getTime();
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    const id = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(id);
  }, []);

  const left = Math.max(0, target - now);
  const sec = Math.floor(left / 1000);
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = sec % 60;
  const clock = `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;

  return (
    <time
      dateTime={new Date(until).toISOString()}
      className="rw-kit-time font-mono tabular-nums"
      data-kit-time="countdown"
      data-tip={formatDate(until, locale, { dateStyle: "medium", timeStyle: "short" })}
      data-tip-kind="kbd"
      data-tip-kbd={clock}
    >
      {fill(t(locale, "kit.left"), { time: clock })}
    </time>
  );
}

export function MiniCal({
  iso,
  kit,
  label,
}: {
  iso: string;
  kit: DateKit;
  label: string;
}) {
  const [y, m, d] = iso.split("-").map(Number);
  const first = new Date(Date.UTC(y, m - 1, 1));
  const lead = (first.getUTCDay() + 6) % 7;
  const days = new Date(Date.UTC(y, m, 0)).getUTCDate();

  return (
    <div className="rw-kit-cal" data-tip-kind="soft">
      <p className="mb-1 text-theme-xs rw-strong">
        {kit.months[m - 1]} {y}
      </p>
      <div className="rw-kit-cal-grid">
        {kit.weekdays.map((wd) => (
          <b key={wd}>{wd.slice(0, 2)}</b>
        ))}
        {Array.from({ length: lead }, (_, i) => (
          <span key={`e${i}`} />
        ))}
        {Array.from({ length: days }, (_, i) => {
          const day = i + 1;
          return (
            <span key={day} className={day === d ? "is-on" : undefined}>
              {day}
            </span>
          );
        })}
      </div>
      <p className="mt-1 rw-dim">{label}</p>
    </div>
  );
}
