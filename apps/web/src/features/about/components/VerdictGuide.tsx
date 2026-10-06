"use client";

import { useState } from "react";

import { Verdict } from "@/components/ui/Verdict";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t, type MessageKey } from "@/i18n/messages";
import type { VerdictKey } from "@/lib/theme/verdict";

import { VERDICT_GROUPS, type VerdictGroupId } from "../sections";

function guideKey(kind: "event" | "cause" | "example", code: VerdictKey): MessageKey {
  return `about.verdicts.${kind}.${code.toLowerCase()}` as MessageKey;
}

const chip = (active: boolean) =>
  `inline-flex h-10 items-center rounded-full border px-3 text-theme-xs font-medium whitespace-nowrap rw-focus-ring ${
    active ? "border-transparent rw-accent-soft rw-accent-ink" : "rw-divider rw-dim-2 rw-hover-bg"
  }`;

type Filter = VerdictGroupId | "all";

/** Every verdict code, grouped by how often a solver meets it.
 *
 *  A row is the code and what it means; opening it adds what to do and an
 *  example. Every row is in the page whether open or not, so a search
 *  engine reads all of them and Chrome's "find in page" opens the one it
 *  finds. The search here narrows by code or by any word of the text. */
export function VerdictGuide() {
  const locale = useLocale();
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<Filter>("all");

  const needle = query.trim().toLowerCase();
  const matches = (code: VerdictKey) =>
    !needle ||
    `${code} ${t(locale, guideKey("event", code))} ${t(locale, guideKey("cause", code))}`
      .toLowerCase()
      .includes(needle);

  const groups = VERDICT_GROUPS.filter((group) => filter === "all" || filter === group.id)
    .map((group) => ({ ...group, codes: group.codes.filter(matches) }))
    .filter((group) => group.codes.length > 0);
  const total = groups.reduce((sum, group) => sum + group.codes.length, 0);

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2">
        <input
          type="search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder={t(locale, "about.verdicts.search")}
          aria-label={t(locale, "about.verdicts.searchLabel")}
          className="h-11 min-w-0 flex-1 basis-48 rounded-full border rw-divider rw-field-bg px-4 text-theme-sm rw-strong rw-fm-inp rw-focus-ring sm:max-w-xs sm:flex-none"
        />
        <div role="group" aria-label={t(locale, "about.verdicts.groupLabel")} className="flex flex-wrap gap-2">
          <button type="button" aria-pressed={filter === "all"} onClick={() => setFilter("all")} className={chip(filter === "all")}>
            {t(locale, "about.verdicts.group.all")}
          </button>
          {VERDICT_GROUPS.map((group) => (
            <button
              key={group.id}
              type="button"
              aria-pressed={filter === group.id}
              onClick={() => setFilter(group.id)}
              className={chip(filter === group.id)}
            >
              {t(locale, group.label)}
            </button>
          ))}
        </div>
      </div>

      <p role="status" className="text-theme-xs rw-dim">
        {total > 0
          ? fill(t(locale, "about.verdicts.found"), { count: total })
          : t(locale, "about.verdicts.none")}
      </p>

      {groups.map((group) => (
        <div key={group.id}>
          <h3 className="mb-1 text-theme-xs font-semibold tracking-wide rw-dim-2 uppercase">
            {t(locale, group.label)} · {group.codes.length}
          </h3>
          <ul>
            {group.codes.map((code) => (
              <li key={code} className="border-t rw-divider">
                <details className="group">
                  <summary className="flex min-h-11 cursor-pointer list-none flex-wrap items-baseline gap-x-3 gap-y-1 rw-radius-sm py-2.5 rw-focus-ring [&::-webkit-details-marker]:hidden">
                    <Verdict verdict={code} variant="badge" />
                    <span className="min-w-0 flex-1 basis-56 text-theme-sm rw-dim [overflow-wrap:anywhere]">
                      {t(locale, guideKey("event", code))}
                    </span>
                  </summary>
                  <dl className="grid gap-x-6 gap-y-2 pb-3 text-theme-sm md:grid-cols-2">
                    <div>
                      <dt className="text-theme-xs rw-faint">{t(locale, "about.verdicts.col.cause")}</dt>
                      <dd className="rw-dim">{t(locale, guideKey("cause", code))}</dd>
                    </div>
                    <div>
                      <dt className="text-theme-xs rw-faint">{t(locale, "about.verdicts.col.example")}</dt>
                      <dd className="rw-dim">{t(locale, guideKey("example", code))}</dd>
                    </div>
                  </dl>
                </details>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
