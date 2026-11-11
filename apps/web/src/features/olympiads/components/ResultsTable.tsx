import type { Route } from "next";
import Link from "next/link";

import { Badge } from "@/components/ui/Badge";
import { t, type Locale } from "@/i18n/messages";
import type { OlympiadResult } from "@/lib/api";

import { MEDAL_COLOR, MEDAL_LABEL, participantPath } from "../catalog";

const CELL = "px-4 py-2.5 text-theme-sm";

/** The published results of an event: place, name, score and medal. */
export function ResultsTable({ results, locale }: { results: OlympiadResult[]; locale: Locale }) {
  return (
    <div className="rw-scroll-x">
      <table className="w-full min-w-[28rem] text-left">
        <thead>
          <tr className="border-b rw-divider text-theme-xs uppercase tracking-wide rw-faint">
            <th scope="col" className={CELL}>
              {t(locale, "olympiads.col.rank")}
            </th>
            <th scope="col" className={CELL}>
              {t(locale, "olympiads.col.name")}
            </th>
            <th scope="col" className={`${CELL} text-right`}>
              {t(locale, "olympiads.col.score")}
            </th>
            <th scope="col" className={CELL}>
              {t(locale, "olympiads.col.medal")}
            </th>
          </tr>
        </thead>
        <tbody className="rw-divide divide-y">
          {results.map((row) => {
            const medal = MEDAL_LABEL[row.medal];
            return (
              <tr key={row.participant}>
                <td className={`${CELL} tabular-nums rw-dim`}>{row.rank ?? ""}</td>
                <td className={CELL}>
                  <Link
                    href={participantPath(row.participant) as Route}
                    className="font-medium rw-strong rw-focus-ring hover:underline"
                  >
                    {row.full_name}
                  </Link>
                </td>
                <td className={`${CELL} text-right tabular-nums`}>{row.score ?? ""}</td>
                <td className={CELL}>
                  {medal && <Badge color={MEDAL_COLOR[row.medal] ?? "neutral"}>{t(locale, medal)}</Badge>}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
