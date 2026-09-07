import type { Route } from "next";
import Link from "next/link";

/** Maqola/post/roadmap uchun umumiy karta — `<li>` ichida ishlatiladi. */
export function ListCard<T extends string>({
  href,
  title,
  summary,
  meta,
}: {
  href?: Route<T>;
  title: string;
  summary?: string;
  meta?: React.ReactNode;
}) {
  const body = (
    <>
      <span className="block font-semibold rw-strong">{title}</span>
      {summary && (
        <span className="mt-1 block text-theme-sm rw-dim">{summary}</span>
      )}
      {meta && (
        <span className="mt-3 flex flex-wrap items-center gap-2 text-theme-xs rw-faint">
          {meta}
        </span>
      )}
    </>
  );

  const className = `block h-full rw-radius border rw-line rw-surface p-5
 rw-shadow transition rw-surface
 ${href ? "rw-hover-line" : ""}`;

  return href ? (
    <Link href={href} className={className}>
      {body}
    </Link>
  ) : (
    <div className={className}>{body}</div>
  );
}
