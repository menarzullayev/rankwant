import Link from "next/link";

import { t, type Locale } from "@/i18n/messages";
import type { SimilarProblem } from "@/lib/api";

/** Teglar va o'xshash masalalar — prototip #9 + #7 (`details` akordeon). */
export function ProblemMetaAccordion({
  topics,
  similar,
  locale,
}: {
  topics: string[];
  similar: SimilarProblem[];
  locale: Locale;
}) {
  if (topics.length === 0 && similar.length === 0) return null;

  return (
    <div className="flex flex-col gap-2">
      {topics.length > 0 && (
        <details className="rw-radius-sm border rw-line rw-panel-bg">
          <summary className="flex cursor-pointer list-none items-center gap-2 px-3 py-2.5 text-theme-sm font-semibold rw-strong [&::-webkit-details-marker]:hidden">
            <TagIcon />
            {t(locale, "problem.tagsAndTopics")}
            <span className="ml-auto rw-radius-full border rw-line rw-panel-2 px-2 py-0.5 text-theme-2xs font-bold tabular-nums rw-faint">
              {topics.length}
            </span>
          </summary>
          <div className="border-t rw-divider px-3 pb-3 pt-2">
            <div className="flex flex-wrap gap-2">
              {topics.map((topic) => (
                <span
                  key={topic}
                  className="rw-radius-full rw-accent-soft px-2.5 py-1 text-theme-xs font-semibold rw-accent-ink"
                >
                  {topic}
                </span>
              ))}
            </div>
          </div>
        </details>
      )}

      {similar.length > 0 && (
        <details className="rw-radius-sm border rw-line rw-panel-bg">
          <summary className="flex cursor-pointer list-none items-center gap-2 px-3 py-2.5 text-theme-sm font-semibold rw-strong [&::-webkit-details-marker]:hidden">
            <SimilarIcon />
            {t(locale, "problem.similar")}
            <span className="ml-auto rw-radius-full border rw-line rw-panel-2 px-2 py-0.5 text-theme-2xs font-bold tabular-nums rw-faint">
              {similar.length}
            </span>
          </summary>
          <ul className="border-t rw-divider">
            {similar.map((item) => (
              <li key={item.slug} className="border-b rw-divider last:border-b-0">
                <Link
                  href={`/problems/${item.slug}`}
                  className="flex flex-wrap items-center gap-2 px-3 py-2 text-theme-sm rw-link-hover"
                >
                  <span className={`level-${item.level} text-theme-xs font-medium`}>
                    {item.level_label}
                  </span>
                  <span className="min-w-0 flex-1 truncate font-medium rw-strong">
                    {item.title}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </details>
      )}
    </div>
  );
}

function TagIcon() {
  return (
    <svg
      className="size-4 shrink-0 rw-accent-ink"
      viewBox="0 0 24 24"
      aria-hidden
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
    >
      <path d="M4 7h16M4 12h10M4 17h7" />
    </svg>
  );
}

function SimilarIcon() {
  return (
    <svg
      className="size-4 shrink-0 rw-accent-ink"
      viewBox="0 0 24 24"
      aria-hidden
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
    >
      <path d="M10 13a5 5 0 0 1 7 0" />
      <path d="M8 21l4-7 4 7" />
      <path d="M12 3v4" />
    </svg>
  );
}
