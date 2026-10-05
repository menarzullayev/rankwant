"use client";

import type { ReactNode } from "react";

import type { GroupId } from "./chrome";

/** Accordion row: closed groups unmount, so their controls leave the tab order.
 *  A closed row shows `summary` — the value inside, without opening it. */
export function Group({
  id,
  title,
  summary,
  open,
  onOpen,
  flush = false,
  children,
}: {
  id: GroupId;
  title: string;
  summary?: string;
  open: boolean;
  onOpen: (id: GroupId) => void;
  /** No rule above the row — for a group that stands in its own box. */
  flush?: boolean;
  children?: ReactNode;
}) {
  const panel = `rw-cz-${id}`;
  return (
    <section className={flush ? "" : "border-t rw-divide"}>
      <h3>
        <button
          type="button"
          aria-expanded={open}
          aria-controls={panel}
          onClick={() => onOpen(id)}
          className="flex min-h-10 w-full items-center justify-between gap-3 py-2 text-start text-theme-sm font-semibold rw-strong rw-focus-ring"
        >
          <span>{title}</span>
          <span className="flex min-w-0 items-center gap-2 font-normal rw-faint">
            {!open && summary ? (
              <span className="truncate text-theme-xs">{summary}</span>
            ) : null}
            <span aria-hidden="true" className="text-theme-xs">
              {open ? "–" : "+"}
            </span>
          </span>
        </button>
      </h3>
      {open ? (
        <div id={panel} className="space-y-6 pt-1 pb-4">
          {children}
        </div>
      ) : null}
    </section>
  );
}

export function Section({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <section>
      <h4 className="mb-2 text-theme-sm font-semibold rw-strong">{title}</h4>
      {children}
    </section>
  );
}
