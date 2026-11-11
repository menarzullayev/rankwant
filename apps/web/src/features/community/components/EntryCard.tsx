import { numericStamp } from "@rankwant/shared/format";
import type { Route } from "next";
import Link from "next/link";

import { UserName } from "@/components/ui/Identity/UserName";
import { fill, t, type Locale } from "@/i18n/messages";

import type { Entry } from "../api";

/** The colour of a score: green above zero, red below. */
function scoreClass(score: number): string {
  if (score > 0) return "rw-ok-ink";
  if (score < 0) return "rw-bad-ink";
  return "rw-faint";
}

/** One entry in the feed: score, title, author, tags, counts. */
export function EntryCard({ entry, locale }: { entry: Entry; locale: Locale }) {
  return (
    <article className="flex gap-4 py-4" aria-labelledby={`entry-${entry.id}`}>
      <div className="w-10 shrink-0 text-center">
        <span className={`block text-theme-sm font-bold tabular-nums ${scoreClass(entry.score)}`}>
          {entry.score > 0 ? `+${entry.score}` : entry.score}
        </span>
        <span className="sr-only">{t(locale, "blogs.score")}</span>
      </div>
      <div className="min-w-0 flex-1 space-y-1">
        <div className="flex flex-wrap items-baseline gap-x-2 gap-y-1 text-theme-xs rw-faint">
          {entry.author ? (
            <UserName
              username={entry.author.username}
              name={entry.author.display_name}
              title={entry.author.title}
              locale={locale}
              className="text-theme-sm"
            />
          ) : (
            <span>—</span>
          )}
          <time dateTime={entry.created_at}>{numericStamp(entry.created_at).slice(0, 10)}</time>
          <span>· {fill(t(locale, "blogs.reading"), { count: entry.reading_minutes })}</span>
        </div>
        <h2 id={`entry-${entry.id}`} className="text-theme-sm font-semibold rw-strong">
          <Link href={`/blogs/${entry.id}` as Route} className="rw-link-hover">
            {entry.title}
          </Link>
        </h2>
        {entry.excerpt && <p className="line-clamp-2 text-theme-sm rw-dim">{entry.excerpt}</p>}
        <div className="flex flex-wrap items-center gap-2 text-theme-xs rw-faint">
          {entry.tags.map((tag) => (
            <Link
              key={tag}
              href={`/blogs?tag=${encodeURIComponent(tag)}` as Route}
              className="rw-chip rw-radius-sm px-2 py-0.5 rw-link-hover"
            >
              #{tag}
            </Link>
          ))}
          <span>{fill(t(locale, "blogs.comments"), { count: entry.comment_count })}</span>
          <span>· {fill(t(locale, "blogs.views"), { count: entry.view_count })}</span>
        </div>
      </div>
    </article>
  );
}
