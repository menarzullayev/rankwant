"use client";

import type { Route } from "next";
import Link from "next/link";
import type { ReactNode } from "react";

import type { TabTone } from "@/lib/theme/kit";

export type KitTab<T extends string = string> = {
  id: T;
  label: string;
  href?: Route;
  icon?: ReactNode;
  count?: number;
};

export function TabBar<T extends string>({
  tone,
  value,
  options,
  label,
  onChange,
  multiple,
  selected,
}: {
  tone: TabTone;
  value?: T;
  options: KitTab<T>[];
  label: string;
  onChange?: (next: T) => void;
  multiple?: boolean;
  selected?: readonly T[];
}) {
  const nav = options.some((o) => o.href);
  let listRole: "group" | "tablist" | undefined = "tablist";
  if (tone === "chips" && multiple) listRole = "group";
  else if (tone === "step" || tone === "crumb" || nav) listRole = undefined;

  return (
    <div
      className="rw-kit-tabs"
      data-kit-tabs={tone}
      role={listRole}
      aria-label={label}
    >
      {nav ? (
        <nav aria-label={label} className="contents">
          {options.map((o) => {
            const on = o.id === value;
            let current: "page" | "step" | undefined;
            if (on && tone === "step") current = "step";
            else if (on) current = "page";
            return (
              <Link
                key={o.id}
                href={(o.href ?? "#") as Route}
                className="rw-kit-tab"
                aria-current={current}
              >
                {o.icon}
                <span>{o.label}</span>
                {o.count !== undefined ? (
                  <span className="rw-kit-count">{o.count}</span>
                ) : null}
              </Link>
            );
          })}
        </nav>
      ) : (
        options.map((o) => {
          const on = multiple
            ? Boolean(selected?.includes(o.id))
            : o.id === value;
          let btnRole: "checkbox" | "tab" | undefined = "tab";
          if (multiple) btnRole = "checkbox";
          else if (tone === "chips") btnRole = undefined;
          return (
            <button
              key={o.id}
              type="button"
              className="rw-kit-tab"
              role={btnRole}
              aria-selected={multiple ? undefined : on}
              aria-pressed={tone === "chips" || multiple ? on : undefined}
              aria-checked={multiple ? on : undefined}
              onClick={() => onChange?.(o.id)}
            >
              {o.icon}
              <span>{o.label}</span>
              {o.count !== undefined ? (
                <span className="rw-kit-count">{o.count}</span>
              ) : null}
            </button>
          );
        })
      )}
    </div>
  );
}
