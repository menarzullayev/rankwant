"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { ADMIN_SECTIONS } from "./sections";

export function AdminNav() {
  const pathname = usePathname();
  return (
    <nav className="no-scrollbar -mx-1 flex gap-1 overflow-x-auto pb-1">
      {ADMIN_SECTIONS.map((s) => {
        const active = pathname === s.href || pathname.startsWith(`${s.href}/`);
        return (
          <Link
            key={s.href}
            href={s.href}
            className={`shrink-0 rw-radius-sm px-3 py-1.5 text-theme-sm font-medium transition ${
              active ? "rw-accent-bg" : "rw-dim-2 rw-hover-bg "
            }`}
          >
            {s.label}
          </Link>
        );
      })}
    </nav>
  );
}
