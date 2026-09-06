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
      <span className="block font-semibold text-gray-800 dark:text-white/90">{title}</span>
      {summary && (
        <span className="mt-1 block text-theme-sm text-gray-500 dark:text-gray-400">
          {summary}
        </span>
      )}
      {meta && (
        <span className="mt-3 flex flex-wrap items-center gap-2 text-theme-xs text-gray-400">
          {meta}
        </span>
      )}
    </>
  );

  const className = `block h-full rounded-2xl border border-gray-200 bg-white p-5
    shadow-theme-xs transition dark:border-[#232936] dark:bg-[#141821]
    ${href ? "hover:border-brand-400" : ""}`;

  return href ? (
    <Link href={href} className={className}>
      {body}
    </Link>
  ) : (
    <div className={className}>{body}</div>
  );
}
