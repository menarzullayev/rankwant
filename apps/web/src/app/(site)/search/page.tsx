import type { Metadata, Route } from "next";
import Link from "next/link";

import { describeHit } from "@/components/search/describe";
import { Highlight } from "@/components/search/Highlight";
import { Icon } from "@/components/ui/Icon";
import { Pager } from "@/components/ui/Pager";
import { fill, t, type Locale } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";
import { NAV } from "@/layout/nav";
import { api, ApiError } from "@/lib/api";
import {
  filterLocal,
  foldText,
  hitHref,
  hitIcon,
  isServerType,
  MIN_QUERY,
  sameHit,
  searchHref,
  SERVER_TYPES,
  type SearchGroup,
  type SearchHit,
  type ServerType,
} from "@/lib/search/model";

/** Rows per type on the mixed view, and per page of a single type. */
const ALL = "all" as const;
const MIXED = 10;
const PAGE_SIZE = 20;
/** The API stops paging here (`core.search.OFFSET_MAX`). */
const MAX_OFFSET = 500;
/** The server's "too many requests". */
const THROTTLED = 429;
/** Sections of the site offered next to the results. */
const PAGES = 4;

export async function generateMetadata(): Promise<Metadata> {
  // Result pages are as many as there are queries; none belongs in an index.
  return { title: t(await getLocale(), "search.title"), robots: { index: false } };
}

function first(value: string | string[] | undefined): string {
  return (Array.isArray(value) ? value[0] : value) ?? "";
}

function Row({ hit, query, locale, marked }: { hit: SearchHit; query: string; locale: Locale; marked: boolean }) {
  const text = describeHit(hit, locale);
  return (
    <li>
      <Link
        href={hitHref(hit) as Route}
        className="flex min-h-14 items-center gap-3 rw-radius border rw-line rw-surface px-3 py-2 transition rw-hover-line rw-focus-ring"
      >
        <span className="flex size-9 shrink-0 items-center justify-center rw-radius-sm border rw-line rw-dim-2">
          <Icon name={hitIcon(hit)} className="size-4" />
        </span>
        <span className="min-w-0 flex-1">
          <span className="block truncate text-theme-sm font-medium rw-strong">
            {marked ? <Highlight text={text.title} query={query} /> : text.title}
          </span>
          {text.subtitle && (
            <span className={`block text-theme-xs rw-dim ${text.quoted ? "line-clamp-2" : "truncate"}`}>
              {text.quoted ? <Highlight text={text.subtitle} query={query} /> : text.subtitle}
            </span>
          )}
        </span>
        {text.meta && <span className="shrink-0 font-mono text-theme-xs rw-dim">{text.meta}</span>}
      </Link>
    </li>
  );
}

function Section({
  group,
  query,
  locale,
  mixed,
  top,
}: {
  group: SearchGroup;
  query: string;
  locale: Locale;
  mixed: boolean;
  /** Shown above the groups already; left out of its own group. */
  top: SearchHit | null;
}) {
  const rows = top ? group.results.filter((hit) => !sameHit(hit, top)) : group.results;
  if (rows.length === 0) return null;
  const label = t(locale, `search.type.${group.type}`);
  const heading = group.fuzzy
    ? fill(t(locale, "search.fuzzy"), { label })
    : `${label} · ${group.count}`;
  return (
    <section className="space-y-2">
      <div className="flex min-h-9 items-center justify-between gap-3">
        <h2 className="text-theme-xs font-semibold tracking-wide rw-faint uppercase">{heading}</h2>
        {mixed && group.count > group.results.length && (
          <Link
            href={searchHref(query, group.type) as Route}
            className="rw-radius-sm px-2 py-1 text-theme-xs font-semibold rw-accent-ink rw-hover-bg rw-focus-ring"
          >
            {t(locale, "search.type.all")}
          </Link>
        )}
      </div>
      <ul className="space-y-2">
        {rows.map((hit) => (
          <Row
            key={`${hit.kind}-${hit.key}`}
            hit={hit}
            query={query}
            locale={locale}
            marked={!group.fuzzy}
          />
        ))}
      </ul>
    </section>
  );
}

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const locale = await getLocale();
  const raw = await searchParams;
  const query = first(raw.q).trim().slice(0, 80);
  const requested = first(raw.type);
  const type: "all" | ServerType = isServerType(requested) ? requested : ALL;
  const wanted = Number.parseInt(first(raw.page), 10);
  const page = Math.min(Math.max(1, Number.isFinite(wanted) ? wanted : 1), MAX_OFFSET / PAGE_SIZE + 1);
  const askable = foldText(query).length >= MIN_QUERY;

  const single = type !== "all";
  // `-1`: not refused. Otherwise the seconds the server asked us to wait.
  let wait = -1;
  const data = askable
    ? await api
        .search(query, type, single ? PAGE_SIZE : MIXED, single ? (page - 1) * PAGE_SIZE : 0)
        .catch((error: unknown) => {
          if (error instanceof ApiError && error.status === THROTTLED) wait = error.retryAfter;
          return null;
        })
    : null;
  const throttled = wait >= 0;
  // The one result the query names outright is shown once, above the rest.
  const top = data && page === 1 ? data.top : null;
  // Sections of the site that match — the first page of the mixed view
  // only: they are a way out of the search, not results to page through.
  const sections =
    askable && !single
      ? filterLocal(
          NAV.map((item) => ({ label: t(locale, item.key), href: item.href })),
          query,
        ).slice(0, PAGES)
      : [];

  const tabs: ("all" | ServerType)[] = ["all", ...SERVER_TYPES];
  const count = (tab: "all" | ServerType) =>
    data ? (tab === "all" ? data.total : data.counts[tab]) : 0;
  const group = single ? data?.groups[0] : undefined;
  const title = query ? fill(t(locale, "search.resultsFor"), { q: query }) : t(locale, "search.title");
  const summary = data ? fill(t(locale, "search.count"), { n: data.total }) : "";

  return (
    <div className="mx-auto w-full max-w-3xl space-y-5">
      <header className="space-y-1">
        <h1 className="text-title-sm font-bold break-words rw-strong">{title}</h1>
        {summary && <p className="text-theme-sm rw-dim">{summary}</p>}
      </header>

      <form action="/search" method="get" role="search" className="flex gap-2">
        <label className="min-w-0 flex-1">
          <span className="sr-only">{t(locale, "search.title")}</span>
          <input
            key={query}
            type="search"
            name="q"
            defaultValue={query}
            minLength={MIN_QUERY}
            maxLength={80}
            required
            autoComplete="off"
            placeholder={t(locale, "search.placeholderPage")}
            className="h-11 w-full border rw-line rw-field-bg px-3 text-theme-sm rw-strong rw-fm-inp rw-focus-ring"
          />
        </label>
        {single && <input type="hidden" name="type" value={type} />}
        <button
          type="submit"
          className="h-11 shrink-0 rw-radius-sm rw-accent-bg px-4 text-theme-sm font-semibold rw-focus-ring"
        >
          {t(locale, "search.submit")}
        </button>
      </form>

      {data && data.total > 0 && (
        <nav aria-label={t(locale, "search.typeLabel")} className="flex gap-2 overflow-x-auto py-1">
          {tabs
            .filter((tab) => tab === type || count(tab) > 0)
            .map((tab) => (
              <Link
                key={tab}
                href={searchHref(query, tab) as Route}
                aria-current={tab === type ? "page" : undefined}
                className={`inline-flex h-11 shrink-0 items-center gap-2 rounded-full border px-4 text-theme-sm whitespace-nowrap transition rw-focus-ring ${
                  tab === type
                    ? "rw-accent-bg font-semibold"
                    : "rw-divider rw-surface rw-dim-2 rw-hover-bg"
                }`}
              >
                {t(locale, `search.type.${tab}`)}
                <span className="font-mono text-theme-xs opacity-70">{count(tab)}</span>
              </Link>
            ))}
        </nav>
      )}

      {!askable && <p className="py-10 text-center text-theme-sm rw-dim">{t(locale, "search.minChars")}</p>}
      {askable && !data && (
        <p role="alert" className="py-10 text-center text-theme-sm rw-dim">
          {throttled
            ? wait > 0
              ? fill(t(locale, "search.throttledWait"), { n: wait })
              : t(locale, "search.throttled")
            : t(locale, "search.failed")}
        </p>
      )}

      {top && (
        <section className="space-y-2">
          <h2 className="text-theme-xs font-semibold tracking-wide rw-faint uppercase">
            {t(locale, "search.top")}
          </h2>
          <ul className="space-y-2">
            <Row hit={top} query={query} locale={locale} marked />
          </ul>
        </section>
      )}

      {sections.length > 0 && (
        <section className="space-y-2">
          <h2 className="text-theme-xs font-semibold tracking-wide rw-faint uppercase">
            {t(locale, "search.type.page")}
          </h2>
          <ul className="flex flex-wrap gap-2">
            {sections.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href as Route}
                  className="inline-flex h-11 items-center rounded-full border rw-divider rw-surface px-4 text-theme-sm rw-strong transition rw-hover-bg rw-focus-ring"
                >
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}
      {data && (single ? !group || group.results.length === 0 : data.groups.length === 0) && (
        <div className="py-10 text-center">
          <p className="text-theme-sm rw-strong">{fill(t(locale, "search.empty"), { q: query })}</p>
          <p className="mt-1 text-theme-xs rw-dim">{t(locale, "search.emptyHint")}</p>
        </div>
      )}

      {data && !single && data.groups.map((item) => (
        <Section key={item.type} group={item} query={query} locale={locale} mixed top={top} />
      ))}

      {group && group.results.length > 0 && (
        <>
          <Section group={group} query={query} locale={locale} mixed={false} top={top} />
          {!group.fuzzy && (
            <Pager
              locale={locale}
              page={page}
              count={Math.min(group.count, MAX_OFFSET + PAGE_SIZE)}
              pageSize={PAGE_SIZE}
              href={(next) => searchHref(query, type, next) as Route}
              label={t(locale, "search.unit")}
            />
          )}
        </>
      )}
    </div>
  );
}
