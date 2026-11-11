"use client";

import Link from "next/link";

import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";

import type { Recommendation } from "../api";

/** Problems the student's coaches suggested — the student's tasks from them. */
export function Recommendations({
  rows,
  onlyOpen = false,
}: {
  rows: Recommendation[];
  /** The classroom page shows only what is still to solve. */
  onlyOpen?: boolean;
}) {
  const locale = useLocale();
  const shown = onlyOpen ? rows.filter((row) => !row.solved) : rows;
  if (onlyOpen && shown.length === 0) return null;

  return (
    <Card title={t(locale, "coaching.recommendations")} bodyClassName="p-0">
      <ul className="divide-y rw-divide">
        {shown.map((row) => (
          <li key={row.id} className="flex flex-wrap items-center gap-3 px-5 py-3">
            <div className="min-w-0 flex-1">
              <Link
                href={`/problems/${encodeURIComponent(row.problem)}`}
                className="font-medium rw-accent-ink hover:underline"
              >
                {row.problem_title}
              </Link>
              <span className="ml-2 text-theme-xs rw-faint">
                {fill(t(locale, "coaching.from"), { user: row.coach })}
              </span>
              {row.note && <p className="mt-1 text-theme-sm rw-dim">{row.note}</p>}
            </div>
            {row.solved && <Badge color="success">{t(locale, "coaching.solved")}</Badge>}
          </li>
        ))}
        {shown.length === 0 && (
          <li className="px-5 py-6 text-center text-theme-sm rw-faint">
            {t(locale, "coaching.recommendationsNone")}
          </li>
        )}
      </ul>
    </Card>
  );
}
