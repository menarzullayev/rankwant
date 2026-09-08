import type { Route } from "next";
import Link from "next/link";

/** Ko'rinadigan sahifa raqamlari: chetlar doim, joriyning atrofi, orasi «…».
 * Katta arxivda (2000+ masala, 80+ sahifa) hammasini chizib bo'lmaydi. */
function pages(current: number, total: number): (number | "gap")[] {
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);

  const around = new Set([1, total, current - 1, current, current + 1]);
  if (current <= 3) [2, 3, 4].forEach((n) => around.add(n));
  if (current >= total - 2)
    [total - 3, total - 2, total - 1].forEach((n) => around.add(n));

  const shown = [...around]
    .filter((n) => n >= 1 && n <= total)
    .sort((a, b) => a - b);
  const out: (number | "gap")[] = [];
  shown.forEach((n, i) => {
    if (i > 0 && n - shown[i - 1] > 1) out.push("gap");
    out.push(n);
  });
  return out;
}

const cell =
  "flex h-9 min-w-9 items-center justify-center rw-radius-sm px-2.5 text-theme-sm transition";

export function Pager({
  page,
  count,
  pageSize,
  href,
  label = "yozuv",
}: {
  page: number;
  count: number;
  pageSize: number;
  /** Berilgan sahifa uchun to'liq URL — chaqiruvchi qolgan filtrlarni saqlaydi. */
  href: (page: number) => Route;
  label?: string;
}) {
  const total = Math.max(1, Math.ceil(count / pageSize));
  if (count === 0) return null;

  const from = (page - 1) * pageSize + 1;
  const to = Math.min(page * pageSize, count);

  return (
    <nav
      aria-label="Sahifalar"
      className="flex flex-wrap items-center justify-between gap-3 px-5 py-4"
    >
      <p className="text-theme-sm rw-dim">
        {from}–{to} / {count} {label}
      </p>

      {total > 1 && (
        <div className="flex flex-wrap items-center gap-1">
          {page > 1 && (
            <Link
              href={href(page - 1)}
              rel="prev"
              className={`${cell} rw-dim-2 rw-hover-bg`}
            >
              Oldingi
            </Link>
          )}

          {pages(page, total).map((entry, index) =>
            entry === "gap" ? (
              <span key={`gap-${index}`} className={`${cell} rw-faint`}>
                …
              </span>
            ) : entry === page ? (
              <span
                key={entry}
                aria-current="page"
                className={`${cell} rw-accent-bg font-medium`}
              >
                {entry}
              </span>
            ) : (
              <Link
                key={entry}
                href={href(entry)}
                className={`${cell} rw-dim-2 rw-hover-bg`}
              >
                {entry}
              </Link>
            ),
          )}

          {page < total && (
            <Link
              href={href(page + 1)}
              rel="next"
              className={`${cell} rw-dim-2 rw-hover-bg`}
            >
              Keyingi
            </Link>
          )}
        </div>
      )}
    </nav>
  );
}
