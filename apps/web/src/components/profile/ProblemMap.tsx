"use client";

import type { Route } from "next";
import Link from "next/link";
import { useState } from "react";

import { TabBar } from "@/components/kit/TabBar";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import type { ProblemTile } from "@/lib/api";
import { padCode } from "@/lib/format";

type StateFilter = "all" | ProblemTile["state"];

const LEVELS = ["beginner", "basic", "intermediate", "upper", "hard", "expert", "master"];
const STATES = ["solved", "attempted", "untouched"] as const;
const STATE_CLASS: Record<ProblemTile["state"], string> = {
  solved: "rw-ok-soft",
  attempted: "rw-warn-soft",
  untouched: "rw-chip rw-faint",
};
const STATE_KEY: Record<ProblemTile["state"], string> = {
  solved: "profile.stateSolved",
  attempted: "profile.stateAttempted",
  untouched: "profile.stateUntouched",
};

/** Arxivdagi har masala — ikki ko'rinishda: raqam tartibida (Robocontest
 *  kabi) yoki yetti daraja guruhida. Katak shu masaladagi urinishlarga
 *  olib boradi. */
export function ProblemMap({ username, problems }: { username: string; problems: ProblemTile[] }) {
  const locale = useLocale();
  const [mode, setMode] = useState<"code" | "level">("code");
  const [filter, setFilter] = useState<StateFilter>("all");
  const counts: Record<ProblemTile["state"], number> = { solved: 0, attempted: 0, untouched: 0 };
  for (const problem of problems) counts[problem.state] += 1;
  const visible =
    filter === "all" ? problems : problems.filter((problem) => problem.state === filter);

  const tile = (problem: ProblemTile) => (
    <Link
      key={problem.slug}
      prefetch={false}
      href={`/users/${username}/attempts?problem=${encodeURIComponent(problem.slug)}` as Route}
      title={`#${padCode(problem.code)} · ${problem.title}${
        problem.rate === null ? "" : ` (${problem.rate}%)`
      }`}
      data-tip-kind="rich"
      data-tip-title={`#${padCode(problem.code)}`}
      className={`flex h-7 min-w-12 items-center justify-center rounded px-1 font-mono text-[12px] font-semibold tabular-nums transition hover:ring-2 hover:ring-[var(--rw-accent)] focus-visible:outline-2 focus-visible:outline-[var(--rw-accent-ink)] ${STATE_CLASS[problem.state]}`}
    >
      {padCode(problem.code)}
    </Link>
  );

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <TabBar
          tone="badge"
          label={t(locale, "filter.filters")}
          value={filter}
          onChange={setFilter}
          options={[
            { id: "all", label: t(locale, "filter.all"), count: problems.length },
            ...STATES.map((state) => ({
              id: state,
              label: t(locale, STATE_KEY[state]),
              count: counts[state],
              icon: (
                <span
                  aria-hidden="true"
                  className={`inline-block size-3 rounded-sm ${STATE_CLASS[state]}`}
                />
              ),
            })),
          ]}
        />
        <div role="tablist" className="rw-kit-tabs flex gap-1" data-kit-tabs="icon">
          {(["code", "level"] as const).map((option) => (
            <button
              key={option}
              type="button"
              role="tab"
              aria-selected={mode === option}
              onClick={() => setMode(option)}
              className={`rw-radius-sm px-3 py-1.5 text-theme-xs font-medium transition rw-focus-ring ${
                mode === option ? "rw-accent-soft rw-accent-ink" : "rw-dim rw-hover-bg"
              }`}
            >
              {t(locale, option === "code" ? "profile.mapByCode" : "profile.mapByLevel")}
            </button>
          ))}
        </div>
      </div>
      {mode === "code" ? (
        <div className="flex flex-wrap gap-1">{visible.map(tile)}</div>
      ) : (
        <div className="space-y-4">
          {LEVELS.map((code) => {
            const rows = visible.filter((problem) => problem.level === code);
            if (rows.length === 0) return null;
            const solved = rows.filter((problem) => problem.state === "solved").length;
            return (
              <section key={code}>
                <h3 className={`level-${code} mb-2 text-theme-sm font-semibold`}>
                  {t(locale, `level.${code}`)}{" "}
                  <span className="font-normal tabular-nums rw-faint">
                    {solved} / {rows.length}
                  </span>
                </h3>
                <div className="flex flex-wrap gap-1">{rows.map(tile)}</div>
              </section>
            );
          })}
        </div>
      )}
    </div>
  );
}
