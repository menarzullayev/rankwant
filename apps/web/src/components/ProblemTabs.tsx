import type { Route } from "next";
import Link from "next/link";

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
  const tabs = [
    ["statement", "Tavsif", `/problems/${slug}`],
    ["status", "Urinishlar", `/problems/${slug}/status`],
    ["stats", "Statistika", `/problems/${slug}/stats`],
    ["solvers", "Yechganlar", `/problems/${slug}/solvers`],
  ] as const;

  return (
    <nav
      aria-label="Masala bo'limlari"
      className="flex flex-wrap items-center gap-1 border-b rw-divider"
    >
      {tabs.map(([key, label, href]) => (
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
          {label}
        </Link>
      ))}
    </nav>
  );
}
