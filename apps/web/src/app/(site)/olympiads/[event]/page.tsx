import type { Metadata, Route } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { KEP_NAME, KIND_LABEL, ResultsTable, STATUS_LABEL, taskPath } from "@/features/olympiads";
import { inReaderAlphabet } from "@/i18n/alphabet";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";
import { api, ApiError, type OlympiadEvent } from "@/lib/api";

export const dynamic = "force-dynamic";

type Props = { params: Promise<{ event: string }> };

async function load(slug: string): Promise<OlympiadEvent | null> {
  try {
    return await api.olympiadEvent(slug);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return null;
    throw error;
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { event } = await params;
  const locale = await getLocale();
  const row = await load(event);
  if (row === null) return { title: t(locale, "olympiads.notFound") };
  return {
    title: inReaderAlphabet(row.title, "uz"),
    description: inReaderAlphabet(row.summary, "uz"),
    alternates: { canonical: `/olympiads/${row.slug}` },
  };
}

const LINK = "font-medium underline underline-offset-2 rw-accent-ink rw-focus-ring";

/** One olympiad event: what it was, its rounds' statements and its results. */
export default async function OlympiadEventPage({ params }: Props) {
  const { event: slug } = await params;
  const locale = await getLocale();
  const event = await load(slug);
  if (event === null) notFound();
  const facts = [
    { key: "olympiads.when" as const, value: event.date_label },
    { key: "olympiads.where" as const, value: event.location },
    { key: "olympiads.organizer" as const, value: event.organizer },
    { key: "olympiads.platform" as const, value: event.platform },
    { key: "olympiads.eligibility" as const, value: event.eligibility },
  ].filter((row) => row.value);
  const kind = KIND_LABEL[event.kind];
  const status = STATUS_LABEL[event.status];

  return (
    <article className="mx-auto max-w-5xl space-y-6">
      <nav aria-label={t(locale, "olympiads.breadcrumbs")} className="text-theme-sm rw-dim">
        <Link href={`/olympiads?season=${event.season}` as Route} className="rw-focus-ring hover:underline">
          {t(locale, "olympiads.title")}
        </Link>
      </nav>
      <header>
        <h1 className="text-title-sm font-bold rw-strong">{inReaderAlphabet(event.title, "uz")}</h1>
        <div className="mt-3 flex flex-wrap gap-2">
          {kind && <Badge color="info">{t(locale, kind)}</Badge>}
          {status && <Badge color="neutral">{t(locale, status)}</Badge>}
        </div>
        {event.description && (
          <p className="mt-3 max-w-3xl text-theme-sm rw-dim">{inReaderAlphabet(event.description, "uz")}</p>
        )}
      </header>

      {facts.length > 0 && (
        <dl className="grid gap-4 rw-radius border rw-line rw-surface p-5 sm:grid-cols-2">
          {facts.map((row) => (
            <div key={row.key}>
              <dt className="text-theme-xs font-semibold uppercase tracking-wide rw-faint">{t(locale, row.key)}</dt>
              <dd className="mt-1 text-theme-sm rw-strong">{inReaderAlphabet(row.value, "uz")}</dd>
            </div>
          ))}
        </dl>
      )}

      {event.sets.map((set) => (
        <Card key={set.slug} title={inReaderAlphabet(set.title, "uz")} bodyClassName="p-0">
          <ul className="rw-divide divide-y">
            {set.tasks.map((task) => (
              <li key={task.slug}>
                <Link
                  href={taskPath(event.slug, task.slug) as Route}
                  className="flex min-h-11 items-center gap-3 px-5 py-2.5 transition rw-hover-bg rw-focus-ring"
                >
                  <span className="w-6 shrink-0 text-theme-sm font-semibold rw-faint">{task.code}</span>
                  <span className="min-w-0 flex-1 truncate text-theme-sm font-medium rw-strong">
                    {inReaderAlphabet(task.title, "uz")}
                  </span>
                  {task.from_kep && <Badge color="neutral">{KEP_NAME}</Badge>}
                </Link>
              </li>
            ))}
          </ul>
        </Card>
      ))}

      {event.results.length > 0 && (
        <Card title={t(locale, "olympiads.results")} bodyClassName="p-0">
          <ResultsTable results={event.results} locale={locale} />
        </Card>
      )}

      {event.resources.length > 0 && (
        <section aria-labelledby="olympiad-resources" className="space-y-2">
          <h2 id="olympiad-resources" className="text-theme-base font-semibold rw-strong">
            {t(locale, "olympiads.resources")}
          </h2>
          <ul className="space-y-1 text-theme-sm">
            {event.resources.map((row) => (
              <li key={row.url}>
                <a href={row.url} target="_blank" rel="noopener noreferrer" className={LINK}>
                  {inReaderAlphabet(row.title, "uz")}
                  <span className="sr-only"> {t(locale, "footer.opensNewTab")}</span>
                </a>
              </li>
            ))}
          </ul>
        </section>
      )}

      <p className="text-theme-xs rw-faint">{t(locale, "olympiads.source")}</p>
    </article>
  );
}
