"use client";

import type { ReactNode } from "react";

import { chip, type GroupId } from "./chrome";

/** Accordion row: closed groups unmount, so their controls leave the tab order. */
export function Group({
  id,
  title,
  open,
  onOpen,
  children,
}: {
  id: GroupId;
  title: string;
  open: boolean;
  onOpen: (id: GroupId) => void;
  children?: ReactNode;
}) {
  const panel = `rw-cz-${id}`;
  return (
    <section>
      <h3 className="mb-2">
        <button
          type="button"
          aria-expanded={open}
          aria-controls={panel}
          onClick={() => onOpen(id)}
          className={`${chip(open)} flex w-full items-center justify-between text-start font-semibold rw-strong`}
        >
          <span>{title}</span>
          <span aria-hidden="true" className="text-theme-xs rw-faint">
            {open ? "–" : "+"}
          </span>
        </button>
      </h3>
      {open ? (
        <div id={panel} className="space-y-6">
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
