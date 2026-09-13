"use client";

import { useMemo, useState } from "react";

import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import type { RatingPoint, RatingSeries } from "@/lib/api";
import { formatDay, type DateKit } from "@/lib/format";

const KINDS = ["contest", "skills", "activity", "challenges"] as const;
type Kind = (typeof KINDS)[number];
const KIND_LABEL: Record<Kind, string> = {
  contest: "leaderboard.contest",
  skills: "leaderboard.skills",
  activity: "leaderboard.activity",
  challenges: "leaderboard.challenges",
};

const W = 720;
const H = 260;
const PAD = { left: 48, right: 16, top: 12, bottom: 28 };

function niceTicks(lo: number, hi: number): number[] {
  const step = [50, 100, 200, 250, 500, 1000].find((s) => (hi - lo) / s <= 6) ?? 2000;
  const out: number[] = [];
  for (let v = Math.ceil(lo / step) * step; v <= hi; v += step) out.push(v);
  return out;
}

function build(points: RatingPoint[]) {
  if (points.length === 0) return null;
  const times = points.map((p) => new Date(p.at).getTime());
  const values = points.flatMap((p) => [p.before, p.after]);
  const spread = Math.max(...values) - Math.min(...values);
  const pad = Math.max(50, spread * 0.1);
  const lo = Math.max(0, Math.min(...values) - pad);
  const hi = Math.max(...values) + pad;
  const t0 = Math.min(...times);
  const span = Math.max(...times) - t0 || 1;
  const x = (time: number) =>
    points.length === 1 ? W / 2 : PAD.left + ((time - t0) / span) * (W - PAD.left - PAD.right);
  const y = (value: number) => PAD.top + (1 - (value - lo) / (hi - lo)) * (H - PAD.top - PAD.bottom);
  return { lo, hi, x, y, coords: points.map((p, i) => ({ x: x(times[i]), y: y(p.after) })) };
}

/** Reyting tarixi — SVG, kutubxonasiz (CSP va to'plam hajmi). Contests
 *  grafigida unvon chegaralari rangli bant bo'lib chiziladi. */
export function RatingChart({ data, kit }: { data: RatingSeries; kit: DateKit }) {
  const locale = useLocale();
  const available = KINDS.filter((kind) => (data.series[kind] ?? []).length > 0);
  const [kind, setKind] = useState<Kind>(
    available.includes("contest") ? "contest" : (available[0] ?? "contest"),
  );
  const [active, setActive] = useState<number | null>(null);
  const points = useMemo(() => data.series[kind] ?? [], [data, kind]);
  const model = useMemo(() => build(points), [points]);

  if (available.length === 0 || !model) {
    return <p className="text-theme-sm rw-faint">{t(locale, "profile.chartEmpty")}</p>;
  }
  const current = active === null ? null : points[active];
  const spot = active === null ? null : model.coords[active];
  const date = (value: string) => formatDay(kit, value);
  const describe = (p: RatingPoint) =>
    `${date(p.at)} · ${p.title || t(locale, `profile.reason.${p.reason}`)}${
      p.rank ? ` · #${p.rank}` : ""
    } · ${p.before} → ${p.after} (${p.delta > 0 ? "+" : ""}${p.delta})`;

  const nearest = (event: React.PointerEvent<SVGSVGElement>) => {
    const box = event.currentTarget.getBoundingClientRect();
    const px = ((event.clientX - box.left) / box.width) * W;
    let best = 0;
    model.coords.forEach((c, i) => {
      if (Math.abs(c.x - px) < Math.abs(model.coords[best].x - px)) best = i;
    });
    setActive(best);
  };

  const onKey = (event: React.KeyboardEvent<HTMLDivElement>) => {
    if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
    event.preventDefault();
    const step = event.key === "ArrowRight" ? 1 : -1;
    setActive((i) => Math.min(points.length - 1, Math.max(0, (i ?? points.length - 1) + step)));
  };

  const path = model.coords.map((c, i) => `${i ? "L" : "M"}${c.x.toFixed(1)},${c.y.toFixed(1)}`).join(" ");

  return (
    <div className="space-y-3">
      {available.length > 1 && (
        <div role="tablist" aria-label={t(locale, "profile.history")} className="flex flex-wrap gap-1.5">
          {available.map((option) => (
            <button
              key={option}
              type="button"
              role="tab"
              aria-selected={kind === option}
              onClick={() => {
                setKind(option);
                setActive(null);
              }}
              className={`rw-radius-sm px-3 py-1.5 text-theme-xs font-medium transition rw-focus-ring ${
                kind === option ? "rw-accent-soft rw-accent-ink" : "rw-dim rw-hover-bg"
              }`}
            >
              {t(locale, KIND_LABEL[option])}
            </button>
          ))}
        </div>
      )}
      <div
        className="relative"
        tabIndex={0}
        onKeyDown={onKey}
        aria-label={t(locale, "profile.chartKeys")}
      >
        <svg
          viewBox={`0 0 ${W} ${H}`}
          className="h-auto w-full select-none"
          onPointerMove={nearest}
          onPointerLeave={() => setActive(null)}
          role="img"
          aria-label={t(locale, "profile.history")}
        >
          {kind === "contest" &&
            data.bands.map((band) => {
              const top = Math.min(band.max ?? model.hi, model.hi);
              const bottom = Math.max(band.min, model.lo);
              if (top <= bottom) return null;
              const y1 = model.y(top);
              const y2 = model.y(bottom);
              return (
                <g key={band.code}>
                  <rect
                    x={PAD.left}
                    y={y1}
                    width={W - PAD.left - PAD.right}
                    height={y2 - y1}
                    className={`rw-band-${band.level}`}
                  />
                  {y2 - y1 > 14 && (
                    <text x={PAD.left + 6} y={y1 + 12} className="fill-[var(--rw-muted)] text-[10px]">
                      {t(locale, `title.${band.code}`)}
                    </text>
                  )}
                </g>
              );
            })}
          {niceTicks(model.lo, model.hi).map((tick) => (
            <g key={tick}>
              <line
                x1={PAD.left}
                x2={W - PAD.right}
                y1={model.y(tick)}
                y2={model.y(tick)}
                stroke="var(--rw-divider)"
                strokeDasharray="2 4"
              />
              <text
                x={PAD.left - 6}
                y={model.y(tick) + 3}
                textAnchor="end"
                className="fill-[var(--rw-faint)] text-[10px] tabular-nums"
              >
                {tick}
              </text>
            </g>
          ))}
          <text x={PAD.left} y={H - 8} className="fill-[var(--rw-faint)] text-[10px]">
            {date(points[0].at)}
          </text>
          <text x={W - PAD.right} y={H - 8} textAnchor="end" className="fill-[var(--rw-faint)] text-[10px]">
            {date(points[points.length - 1].at)}
          </text>
          <path d={path} fill="none" stroke="var(--rw-accent-ink)" strokeWidth="2" strokeLinejoin="round" />
          {model.coords.map((c, i) => (
            <circle
              key={i}
              cx={c.x}
              cy={c.y}
              r={i === active ? 5 : 3}
              fill="var(--rw-surface)"
              stroke="var(--rw-accent-ink)"
              strokeWidth="2"
            />
          ))}
        </svg>
        {current && spot && (
          <div
            className="pointer-events-none absolute z-10 w-max max-w-64 -translate-x-1/2 -translate-y-full rw-radius-sm border rw-line rw-surface px-3 py-2 text-theme-xs rw-shadow"
            style={{ left: `${(spot.x / W) * 100}%`, top: `calc(${(spot.y / H) * 100}% - 8px)` }}
          >
            <p className="font-medium rw-strong">{date(current.at)}</p>
            <p className="rw-dim">
              {current.title || t(locale, `profile.reason.${current.reason}`)}
              {current.rank ? ` · #${current.rank}` : ""}
            </p>
            <p className="tabular-nums rw-strong">
              {current.before} → {current.after}{" "}
              <span className={current.delta >= 0 ? "rw-ok-ink" : "rw-bad-ink"}>
                ({current.delta > 0 ? "+" : ""}
                {current.delta})
              </span>
            </p>
          </div>
        )}
        <p className="sr-only" aria-live="polite">
          {current ? describe(current) : ""}
        </p>
      </div>
    </div>
  );
}
