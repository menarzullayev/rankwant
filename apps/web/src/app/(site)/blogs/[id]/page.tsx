import { numericStamp } from "@rankwant/shared/format";
import type { Metadata, Route } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { cache } from "react";

import { Card } from "@/components/ui/Card";
import { UserName } from "@/components/ui/Identity/UserName";
import { Markdown } from "@/components/ui/Markdown";
import { Discussion, EntryActions, type EntryDetail, type ThreadPage } from "@/features/community";
import { getLocale } from "@/i18n/server";
import { fill, t } from "@/i18n/messages";
import { ApiError } from "@/lib/api";
import { getSessionUser, getWithSession } from "@/lib/api.server";

export const dynamic = "force-dynamic";

/** One request per render: metadata and the page read the same entry. */
const loadEntry = cache(async (id: string): Promise<EntryDetail | null> => {
  try {
    return await getWithSession<EntryDetail>(`/blogs/${encodeURIComponent(id)}/`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return null;
    throw error;
  }
});

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const entry = await loadEntry((await params).id);
  if (!entry) return { title: t(await getLocale(), "blogs.title") };
  return { title: entry.title, description: entry.excerpt };
}

/** A member's entry with its discussion (decision 2026-11-11 ④). */
export default async function EntryPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const locale = await getLocale();
  const entry = await loadEntry(id);
  if (!entry) notFound();
  const signedIn = (await getSessionUser()) !== null;
  const thread = await getWithSession<ThreadPage>(`/discussions/entry/${entry.id}/`).catch(
    () => null,
  );

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <Link href={"/blogs" as Route} className="text-theme-sm rw-dim rw-link-hover">
        ← {t(locale, "blogs.title")}
      </Link>
      <article className="space-y-4" aria-labelledby="entry-title">
        <header className="space-y-2">
          <h1 id="entry-title" className="text-title-sm font-bold rw-strong">
            {entry.title}
          </h1>
          <p className="flex flex-wrap items-baseline gap-x-2 gap-y-1 text-theme-xs rw-faint">
            {entry.author && (
              <UserName
                username={entry.author.username}
                name={entry.author.display_name}
                title={entry.author.title}
                locale={locale}
                className="text-theme-sm"
              />
            )}
            <time dateTime={entry.created_at}>{numericStamp(entry.created_at).slice(0, 16)}</time>
            {entry.edited_at && <span>· {t(locale, "discussion.edited")}</span>}
            <span>· {fill(t(locale, "blogs.reading"), { count: entry.reading_minutes })}</span>
            <span>· {fill(t(locale, "blogs.views"), { count: entry.view_count })}</span>
          </p>
          {entry.tags.length > 0 && (
            <p className="flex flex-wrap gap-2">
              {entry.tags.map((tag) => (
                <Link
                  key={tag}
                  href={`/blogs?tag=${encodeURIComponent(tag)}` as Route}
                  className="rw-chip rw-radius-sm px-2 py-0.5 text-theme-xs rw-link-hover"
                >
                  #{tag}
                </Link>
              ))}
            </p>
          )}
        </header>
        <Card className="p-5">
          <Markdown>{entry.body}</Markdown>
        </Card>
        <EntryActions entry={entry} signedIn={signedIn} />
      </article>

      {thread && (
        <Card className="p-5">
          <Discussion target={{ kind: "entry", ref: String(entry.id) }} initial={thread} signedIn={signedIn} />
        </Card>
      )}
    </div>
  );
}
