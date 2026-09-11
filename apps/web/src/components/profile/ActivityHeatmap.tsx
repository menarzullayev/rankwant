"use client";

import { useState } from "react";

import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import { getJson, type Calendar } from "@/lib/api";
import { dateLocales } from "@/lib/format";

const CELL = 11;
const GAP = 3;
const LEFT = 26;
const TOP = 16;
/** Kunlik urinishlar bo'yicha pog'ona: 0, 1–2, 3–5, 6–10, 11+. */
const STEPS = [0, 2, 5, 10];
const MIX = [0, 30, 55, 78, 100];

const level = (n: number) => (n === 0 ? 0 : STEPS.filter((step) => n > step).length);
const colour = (lvl: number) =>
  lvl === 0
    ? "var(--rw-chip)"
    : `color-mix(in oklab, var(--rw-accent) ${MIX[lvl]}%, var(--rw-chip))`;

/** Faollik xaritasi — yil bo'yicha, kun kvadratchalari (GitHub kabi). */
export function ActivityHeatmap({ username, initial }: { username: string; initial: Calendar }) {
  const locale = useLocale();
  const [data, setData] = useState(initial);
  const [busy, setBusy] = useState(false);

  async function choose(year: number) {
    setBusy(true);
    try {
      setData(await getJson<Calendar>(`/users/${username}/calendar/?year=${year}`));
    } catch {
      // Tarmoq uzildi — oldingi yil ko'rinishda qoladi.
    } finally {
      setBusy(false);
    }
  }

  const counts = new Map(data.days.map((day) => [day.date, day]));
  const first = new Date(Date.UTC(data.year, 0, 1));
  const offset = (first.getUTCDay() + 6) % 7; // dushanba — 0
  const total = Math.round((Date.UTC(data.year + 1, 0, 1) - first.getTime()) / 86_400_000);
  const columns = Math.ceil((total + offset) / 7);
  const label = (iso: string) =>
    new Date(`${iso}T00:00:00Z`).toLocaleDateString(dateLocales(locale), {
      day: "numeric",
      month: "long",
      timeZone: "UTC",
    });
  const weekday = (index: number) =>
    new Date(Date.UTC(2024, 0, 1 + index)).toLocaleDateString(dateLocales(locale), {
      weekday: "short",
      timeZone: "UTC",
    });

  const cells = Array.from({ length: total }, (_, i) => {
    const iso = new Date(Date.UTC(data.year, 0, 1 + i)).toISOString().slice(0, 10);
    const day = counts.get(iso);
    return { iso, index: i + offset, attempts: day?.attempts ?? 0, solved: day?.solved ?? 0 };
  });
  const months = Array.from({ length: 12 }, (_, month) => {
    const index =
      Math.round((Date.UTC(data.year, month, 1) - first.getTime()) / 86_400_000) + offset;
    return {
      col: Math.floor(index / 7),
      name: new Date(Date.UTC(data.year, month, 1)).toLocaleDateString(dateLocales(locale), {
        month: "short",
        timeZone: "UTC",
      }),
    };
  });

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-theme-sm rw-strong">
          {fill(t(locale, "profile.heatmapTotal"), {
            year: data.year,
            attempts: data.attempts,
            solved: data.solved,
          })}
        </p>
        {data.years.length > 1 && (
          <label className="flex items-center gap-2 text-theme-sm rw-dim">
            {t(locale, "profile.year")}
            <select
              value={data.year}
              disabled={busy}
              onChange={(event) => void choose(Number(event.target.value))}
              className="h-9 rw-radius-sm border rw-line px-2 text-theme-sm rw-strong rw-field-bg rw-focus-ring"
            >
              {data.years.map((year) => (
                <option key={year} value={year}>
                  {year}
                </option>
              ))}
            </select>
          </label>
        )}
      </div>
      <div className="overflow-x-auto">
        <svg
          width={LEFT + columns * (CELL + GAP)}
          height={TOP + 7 * (CELL + GAP)}
          role="img"
          aria-label={t(locale, "profile.heatmapTitle")}
          className={busy ? "opacity-60" : undefined}
        >
          {months.map((month) => (
            <text
              key={month.name + month.col}
              x={LEFT + month.col * (CELL + GAP)}
              y={10}
              className="fill-[var(--rw-faint)] text-[10px]"
            >
              {month.name}
            </text>
          ))}
          {[0, 2, 4].map((row) => (
            <text
              key={row}
              x={0}
              y={TOP + row * (CELL + GAP) + CELL - 2}
              className="fill-[var(--rw-faint)] text-[9px]"
            >
              {weekday(row)}
            </text>
          ))}
          {cells.map((cell) => (
            <rect
              key={cell.iso}
              x={LEFT + Math.floor(cell.index / 7) * (CELL + GAP)}
              y={TOP + (cell.index % 7) * (CELL + GAP)}
              width={CELL}
              height={CELL}
              rx={2}
              style={{ fill: colour(level(cell.attempts)) }}
            >
              <title>
                {fill(t(locale, "profile.heatmapTip"), {
                  date: label(cell.iso),
                  attempts: cell.attempts,
                  solved: cell.solved,
                })}
              </title>
            </rect>
          ))}
        </svg>
      </div>
      <div className="flex flex-wrap items-center justify-between gap-3 text-theme-xs rw-dim">
        <p>
          {fill(t(locale, "profile.streakCurrent"), { n: data.streak.current })} ·{" "}
          {fill(t(locale, "profile.streakLongest"), { n: data.streak.longest })}
        </p>
        <p className="flex items-center gap-1" aria-hidden="true">
          {t(locale, "profile.less")}
          {[0, 1, 2, 3, 4].map((lvl) => (
            <span
              key={lvl}
              className="inline-block size-2.5 rounded-sm"
              style={{ background: colour(lvl) }}
            />
          ))}
          {t(locale, "profile.more")}
        </p>
      </div>
    </div>
  );
}
