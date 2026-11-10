"use client";

import type { Route } from "next";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { useLocale } from "@/i18n/LocaleProvider";
import { t, type MessageKey } from "@/i18n/messages";

/** The sections of `/studio` (2026-11-10). One list, so a new section —
 *  contests next — is a line here, not a second menu. */
const SECTIONS: readonly { href: Route; key: MessageKey }[] = [
  { href: "/studio/problems", key: "studio.nav.problems" },
];

export function StudioNav() {
  const locale = useLocale();
  const pathname = usePathname() ?? "";
  return (
    <nav
      aria-label={t(locale, "studio.title")}
      className="rw-kit-tabs !flex-wrap !overflow-x-visible shadow-[inset_0_-1px_0_var(--rw-divider)]"
      data-kit-tabs="scroll"
    >
      {SECTIONS.map((section) => {
        const current = pathname.startsWith(section.href);
        return (
          <Link
            key={section.href}
            href={section.href}
            aria-current={current ? "page" : undefined}
            className={`rw-kit-tab ${current ? "rw-accent-ink" : "rw-dim rw-hover-strong"}`}
          >
            {t(locale, section.key)}
          </Link>
        );
      })}
    </nav>
  );
}
