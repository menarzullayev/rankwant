"use client";

import type { Route } from "next";
import Link from "next/link";

import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

/** Masala bo'limlari — KEP va RoboContest'dagi kabi sahifa tepasida.
 *
 * Pastki paneldagi tablardan farqi: bular butun sahifani almashtiradi
 * (matn + muharrir ↔ urinishlar ↔ statistika), pastdagilar esa faqat
 * ishchi holatni (natija, namuna, o'z testi). */
export function ProblemTabs({
  slug,
  current,
}: {
  slug: string;
  current: "statement" | "status" | "stats" | "solvers";
}) {
  const locale = useLocale();
  // Sarlavhalar endi KALIT: matn `t()` dan olinadi. Ilgari bu yerda
  // o'zbekcha so'zlar to'g'ridan-to'g'ri turardi va matn qidiruvchi
  // skaner ularni ko'rmasdi (JSX matni emas, massiv elementi edi) —
  // shuning uchun ular uzoq vaqt e'tibordan chetda qoldi.
  const tabs = [
    ["statement", "problem.tab.statement", `/problems/${slug}`],
    ["status", "problem.tab.status", `/problems/${slug}/status`],
    ["stats", "problem.tab.stats", `/problems/${slug}/stats`],
    ["solvers", "problem.tab.solvers", `/problems/${slug}/solvers`],
  ] as const;

  return (
    <nav
      aria-label={t(locale, "problem.tabsLabel")}
      className="flex flex-wrap items-center gap-1 border-b rw-divider"
    >
      {tabs.map(([key, labelKey, href]) => (
        <Link
          key={key}
          href={href as Route}
          aria-current={key === current ? "page" : undefined}
          className={`-mb-px border-b-2 px-3 py-2 text-theme-sm font-medium transition ${
            key === current
              ? "rw-accent-line rw-accent-ink"
              : "border-transparent rw-dim rw-hover-strong"
          }`}
        >
          {t(locale, labelKey)}
        </Link>
      ))}
    </nav>
  );
}
