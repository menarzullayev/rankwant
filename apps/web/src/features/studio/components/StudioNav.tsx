"use client";

import type { Route } from "next";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, type MessageKey } from "@/i18n/messages";
import { isOn } from "@/lib/flags";

/** The sections of `/studio` (2026-11-10). One list, so a new section
 *  is a line here, not a second menu. */
const SECTIONS: readonly { href: Route; key: MessageKey }[] = [
  { href: "/studio/problems", key: "studio.nav.problems" },
  { href: "/studio/contests", key: "studio.nav.contests" },
  { href: "/studio/courses", key: "studio.nav.courses" },
  // A teacher's quizzes and question bank (ADR-0061 § 5).
  { href: "/studio/quizzes", key: "studio.nav.quizzes" },
  { href: "/studio/questions", key: "studio.nav.questions" },
];

export function StudioNav() {
  const locale = useLocale();
  const pathname = usePathname() ?? "";
  const { user } = useSession();
  // Courses: staff prepare them before the section opens (`courses` flag).
  const courses = isOn("courses") || Boolean(user?.is_staff);
  return (
    <nav
      aria-label={t(locale, "studio.title")}
      className="rw-kit-tabs !flex-wrap !overflow-x-visible shadow-[inset_0_-1px_0_var(--rw-divider)]"
      data-kit-tabs="scroll"
    >
      {SECTIONS.filter((section) => courses || section.href !== "/studio/courses").map((section) => {
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
