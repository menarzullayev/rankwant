import type { Metadata, Route } from "next";
import Link from "next/link";

import { EmptyState } from "@/components/ui/EmptyState";
import {
  CATEGORIES,
  CATEGORY_LABEL,
  GLOSSARY_PATH,
  LEVELS,
  LEVEL_LABEL,
  LibraryCard,
  isLevel,
} from "@/features/algorithms";
import { getLocale } from "@/i18n/server";
import { fill, t } from "@/i18n/messages";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";

type Props = { searchParams: Promise<Record<string, string | string[] | undefined>> };

const CHIP =
  "inline-flex min-h-9 items-center gap-1.5 rw-radius-full border rw-line px-3 text-theme-xs font-medium transition rw-hover-line rw-focus-ring";

export async function generateMetadata(): Promise<Metadata> {
  const locale = await getLocale();
  return {
    title: t(locale, "nav.algorithms"),
    description: t(locale, "algorithms.intro"),
    alternates: { canonical: "/algorithms" },
  };
}

/** The algorithms library (ADR-0062): every article by section, filtered by
 *  level. One request (`/articles/library/`), so the filter needs no paging. */
export default async function AlgorithmsPage({ searchParams }: Props) {
  const locale = await getLocale();
  const raw = (await searchParams).level;
  const level = isLevel(typeof raw === "string" ? raw : undefined) ? (raw as string) : null;
  const entries = await api.algorithmLibrary(locale);
  const shown = level ? entries.filter((entry) => entry.level === level) : entries;
  const groups = CATEGORIES.map((category) => ({
    category,
    rows: shown.filter((entry) => entry.category === category),
  })).filter((group) => group.rows.length > 0);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-title-sm font-bold rw-strong">{t(locale, "nav.algorithms")}</h1>
        <p className="mt-2 max-w-2xl text-theme-sm rw-dim">{t(locale, "algorithms.intro")}</p>
        {entries.length > 0 && (
          <p className="mt-1 flex flex-wrap gap-x-3 text-theme-xs rw-faint">
            <span>{fill(t(locale, "algorithms.count"), { count: shown.length })}</span>
            <Link href={GLOSSARY_PATH as Route} className="font-medium rw-accent-ink rw-focus-ring hover:underline">
              {t(locale, "algorithms.glossary.title")}
            </Link>
          </p>
        )}
      </header>

      {entries.length > 0 && (
        <nav aria-label={t(locale, "algorithms.levelFilter")} className="flex flex-wrap gap-2">
          <Link
            href={"/algorithms" as Route}
            aria-current={level === null ? "page" : undefined}
            className={`${CHIP} ${level === null ? "rw-accent-soft rw-accent-ink" : "rw-dim"}`}
          >
            {t(locale, "algorithms.level.all")}
          </Link>
          {LEVELS.map((item) => (
            <Link
              key={item}
              href={`/algorithms?level=${item}` as Route}
              aria-current={level === item ? "page" : undefined}
              className={`${CHIP} ${level === item ? "rw-accent-soft rw-accent-ink" : "rw-dim"}`}
            >
              {t(locale, LEVEL_LABEL[item])}
            </Link>
          ))}
        </nav>
      )}

      {groups.length > 1 && (
        <nav aria-label={t(locale, "algorithms.sections")} className="flex flex-wrap gap-2">
          {groups.map((group) => (
            <a key={group.category} href={`#cat-${group.category}`} className={`${CHIP} rw-dim`}>
              {t(locale, CATEGORY_LABEL[group.category])}
              <span className="rw-faint">{group.rows.length}</span>
            </a>
          ))}
        </nav>
      )}

      {groups.map((group) => (
        <section key={group.category} id={`cat-${group.category}`} className="space-y-3">
          <h2 className="text-theme-lg font-semibold rw-strong">
            <Link href={`/algorithms/${group.category}` as Route} className="rw-focus-ring hover:underline">
              {t(locale, CATEGORY_LABEL[group.category])}
            </Link>{" "}
            <span className="text-theme-sm font-normal rw-faint">{group.rows.length}</span>
          </h2>
          <ul className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {group.rows.map((entry) => (
              <li key={entry.slug}>
                <LibraryCard entry={entry} locale={locale} />
              </li>
            ))}
          </ul>
        </section>
      ))}

      {groups.length === 0 && (
        <EmptyState variant="card" title={t(locale, "common.empty")} hint={t(locale, "common.emptyHint")} />
      )}
    </div>
  );
}
