import type { Metadata, Route } from "next";
import Link from "next/link";

import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Pager } from "@/components/ui/Pager";
import { BLOG_TABS, EntryCard, type BlogTab, type Entry } from "@/features/community";
import { getLocale } from "@/i18n/server";
import { t, type MessageKey } from "@/i18n/messages";
import { getJson, type Paginated } from "@/lib/api";
import { getSessionUser, getWithSession } from "@/lib/api.server";

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  const locale = await getLocale();
  return { title: t(locale, "blogs.title"), description: t(locale, "blogs.description") };
}

const PAGE_SIZE = 25;

const TAB_LABEL: Record<BlogTab, MessageKey> = {
  new: "blogs.tab.new",
  top: "blogs.tab.top",
  following: "blogs.tab.following",
};

type Search = { tab?: string; tag?: string; author?: string; page?: string };

const DEFAULT_TAB: BlogTab = "new";

/** An unknown `?tab=` falls back to the newest entries. */
function pickTab(raw: string): BlogTab {
  return (BLOG_TABS as readonly string[]).includes(raw) ? (raw as BlogTab) : DEFAULT_TAB;
}

function one(value: string | undefined): string {
  return value?.trim() ?? "";
}

/** Member blogs (decision 2026-11-11 ④): new, popular this week, followed. */
export default async function BlogsPage({ searchParams }: { searchParams: Promise<Search> }) {
  const query = await searchParams;
  const locale = await getLocale();
  const signedIn = (await getSessionUser()) !== null;
  const tab = pickTab(one(query.tab));
  const tag = one(query.tag);
  const author = one(query.author);
  const page = Math.max(1, Number.parseInt(one(query.page), 10) || 1);

  const params = new URLSearchParams({ tab, page: String(page) });
  if (tag) params.set("tag", tag);
  if (author) params.set("author", author);

  const [data, tags] = await Promise.all([
    getWithSession<Paginated<Entry>>(`/blogs/?${params}`),
    getJson<{ tag: string; count: number }[]>("/blogs/tags/").catch(() => []),
  ]);

  const href = (next: Partial<Search>): Route => {
    const out = new URLSearchParams();
    const merged = { tab, tag, author, ...next };
    if (merged.tab && merged.tab !== "new") out.set("tab", merged.tab);
    if (merged.tag) out.set("tag", merged.tag);
    if (merged.author) out.set("author", merged.author);
    if (next.page && next.page !== "1") out.set("page", next.page);
    const text = out.toString();
    return (text ? `/blogs?${text}` : "/blogs") as Route;
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div className="space-y-1">
          <h1 className="text-title-sm font-bold rw-strong">{t(locale, "blogs.title")}</h1>
          <p className="text-theme-sm rw-dim">{t(locale, "blogs.description")}</p>
        </div>
        <Link
          href={"/blogs/new" as Route}
          className="inline-flex min-h-10 items-center rw-radius-sm rw-accent-bg px-4 text-theme-sm font-semibold rw-focus-ring"
        >
          {t(locale, "blogs.write")}
        </Link>
      </div>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_16rem]">
        <Card>
          <nav
            aria-label={t(locale, "blogs.tabsLabel")}
            className="flex flex-wrap gap-1 border-b rw-divider px-4"
          >
            {BLOG_TABS.filter((key) => key !== "following" || signedIn).map((key) => (
              <Link
                key={key}
                href={href({ tab: key, page: "1" })}
                aria-current={key === tab ? "page" : undefined}
                className={`-mb-px border-b-2 px-3 py-3 text-theme-sm font-medium rw-focus-ring ${
                  key === tab ? "rw-accent-line rw-accent-ink" : "border-transparent rw-dim rw-hover-strong"
                }`}
              >
                {t(locale, TAB_LABEL[key])}
              </Link>
            ))}
          </nav>

          {(tag || author) && (
            <p className="flex flex-wrap items-center gap-2 px-5 pt-4 text-theme-sm rw-dim">
              {tag && <span className="rw-chip rw-radius-sm px-2 py-0.5">#{tag}</span>}
              {author && <span className="rw-chip rw-radius-sm px-2 py-0.5">@{author}</span>}
              <Link href={href({ tag: "", author: "", page: "1" })} className="rw-link-hover rw-accent-ink">
                {t(locale, "blogs.clearFilter")}
              </Link>
            </p>
          )}

          {data.results.length === 0 ? (
            <div className="p-5">
              <EmptyState
                variant="card"
                title={t(locale, tab === "following" ? "blogs.emptyFollowing" : "blogs.empty")}
                hint={t(locale, "blogs.emptyHint")}
              />
            </div>
          ) : (
            <ul className="divide-y rw-divide px-5">
              {data.results.map((entry) => (
                <li key={entry.id}>
                  <EntryCard entry={entry} locale={locale} />
                </li>
              ))}
            </ul>
          )}

          <Pager
            locale={locale}
            page={page}
            count={data.count}
            pageSize={PAGE_SIZE}
            href={(next) => href({ page: String(next) })}
            label={t(locale, "blogs.unit")}
          />
        </Card>

        {tags.length > 0 && (
          <aside aria-labelledby="blog-tags" className="space-y-3">
            <h2 id="blog-tags" className="text-theme-sm font-semibold rw-strong">
              {t(locale, "blogs.popularTags")}
            </h2>
            <ul className="flex flex-wrap gap-2">
              {tags.map((row) => (
                <li key={row.tag}>
                  <Link
                    href={href({ tag: row.tag, page: "1" })}
                    aria-current={row.tag === tag ? "page" : undefined}
                    className="inline-flex min-h-8 items-center rw-chip rw-radius-sm px-2 text-theme-xs rw-link-hover"
                  >
                    #{row.tag} <span className="ms-1 rw-faint">{row.count}</span>
                  </Link>
                </li>
              ))}
            </ul>
          </aside>
        )}
      </div>
    </div>
  );
}
