"use client";

import { regionName } from "@rankwant/shared/regions";
import { useEffect, useState } from "react";

import { Card } from "@/components/ui/Card";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import { getJson } from "@/lib/api";

/** Active members by region (decision 2026-11-11 ④): a tile map of the
 *  fourteen regions, laid out roughly as they lie (west → east, north →
 *  south). A tile map, not a drawn border map: no geometry ships with the
 *  page, and every region gets a tile big enough to read. */

type Region = { code: string; users: number };
type Activity = { days: number; total: number; regions: Region[] };

const PERIODS = [7, 30, 90, 365] as const;

/** Column and row of each region's tile. */
const PLACE: Record<string, [number, number]> = {
  qoraqalpogiston: [1, 1],
  navoiy: [2, 1],
  jizzax: [3, 1],
  sirdaryo: [4, 1],
  toshkent: [5, 1],
  namangan: [6, 1],
  xorazm: [1, 2],
  buxoro: [2, 2],
  samarqand: [3, 2],
  "toshkent-shahri": [5, 2],
  fargona: [6, 2],
  andijon: [7, 2],
  qashqadaryo: [3, 3],
  surxondaryo: [4, 4],
};

export function RegionMap() {
  const locale = useLocale();
  const [days, setDays] = useState<number>(30);
  const [data, setData] = useState<Activity | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let live = true;
    getJson<Activity>(`/stats/regions/?days=${days}`)
      .then((value) => {
        if (live) setData(value);
      })
      .catch(() => {
        if (live) setFailed(true);
      });
    return () => {
      live = false;
    };
  }, [days]);

  if (failed) return null;
  const top = Math.max(1, ...(data?.regions.map((r) => r.users) ?? [1]));
  const ranked = [...(data?.regions ?? [])].sort((a, b) => b.users - a.users);

  return (
    <Card title={t(locale, "regions.title")}>
      <div className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="text-theme-sm rw-dim">
            {data ? fill(t(locale, "regions.total"), { count: data.total }) : "…"}
          </p>
          <div className="flex flex-wrap gap-1" role="group" aria-label={t(locale, "regions.period")}>
            {PERIODS.map((value) => (
              <button
                key={value}
                type="button"
                aria-pressed={value === days}
                onClick={() => setDays(value)}
                className={`min-h-9 rw-radius-sm border px-3 text-theme-xs font-medium rw-focus-ring ${
                  value === days ? "rw-accent-line rw-accent-ink" : "rw-line rw-dim rw-hover-bg"
                }`}
              >
                {fill(t(locale, "regions.days"), { count: value })}
              </button>
            ))}
          </div>
        </div>

        {/* The tile map from `sm`; a ranked list on a phone, where seven
            columns would not leave room for a name. */}
        <ul
          className="hidden gap-2 sm:grid"
          style={{ gridTemplateColumns: "repeat(7, minmax(0, 1fr))" }}
          aria-label={t(locale, "regions.title")}
        >
          {(data?.regions ?? []).map((region) => {
            const [col, row] = PLACE[region.code] ?? [1, 4];
            const share = region.users / top;
            return (
              <li
                key={region.code}
                style={{
                  gridColumn: col,
                  gridRow: row,
                  background: `color-mix(in srgb, var(--rw-accent) ${Math.round(8 + share * 42)}%, transparent)`,
                }}
                className="flex min-h-16 flex-col justify-between rw-radius-sm border rw-line p-2"
              >
                <span className="line-clamp-2 text-theme-xs font-medium rw-strong">
                  {regionName(region.code, locale)}
                </span>
                <span className="text-theme-sm font-bold tabular-nums rw-strong">{region.users}</span>
              </li>
            );
          })}
        </ul>

        <ol className="space-y-1.5 sm:hidden">
          {ranked.map((region) => (
            <li key={region.code} className="flex items-center gap-2 text-theme-sm">
              <span className="w-28 shrink-0 truncate rw-strong">{regionName(region.code, locale)}</span>
              <span className="h-2 flex-1 overflow-hidden rounded-full rw-chip">
                <span
                  className="block h-full rounded-full rw-accent-bg"
                  style={{ width: `${Math.round((region.users / top) * 100)}%` }}
                />
              </span>
              <span className="w-10 shrink-0 text-end tabular-nums rw-dim">{region.users}</span>
            </li>
          ))}
        </ol>
      </div>
    </Card>
  );
}
