"use client";

import { useState } from "react";

import { Segmented } from "@/components/ui/Segmented";

import { Person, type PersonRow } from "./Person";

export type TopTab = {
  key: string;
  label: string;
  rows: (PersonRow & { value: number })[];
};

/** Top three by each rating kind, one list on screen at a time.
 *
 *  Every list arrives with the page: the server reads six short, indexed
 *  queries in parallel, so switching a tab costs no request and works before
 *  hydration finishes loading anything else. */
export function TopUsers({
  tabs,
  label,
  empty,
}: {
  tabs: TopTab[];
  /** Names the tab group for a screen reader. */
  label: string;
  empty: string;
}) {
  const [active, setActive] = useState(tabs[0]?.key ?? "");
  const current = tabs.find((tab) => tab.key === active) ?? tabs[0];
  if (!current) return null;

  return (
    <div className="space-y-4">
      <div className="overflow-x-auto">
        <Segmented
          value={current.key}
          onChange={setActive}
          options={tabs.map((tab) => ({ value: tab.key, label: tab.label }))}
          label={label}
        />
      </div>
      {current.rows.length > 0 ? (
        <ol className="grid gap-4 sm:grid-cols-3">
          {current.rows.map((row, i) => (
            <li key={row.username} className="rw-radius-sm border rw-line p-4">
              <p className="text-theme-xl font-bold rw-faint">{i + 1}</p>
              <div className="mt-2">
                <Person person={row}>
                  <span className="block truncate text-theme-xs rw-dim">{row.username}</span>
                </Person>
              </div>
              <p className="mt-3 text-theme-xl font-bold tabular-nums rw-strong">{row.value}</p>
            </li>
          ))}
        </ol>
      ) : (
        <p className="text-theme-sm rw-dim">{empty}</p>
      )}
    </div>
  );
}
